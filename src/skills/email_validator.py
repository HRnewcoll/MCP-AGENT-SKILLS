"""Email validator skill – validate, parse, and analyse email addresses.

Covers the "Communication" category from the awesome-openclaw-skills
directory.  Uses Python stdlib ``re`` and ``email.headerregistry`` only.

Supported actions
-----------------
validate        Check if an email address is syntactically valid.
parse           Break an email into local-part and domain.
extract         Extract all email addresses from a block of text.
check_domain    Check if the domain part looks well-formed.
normalize       Lowercase the domain and strip surrounding whitespace.
bulk_validate   Validate a comma-separated list of emails.
"""

from __future__ import annotations

import re


# RFC 5322 simplified regex (covers the vast majority of real-world addresses)
_EMAIL_RE = re.compile(
    r"""^
    [a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+
    @
    [a-zA-Z0-9]
    (?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?
    (?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*
    \.[a-zA-Z]{2,}
    $""",
    re.VERBOSE,
)

_EXTRACT_RE = re.compile(
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
    r"\.[a-zA-Z]{2,}"
)


class EmailValidatorSkill:
    """Validate, parse, and extract email addresses."""

    name = "email_validator"
    description = (
        "Validate and analyse email addresses. "
        "Supported actions: 'validate' (email); 'parse' (email); "
        "'extract' (text); 'check_domain' (email or domain); "
        "'normalize' (email); 'bulk_validate' (emails – comma-separated)."
    )

    def run(
        self,
        action: str,
        email: str = "",
        text: str = "",
        emails: str = "",
    ) -> str:
        """
        Perform an email validation operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        email:
            Single email address to process.
        text:
            Block of text to extract emails from (for ``"extract"``).
        emails:
            Comma-separated list of emails for ``"bulk_validate"``.

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "validate":
            return self._validate(email)
        if action == "parse":
            return self._parse(email)
        if action == "extract":
            return self._extract(text or email)
        if action == "check_domain":
            return self._check_domain(email)
        if action == "normalize":
            return self._normalize(email)
        if action == "bulk_validate":
            return self._bulk_validate(emails or email)
        return (
            f"Error: unknown action {action!r}. "
            "Use validate, parse, extract, check_domain, normalize, or bulk_validate."
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _validate(email: str) -> str:
        if not email:
            return "Error: email is required"
        addr = email.strip()
        if _EMAIL_RE.match(addr):
            return f"'{addr}' is a VALID email address"
        return f"'{addr}' is NOT a valid email address"

    @staticmethod
    def _parse(email: str) -> str:
        if not email:
            return "Error: email is required"
        addr = email.strip()
        if "@" not in addr:
            return "Error: not a valid email format (missing @)"
        local, _, domain = addr.partition("@")
        return (
            f"Email    : {addr}\n"
            f"Local    : {local}\n"
            f"Domain   : {domain}"
        )

    @staticmethod
    def _extract(text: str) -> str:
        if not text:
            return "Error: text is required"
        found = _EXTRACT_RE.findall(text)
        if not found:
            return "(no email addresses found)"
        unique = list(dict.fromkeys(found))  # preserve order, deduplicate
        return f"{len(unique)} email(s) found:\n" + "\n".join(unique)

    @staticmethod
    def _check_domain(email_or_domain: str) -> str:
        if not email_or_domain:
            return "Error: email or domain is required"
        if "@" in email_or_domain:
            domain = email_or_domain.partition("@")[2].strip()
        else:
            domain = email_or_domain.strip()
        parts = domain.split(".")
        issues: list[str] = []
        if len(parts) < 2:
            issues.append("no TLD found")
        if any(len(p) == 0 for p in parts):
            issues.append("empty domain segment")
        if len(domain) > 253:
            issues.append("domain too long (>253 chars)")
        if issues:
            return f"Domain '{domain}' has issues: " + "; ".join(issues)
        return f"Domain '{domain}' appears well-formed"

    @staticmethod
    def _normalize(email: str) -> str:
        if not email:
            return "Error: email is required"
        addr = email.strip()
        if "@" not in addr:
            return "Error: not a valid email format"
        local, _, domain = addr.partition("@")
        return f"{local}@{domain.lower()}"

    @staticmethod
    def _bulk_validate(emails: str) -> str:
        if not emails:
            return "Error: emails is required for bulk_validate"
        addrs = [e.strip() for e in emails.split(",") if e.strip()]
        if not addrs:
            return "Error: no email addresses provided"
        valid: list[str] = []
        invalid: list[str] = []
        for addr in addrs:
            (valid if _EMAIL_RE.match(addr) else invalid).append(addr)
        lines = [
            f"Validated {len(addrs)} address(es):",
            f"  Valid ({len(valid)}): " + (", ".join(valid) if valid else "none"),
            f"  Invalid ({len(invalid)}): " + (", ".join(invalid) if invalid else "none"),
        ]
        return "\n".join(lines)
