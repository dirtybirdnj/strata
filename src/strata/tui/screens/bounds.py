"""Bounds configuration screen - set map boundaries."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static, RadioSet, RadioButton


# Common preset bounds for quick selection
PRESET_BOUNDS = {
    "vermont": {
        "name": "Vermont (Full State)",
        "bounds": [-73.44, 42.72, -71.46, 45.02],
        "description": "Entire state of Vermont",
    },
    "lake_champlain": {
        "name": "Lake Champlain Region",
        "bounds": [-73.84, 43.50, -72.40, 45.20],
        "description": "Lake Champlain and surrounding towns (VT/NY)",
    },
    "lake_champlain_quebec": {
        "name": "Lake Champlain + Quebec",
        "bounds": [-73.84, 43.50, -72.40, 45.50],
        "description": "Lake Champlain extending into Quebec",
    },
    "hawaii": {
        "name": "Hawaiian Islands",
        "bounds": [-160.25, 18.90, -154.80, 22.25],
        "description": "Main Hawaiian islands",
    },
    "oahu": {
        "name": "Oahu",
        "bounds": [-158.30, 21.25, -157.65, 21.72],
        "description": "Island of Oahu",
    },
    "niagara": {
        "name": "Niagara Falls Region",
        "bounds": [-79.30, 42.85, -78.85, 43.30],
        "description": "Niagara Falls area (US/Canada)",
    },
    "continental_us": {
        "name": "Continental US",
        "bounds": [-125.0, 24.5, -66.9, 49.5],
        "description": "Lower 48 states",
    },
}


class BoundsScreen(Screen):
    """Configure map boundaries."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "continue_next", "Continue"),
        Binding("p", "preview_svg", "Preview SVG"),
    ]

    CSS = """
    #bounds-container {
        padding: 1 2;
    }

    #preset-section {
        margin-bottom: 2;
    }

    #manual-section {
        margin-top: 1;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        padding-bottom: 1;
    }

    .bounds-input-row {
        layout: horizontal;
        height: 3;
        margin: 0 0 1 0;
    }

    .bounds-input-row Label {
        width: 10;
        padding-top: 1;
    }

    .bounds-input-row Input {
        width: 20;
    }

    #preview-info {
        margin-top: 1;
        padding: 1;
        border: solid $secondary;
    }

    #button-row {
        dock: bottom;
        height: 3;
        padding: 1;
        layout: horizontal;
    }

    RadioSet {
        height: auto;
        margin: 1 0;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.current_bounds: list[float] | None = None

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Static("[3/5] Configure Bounds", id="step"),
            Static(
                "\nDefine the geographic area for your map.\n"
                "You can select a preset or enter custom coordinates.\n",
            ),
            Vertical(
                Static("Presets", classes="section-title"),
                RadioSet(
                    RadioButton("Vermont (Full State)", id="preset-vermont"),
                    RadioButton("Lake Champlain Region", id="preset-lake_champlain"),
                    RadioButton("Lake Champlain + Quebec", id="preset-lake_champlain_quebec"),
                    RadioButton("Hawaiian Islands", id="preset-hawaii"),
                    RadioButton("Oahu", id="preset-oahu"),
                    RadioButton("Niagara Falls Region", id="preset-niagara"),
                    RadioButton("Custom (enter below)", id="preset-custom", value=True),
                    id="preset-radio",
                ),
                id="preset-section",
            ),
            Vertical(
                Static("Manual Bounds (WGS84)", classes="section-title"),
                Horizontal(
                    Label("West:"),
                    Input(placeholder="-73.44", id="west"),
                    Label("  East:"),
                    Input(placeholder="-71.46", id="east"),
                    classes="bounds-input-row",
                ),
                Horizontal(
                    Label("South:"),
                    Input(placeholder="42.72", id="south"),
                    Label("  North:"),
                    Input(placeholder="45.02", id="north"),
                    classes="bounds-input-row",
                ),
                id="manual-section",
            ),
            Static(
                "Tip: After continuing, you'll see an SVG preview where you can\n"
                "visually adjust the crop area.",
                id="preview-info",
            ),
            Horizontal(
                Button("<- Back", id="back-btn"),
                Button("Preview Bounds", id="preview-btn", variant="warning"),
                Button("Continue ->", id="continue-btn", variant="primary"),
                id="button-row",
            ),
            id="bounds-container",
        )

        yield Footer()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle preset selection."""
        button_id = str(event.pressed.id)
        if button_id.startswith("preset-"):
            preset_key = button_id[7:]  # Remove "preset-" prefix

            if preset_key in PRESET_BOUNDS:
                preset = PRESET_BOUNDS[preset_key]
                bounds = preset["bounds"]

                # Update input fields
                self.query_one("#west", Input).value = str(bounds[0])
                self.query_one("#south", Input).value = str(bounds[1])
                self.query_one("#east", Input).value = str(bounds[2])
                self.query_one("#north", Input).value = str(bounds[3])

                self.notify(f"Selected: {preset['name']}")

    def _get_bounds(self) -> list[float] | None:
        """Get current bounds from inputs."""
        try:
            west = float(self.query_one("#west", Input).value)
            south = float(self.query_one("#south", Input).value)
            east = float(self.query_one("#east", Input).value)
            north = float(self.query_one("#north", Input).value)

            # Validate
            if south >= north:
                self.notify("South must be less than North", severity="error")
                return None
            if west >= east and not (west > 0 and east < 0):  # Allow antimeridian crossing
                self.notify("West must be less than East", severity="error")
                return None

            return [west, south, east, north]
        except ValueError:
            self.notify("Please enter valid numeric coordinates", severity="error")
            return None

    def action_back(self) -> None:
        """Go back to source browser."""
        self.app.pop_screen()

    def action_preview_svg(self) -> None:
        """Generate a preview SVG for visual bounds adjustment."""
        bounds = self._get_bounds()
        if not bounds:
            return

        self.notify(
            "SVG preview generation coming soon!\n"
            "This will create an SVG you can view to adjust the crop.",
            severity="information",
        )

    def action_continue_next(self) -> None:
        """Continue to layer configuration."""
        bounds = self._get_bounds()
        if not bounds:
            return

        self.app.recipe_data["bounds"] = bounds

        self.notify(
            f"Bounds set: [{bounds[0]:.2f}, {bounds[1]:.2f}, {bounds[2]:.2f}, {bounds[3]:.2f}]",
            severity="information",
        )

        # Push layer config screen
        from .layer_config import LayerConfigScreen
        self.app.push_screen(LayerConfigScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "preview-btn":
            self.action_preview_svg()
        elif event.button.id == "continue-btn":
            self.action_continue_next()
