"""
Strata TUI Wizard Application.

A terminal-based wizard for creating .strata.yaml recipes.
Built with Textual for a rich, interactive experience.
"""

from textual.app import App
from textual.binding import Binding

from .screens import WelcomeScreen


class StrataWizard(App):
    """Main Strata TUI wizard application."""

    TITLE = "Strata Recipe Builder"

    CSS = """
    Screen {
        background: $surface;
    }

    #logo {
        color: $accent;
        text-align: center;
        padding: 1;
    }

    #step {
        text-align: right;
        color: $text-muted;
        padding: 0 2;
    }

    #intro {
        padding: 1 2;
    }

    #main {
        padding: 1 2;
    }

    #name-section, #desc-section {
        margin: 1 0;
    }

    .hint {
        color: $text-muted;
        text-style: italic;
    }

    Button {
        margin: 0 1;
    }

    .panel-title {
        text-style: bold;
        color: $text;
    }

    Input {
        margin: 0 1;
    }

    Input:focus {
        border: tall $accent;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("f1", "help", "Help"),
    ]

    def __init__(
        self,
        initial_name: str | None = None,
        template: str | None = None,
        output_dir: str | None = None,
    ):
        super().__init__()
        self.initial_name = initial_name
        self.template = template
        self.output_dir = output_dir
        self.recipe_data: dict = {
            "name": initial_name or "",
            "description": "",
            "sources": {},
            "layers": [],
            "bounds": None,
            "output": {},
        }

    def on_mount(self) -> None:
        """Initialize the app."""
        self.push_screen(WelcomeScreen())

    def action_help(self) -> None:
        """Show help."""
        self.notify(
            "Strata Recipe Builder\n\n"
            "Navigate with arrow keys and Tab\n"
            "Press Enter to select/continue\n"
            "Press Escape to go back",
            title="Help",
            timeout=5,
        )


def run_wizard(
    name: str | None = None,
    template: str | None = None,
    output_dir: str | None = None,
) -> dict | None:
    """Run the Strata wizard and return the recipe data."""
    app = StrataWizard(
        initial_name=name,
        template=template,
        output_dir=output_dir,
    )
    result = app.run()
    if result:
        print(result)
    return app.recipe_data


if __name__ == "__main__":
    run_wizard()
