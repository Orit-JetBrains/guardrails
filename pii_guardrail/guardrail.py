"""PII Guardrail: validate that a prompt contains no PII using Microsoft Presidio."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer import RecognizerResult


@dataclass
class PIIFinding:
    """A single PII entity detected in text."""

    entity_type: str
    start: int
    end: int
    score: float
    text: str

    @classmethod
    def from_recognizer_result(cls, result: RecognizerResult, text: str) -> "PIIFinding":
        return cls(
            entity_type=result.entity_type,
            start=result.start,
            end=result.end,
            score=result.score,
            text=text[result.start : result.end],
        )


@dataclass
class GuardrailResult:
    """Result of PII validation."""

    valid: bool
    """True if no PII was detected."""
    findings: List[PIIFinding] = field(default_factory=list)
    """PII entities found (empty when valid is True)."""
    message: str = ""
    """Human-readable summary."""

    def __post_init__(self) -> None:
        if not self.message:
            if self.valid:
                self.message = "No PII detected. Prompt is safe."
            else:
                types = {f.entity_type for f in self.findings}
                self.message = f"PII detected: {', '.join(sorted(types))}. Found {len(self.findings)} occurrence(s)."


class PIIGuardrail:
    """
    Guardrail that validates prompts for absence of PII using Microsoft Presidio.
    """

    def __init__(
        self,
        language: str = "en",
        entities: List[str] | None = None,
    ) -> None:
        """
        Initialize the guardrail.

        Args:
            language: Language code for analysis (default: "en").
            entities: PII entity types to check. If None, all supported entities are checked.
        """
        self._engine = AnalyzerEngine()
        self._language = language
        self._entities = entities

    def validate(self, prompt: str) -> GuardrailResult:
        """
        Validate that the prompt contains no PII.

        Args:
            prompt: The text (e.g. user prompt) to validate.

        Returns:
            GuardrailResult with valid=True if no PII found, valid=False and findings otherwise.
        """
        if not prompt or not prompt.strip():
            return GuardrailResult(valid=True, message="Empty prompt. No PII to check.")

        results = self._engine.analyze(
            text=prompt,
            language=self._language,
            entities=self._entities,
        )

        findings = [PIIFinding.from_recognizer_result(r, prompt) for r in results]
        valid = len(findings) == 0

        return GuardrailResult(valid=valid, findings=findings)

    def get_supported_entities(self) -> List[str]:
        """Return the list of PII entity types this guardrail can detect."""
        return self._engine.get_supported_entities(language=self._language)


def validate_prompt(
    prompt: str,
    language: str = "en",
    entities: List[str] | None = None,
) -> GuardrailResult:
    """
    Convenience function to validate a prompt for PII in one call.

    Args:
        prompt: The text to validate.
        language: Language code (default: "en").
        entities: PII entity types to check; None = all supported.

    Returns:
        GuardrailResult indicating whether the prompt is PII-free.
    """
    guardrail = PIIGuardrail(language=language, entities=entities)
    return guardrail.validate(prompt)
