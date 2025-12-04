"""Welcome screen - entry point for the Strata wizard."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static


class WelcomeScreen(Screen):
    """Welcome screen - Step 1: Recipe name and description."""

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
╚═╝ ╩ ╩╚═╩ ╩ ╩ ╩ ╩  Recipe Builder
                """,
                id="logo",
            ),
            Static("[1/5] Welcome", id="step"),
            Static(
                "\nLet's create a new map recipe.\n\n"
                "A recipe defines:\n"
                "  - Where to get geographic data (sources)\n"
                "  - How to process it (layers with operations)\n"
                "  - What to output (SVG, GeoJSON, tiles)\n",
                id="intro",
            ),
            Vertical(
                Label("Recipe name:"),
                Input(placeholder="hawaii_islands", id="name"),
                Static(
                    "(lowercase, underscores, used for output directory)",
                    classes="hint",
                ),
                id="name-section",
            ),
            Vertical(
                Label("Description (optional):"),
                Input(placeholder="Hawaiian islands with roads and water", id="description"),
                id="desc-section",
            ),
            Button("Continue to Source Selection ->", id="next", variant="primary"),
            id="main",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the name input on mount."""
        self.query_one("#name", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "next":
            self.action_next()

    def action_next(self) -> None:
        """Move to source browser screen."""
        name_input = self.query_one("#name", Input)
        desc_input = self.query_one("#description", Input)

        # Validate name
        name = name_input.value.strip()
        if not name:
            self.notify("Please enter a recipe name", severity="error")
            name_input.focus()
            return

        # Store in app
        self.app.recipe_data["name"] = name
        self.app.recipe_data["description"] = desc_input.value

        # Push source browser screen
        from .source_browser import SourceBrowserScreen
        self.app.push_screen(SourceBrowserScreen())

    def action_cancel(self) -> None:
        """Cancel wizard."""
        self.app.exit()
