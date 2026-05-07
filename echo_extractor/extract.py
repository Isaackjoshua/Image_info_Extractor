"""CLI entry point for the Echocardiogram Report → Excel Extractor."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import shutil
import time
from pathlib import Path

import anthropic

from .api_client import extract_patient
from .grouping import group_by_patient
from .images import encode_page, filter_report_pages
from .state import ProcessingState
from .writer import append_patient_row, verify_rows

log = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_CONCURRENCY = 3

# Sonnet-4 approximate pricing (USD per million tokens)
INPUT_PRICE_PER_M = 3.0
OUTPUT_PRICE_PER_M = 15.0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract echocardiogram measurements from TIFF report pages into xlsx."
    )
    p.add_argument("--images", required=True, type=Path, metavar="DIR",
                   help="Directory containing .tif files")
    p.add_argument("--xlsx", required=True, type=Path, metavar="FILE",
                   help="Path to the xlsx template (read/write in-place)")
    p.add_argument("--output", type=Path, metavar="FILE",
                   help="Write results here instead of modifying --xlsx in-place")
    p.add_argument("--api-key", metavar="KEY",
                   help="Anthropic API key (default: ANTHROPIC_API_KEY env var)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"Claude model to use (default: {DEFAULT_MODEL})")
    p.add_argument("--dry-run", action="store_true",
                   help="Parse and group images but make no API calls and write nothing")
    p.add_argument("--limit", type=int, metavar="N",
                   help="Process only the first N patients (for testing)")
    p.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, metavar="N",
                   help=f"Max patients processed in parallel (default: {DEFAULT_CONCURRENCY})")
    p.add_argument("--allow-duplicate", action="store_true",
                   help="Re-process patients already in state.json (writes a second row)")
    p.add_argument("--verify", action="store_true",
                   help="After writing, print a summary table with range checks")
    p.add_argument("--verbose", action="store_true",
                   help="Enable DEBUG logging")

    crop_g = p.add_mutually_exclusive_group()
    crop_g.add_argument("--crop-phi", dest="crop_phi", action="store_true", default=True,
                        help="Crop top 5%% of each page to remove PHI header (default: ON)")
    crop_g.add_argument("--no-crop-phi", dest="crop_phi", action="store_false",
                        help="Disable PHI cropping")

    return p.parse_args()


async def _process_patient(
    sem: asyncio.Semaphore,
    patient_id: str,
    image_files,
    client: anthropic.Anthropic,
    model: str,
    crop_phi: bool,
    xlsx_path: Path,
    output_path: Path,
    responses_dir: Path,
    state: ProcessingState,
) -> dict:
    """Process one patient under the semaphore. Returns a result dict."""
    async with sem:
        log.info("Processing patient %s", patient_id)
        t0 = time.monotonic()

        report_pages = filter_report_pages(image_files)
        if not report_pages:
            log.error("Patient %s: no report pages found — skipping", patient_id)
            return {"patient_id": patient_id, "status": "no_report_pages", "tokens": 0}

        # Encode images in a thread so we don't block the event loop
        loop = asyncio.get_event_loop()
        encoded = await loop.run_in_executor(
            None,
            lambda: [encode_page(p.path, crop_phi) for p in report_pages],
        )

        try:
            data, usage = await loop.run_in_executor(
                None,
                lambda: extract_patient(client, encoded, patient_id, model, responses_dir),
            )
        except Exception as e:
            log.error("Patient %s: extraction failed: %s", patient_id, e)
            return {"patient_id": patient_id, "status": "failed", "tokens": 0, "error": str(e)}

        append_patient_row(data, xlsx_path, output_path)
        state.mark_processed(patient_id)

        elapsed = time.monotonic() - t0
        total_tokens = usage["input_tokens"] + usage["output_tokens"]
        log.info("Patient %s done in %.1fs (%d tokens)", patient_id, elapsed, total_tokens)
        return {
            "patient_id": patient_id,
            "status": "ok",
            "tokens": total_tokens,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
        }


async def _run(args: argparse.Namespace) -> None:
    # Resolve output path
    output_path = args.output if args.output else args.xlsx

    # If output differs from xlsx, copy template first so we have the headers
    if args.output and not args.output.exists():
        shutil.copy2(args.xlsx, args.output)
        log.info("Copied template to %s", args.output)

    state = ProcessingState(Path("state.json"))
    groups = group_by_patient(args.images)

    # Determine which patients to process
    patients = sorted(groups.keys())
    if args.limit:
        patients = patients[: args.limit]

    if args.dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN — no API calls will be made")
        print(f"Images dir : {args.images}")
        print(f"xlsx       : {args.xlsx}")
        print(f"Output     : {output_path}")
        print(f"Model      : {args.model}")
        print(f"Crop PHI   : {args.crop_phi}")
        print(f"Concurrency: {args.concurrency}")
        print(f"\nFound {len(groups)} patient(s):\n")
        for pid in patients:
            imgs = groups[pid]
            report_pages = filter_report_pages(imgs)
            already = state.is_processed(pid)
            print(
                f"  {pid}  total={len(imgs)}  report_pages={len(report_pages)}"
                + ("  [ALREADY PROCESSED]" if already else "")
            )
        print(f"\n{'='*60}\n")
        return

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY not set. Use --api-key or set the env var.")

    client = anthropic.Anthropic(api_key=api_key)
    responses_dir = Path("responses")
    sem = asyncio.Semaphore(args.concurrency)

    # Filter patients
    to_process = []
    for pid in patients:
        if state.is_processed(pid) and not args.allow_duplicate:
            log.warning("Patient %s already processed — skipping (use --allow-duplicate to override)", pid)
            continue
        to_process.append(pid)

    if not to_process:
        log.info("No new patients to process.")
        return

    tasks = [
        _process_patient(
            sem, pid, groups[pid], client, args.model,
            args.crop_phi, args.xlsx, output_path, responses_dir, state,
        )
        for pid in to_process
    ]

    results = await asyncio.gather(*tasks)

    # Summary
    successes = [r for r in results if r["status"] == "ok"]
    failures = [r for r in results if r["status"] != "ok"]
    total_input = sum(r.get("input_tokens", 0) for r in successes)
    total_output = sum(r.get("output_tokens", 0) for r in successes)
    avg_tokens = (sum(r["tokens"] for r in successes) / len(successes)) if successes else 0
    cost = (total_input / 1_000_000) * INPUT_PRICE_PER_M + (total_output / 1_000_000) * OUTPUT_PRICE_PER_M

    summary = (
        f"Run summary\n"
        f"===========\n"
        f"Patients attempted : {len(to_process)}\n"
        f"Successes          : {len(successes)}\n"
        f"Failures           : {len(failures)}\n"
        f"Avg tokens/patient : {avg_tokens:.0f}\n"
        f"Total input tokens : {total_input}\n"
        f"Total output tokens: {total_output}\n"
        f"Estimated cost     : ${cost:.4f}\n"
    )
    if failures:
        summary += "\nFailed patients:\n"
        for r in failures:
            summary += f"  {r['patient_id']}: {r.get('error', r['status'])}\n"

    print("\n" + summary)
    Path("run_summary.txt").write_text(summary, encoding="utf-8")

    if args.verify and successes:
        verify_rows(output_path)


def main() -> None:
    args = _parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
