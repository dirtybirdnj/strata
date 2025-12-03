"""
Configuration debugger TUI.

Interactive error fixing for malformed .strata.yaml files.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Static


class ConfigDebugger(App):
    """TUI for debugging configuration errors."""

    CSS = """
    #error-list {
        padding: 1 2;
    }

    .error-item {
        margin: 1 0;
        padding: 1;
        border: solid $error;
    }

    .error-line {
        color: $error;
    }

    .suggestion {
        color: $success;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("f", "fix", "Fix Selected"),
        Binding("a", "fix_all", "Fix All"),
        Binding("e", "edit", "Open in Editor"),
    ]

    def __init__(self, recipe_path: str):
        super().__init__()
        self.recipe_path = Path(recipe_path)
        self.errors: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"Configuration Errors: {self.recipe_path.name}", id="title"),
            Static(
                "\n[yellow]Config debugger not yet implemented.[/]\n\n"
                "This will show:\n"
                "  • Validation errors with line numbers\n"
                "  • Suggestions for fixes (typos, missing fields)\n"
                "  • Interactive repair options\n",
                id="placeholder",
            ),
            id="error-list",
        )
        yield Footer()

    def action_fix(self) -> None:
        """Fix selected error."""
        self.notify("Fix not yet implemented")

    def action_fix_all(self) -> None:
        """Fix all errors."""
        self.notify("Fix all not yet implemented")

    def action_edit(self) -> None:
        """Open in external editor."""
        import os
        import subprocess

        editor = os.environ.get("EDITOR", "vim")
        subprocess.run([editor, str(self.recipe_path)])


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m strata.tui.debug <recipe.strata.yaml>")
        sys.exit(1)

    app = ConfigDebugger(sys.argv[1])
    app.run()
