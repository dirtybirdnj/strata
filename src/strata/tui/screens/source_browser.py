"""Source browser screen - browse and select data sources."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    Tree,
)
from textual.widgets.tree import TreeNode

from ..catalog import (
    US_STATES,
    TIGER_LAYERS,
    QUEBEC_LAYERS,
    CANADA_LAYERS,
    NRN_PROVINCES,
    get_states_list,
)


class SourceBrowserScreen(Screen):
    """Browse and select data sources for the recipe."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "toggle_select", "Select/Deselect"),
        Binding("a", "add_custom", "Add Custom"),
        Binding("c", "continue_next", "Continue"),
        Binding("/", "focus_search", "Search"),
    ]

    CSS = """
    #browser-container {
        layout: horizontal;
        height: 100%;
    }

    #source-tree {
        width: 45%;
        border: solid $primary;
        padding: 1;
    }

    #right-panel {
        width: 55%;
        padding: 0 1;
    }

    #selected-panel {
        height: 60%;
        border: solid $success;
        padding: 1;
    }

    #info-panel {
        height: 40%;
        border: solid $secondary;
        padding: 1;
    }

    .panel-title {
        text-style: bold;
        color: $text;
        padding-bottom: 1;
    }

    #selected-list {
        height: 100%;
    }

    #search-box {
        dock: top;
        margin-bottom: 1;
    }

    #button-row {
        dock: bottom;
        height: 3;
        padding: 1;
    }

    .selected-count {
        color: $success;
        text-style: bold;
    }

    Tree {
        scrollbar-gutter: stable;
    }

    Tree > .tree--cursor {
        background: $accent;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.selected_sources: dict[str, dict] = {}  # uri -> {name, description}

    def compose(self) -> ComposeResult:
        yield Header()

        yield Container(
            Static("[2/5] Select Data Sources", id="step"),
            Input(placeholder="Type to filter... (e.g. 'hawaii', 'water')", id="search-box"),
            Horizontal(
                Vertical(
                    Static("Available Sources", classes="panel-title"),
                    Tree("Data Sources", id="source-tree"),
                    id="tree-panel",
                ),
                Vertical(
                    Vertical(
                        Static("Selected Sources (0)", id="selected-title", classes="panel-title"),
                        ListView(id="selected-list"),
                        id="selected-panel",
                    ),
                    Vertical(
                        Static("Source Info", classes="panel-title"),
                        Static("Select a source to see details", id="info-text"),
                        id="info-panel",
                    ),
                    id="right-panel",
                ),
                id="browser-container",
            ),
            Horizontal(
                Button("<- Back", id="back-btn"),
                Button("Add Custom Source", id="custom-btn", variant="warning"),
                Button("Continue ->", id="continue-btn", variant="primary"),
                id="button-row",
            ),
            id="main",
        )

        yield Footer()

    def on_mount(self) -> None:
        """Build the source tree on mount."""
        tree = self.query_one("#source-tree", Tree)
        tree.show_root = False

        # US Census TIGER data
        census_node = tree.root.add("US Census TIGER/Line (2023)", expand=False)

        # Group states by region for easier navigation
        regions = {
            "New England": ["ct", "me", "ma", "nh", "ri", "vt"],
            "Mid-Atlantic": ["nj", "ny", "pa"],
            "South Atlantic": ["de", "dc", "fl", "ga", "md", "nc", "sc", "va", "wv"],
            "East South Central": ["al", "ky", "ms", "tn"],
            "West South Central": ["ar", "la", "ok", "tx"],
            "East North Central": ["il", "in", "mi", "oh", "wi"],
            "West North Central": ["ia", "ks", "mn", "mo", "ne", "nd", "sd"],
            "Mountain": ["az", "co", "id", "mt", "nv", "nm", "ut", "wy"],
            "Pacific": ["ak", "ca", "hi", "or", "wa"],
            "Territories": ["pr"],
        }

        for region_name, state_codes in regions.items():
            region_node = census_node.add(region_name, expand=False)
            for state_code in state_codes:
                if state_code in US_STATES:
                    state_info = US_STATES[state_code]
                    state_node = region_node.add(
                        f"{state_info['name']} ({state_code.upper()})",
                        expand=False,
                    )
                    # Add layer types under each state
                    for layer_code, layer_info in TIGER_LAYERS.items():
                        uri = f"census:tiger/2023/{state_code}/{layer_code}"
                        state_node.add_leaf(
                            f"{layer_info['name']}",
                            data={"uri": uri, "info": layer_info, "state": state_info["name"]},
                        )

        # Quebec data
        quebec_node = tree.root.add("Quebec (Canada)", expand=False)
        for layer_code, layer_info in QUEBEC_LAYERS.items():
            uri = f"quebec:{layer_code}"
            quebec_node.add_leaf(
                f"{layer_info['name']}",
                data={"uri": uri, "info": layer_info, "state": "Quebec"},
            )

        # Canada-wide data (CanVec, NRN)
        canada_node = tree.root.add("Canada (National)", expand=False)

        # CanVec hydro
        canvec_node = canada_node.add("CanVec (Natural Resources Canada)", expand=False)
        for layer_code, layer_info in CANADA_LAYERS.items():
            canvec_node.add_leaf(
                f"{layer_info['name']}",
                data={"uri": layer_info["uri"], "info": layer_info, "state": "Canada"},
            )

        # NRN roads by province
        nrn_node = canada_node.add("NRN Roads (Statistics Canada)", expand=False)
        for prov_code, prov_info in NRN_PROVINCES.items():
            uri = f"canada:nrn/{prov_code}"
            nrn_node.add_leaf(
                f"{prov_info['name']} Roads",
                data={
                    "uri": uri,
                    "info": {
                        "name": f"NRN Roads - {prov_info['name']}",
                        "description": f"National Road Network for {prov_info['name']}",
                        "geometry": "line",
                    },
                    "state": prov_info["name"],
                },
            )

        # Custom sources section
        custom_node = tree.root.add("Custom Sources", expand=False)
        custom_node.add_leaf("+ Add file path...", data={"action": "add_file"})
        custom_node.add_leaf("+ Add URL...", data={"action": "add_url"})

        # Expand census by default to show regions
        census_node.expand()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection - show info panel."""
        node = event.node
        if node.data and isinstance(node.data, dict):
            if "uri" in node.data:
                info = node.data["info"]
                state = node.data.get("state", "")
                uri = node.data["uri"]

                info_text = (
                    f"URI: {uri}\n\n"
                    f"Region: {state}\n"
                    f"Type: {info.get('geometry', 'unknown')}\n"
                    f"Description: {info.get('description', '')}\n"
                )

                if "features" in info:
                    info_text += f"Features: ~{info['features']}\n"

                # Check if cached
                try:
                    from strata.thoreau.cache import is_cached
                    if is_cached(uri):
                        info_text += "\n[cached locally]"
                except Exception:
                    pass

                self.query_one("#info-text", Static).update(info_text)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """When a node is expanded, auto-scroll to show children."""
        pass

    def action_toggle_select(self) -> None:
        """Toggle selection of the current tree item."""
        tree = self.query_one("#source-tree", Tree)
        node = tree.cursor_node

        if node and node.data and isinstance(node.data, dict) and "uri" in node.data:
            uri = node.data["uri"]
            info = node.data["info"]
            state = node.data.get("state", "")

            if uri in self.selected_sources:
                # Deselect
                del self.selected_sources[uri]
                self.notify(f"Removed: {info['name']}")
            else:
                # Select
                self.selected_sources[uri] = {
                    "name": f"{state} - {info['name']}",
                    "description": info.get("description", ""),
                    "geometry": info.get("geometry", "unknown"),
                }
                self.notify(f"Added: {info['name']}", severity="information")

            self._update_selected_list()

    def _update_selected_list(self) -> None:
        """Update the selected sources list view."""
        list_view = self.query_one("#selected-list", ListView)
        list_view.clear()

        for uri, info in self.selected_sources.items():
            list_view.append(ListItem(Label(f"{info['name']}\n  {uri}")))

        # Update count in title
        count = len(self.selected_sources)
        title = self.query_one("#selected-title", Static)
        title.update(f"Selected Sources ({count})")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-box":
            self._filter_tree(event.value.lower())

    def _filter_tree(self, query: str) -> None:
        """Filter the tree based on search query."""
        tree = self.query_one("#source-tree", Tree)

        def filter_node(node: TreeNode, query: str) -> bool:
            """Recursively filter nodes. Returns True if node or any child matches."""
            # Check if this node matches
            label = str(node.label).lower()
            matches = query in label

            # Check data for URI matches
            if node.data and isinstance(node.data, dict):
                if "uri" in node.data:
                    matches = matches or query in node.data["uri"].lower()
                if "info" in node.data:
                    desc = node.data["info"].get("description", "").lower()
                    matches = matches or query in desc

            # Check children
            child_matches = False
            for child in node.children:
                if filter_node(child, query):
                    child_matches = True

            # Show node if it matches or has matching children
            # Note: Textual's Tree doesn't have a hide mechanism, so we expand matches
            if matches or child_matches:
                if not node.is_expanded and node.children:
                    node.expand()
                return True

            return False

        if query:
            for child in tree.root.children:
                filter_node(child, query)
        else:
            # Collapse all when search cleared
            for child in tree.root.children:
                child.collapse()
            # Keep Census expanded
            if tree.root.children:
                tree.root.children[0].expand()

    def action_focus_search(self) -> None:
        """Focus the search box."""
        self.query_one("#search-box", Input).focus()

    def action_add_custom(self) -> None:
        """Add a custom source."""
        self.notify("Custom source dialog coming soon!", severity="warning")

    def action_back(self) -> None:
        """Go back to welcome screen."""
        self.app.pop_screen()

    def action_continue_next(self) -> None:
        """Continue to next screen."""
        if not self.selected_sources:
            self.notify("Please select at least one data source", severity="error")
            return

        # Store selections in app
        self.app.recipe_data["sources"] = self.selected_sources.copy()

        # TODO: Push bounds configuration screen
        self.notify(
            f"Selected {len(self.selected_sources)} sources. Next: Bounds configuration",
            severity="information",
        )

        # For now, show what we have
        from .bounds import BoundsScreen
        self.app.push_screen(BoundsScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back-btn":
            self.action_back()
        elif event.button.id == "custom-btn":
            self.action_add_custom()
        elif event.button.id == "continue-btn":
            self.action_continue_next()
