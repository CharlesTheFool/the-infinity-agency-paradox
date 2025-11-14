"""
Mini-Map System
Provides spatial navigation visualization for the game
"""

from typing import Dict, List, Set, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from src.minimap_config import *
from src.map_layouts import MapLayout


class MiniMap:
    """Renders mini-map HUD showing POI layout and progress"""

    def __init__(self, console: Console, poi_system, knowledge_menu, loop_manager):
        self.console = console
        self.poi_system = poi_system
        self.knowledge_menu = knowledge_menu
        self.loop_manager = loop_manager

    def render(self) -> None:
        """Main render method - switches between views based on state"""
        if self.poi_system.ship_flying:
            self._render_space_view()
        else:
            self._render_planet_view()

    # === PLANET VIEW (POI Graph) ===

    def _render_planet_view(self) -> None:
        """Render POI connection graph for current location"""
        location_id = self.poi_system.current_location
        location_data = self.poi_system.location_data["locations"][location_id]
        location_name = location_data.get("name", location_id.replace("_", " ").title())

        # Build map content
        content = Text()

        # Header
        content.append(f"LOCATION: {location_name.upper()}\n", style=COLOR_HEADER)
        content.append("─" * 45 + "\n", style=COLOR_BORDER)
        content.append("\n", style="white")

        # Generate spatial map using MapLayout
        layout_generator = MapLayout(
            self.poi_system.location_data,
            self.poi_system,
            self.knowledge_menu,
            self.loop_manager
        )

        spatial_map = layout_generator.generate_spatial_map(location_id)
        content.append(spatial_map)

        # Add ship state indicator if in ship
        if self.poi_system.in_ship:
            content.append("[IN SHIP]\n".center(45), style="cyan")
            content.append("\n")

        # Progress summary
        content.append("─" * 45 + "\n", style=COLOR_BORDER)
        poi_completion = self._calculate_location_completion(location_id)

        # Count visited POIs
        all_pois = location_data.get("points_of_interest", {})
        visited_count = sum(1 for poi_id in all_pois.keys()
                          if f"{location_id}.{poi_id}" in self.poi_system.visited_pois)

        content.append(f"Entries: {poi_completion['entries_found']}/{poi_completion['total_entries']} discovered",
                      style="white")
        if poi_completion['total_entries'] > 0:
            percent = int((poi_completion['entries_found'] / poi_completion['total_entries']) * 100)
            color = COLOR_COMPLETE if percent == 100 else COLOR_PARTIAL if percent > 0 else "white"
            content.append(f" ({percent}%)\n", style=color)
        else:
            content.append("\n")

        content.append(f"Explored: {visited_count}/{len(all_pois)} POIs visited\n", style="white")

        # Render panel
        panel = Panel(
            content,
            border_style=COLOR_BORDER,
            width=50,
            padding=(0, 1)
        )

        self.console.print(panel)

    # === SPACE VIEW (Solar System) ===

    def _render_space_view(self) -> None:
        """Render solar system overview when flying"""
        content = Text()

        # Header
        content.append("IN ORBIT - SELECT DESTINATION\n", style=COLOR_HEADER)
        content.append("─" * 45 + "\n", style=COLOR_BORDER)
        content.append("\n")

        # Show all locations
        locations = self.poi_system.location_data.get("locations", {})
        for loc_id, loc_data in locations.items():
            prefix = LOCATION_PREFIXES.get(loc_id, "[?]")
            loc_name = loc_data.get("name", loc_id.replace("_", " ").title())

            # Check accessibility
            always_accessible = loc_data.get("always_accessible", False)
            requires_knowledge = loc_data.get("requires_knowledge", [])
            is_accessible = always_accessible or self.knowledge_menu.progress.has_all_knowledge(requires_knowledge)

            # Get completion for this location
            completion = self._calculate_location_completion(loc_id)

            # Build location entry
            if is_accessible:
                content.append(f"  {prefix} {loc_name}\n", style="white")

                # Show completion status
                if completion['total_entries'] > 0:
                    found = completion['entries_found']
                    total = completion['total_entries']
                    percent = int((found / total) * 100)
                    color = COLOR_COMPLETE if percent == 100 else COLOR_PARTIAL if percent > 0 else "dim"
                    content.append(f"      {found}/{total} entries ({percent}%)\n", style=color)
                else:
                    content.append(f"      No entries\n", style="dim")
            else:
                content.append(f"  {prefix} {loc_name} ", style="dim")
                content.append(f"[LOCKED]\n", style=COLOR_LOCKED)
                # Show requirement
                missing = [k.replace("_", " ") for k in requires_knowledge
                          if not self.knowledge_menu.has_knowledge(k)]
                if missing:
                    content.append(f"      Requires: {', '.join(missing)}\n", style="dim")

            content.append("\n")

        content.append("─" * 45 + "\n", style=COLOR_BORDER)

        # Render panel
        panel = Panel(
            content,
            border_style="yellow",
            width=50,
            padding=(0, 1)
        )

        self.console.print(panel)

    # === HELPER METHODS ===

    def _get_poi_marker(self, location_id: str, poi_id: str) -> str:
        """Get single-character marker for POI based on its primary state"""
        location_data = self.poi_system.location_data["locations"][location_id]
        poi_data = location_data.get("points_of_interest", {}).get(poi_id, {})

        # Check entry status
        entries = poi_data.get("entries", [])
        if entries:
            all_discovered = True
            has_accessible = False

            for entry_id in entries:
                full_entry_id = f"{location_id}.{entry_id}"
                if full_entry_id in self.knowledge_menu.all_entries:
                    entry = self.knowledge_menu.all_entries[full_entry_id]

                    if not entry.discovered:
                        all_discovered = False
                        can_access, _ = self.knowledge_menu.can_access_entry(full_entry_id)
                        if can_access:
                            has_accessible = True

            if all_discovered:
                return ICON_COMPLETED
            elif has_accessible:
                return ICON_ENTRY_AVAILABLE
            else:
                return ICON_ENTRY_LOCKED

        # No entries - check if visited
        full_poi_id = f"{location_id}.{poi_id}"
        if full_poi_id in self.poi_system.visited_pois:
            return ICON_VISITED

        return ICON_UNKNOWN

    def _get_poi_details(self, location_id: str, poi_id: str, poi_data: Dict) -> List[str]:
        """Get list of detail strings for a POI"""
        details = []

        # Ship
        if poi_data.get("has_ship", False):
            details.append(f"{ICON_SHIP} Ship docked")

        # NPCs
        npcs = poi_data.get("npcs", [])
        for npc_id in npcs:
            npc_name = npc_id.replace("_", " ").title()
            details.append(f"{ICON_NPC} {npc_name} (NPC)")

        # Entries
        entries = poi_data.get("entries", [])
        if entries:
            found_count = 0
            accessible_count = 0
            locked_count = 0

            for entry_id in entries:
                full_entry_id = f"{location_id}.{entry_id}"
                if full_entry_id in self.knowledge_menu.all_entries:
                    entry = self.knowledge_menu.all_entries[full_entry_id]

                    if entry.discovered:
                        found_count += 1
                    else:
                        can_access, _ = self.knowledge_menu.can_access_entry(full_entry_id)
                        if can_access:
                            accessible_count += 1
                        else:
                            locked_count += 1

            total = len(entries)
            if found_count == total:
                details.append(f"{ICON_COMPLETED} All {total} entries discovered")
            else:
                if accessible_count > 0:
                    details.append(f"{ICON_ENTRY_AVAILABLE} {accessible_count} entries available")
                if locked_count > 0:
                    details.append(f"{ICON_ENTRY_LOCKED} {locked_count} entries locked")
                if found_count > 0:
                    details.append(f"  ({found_count}/{total} found)")

        # If no details, indicate empty
        if not details:
            details.append(f"{ICON_VISITED} No entries or NPCs")

        return details

    def _get_poi_color(self, location_id: str, poi_id: str) -> str:
        """Determine color for POI based on visit/completion status"""
        full_poi_id = f"{location_id}.{poi_id}"

        # Check if all entries are discovered
        location_data = self.poi_system.location_data["locations"][location_id]
        poi_data = location_data.get("points_of_interest", {}).get(poi_id, {})
        entries = poi_data.get("entries", [])

        if entries:
            all_discovered = True
            for entry_id in entries:
                full_entry_id = f"{location_id}.{entry_id}"
                if full_entry_id in self.knowledge_menu.all_entries:
                    entry = self.knowledge_menu.all_entries[full_entry_id]
                    if not entry.discovered:
                        all_discovered = False
                        break

            if all_discovered:
                return COLOR_COMPLETE

        # Check if visited
        if full_poi_id in self.poi_system.visited_pois:
            return COLOR_VISITED

        # Unvisited
        return COLOR_UNVISITED

    def _calculate_location_completion(self, location_id: str) -> Dict[str, int]:
        """Calculate entry completion stats for a location"""
        total_entries = 0
        entries_found = 0

        # Count entries in this location
        for entry_id, entry in self.knowledge_menu.all_entries.items():
            if entry.location_id == location_id:
                total_entries += 1
                if entry.discovered:
                    entries_found += 1

        return {
            "total_entries": total_entries,
            "entries_found": entries_found
        }
