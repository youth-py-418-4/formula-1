#!/usr/bin/env python3
"""Parse telemetry-only Formula 1 data from a local TracingInsights dataset into CSV files.

The downloaded dataset stores each Grand Prix as a folder tree:

    <Grand Prix>/<Session>/<Driver>/*.json

Most JSON files are table-shaped dictionaries where each key contains a list of
equal-length values. This script reads only telemetry lap files from the local
dataset (plus the session-level drivers.json), normalizes them into rows, and
writes CSV files that are convenient for Power BI.

Examples:

    python download_gp_to_csv.py --grand-prix "Australian Grand Prix" --output australian_gp_telemetry.csv
    python download_gp_to_csv.py --grand-prix "Australian Grand Prix" --session Race --output race_telemetry.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DEFAULT_DATA_ROOT = Path("data")


@dataclass(frozen=True)
class SourceFile:
    path: str
    local_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse telemetry-only data from a single Grand Prix and flatten it into CSV files."
    )
    parser.add_argument(
        "--grand-prix",
        required=True,
        help='Grand Prix folder name, for example "Australian Grand Prix".',
    )
    parser.add_argument(
        "--session",
        default=None,
        help='Optional session folder name, for example "Race" or "Qualifying". Defaults to all sessions.',
    )
    parser.add_argument(
        "--data-root",
        default=str(DEFAULT_DATA_ROOT),
        help=f"Local dataset root folder. Default: {DEFAULT_DATA_ROOT}",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging to stderr.",
    )
    return parser.parse_args()


def list_json_files(base_path: Path, root_path: Path) -> List[SourceFile]:
    logger = logging.getLogger(__name__)
    logger.info("Listing directory: %s", base_path)
    files: List[SourceFile] = []
    for path in sorted(base_path.iterdir()):
        if path.is_dir():
            files.extend(list_json_files(path, root_path))
        elif path.is_file() and path.name.lower().endswith("_tel.json"):
            files.append(SourceFile(path=path.relative_to(root_path).as_posix(), local_path=path))

    return files


def flatten_scalar_dict(value: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    flattened: Dict[str, Any] = {}
    for key, item in value.items():
        column = f"{prefix}{key}" if prefix else str(key)
        if isinstance(item, dict):
            flattened.update(flatten_scalar_dict(item, prefix=f"{column}."))
        elif isinstance(item, list):
            flattened[column] = json.dumps(item, ensure_ascii=False)
        else:
            flattened[column] = item
    return flattened


def unwrap_single_nested_dict(payload: Any) -> Any:
    while isinstance(payload, dict) and len(payload) == 1:
        only_value = next(iter(payload.values()))
        if isinstance(only_value, dict):
            payload = only_value
        else:
            break
    return payload


def rowify_json(payload: Any) -> List[Dict[str, Any]]:
    payload = unwrap_single_nested_dict(payload)

    if isinstance(payload, list):
        rows: List[Dict[str, Any]] = []
        for index, item in enumerate(payload):
            if isinstance(item, dict):
                row = flatten_scalar_dict(item)
            else:
                row = {"value": item}
            row["row_index"] = index
            rows.append(row)
        return rows

    if not isinstance(payload, dict):
        return [{"value": payload, "row_index": 0}]

    list_columns = [key for key, value in payload.items() if isinstance(value, list)]
    row_count = max((len(payload[key]) for key in list_columns), default=1)

    rows: List[Dict[str, Any]] = []
    for index in range(row_count):
        row: Dict[str, Any] = {"row_index": index}
        for key, value in payload.items():
            if isinstance(value, list):
                row[key] = value[index] if index < len(value) else None
            elif isinstance(value, dict):
                nested = flatten_scalar_dict(value, prefix=f"{key}.")
                if len(nested) == 1 and next(iter(nested.keys())).endswith("value"):
                    row[key] = next(iter(nested.values()))
                else:
                    row.update(nested)
            else:
                row[key] = value
        rows.append(row)

    return rows


def normalize_csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def load_rows_for_file(source_file: SourceFile, grand_prix: str) -> List[Dict[str, Any]]:
    logger = logging.getLogger(__name__)
    logger.info("Downloading: %s", source_file.path)
    with source_file.local_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    rows = rowify_json(payload)
    # Derive session, driver and lap from the source path
    parts = source_file.path.split("/")
    # expected pattern: <Grand Prix>/<Session>/<Driver>/<file>
    session_name = parts[1] if len(parts) > 1 else ""
    driver_code = parts[2] if len(parts) > 2 else ""
    stem = Path(source_file.path).stem

    # try to infer lap number from file stem like "1_tel" -> 1
    lap_number: Optional[int]
    try:
        lap_part = stem.split("_")[0]
        lap_number = int(lap_part)
    except Exception:
        lap_number = None

    for row in rows:
        # Keep only the useful contextual columns for telemetry
        row["grand_prix"] = grand_prix
        row["session"] = session_name
        row["driver"] = driver_code
        row["lap"] = lap_number

        # Remove helper / internal columns the user requested to drop
        for drop in ("row_index", "data_key", "source_path", "source_file", "record_name", "repo", "ref"):
            row.pop(drop, None)

    logger.info("Produced %d rows from %s", len(rows), source_file.path)
    return rows


def write_csv(rows: Iterable[Dict[str, Any]], output_path: Path) -> None:
    all_rows = list(rows)
    if not all_rows:
        raise RuntimeError("No rows were produced. Check the Grand Prix/session name.")

    fieldnames: List[str] = []
    seen = set()
    for row in all_rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    logger = logging.getLogger(__name__)
    logger.info("Writing %d rows to %s", len(all_rows), output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in all_rows:
            writer.writerow({key: normalize_csv_value(value) for key, value in row.items()})
    logger.info("Finished writing CSV.")


def write_drivers_csv(payload: Any, output_path: Path) -> None:
    """Write drivers JSON (list or dict) to CSV in a best-effort flattened form."""
    logger = logging.getLogger(__name__)
    if isinstance(payload, dict) and len(payload) == 1:
        only_value = next(iter(payload.values()))
        if isinstance(only_value, (list, dict)):
            payload = only_value
    payload = unwrap_single_nested_dict(payload)
    rows: List[Dict[str, Any]] = []
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                rows.append(flatten_scalar_dict(item))
            else:
                rows.append({"value": item})
    elif isinstance(payload, dict):
        for key, val in payload.items():
            row = {"code": key}
            if isinstance(val, dict):
                row.update(flatten_scalar_dict(val))
            else:
                row["value"] = val
            rows.append(row)
    else:
        raise RuntimeError("Unsupported drivers.json format")

    if not rows:
        logger.warning("drivers.json empty or produced no rows")
        return

    # determine fieldnames preserving order seen
    fieldnames: List[str] = []
    seen = set()
    for row in rows:
        for k in row.keys():
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: normalize_csv_value(v) for k, v in row.items()})
    logger.info("Wrote drivers CSV to %s", output_path)


def main() -> int:
    args = parse_args()
    # Configure logging early so subsequent calls emit output
    level = logging.DEBUG if getattr(args, "verbose", False) else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s: %(message)s", stream=sys.stderr)
    logger = logging.getLogger(__name__)
    logger.info("Starting downloader for: %s", args.grand_prix)
    data_root = Path(args.data_root)
    if not data_root.exists():
        logger.error("Local data root does not exist: %s", data_root)
        return 1
    base_path = data_root / args.grand_prix
    if args.session:
        base_path = base_path / args.session.strip("/")
    if not base_path.exists():
        logger.error("Grand Prix/session folder does not exist: %s", base_path)
        return 1
    source_files = list_json_files(base_path, data_root)

    if not source_files:
        logger.error(
            "No telemetry JSON files found under %r. Check the Grand Prix and session names.",
            args.grand_prix,
        )
        return 1

    all_rows: List[Dict[str, Any]] = []
    for idx, source_file in enumerate(source_files, start=1):
        logger.info("Processing file %d/%d: %s", idx, len(source_files), source_file.path)
        try:
            all_rows.extend(load_rows_for_file(source_file, args.grand_prix))
        except Exception as exc:
            logger.exception("Failed while processing %s: %s", source_file.path, exc)
            raise RuntimeError(f"Failed while processing {source_file.path}: {exc}") from exc

    # Prepare Grand Prix folder and write drivers.csv from the local dataset
    gp_slug = args.grand_prix.strip("/").replace(" ", "_")
    gp_dir = Path(gp_slug)
    gp_dir.mkdir(parents=True, exist_ok=True)

    drivers_path = base_path / "drivers.json"
    if drivers_path.exists():
        try:
            logger.info("Reading drivers metadata from %s", drivers_path)
            with drivers_path.open("r", encoding="utf-8") as handle:
                drivers_payload = json.load(handle)
            drivers_csv_path = gp_dir / "drivers.csv"
            write_drivers_csv(drivers_payload, drivers_csv_path)
        except Exception as exc:
            logger.info("Failed to parse drivers.json: %s", exc)
    else:
        logger.info("No drivers.json found at %s", drivers_path)

    # Decide telemetry CSV output path: place inside gp_dir with provided filename
    output_name = Path(args.output).name
    telemetry_out = gp_dir / output_name
    write_csv(all_rows, telemetry_out)
    logger.info("Wrote %d telemetry rows from %d lap files to %s", len(all_rows), len(source_files), telemetry_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
