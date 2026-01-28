#!/usr/bin/env python3
"""
Convert MTBench question.jsonl to simple {input: "..."} format.

By default, extracts only the first turn from each question.
Use --all-turns to create separate entries for each turn.
"""

import json
import argparse
from pathlib import Path


def convert_mtbench(input_file: str, output_file: str, all_turns: bool = False):
    """Convert MTBench format to simple input format."""

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    output_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        data = json.loads(line)
        turns = data.get("turns", [])

        if all_turns:
            # Create separate entry for each turn
            for turn in turns:
                output_lines.append(json.dumps({"input": turn}, ensure_ascii=False))
        else:
            # Only use the first turn
            if turns:
                output_lines.append(json.dumps({"input": turns[0]}, ensure_ascii=False))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        if output_lines:
            f.write("\n")

    print(f"Converted {len(lines)} questions to {len(output_lines)} entries")
    print(f"Output written to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert MTBench to simple input format"
    )
    parser.add_argument("input_file", help="Input MTBench JSONL file")
    parser.add_argument("output_file", help="Output JSONL file")
    parser.add_argument(
        "--all-turns",
        action="store_true",
        help="Include all turns as separate entries (default: first turn only)",
    )

    args = parser.parse_args()
    convert_mtbench(args.input_file, args.output_file, args.all_turns)


if __name__ == "__main__":
    main()
