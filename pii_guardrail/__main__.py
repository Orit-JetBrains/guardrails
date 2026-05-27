"""CLI entry point: python -m pii_guardrail "your prompt here" """

import argparse
import json
import sys

from . import validate_prompt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a prompt for PII using Microsoft Presidio."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Prompt text to validate (or read from stdin if omitted)",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="en",
        help="Language code (default: en)",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    args = parser.parse_args()

    if args.prompt is None:
        prompt = sys.stdin.read()
    else:
        prompt = args.prompt

    result = validate_prompt(prompt, language=args.language)

    if args.json:
        out = {
            "valid": result.valid,
            "message": result.message,
            "findings": [
                {
                    "entity_type": f.entity_type,
                    "start": f.start,
                    "end": f.end,
                    "score": f.score,
                    "text": f.text,
                }
                for f in result.findings
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        status = "PASS" if result.valid else "FAIL"
        print(f"{status}: {result.message}")
        for f in result.findings:
            print(f"  - {f.entity_type}: {f.text!r}")

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
