#!/usr/bin/env python3
"""Example: validate prompts for PII using the PII guardrail."""

from pii_guardrail import validate_prompt, PIIGuardrail

# One-off validation
safe_prompt = "What is the capital of France?"
result = validate_prompt(safe_prompt)
print(f"Prompt: {safe_prompt!r}")
print(f"Valid: {result.valid} — {result.message}\n")

# Prompt that contains PII
pii_prompt = "Call John Smith at 212-555-5555 or email john.smith@example.com."
result2 = validate_prompt(pii_prompt)
print(f"Prompt: {pii_prompt!r}")
print(f"Valid: {result2.valid} — {result2.message}")
for f in result2.findings:
    print(f"  - {f.entity_type}: {f.text!r} (score={f.score:.2f})")

# Reusable guardrail instance (e.g. in a server)
guardrail = PIIGuardrail(language="en")
print("\nSupported PII entities:", guardrail.get_supported_entities()[:10], "...")
