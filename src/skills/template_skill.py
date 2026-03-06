"""Template skill – render string templates with variable substitution.

Covers the "Coding Agents & IDEs" and "Productivity & Tasks" categories.
Uses Python's stdlib ``string.Template`` plus a simple Jinja2-like
``{{variable}}`` style for convenience.  No external dependencies.

Supported actions
-----------------
render          Substitute variables into a template string.
list_vars       List all placeholders found in a template.
preview         Show the template with variable names highlighted.
"""

from __future__ import annotations

import re
import string


class TemplateSkill:
    """Render string templates with variable substitution."""

    name = "template"
    description = (
        "Render text templates with variable substitution. "
        "Supported actions: 'render' (template, variables); "
        "'list_vars' (template); 'preview' (template)."
        "\nVariables can use $name / ${name} (Python style) "
        "or {{name}} (double-brace style)."
        "\nPass variables as: key1=value1,key2=value2"
    )

    def run(
        self,
        action: str,
        template: str = "",
        variables: str = "",
    ) -> str:
        """
        Perform a template operation.

        Parameters
        ----------
        action:
            One of ``"render"``, ``"list_vars"``, ``"preview"``.
        template:
            The template string with variable placeholders.
        variables:
            Comma-separated ``key=value`` pairs for ``"render"``
            (e.g. ``"name=Alice,lang=Python"``).

        Returns
        -------
        str
            Rendered text or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "render":
            return self._render(template, variables)
        if action == "list_vars":
            return self._list_vars(template)
        if action == "preview":
            return self._preview(template)
        return (
            f"Error: unknown action {action!r}. "
            "Use render, list_vars, or preview."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_vars(vars_str: str) -> dict[str, str]:
        """Parse ``"key=val,key2=val2"`` into a dict."""
        mapping: dict[str, str] = {}
        if not vars_str.strip():
            return mapping
        for pair in vars_str.split(","):
            pair = pair.strip()
            if "=" in pair:
                k, _, v = pair.partition("=")
                mapping[k.strip()] = v.strip()
        return mapping

    def _render(self, template: str, vars_str: str) -> str:
        if not template:
            return "Error: template is required"
        mapping = self._parse_vars(vars_str)
        # Support {{name}} syntax by converting to ${name}
        tpl = re.sub(r"\{\{(\w+)\}\}", r"${\1}", template)
        try:
            result = string.Template(tpl).substitute(mapping)
        except KeyError as exc:
            return f"Error: missing variable {exc}"
        except ValueError as exc:
            return f"Error: {exc}"
        return result

    @staticmethod
    def _list_vars(template: str) -> str:
        if not template:
            return "Error: template is required"
        # Find $name, ${name}, and {{name}} style variables
        found = set()
        found.update(re.findall(r"\$\{?(\w+)\}?", template))
        found.update(re.findall(r"\{\{(\w+)\}\}", template))
        if not found:
            return "(no variables found)"
        return "Variables: " + ", ".join(sorted(found))

    @staticmethod
    def _preview(template: str) -> str:
        if not template:
            return "Error: template is required"
        # Highlight variable placeholders
        highlighted = re.sub(r"\$\{?(\w+)\}?", r"[${\1}]", template)
        highlighted = re.sub(r"\{\{(\w+)\}\}", r"[{{\1}}]", highlighted)
        return highlighted
