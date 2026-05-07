"""Anthropic API wrapper: send report pages, get structured EchoData back."""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

import anthropic
from pydantic import ValidationError

from .schema import EXTRACTION_PROMPT, EchoData

if TYPE_CHECKING:
    from .images import ImageFile

log = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_BACKOFF = 2.0  # seconds


def _build_messages(encoded_pages: list[tuple[str, str]], schema_json: str, n_pages: int) -> list[dict]:
    content: list[dict] = []
    for b64_data, media_type in encoded_pages:
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": b64_data},
        })
    prompt = EXTRACTION_PROMPT.format(n_pages=n_pages, schema_json=schema_json)
    content.append({"type": "text", "text": prompt})
    return [{"role": "user", "content": content}]


def extract_patient(
    client: anthropic.Anthropic,
    encoded_pages: list[tuple[str, str]],
    patient_id: str,
    model: str,
    responses_dir: Path,
) -> tuple[EchoData, dict]:
    """Call the API, parse the response, return (EchoData, usage_dict).

    Retries up to MAX_RETRIES times on rate-limit / transient errors.
    Saves the raw JSON response to responses_dir/{patient_id}.json.
    """
    schema_json = json.dumps(EchoData.model_json_schema(), indent=2)
    messages = _build_messages(encoded_pages, schema_json, len(encoded_pages))

    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.debug("API call attempt %d/%d for %s", attempt, MAX_RETRIES, patient_id)
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0,
                messages=messages,
            )
            break
        except anthropic.RateLimitError as e:
            wait = BASE_BACKOFF ** attempt
            log.warning("Rate limit hit (attempt %d). Retrying in %.1fs", attempt, wait)
            time.sleep(wait)
            last_error = e
        except anthropic.APIError as e:
            if attempt < MAX_RETRIES:
                wait = BASE_BACKOFF ** attempt
                log.warning("API error %s (attempt %d). Retrying in %.1fs", e, attempt, wait)
                time.sleep(wait)
                last_error = e
            else:
                raise
    else:
        raise last_error  # type: ignore[misc]

    raw_text = response.content[0].text.strip()

    # Strip accidental markdown fences
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[-1]
        if raw_text.endswith("```"):
            raw_text = raw_text[: raw_text.rfind("```")]

    # Save raw response for audit
    responses_dir.mkdir(parents=True, exist_ok=True)
    (responses_dir / f"{patient_id}.json").write_text(raw_text, encoding="utf-8")

    try:
        data = EchoData.model_validate_json(raw_text)
    except ValidationError as e:
        log.error("Schema validation failed for %s: %s", patient_id, e)
        raise

    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    log.info(
        "Patient %s: %d input tokens, %d output tokens",
        patient_id, usage["input_tokens"], usage["output_tokens"],
    )
    return data, usage
