"""Layer configuration screen - configure map layers from sources."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
)


# Default styles by geometry type
DEFAULT_STYLES = {
    "polygon": {
        "stroke": "#424242",
        "stroke_width": 0.5,
        "fill": "#f5f5f5",
        "vary_fill": True,
    },
    "line": {
        "stroke": "#1976d2",
        "stroke_width": 0.4,
        "fill": None,
    },
    "point": {
        "stroke": "#1565c0",
        "stroke_width": 0.6,
        "fill": "#2196f3",
        "marker": "circle",
        "marker_size": 6,
    },
}

# Common operations by layer type
COMMON_OPERATIONS = {
    "cousub": ["subtract water", "simplify"],
    "areawater": ["simplify"],
    "linearwater": ["simplify"],
    "prisecroads": ["simplify"],
    "county": ["simplify"],
    "state": ["simplify"],
    "place": ["simplify"],
    "tract": ["simplify"],
    "municipalities": ["simplify"],
    "mrc": ["simplify"],
    "regions": ["simplify"],
}


class LayerConfigScreen(Screen):
    """Configure layers from selected sources."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "continue_next", "Continue"),
        Binding("up", "move_up", "Move Up"),
        Binding("down", "move_down", "Move Down"),
    ]

    CSS = """
    #layer-container {
        layout: horizontal;
        height: 100%;
    }

    #layer-list-panel {
        width: 40%;
        border: solid $primary;
        padding: 1;
    }

    #layer-config-panel {
        width: 60%;
        padding: 1;
    }

    .panel-title {
        text-style: bold;
        padding-bottom: 1;
    }

    #layer-list {
        height: 100%;
    }

    .config-section {
        margin: 1 0;
        padding: 1;
        border: solid $secondary;
    }

    .config-row {
        layout: horizontal;
        height: 3;
    }

    .config-row Label {
        width: 15;
        padding-top: 1;
    }

    .config-row Input {
        width: 20;
    }

    #button-row {
        dock: bottom;
        height: 3;
        padding: 1;
    }

    #auto-config-btn {
        margin-bottom: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.layers: list[dict] = []
        self.selected_layer_idx: int = 0

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Static("[4/5] Configure Layers", id="step"),
            Static(
                "\nArrange and style your map layers.\n"
                "Layers are drawn in order (first = bottom).\n",
            ),
            Button("Auto-Configure Layers", id="auto-config-btn", variant="success"),
            Horizontal(
                Vertical(
                    Static("Layers (draw order)", classes="panel-title"),
                    ListView(id="layer-list"),
                    Horizontal(
                        Button("^ Up", id="up-btn"),
                        Button("v Down", id="down-btn"),
                        Button("Remove", id="remove-btn", variant="error"),
                    ),
                    id="layer-list-panel",
                ),
                Vertical(
                    Static("Layer Settings", classes="panel-title"),
                    VerticalScroll(
                        Vertical(
                            Static("Style", classes="panel-title"),
                            Horizontal(
                                Label("Stroke:"),
                                Input(placeholder="#424242", id="stroke-color"),
                                classes="config-row",
                            ),
                            Horizontal(
                                Label("Stroke Width:"),
                                Input(placeholder="0.5", id="stroke-width"),
                                classes="config-row",
                            ),
                            Horizontal(
                                Label("Fill:"),
                                Input(placeholder="#f5f5f5 or none", id="fill-color"),
                                classes="config-row",
                            ),
                            Checkbox("Vary fill colors", id="vary-fill", value=True),
                            id="style-section",
                            classes="config-section",
                        ),
                        Vertical(
                            Static("Operations", classes="panel-title"),
                            Checkbox("Simplify geometry", id="op-simplify", value=True),
                            Checkbox("Subtract water bodies", id="op-subtract-water"),
                            Checkbox("Remove small holes", id="op-remove-holes"),
                            id="ops-section",
                            classes="config-section",
                        ),
                    ),
                    id="layer-config-panel",
                ),
                id="layer-container",
            ),
            Horizontal(
                Button("<- Back", id="back-btn"),
                Button("Continue to Output ->", id="continue-btn", variant="primary"),
                id="button-row",
            ),
            id="main",
        )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize layers from selected sources."""
        sources = self.app.recipe_data.get("sources", {})
        if sources:
            self._auto_configure_layers()

    def _auto_configure_layers(self) -> None:
        """Auto-configure layers based on selected sources."""
        sources = self.app.recipe_data.get("sources", {})

        self.layers = []
        order = 1

        # Sort sources by type for logical layer ordering
        # Polygons first (base), then lines (roads), then points (POIs)
        polygon_sources = []
        line_sources = []
        point_sources = []
        water_sources = []

        for uri, info in sources.items():
            geom = info.get("geometry", "polygon")
            name = info.get("name", uri.split(":")[-1])

            # Detect water sources
            if "water" in uri.lower() or "water" in name.lower():
                water_sources.append((uri, info))
            elif geom == "polygon":
                polygon_sources.append((uri, info))
            elif geom == "line":
                line_sources.append((uri, info))
            else:
                point_sources.append((uri, info))

        # Build layers in order: base polygons, water, roads, points
        for uri, info in polygon_sources:
            layer = self._create_layer(uri, info, order)
            # Auto-add subtract water if we have water sources
            if water_sources:
                layer["operations"].insert(0, {"type": "subtract", "target": "water"})
            self.layers.append(layer)
            order += 1

        for uri, info in water_sources:
            self.layers.append(self._create_layer(uri, info, order))
            order += 1

        for uri, info in line_sources:
            self.layers.append(self._create_layer(uri, info, order))
            order += 1

        for uri, info in point_sources:
            self.layers.append(self._create_layer(uri, info, order))
            order += 1

        self._update_layer_list()

    def _create_layer(self, uri: str, info: dict, order: int) -> dict:
        """Create a layer configuration from a source."""
        geom = info.get("geometry", "polygon")
        name_parts = uri.split("/")
        layer_name = name_parts[-1] if len(name_parts) > 1 else uri.replace(":", "_")

        # Get default style for geometry type
        style = DEFAULT_STYLES.get(geom, DEFAULT_STYLES["polygon"]).copy()

        # Default operations
        operations = [{"type": "simplify", "tolerance": 0.0003}]

        return {
            "name": layer_name,
            "source": uri,
            "source_info": info,
            "order": order,
            "style": style,
            "operations": operations,
        }

    def _update_layer_list(self) -> None:
        """Update the layer list view."""
        list_view = self.query_one("#layer-list", ListView)
        list_view.clear()

        for i, layer in enumerate(self.layers):
            prefix = ">" if i == self.selected_layer_idx else " "
            geom = layer["source_info"].get("geometry", "?")
            icon = {"polygon": "[P]", "line": "[L]", "point": "[.]"}.get(geom, "[?]")
            list_view.append(
                ListItem(Label(f"{prefix} {layer['order']}. {icon} {layer['name']}"))
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle layer selection."""
        self.selected_layer_idx = event.list_view.index
        self._load_layer_config()

    def _load_layer_config(self) -> None:
        """Load the selected layer's config into the form."""
        if 0 <= self.selected_layer_idx < len(self.layers):
            layer = self.layers[self.selected_layer_idx]
            style = layer.get("style", {})

            self.query_one("#stroke-color", Input).value = style.get("stroke", "#424242")
            self.query_one("#stroke-width", Input).value = str(style.get("stroke_width", 0.5))
            self.query_one("#fill-color", Input).value = style.get("fill", "") or "none"
            self.query_one("#vary-fill", Checkbox).value = style.get("vary_fill", False)

    def action_move_up(self) -> None:
        """Move selected layer up (draws earlier/below)."""
        if self.selected_layer_idx > 0:
            self.layers[self.selected_layer_idx], self.layers[self.selected_layer_idx - 1] = (
                self.layers[self.selected_layer_idx - 1],
                self.layers[self.selected_layer_idx],
            )
            # Update order numbers
            for i, layer in enumerate(self.layers):
                layer["order"] = i + 1
            self.selected_layer_idx -= 1
            self._update_layer_list()

    def action_move_down(self) -> None:
        """Move selected layer down (draws later/above)."""
        if self.selected_layer_idx < len(self.layers) - 1:
            self.layers[self.selected_layer_idx], self.layers[self.selected_layer_idx + 1] = (
                self.layers[self.selected_layer_idx + 1],
                self.layers[self.selected_layer_idx],
            )
            for i, layer in enumerate(self.layers):
                layer["order"] = i + 1
            self.selected_layer_idx += 1
            self._update_layer_list()

    def action_back(self) -> None:
        """Go back to bounds screen."""
        self.app.pop_screen()

    def action_continue_next(self) -> None:
        """Continue to output configuration."""
        if not self.layers:
            self.notify("Please configure at least one layer", severity="error")
            return

        # Store layers in app
        self.app.recipe_data["layers"] = self.layers

        # Push output config screen
        from .output_config import OutputConfigScreen
        self.app.push_screen(OutputConfigScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "continue-btn":
            self.action_continue_next()
        elif event.button.id == "auto-config-btn":
            self._auto_configure_layers()
            self.notify("Layers auto-configured from sources")
        elif event.button.id == "up-btn":
            self.action_move_up()
        elif event.button.id == "down-btn":
            self.action_move_down()
        elif event.button.id == "remove-btn":
            if self.layers and self.selected_layer_idx < len(self.layers):
                removed = self.layers.pop(self.selected_layer_idx)
                self.notify(f"Removed: {removed['name']}")
                if self.selected_layer_idx >= len(self.layers):
                    self.selected_layer_idx = max(0, len(self.layers) - 1)
                self._update_layer_list()
