# Echocardiogram Report → Excel Extractor

A Python CLI tool that extracts structured measurements from echocardiogram "Adult Echo Report" TIFF pages using the Anthropic Claude vision API and appends one row per patient to an existing Excel template.

---

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Requires **Python 3.11+**.

---

## Environment setup

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or pass it directly with `--api-key`.

---

## Usage

### Basic run

```bash
python3 -m echo_extractor.extract \
  --images /path/to/tiff/directory \
  --xlsx   SAMPLE.xlsx
```

Results are appended in-place to `SAMPLE.xlsx`. A `state.json` tracks which patients have been processed so the same patient is never written twice.

### Write to a separate output file

```bash
python3 -m echo_extractor.extract \
  --images /path/to/tiffs \
  --xlsx   SAMPLE.xlsx \
  --output results.xlsx
```

### Dry run (no API calls, no writes)

```bash
python3 -m echo_extractor.extract \
  --images . \
  --xlsx   SAMPLE.xlsx \
  --dry-run
```

### Test with one patient

```bash
python3 -m echo_extractor.extract \
  --images /path/to/tiffs \
  --xlsx   SAMPLE.xlsx \
  --limit 1 --verbose
```

### Verify extracted values

```bash
python3 -m echo_extractor.extract \
  --images /path/to/tiffs \
  --xlsx   SAMPLE.xlsx \
  --verify
```

Prints a range-check table for the first 5 rows after writing.

### Re-process a patient

```bash
python3 -m echo_extractor.extract \
  --images /path/to/tiffs \
  --xlsx   SAMPLE.xlsx \
  --allow-duplicate
```

---

## Options

| Flag | Default | Description |
|---|---|---|
| `--images DIR` | required | Directory of `.tif` files |
| `--xlsx FILE` | required | xlsx template — read and written in-place |
| `--output FILE` | same as `--xlsx` | Write to a different file |
| `--api-key KEY` | `ANTHROPIC_API_KEY` | Anthropic API key |
| `--model MODEL` | `claude-sonnet-4-6` | Claude model |
| `--dry-run` | off | Parse only, no API calls |
| `--limit N` | all | Process only first N patients |
| `--concurrency N` | 3 | Parallel patients |
| `--allow-duplicate` | off | Re-process already-processed patients |
| `--crop-phi / --no-crop-phi` | crop on | Remove top 5% of each page (PHI header) |
| `--verify` | off | Print range-check table after writing |
| `--verbose` | off | DEBUG logging |

---

## PHI handling

By default (`--crop-phi` is ON), the top ~5% of each report page — the strip containing the patient name and ID — is cropped before the image is sent to the API. The patient ID used for state tracking and file grouping is read from the **filename**, not from the image.

To disable cropping:

```bash
python3 -m echo_extractor.extract --images . --xlsx SAMPLE.xlsx --no-crop-phi
```

---

## How it works

1. All `.tif` files in the `--images` directory are grouped by patient ID (parsed from filenames).
2. Per patient, only **report pages** (1024×768 pixels) are selected. Ultrasound scan pages (1152×864) are ignored.
3. Each patient's 4 report pages are encoded as PNG, optionally cropped, and sent in a single Anthropic API call.
4. The model returns JSON matching the `EchoData` Pydantic schema.
5. The JSON is validated and written to the next empty row of the xlsx.
6. The patient ID is added to `state.json` to prevent duplicate processing.
7. Raw API responses are saved to `./responses/<patient_id>.json` for auditing.

---

## Expected runtime and cost

| Metric | Estimate |
|---|---|
| Tokens per patient | ~8 000–14 000 input, ~500–1 000 output |
| Runtime per patient | ~10–20 seconds |
| Cost per patient (Sonnet-4) | ~$0.03–0.05 |
| Cost per 100 patients | ~$3–5 |

---

## Resumability

Running the tool again with the same `--images` directory skips patients already in `state.json`. To process a new batch of patients, just point `--images` at a directory containing only the new patients' files and use the same `--xlsx`.

---

## Running tests

```bash
python3 -m pytest tests/ -v
```
