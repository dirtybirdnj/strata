"""Output configuration screen - configure output formats and generate recipe."""

from pathlib import Path

import yaml
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
    Select,
    Static,
    TextArea,
)


# Common page sizes for plotter output
PAGE_SIZES = {
    "letter": [8.5, 11],
    "tabloid": [11, 17],
    "12x24": [12, 24],
    "18x24": [18, 24],
    "24x36": [24, 36],
    "a4": [8.27, 11.69],
    "a3": [11.69, 16.54],
}


class OutputConfigScreen(Screen):
    """Configure output formats and generate the recipe."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "generate", "Generate"),
    ]

    CSS = """
    #output-container {
        padding: 1 2;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        padding: 1 0;
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

    #format-section {
        layout: horizontal;
    }

    #preview-section {
        margin-top: 1;
        height: 40%;
    }

    #preview-area {
        height: 100%;
        border: solid $primary;
    }

    #button-row {
        dock: bottom;
        height: 3;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Static("[5/5] Output Configuration", id="step"),
            Vertical(
                Static("Page Size", classes="section-title"),
                Horizontal(
                    Label("Preset:"),
                    Select(
                        [(name, name) for name in PAGE_SIZES.keys()],
                        id="page-preset",
                        value="12x24",
                    ),
                    classes="config-row",
                ),
                Horizontal(
                    Label("Width (in):"),
                    Input(value="12", id="page-width"),
                    Label("  Height (in):"),
                    Input(value="24", id="page-height"),
                    classes="config-row",
                ),
                Horizontal(
                    Label("Margin (in):"),
                    Input(value="0.5", id="margin"),
                    classes="config-row",
                ),
                id="page-section",
                classes="config-section",
            ),
            Vertical(
                Static("Output Formats", classes="section-title"),
                Horizontal(
                    Checkbox("SVG (for plotters)", id="fmt-svg", value=True),
                    Checkbox("GeoJSON (for web)", id="fmt-geojson", value=True),
                    id="format-section",
                ),
                Checkbox("Generate per-layer files", id="per-layer", value=True),
                Checkbox("Generate combined file", id="combined", value=True),
                id="format-config",
                classes="config-section",
            ),
            Vertical(
                Static("Recipe Preview", classes="section-title"),
                TextArea(id="preview-area", read_only=True),
                id="preview-section",
            ),
            Horizontal(
                Button("<- Back", id="back-btn"),
                Button("Preview Recipe", id="preview-btn", variant="warning"),
                Button("Generate Recipe", id="generate-btn", variant="success"),
                id="button-row",
            ),
            id="output-container",
        )

        yield Footer()

    def on_mount(self) -> None:
        """Generate initial preview."""
        self._update_preview()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle page size preset selection."""
        if event.select.id == "page-preset":
            preset = str(event.value)
            if preset in PAGE_SIZES:
                size = PAGE_SIZES[preset]
                self.query_one("#page-width", Input).value = str(size[0])
                self.query_one("#page-height", Input).value = str(size[1])
                self._update_preview()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update preview when inputs change."""
        self._update_preview()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Update preview when checkboxes change."""
        self._update_preview()

    def _build_recipe(self) -> dict:
        """Build the recipe dictionary from wizard data."""
        data = self.app.recipe_data

        # Build sources section
        sources = {}
        for uri, info in data.get("sources", {}).items():
            # Generate a clean source name from URI
            parts = uri.split("/")
            if len(parts) >= 2:
                name = f"{parts[-2]}_{parts[-1]}"
            else:
                name = uri.replace(":", "_").replace("/", "_")

            sources[name] = {
                "uri": uri,
                "description": info.get("description", info.get("name", "")),
            }

        # Build layers section
        layers = []
        for layer in data.get("layers", []):
            layer_config = {
                "name": layer["name"],
                "source": layer["name"],  # Match source name
                "operations": layer.get("operations", [{"type": "simplify", "tolerance": 0.0003}]),
                "style": layer.get("style", {}),
                "order": layer["order"],
            }
            layers.append(layer_config)

        # Build output section
        try:
            page_width = float(self.query_one("#page-width", Input).value)
            page_height = float(self.query_one("#page-height", Input).value)
            margin = float(self.query_one("#margin", Input).value)
        except ValueError:
            page_width, page_height, margin = 12, 24, 0.5

        formats = []

        if self.query_one("#fmt-svg", Checkbox).value:
            formats.append({
                "type": "svg",
                "quality": [
                    {"name": "fine", "simplify": 0.0002},
                    {"name": "medium", "simplify": 0.0005},
                ],
                "options": {
                    "per_layer": self.query_one("#per-layer", Checkbox).value,
                    "combined": self.query_one("#combined", Checkbox).value,
                    "page_size": [page_width, page_height],
                    "margin": margin,
                },
            })

        if self.query_one("#fmt-geojson", Checkbox).value:
            formats.append({
                "type": "geojson",
                "options": {
                    "per_layer": self.query_one("#per-layer", Checkbox).value,
                    "precision": 6,
                },
            })

        bounds = data.get("bounds", [-73.44, 42.72, -71.46, 45.02])

        recipe = {
            "name": data.get("name", "untitled"),
            "description": data.get("description", ""),
            "version": 1,
            "sources": sources,
            "layers": layers,
            "output": {
                "bounds": bounds,
                "projection": "epsg:4326",
                "formats": formats,
            },
        }

        return recipe

    def _update_preview(self) -> None:
        """Update the recipe preview."""
        try:
            recipe = self._build_recipe()
            yaml_str = yaml.dump(
                recipe,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
            self.query_one("#preview-area", TextArea).load_text(yaml_str)
        except Exception as e:
            self.query_one("#preview-area", TextArea).load_text(f"Error: {e}")

    def action_back(self) -> None:
        """Go back to layer config."""
        self.app.pop_screen()

    def action_generate(self) -> None:
        """Generate and save the recipe."""
        recipe = self._build_recipe()
        name = recipe["name"]

        # Save to examples directory
        output_path = Path("examples") / f"{name}.strata.yaml"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        yaml_str = yaml.dump(
            recipe,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

        # Add header comment
        header = f"""# {recipe.get('description', name)}
# Generated by Strata TUI Wizard
#
# Build with: strata build {output_path}
#

"""
        with open(output_path, "w") as f:
            f.write(header + yaml_str)

        self.notify(f"Recipe saved to: {output_path}", severity="information")

        # Offer to build
        self.app.exit(message=f"Recipe saved: {output_path}\nRun: strata build {output_path}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "preview-btn":
            self._update_preview()
            self.notify("Preview updated")
        elif event.button.id == "generate-btn":
            self.action_generate()
