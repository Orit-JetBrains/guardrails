# PII Guardrail

A small guardrail that validates prompts (or any text) for **no PII** using [Microsoft Presidio](https://microsoft.github.io/presidio/). If PII is detected, validation fails and you get details on what was found.

## Setup

1. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_lg
   ```

   Or install the project in editable mode (so `pii_guardrail` is importable):

   ```bash
   pip install -e .
   python -m spacy download en_core_web_lg
   ```

   Presidio’s analyzer uses spaCy for NER; the `en_core_web_lg` model is required for English.

## Usage

### Python API

```python
from pii_guardrail import validate_prompt, GuardrailResult, PIIGuardrail

# One-off check
result: GuardrailResult = validate_prompt("What is the capital of France?")
assert result.valid
print(result.message)  # "No PII detected. Prompt is safe."

# Prompt with PII
result = validate_prompt("Call John at 212-555-5555 or email john@example.com.")
assert not result.valid
for f in result.findings:
    print(f.entity_type, f.text)  # e.g. PHONE_NUMBER, EMAIL_ADDRESS

# Reusable guardrail (e.g. in a server)
guardrail = PIIGuardrail(language="en")
guardrail.validate("User input here")
guardrail.get_supported_entities()  # list of PII types checked
```

### CLI

Validate a string:

```bash
python -m pii_guardrail "Your prompt text here"
# PASS: No PII detected. Prompt is safe.
# or
# FAIL: PII detected: EMAIL_ADDRESS, PHONE_NUMBER. Found 2 occurrence(s).
```

Pipe text:

```bash
echo "Contact 212-555-5555" | python -m pii_guardrail
```

JSON output (exit code 0 = no PII, 1 = PII found):

```bash
python -m pii_guardrail -j "My SSN is 123-45-6789"
```

### Example script

```bash
python example_usage.py
```

## Integration idea

Use the guardrail before sending the user prompt to your LLM or logging pipeline:

```python
from pii_guardrail import validate_prompt

def handle_user_prompt(prompt: str) -> str:
    result = validate_prompt(prompt)
    if not result.valid:
        raise ValueError(f"Prompt contains PII: {result.message}")
    return call_llm(prompt)
```

## Supported PII

Presidio detects many entity types (names, phones, emails, SSN, credit cards, locations, etc.). Full list:

```python
from pii_guardrail import PIIGuardrail
print(PIIGuardrail().get_supported_entities())
```

You can restrict checks to specific entities via `PIIGuardrail(entities=["EMAIL_ADDRESS", "PHONE_NUMBER"])` or `validate_prompt(..., entities=[...])`.

## License

Use Presidio according to its license; this wrapper is provided as-is.
