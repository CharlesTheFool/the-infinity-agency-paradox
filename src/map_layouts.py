"""
Map Layout Generator
Creates ASCII spatial maps for POI graphs showing trails and spatial relationships
"""

from typing import Dict, List, Tuple
from rich.text import Text

from src.minimap_config import *


class MapLayout:
    """Generates spatial ASCII maps based on POI topology"""

    def __init__(self, location_data: Dict, poi_system, knowledge_menu, loop_manager):
        self.location_data = location_data
        self.poi_system = poi_system
        self.knowledge_menu = knowledge_menu
        self.loop_manager = loop_manager

    def generate_spatial_map(self, location_id: str) -> Text:
        """Generate spatial map for location"""
        topology = self._analyze_topology(location_id)

        if topology == "quantum_glitch":
            return self._render_quantum_glitch(location_id)
        elif topology == "single":
            return self._render_single_poi(location_id)
        elif topology == "linear_2":
            return self._render_vertical_stack(location_id)
        elif topology == "linear_3":
            return self._render_linear_3(location_id)
        elif topology == "triangle_3":
            return self._render_triangle_3(location_id)
        else:
            # Fallback to simple layout
            return self._render_simple_list(location_id)

    def _analyze_topology(self, location_id: str) -> str:
        """Determine POI graph topology"""
        location_data = self.location_data["locations"][location_id]
        pois = location_data.get("points_of_interest", {})
        poi_count = len(pois)

        # Special case: Quantum Moon has unique glitchy navigation
        if location_id == "quantum_moon":
            return "quantum_glitch"

        if poi_count == 1:
            return "single"

        elif poi_count == 2:
            return "linear_2"

        elif poi_count == 3:
            # Check if all are connected (triangle) or linear chain
            poi_ids = list(pois.keys())
            connections_count = [len(pois[poi_id].get("connections", [])) for poi_id in poi_ids]

            # Triangle: all have 2 connections
            if all(c == 2 for c in connections_count):
                return "triangle_3"
            # Linear chain: one has 1 connection, one has 2, one has 1
            elif sorted(connections_count) == [1, 1, 2]:
                return "linear_3"

        return "complex"

    def _render_vertical_stack(self, location_id: str) -> Text:
        """Render 2-POI vertical stack map"""
        content = Text()
        location_data = self.location_data["locations"][location_id]
        pois = location_data.get("points_of_interest", {})

        # Sort POIs by grid position (y-coordinate) for proper spatial ordering
        poi_items = [(poi_id, pois[poi_id]) for poi_id in pois.keys()]
        poi_items.sort(key=lambda x: x[1].get("grid_position", [0, 0])[1])

        top_poi_id, top_poi = poi_items[0]
        bottom_poi_id, bottom_poi = poi_items[1]

        # Get POI names
        top_name = top_poi.get("name", top_poi_id.replace("_", " ").title())
        bottom_name = bottom_poi.get("name", bottom_poi_id.replace("_", " ").title())

        # Render top POI
        top_is_current = top_poi_id == self.poi_system.current_poi
        top_box = f"[{top_name}]"
        content.append(top_box.center(46) + "\n", style="bold cyan" if top_is_current else "white")

        # Render top marker with inline details
        top_marker = "@" if top_is_current else self._get_poi_marker(location_id, top_poi_id)
        top_inline = self._get_inline_details(location_id, top_poi_id, top_poi, is_current=top_is_current)
        marker_line = f"{top_marker}  {top_inline}" if top_inline else top_marker
        # Check for collapsed state
        if top_marker == ICON_COLLAPSED:
            marker_style = COLOR_COLLAPSED
        else:
            marker_style = "bold cyan" if top_is_current else ("white" if top_inline else "dim")
        content.append(marker_line.center(46) + "\n\n", style=marker_style)

        # Render vertical connector
        content.append(TRAIL_VERTICAL.center(46) + "\n", style="dim")
        content.append(TRAIL_VERTICAL.center(46) + "\n\n", style="dim")

        # Render bottom POI
        bottom_is_current = bottom_poi_id == self.poi_system.current_poi
        bottom_box = f"[{bottom_name}]"
        content.append(bottom_box.center(46) + "\n", style="bold cyan" if bottom_is_current else "white")

        # Render bottom marker with inline details
        bottom_marker = "@" if bottom_is_current else self._get_poi_marker(location_id, bottom_poi_id)
        bottom_inline = self._get_inline_details(location_id, bottom_poi_id, bottom_poi, is_current=bottom_is_current)
        marker_line = f"{bottom_marker}  {bottom_inline}" if bottom_inline else bottom_marker
        # Check for collapsed state
        if bottom_marker == ICON_COLLAPSED:
            marker_style = COLOR_COLLAPSED
        else:
            marker_style = "bold cyan" if bottom_is_current else ("white" if bottom_inline else "dim")
        content.append(marker_line.center(46) + "\n", style=marker_style)

        return content

    def _render_linear_3(self, location_id: str) -> Text:
        """Render 3-POI vertical chain map"""
        content = Text()
        location_data = self.location_data["locations"][location_id]
        pois = location_data.get("points_of_interest", {})

        # Sort POIs by grid position (y-coordinate)
        poi_items = [(poi_id, pois[poi_id]) for poi_id in pois.keys()]
        poi_items.sort(key=lambda x: x[1].get("grid_position", [0, 0])[1])

        # Render each POI with connectors
        for idx, (poi_id, poi_data) in enumerate(poi_items):
            poi_name = poi_data.get("name", poi_id.replace("_", " ").title())
            is_current = poi_id == self.poi_system.current_poi

            # Render POI box
            poi_box = f"[{poi_name}]"
            content.append(poi_box.center(46) + "\n", style="bold cyan" if is_current else "white")

            # Render marker with inline details
            marker = "@" if is_current else self._get_poi_marker(location_id, poi_id)
            inline_details = self._get_inline_details(location_id, poi_id, poi_data, is_current=is_current)
            marker_line = f"{marker}  {inline_details}" if inline_details else marker
            # Check for collapsed state
            if marker == ICON_COLLAPSED:
                marker_style = COLOR_COLLAPSED
            else:
                marker_style = "bold cyan" if is_current else ("white" if inline_details else "dim")
            content.append(marker_line.center(46) + "\n", style=marker_style)

            # Add vertical connector if not the last POI
            if idx < len(poi_items) - 1:
                content.append("\n", style="white")
                content.append(TRAIL_VERTICAL.center(46) + "\n", style="dim")
                content.append(TRAIL_VERTICAL.center(46) + "\n\n", style="dim")

        return content

    def _render_single_poi(self, location_id: str) -> Text:
        """Render centered single POI map"""
        content = Text()
        location_data = self.location_data["locations"][location_id]
        pois = location_data.get("points_of_interest", {})

        # Get the single POI
        poi_id = list(pois.keys())[0]
        poi_data = pois[poi_id]
        poi_name = poi_data.get("name", poi_id.replace("_", " ").title())
        is_current = poi_id == self.poi_system.current_poi

        # Center POI name
        poi_line = f"[{poi_name}]".center(46)
        content.append(poi_line + "\n", style="bold cyan" if is_current else "white")

        # Marker with inline details
        marker = "@" if is_current else self._get_poi_marker(location_id, poi_id)
        inline_details = self._get_inline_details(location_id, poi_id, poi_data, is_current=is_current)
        marker_line = f"{marker}  {inline_details}" if inline_details else marker
        # Check for collapsed state
        if marker == ICON_COLLAPSED:
            marker_style = COLOR_COLLAPSED
        else:
            marker_style = "bold cyan" if is_current else ("white" if inline_details else "dim")
        content.append(marker_line.center(46) + "\n", style=marker_style)

        return content

    def _render_triangle_3(self, location_id: str) -> Text:
        """Render 3-POI triangular layout"""
        content = Text()
        location_data = self.location_data["locations"][location_id]
        pois = location_data.get("points_of_interest", {})

        # Sort POIs by grid position to identify top and bottom POIs
        poi_items = [(poi_id, pois[poi_id]) for poi_id in pois.keys()]
        poi_items.sort(key=lambda x: (x[1].get("grid_position", [0, 0])[1], x[1].get("grid_position", [0, 0])[0]))

        top_poi_id, top_poi = poi_items[0]
        left_poi_id, left_poi = poi_items[1] if poi_items[1][1].get("grid_position", [0, 0])[0] < 0 else poi_items[2]
        right_poi_id, right_poi = poi_items[2] if poi_items[1][1].get("grid_position", [0, 0])[0] < 0 else poi_items[1]

        # Get names
        top_name = top_poi.get("name", top_poi_id.replace("_", " ").title())
        left_name = left_poi.get("name", left_poi_id.replace("_", " ").title())
        right_name = right_poi.get("name", right_poi_id.replace("_", " ").title())

        # Render top POI
        top_is_current = top_poi_id == self.poi_system.current_poi
        content.append(f"[{top_name}]".center(46) + "\n", style="bold cyan" if top_is_current else "white")
        top_marker = "@" if top_is_current else self._get_poi_marker(location_id, top_poi_id)
        top_inline = self._get_inline_details(location_id, top_poi_id, top_poi, is_current=top_is_current)
        top_marker_line = f"{top_marker}  {top_inline}" if top_inline else top_marker
        # Check for collapsed state
        if top_marker == ICON_COLLAPSED:
            marker_style = COLOR_COLLAPSED
        else:
            marker_style = "bold cyan" if top_is_current else ("white" if top_inline else "dim")
        content.append(top_marker_line.center(46) + "\n\n", style=marker_style)

        # Render diagonal connectors
        content.append("/                 \\".center(46) + "\n", style="dim")
        content.append("/                   \\".center(46) + "\n\n", style="dim")

        # Render bottom left POI
        left_is_current = left_poi_id == self.poi_system.current_poi
        left_box = f"[{left_name}]"
        content.append(f"{left_box:<23}", style="bold cyan" if left_is_current else "white")

        # Render bottom right POI
        right_is_current = right_poi_id == self.poi_system.current_poi
        right_box = f"[{right_name}]"
        content.append(f"{right_box:>23}\n", style="bold cyan" if right_is_current else "white")

        # Render left marker
        left_marker = "@" if left_is_current else self._get_poi_marker(location_id, left_poi_id)
        left_inline = self._get_inline_details(location_id, left_poi_id, left_poi, is_current=left_is_current)
        left_marker_line = f"{left_marker}  {left_inline}" if left_inline else left_marker
        # Check for collapsed state
        if left_marker == ICON_COLLAPSED:
            left_style = COLOR_COLLAPSED
        else:
            left_style = "bold cyan" if left_is_current else ("white" if left_inline else "dim")
        content.append(f"{left_marker_line:<23}", style=left_style)

        # Render right marker
        right_marker = "@" if right_is_current else self._get_poi_marker(location_id, right_poi_id)
        right_inline = self._get_inline_details(location_id, right_poi_id, right_poi, is_current=right_is_current)
        right_marker_line = f"{right_marker}  {right_inline}" if right_inline else right_marker
        # Check for collapsed state
        if right_marker == ICON_COLLAPSED:
            right_style = COLOR_COLLAPSED
        else:
            right_style = "bold cyan" if right_is_current else ("white" if right_inline else "dim")
        content.append(f"{right_marker_line:>23}\n", style=right_style)

        return content

    def _render_quantum_glitch(self, location_id: str) -> Text:
        """Render Quantum Moon with glitch effect until grove is reached"""
        content = Text()
        location_data = self.location_data["locations"][location_id]
        pois = location_data.get("points_of_interest", {})

        # Check if player is at grove (puzzle solved)
        at_grove = self.poi_system.current_poi == "grove"

        if at_grove:
            # Normal clear map at grove
            content.append("[Quantum Moon Surface]".center(46) + "\n", style="dim")
            content.append(".".center(46) + "\n\n", style="dim")
            content.append(TRAIL_VERTICAL.center(46) + "\n", style="dim")
            content.append(TRAIL_VERTICAL.center(46) + "\n\n", style="dim")
            content.append("[The Grove]".center(46) + "\n", style="bold cyan")

            # Get grove details
            grove_poi = pois.get("grove", {})
            grove_inline = self._get_inline_details(location_id, "grove", grove_poi, is_current=True)
            marker_line = f"@  {grove_inline}" if grove_inline else "@"
            content.append(marker_line.center(46) + "\n", style="bold cyan")
        else:
            # Glitchy unintelligible map at surface
            content.append("[Q̴u̷a̸n̶t̴u̵m̶ ̷M̸o̷o̶n̸ ̴S̵u̸r̷f̵a̴c̶e̸]".center(46) + "\n", style="bold cyan")
            surface_poi = pois.get("surface", {})
            surface_inline = self._get_inline_details(location_id, "surface", surface_poi, is_current=True)
            marker_line = f"@  {surface_inline}" if surface_inline else "@"
            content.append(marker_line.center(46) + "\n\n", style="bold cyan")

            # Glitched connector
            content.append("│̵̢̛̗̾?̴̰̓́?̶͎̈́̕│̶̮̍".center(46) + "\n", style="dim")
            content.append("░̷▒̸▓̶█̴▓̶▒̸░".center(46) + "\n\n", style="dim")

            # Corrupted grove representation
            content.append("[?̶?̸?̷?̶?̴?̵?̸]".center(46) + "\n", style="dim")
            content.append("█̴░̸▓̷░̶█".center(46) + "\n", style="dim")

            # Hint text
            content.append("\n")
            content.append("  (Quantum instability detected)".center(46) + "\n", style="yellow dim italic")

        return content

    def _render_simple_list(self, location_id: str) -> Text:
        """Fallback: simple list for complex topologies"""
        content = Text()
        content.append("  Complex layout - list view\n\n", style="dim")
        return content

    def _get_inline_details(self, location_id: str, poi_id: str, poi_data: Dict, is_current: bool) -> str:
        """Build compact inline detail string for marker line"""
        parts = []

        # Player location
        if is_current:
            parts.append("You")

        # Ship location (always show - critical navigation info)
        if poi_data.get("has_ship", False):
            parts.append("Ship docked")

        # Only show NPCs and entries if this is the current POI
        if is_current:
            # NPCs (show name directly)
            npcs = poi_data.get("npcs", [])
            for npc_id in npcs:
                npc_name = npc_id.replace("_", " ").title()
                parts.append(npc_name)

            # Entry counts
            entries = poi_data.get("entries", [])
            if entries:
                accessible = 0
                locked = 0
                found = 0

                for entry_id in entries:
                    full_entry_id = f"{location_id}.{entry_id}"
                    if full_entry_id in self.knowledge_menu.all_entries:
                        entry = self.knowledge_menu.all_entries[full_entry_id]

                        if entry.discovered:
                            found += 1
                        else:
                            can_access, _ = self.knowledge_menu.can_access_entry(full_entry_id)
                            if can_access:
                                accessible += 1
                            else:
                                locked += 1

                total = len(entries)
                if found == total:
                    parts.append("all found")
                else:
                    if accessible > 0:
                        parts.append(f"{accessible} entries")
                    if locked > 0:
                        parts.append(f"{locked} locked")

        # Join with middle dot separator
        if parts:
            detail_str = " · ".join(parts)
            # Abbreviate if too long to fit
            if len(detail_str) > 28:
                detail_str = detail_str.replace("Ship docked", "Ship")
            return f"({detail_str})"
        return ""

    def _get_poi_marker(self, location_id: str, poi_id: str) -> str:
        """Get single-character marker for POI"""
        location_data = self.location_data["locations"][location_id]
        poi_data = location_data.get("points_of_interest", {}).get(poi_id, {})

        # Check if quantum cavern has collapsed (time-based blocker)
        if poi_id == "quantum_cavern" and self.loop_manager.cavern_has_collapsed:
            return ICON_COLLAPSED  # "◌" - fallen into black hole

        # Check if POI itself requires knowledge to access
        poi_requires = poi_data.get("requires_knowledge", [])
        if poi_requires:
            for knowledge_id in poi_requires:
                if knowledge_id not in self.knowledge_menu.progress.knowledge_gained:
                    return ICON_LOCKED_POI  # "⚠"

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
