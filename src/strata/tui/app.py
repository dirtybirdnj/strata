"""
Strata TUI Wizard Application.

A 1980s BIOS-style wizard for creating .strata.yaml recipes.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static


class WelcomeScreen(Screen):
    """Welcome screen - Step 1/5."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "next", "Continue"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(
                """
╔═╗╔╦╗╦═╗╔═╗╔╦╗╔═╗
╚═╗ ║ ╠╦╝╠═╣ ║ ╠═╣
╚═╝ ╩ ╩╚═╩ ╩ ╩ ╩ ╩  Recipe Wizard
                """,
                id="logo",
            ),
            Static("[1/5] Welcome", id="step"),
            Static(
                "\nWelcome! Let's create a new map recipe.\n\n"
                "A recipe defines:\n"
                "  • Where to get geographic data (sources)\n"
                "  • How to process it (layers with operations)\n"
                "  • What to output (SVG, GeoJSON, tiles)\n",
                id="intro",
            ),
            Vertical(
                Label("Recipe name:"),
                Input(placeholder="champlain_region", id="name"),
                Static(
                    "(lowercase, underscores, used for output directory)",
                    classes="hint",
                ),
                id="name-section",
            ),
            Vertical(
                Label("Description (optional):"),
                Input(placeholder="Lake Champlain and surrounding towns", id="description"),
                id="desc-section",
            ),
            Button("Continue →", id="next", variant="primary"),
            id="main",
        )
        yield Footer()

    def action_next(self) -> None:
        """Move to next screen."""
        name_input = self.query_one("#name", Input)
        desc_input = self.query_one("#description", Input)

        # Store in app
        self.app.recipe_data["name"] = name_input.value or "untitled"
        self.app.recipe_data["description"] = desc_input.value

        # TODO: Push next screen
        self.app.exit(message="Wizard not yet fully implemented - recipe data captured")

    def action_cancel(self) -> None:
        """Cancel wizard."""
        self.app.exit()


class StrataWizard(App):
    """Main Strata TUI wizard application."""

    CSS = """
    #logo {
        color: $accent;
        text-align: center;
        padding: 1;
    }

    #step {
        text-align: right;
        color: $text-muted;
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

    #next {
        margin-top: 2;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
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
            "output": {},
        }

    def on_mount(self) -> None:
        """Initialize the app."""
        self.push_screen(WelcomeScreen())

    def action_help(self) -> None:
        """Show help."""
        self.notify("Help not yet implemented", title="Help")


if __name__ == "__main__":
    app = StrataWizard()
    app.run()
