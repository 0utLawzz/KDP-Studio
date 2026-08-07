#!/usr/bin/env python3
"""Run the generator safe-margin matrix for the validation stage.

The stage matrix deliberately covers the five palettes copied from
generate_template.py plus the three existing generator treatments, across
all supported trim sizes.  Both PDF generators run for every case.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from argparse import Namespace
from pathlib import Path


PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import generate_cover  # noqa: E402
import generate_interior  # noqa: E402
from text_bounds import TextBoundsError  # noqa: E402


MATRIX_PALETTES = (
    "lavender_mint",
    "sage_teal",
    "bright_momentum",
    "cobalt_coral",
    "sunshine_mint",
    "berry_pop",
    "ocean_lime",
    "tangerine_sky",
)
TRIM_SIZES = ("6x9", "5x8", "8.5x11")


def _cover_args(output, palette, trim_size):
    return Namespace(
        output=str(output),
        title="My Daily Planner",
        subtitle="A thoughtful daily companion",
        author_name="Bright Mindful Pages",
        color_palette=palette,
        trim_size=trim_size,
        page_count=84,
        day_count=60,
    )


def _interior_args(output, palette, trim_size):
    return Namespace(
        output=str(output),
        title="My Daily Planner",
        author_name="Bright Mindful Pages",
        book_type="default",
        color_palette=palette,
        trim_size=trim_size,
        day_count=60,
        interior_type="full_color",
        include_habit_tracker=True,
        include_weekly_review=True,
    )


def _run_case(generator_name, palette, trim_size, output):
    try:
        if generator_name == "cover":
            generate_cover.generate_cover(
                _cover_args(output, palette, trim_size), str(output)
            )
        else:
            generate_interior.generate_interior(
                _interior_args(output, palette, trim_size), str(output)
            )
    except TextBoundsError as error:
        return "FAIL", error.overflow, str(error)
    except Exception as error:  # Keep the matrix report useful for non-margin failures.
        return "FAIL", None, f"{type(error).__name__}: {error}"
    return "PASS", 0.0, ""


def run_matrix():
    rows = []
    with tempfile.TemporaryDirectory(prefix="kdp-generator-matrix-") as temp_dir:
        for palette in MATRIX_PALETTES:
            for trim_size in TRIM_SIZES:
                for generator_name in ("cover", "interior"):
                    output = Path(temp_dir) / f"{generator_name}-{palette}-{trim_size}.pdf"
                    status, overflow, detail = _run_case(
                        generator_name, palette, trim_size, output
                    )
                    rows.append(
                        {
                            "generator": generator_name,
                            "palette": palette,
                            "trim_size": trim_size,
                            "status": status,
                            "overflow": overflow,
                            "detail": detail,
                        }
                    )
    return rows


def print_report(rows):
    print(
        "Generator safe-margin matrix: "
        f"{len(MATRIX_PALETTES)} palettes × {len(TRIM_SIZES)} trims × 2 generators"
    )
    print("Palettes: " + ", ".join(MATRIX_PALETTES))
    print()
    headers = ("generator", "palette", "trim", "result", "overflow", "details")
    print(" | ".join(headers))
    print("-+-".join("-" * len(header) for header in headers))
    for row in rows:
        overflow = (
            f"{row['overflow']:.2f}pt"
            if row["overflow"] is not None
            else "n/a"
        )
        print(
            " | ".join(
                (
                    row["generator"],
                    row["palette"],
                    row["trim_size"],
                    row["status"],
                    overflow,
                    row["detail"] or "-",
                )
            )
        )
    print()
    passed = sum(row["status"] == "PASS" for row in rows)
    failed = len(rows) - passed
    print(f"Summary: {passed} passed, {failed} failed")
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Retained for CLI compatibility; the matrix always prints its report.",
    )
    parser.parse_args()
    failed = print_report(run_matrix())
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())