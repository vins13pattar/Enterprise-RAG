import re

INJECTION = re.compile(r"ignore previous|system prompt|developer message|exfiltrate", re.I)
PII = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|[\w.]+@[\w.]+", re.I)


def inspect_text(text: str) -> dict:
    return {
        "prompt_injection": bool(INJECTION.search(text)),
        "pii": bool(PII.search(text)),
        "redacted": PII.sub("[REDACTED]", text),
    }
