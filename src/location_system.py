"""
Location System - Navigation and Location Management
Handles location visiting, entry discovery, and content display
"""

import time
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from src.visualizer import Visualizer
from src.knowledge_menu import KnowledgeMenu


class LocationSystem:
    """Manages locations and exploration"""

    def __init__(self, console: Console, visualizer: Visualizer, knowledge_menu: KnowledgeMenu, location_data: Dict):
        self.console = console
        self.visualizer = visualizer
        self.knowledge_menu = knowledge_menu
        self.location_data = location_data
        self.current_location = "timber_hearth"  # Start at home

    def can_visit_location(self, location_id: str) -> Tuple[bool, str]:
        """Check if location can be visited. Returns (can_visit, reason_if_not)"""
        if location_id not in self.location_data["locations"]:
            return False, "Unknown location"

        loc_info = self.location_data["locations"][location_id]

        # Check if always accessible
        if loc_info.get("always_accessible", False):
            return True, ""

        # Check knowledge requirements
        required_knowledge = loc_info.get("requires_knowledge", [])
        if required_knowledge:
            if not self.knowledge_menu.progress.has_all_knowledge(required_knowledge):
                missing = [k for k in required_knowledge if not self.knowledge_menu.has_knowledge(k)]
                if "ship_operation" in missing:
                    return False, "You need the ship's launch code first"
                return False, f"Requires knowledge: {', '.join(missing)}"

        # Check exploration percentage
        required_pct = loc_info.get("requires_exploration_percentage", 0)
        if required_pct > 0:
            total_entries = self.knowledge_menu.get_total_entries()
            current_pct = self.knowledge_menu.progress.get_completion_percentage(total_entries) / 100
            if current_pct < required_pct:
                needed = int((required_pct - current_pct) * 100)
                return False, f"You must explore {needed}% more before this location becomes accessible"

        return True, ""

    def visit_location(self, location_id: str) -> bool:
        """
        Visit a location and display its contents.
        Returns True if visit was successful.
        """
        # Check if can visit
        can_visit, reason = self.can_visit_location(location_id)
        if not can_visit:
            self.console.print(f"\n[red]Cannot visit this location: {reason}[/red]\n")
            return False

        # Mark location as visited
        self.knowledge_menu.progress.locations_visited.add(location_id)
        self.current_location = location_id

        # Display location
        self._display_location(location_id)

        return True

    def _display_location(self, location_id: str):
        """Display location and its available content"""
        loc_info = self.location_data["locations"][location_id]

        self.visualizer.clear_screen()

        # Check if first visit for atmospheric arrival
        is_first_visit = location_id not in self.knowledge_menu.progress.locations_visited

        # Location header with atmospheric arrival
        emoji = loc_info.get("emoji", "📍")
        name = loc_info["name"]

        header = Text()
        header.append(f"\n{emoji} ", style="bold")
        header.append(f"{name.upper()}\n\n", style="bold cyan")

        # Atmospheric first-visit descriptions
        if is_first_visit:
            arrivals = {
                "timber_hearth": (
                    "You stand in Timber Hearth Village, your home among the stars.\n"
                    "The Observatory tower rises against the sky. Your ship waits,\n"
                    "patient and ready. Ancient Nomai ruins dot the landscape—\n"
                    "evidence of those who came before.\n"
                ),
                "attlerock": (
                    "The Attlerock looms before you—Timber Hearth's cratered moon.\n"
                    "Nomai ruins cover its surface, stone structures that have\n"
                    "endured for millennia.\n\n"
                    "Wait... some of the inscriptions are FLICKERING. Phasing in\n"
                    "and out of existence. Quantum instability?\n\n"
                    "You'll need to understand what's happening here.\n"
                ),
                "brittle_hollow": (
                    "Brittle Hollow spreads beneath you—a fractured planet slowly\n"
                    "collapsing into its own black hole. Chunks of surface fall\n"
                    "away as you watch.\n\n"
                    "A massive tower pierces the sky. Nomai construction. The\n"
                    "architecture suggests... temporal research?\n\n"
                    "Time to investigate.\n"
                ),
                "quantum_moon": (
                    "The Quantum Moon materializes around you.\n\n"
                    "This shouldn't be possible. A moon that exists in six locations\n"
                    "simultaneously, collapsing into singular reality only when\n"
                    "observed...\n\n"
                    "And there, in a grove bathed in impossible light...\n\n"
                    "A Nomai. Alive.\n\n"
                    "After 280,000 years.\n"
                )
            }
            header.append(arrivals.get(location_id, loc_info.get("description", "")), style="white")
        else:
            # Return visit - shorter description
            header.append(loc_info.get("description", ""), style="white")

        header.append("\n")

        self.console.print(header)
        time.sleep(2 if is_first_visit else 1)

        # Show available entries
        self._show_location_entries(location_id)

    def _show_location_entries(self, location_id: str):
        """Show available entries at current location"""
        loc_info = self.location_data["locations"][location_id]
        entries = loc_info.get("entries", {})

        available_entries = []
        locked_entries = []

        for entry_id, entry_data in entries.items():
            full_entry_id = f"{location_id}.{entry_id}"
            can_access, reason = self.knowledge_menu.can_access_entry(full_entry_id)

            entry_info = {
                "id": entry_id,
                "full_id": full_entry_id,
                "title": entry_data["title"],
                "type": entry_data["type"],
                "is_quantum": entry_data.get("quantum", False),
                "discovered": self.knowledge_menu.all_entries[full_entry_id].discovered
            }

            if can_access or entry_info["discovered"]:
                available_entries.append(entry_info)
            else:
                locked_entries.append({**entry_info, "lock_reason": reason})

        # Display available entries
        if available_entries:
            self.console.print(Text("\n🔍 AVAILABLE TO EXPLORE:\n", style="bold green"))
            for i, entry in enumerate(available_entries, 1):
                status = "✓" if entry["discovered"] else "●"
                quantum_mark = " ⟁" if entry["is_quantum"] and not entry["discovered"] else ""
                discovered_mark = " [dim](already discovered)[/dim]" if entry["discovered"] else ""

                self.console.print(f"  {status} {i}. {entry['title']}{quantum_mark}{discovered_mark}")

        # Display locked entries
        if locked_entries:
            self.console.print(Text("\n🔒 LOCKED:\n", style="bold red"))
            for entry in locked_entries:
                quantum_mark = " ⟁" if entry["is_quantum"] else ""
                self.console.print(f"  ? {entry['title']}{quantum_mark} - [dim]{entry['lock_reason']}[/dim]")

        self.console.print("\n")

    def explore_entry(self, location_id: str, entry_id: str) -> Optional[Dict]:
        """
        Explore a specific entry at the current location.
        Returns entry data if successful, None otherwise.
        """
        full_entry_id = f"{location_id}.{entry_id}"

        # Check if entry exists
        if full_entry_id not in self.knowledge_menu.all_entries:
            self.console.print(f"\n[red]Entry not found: {entry_id}[/red]\n")
            return None

        # Check if can access
        can_access, reason = self.knowledge_menu.can_access_entry(full_entry_id)

        # If quantum and not stabilized, show quantum text
        entry_data = self._get_entry_raw_data(full_entry_id)
        if entry_data.get("quantum", False) and not can_access:
            self._show_quantum_text(entry_data)
            return None

        # If other lock reason, show message
        if not can_access:
            self.console.print(f"\n[red]Cannot access: {reason}[/red]\n")
            return None

        # Mark as discovered (returns True if newly discovered)
        was_new = self.knowledge_menu.discover_entry(full_entry_id)

        if was_new:
            self._show_discovery_notification(entry_data["title"])

        return entry_data

    def _get_entry_raw_data(self, full_entry_id: str) -> Dict:
        """Get raw entry data from location config"""
        parts = full_entry_id.split(".")
        if len(parts) != 2:
            return {}

        loc_id, entry_id = parts
        return self.location_data["locations"].get(loc_id, {}).get("entries", {}).get(entry_id, {})

    def _show_quantum_text(self, entry_data: Dict):
        """Display unstabilized quantum text"""
        self.visualizer.clear_screen()

        quantum_text = Text()
        quantum_text.append("\n⟁ QUANTUM TEXT DETECTED ⟁\n\n", style="bold yellow")
        quantum_text.append("The inscription FLICKERS and phases in and out of existence.\n\n", style="yellow")
        quantum_text.append("Fragments: ", style="white")
        quantum_text.append(f"\"...{entry_data['title']}...\" ", style="italic dim")
        quantum_text.append("\"...knowledge...\" ", style="italic dim")
        quantum_text.append("\"...understanding...\"\n\n", style="italic dim")
        quantum_text.append("The words shimmer and VANISH before you can read them.\n\n", style="yellow")

        if not self.knowledge_menu.has_knowledge("quantum_stabilization_ability"):
            quantum_text.append("You need to learn how to stabilize quantum texts.\n", style="red")
            quantum_text.append("Perhaps there's a technique documented somewhere on the Attlerock?\n", style="dim")
        else:
            quantum_text.append("Use the ", style="white")
            quantum_text.append("'stabilize'", style="bold cyan")
            quantum_text.append(" command to collapse the waveform.\n", style="white")

        self.console.print(Panel(quantum_text, border_style="yellow", title="UNSTABLE"))
        time.sleep(2)

    def _show_discovery_notification(self, entry_title: str):
        """Show notification for newly discovered entry"""
        notif = Text()
        notif.append("📝 NEW ENTRY ADDED TO LOG\n", style="bold green")
        notif.append(f"{entry_title}", style="cyan")

        self.console.print(Panel(notif, border_style="green"))
        time.sleep(1.5)

    def get_available_locations(self) -> List[Dict]:
        """Get list of locations with accessibility status"""
        locations = []

        for loc_id, loc_info in self.location_data["locations"].items():
            can_visit, reason = self.can_visit_location(loc_id)
            locations.append({
                "id": loc_id,
                "name": loc_info["name"],
                "emoji": loc_info.get("emoji", "📍"),
                "can_visit": can_visit,
                "lock_reason": reason,
                "visited": loc_id in self.knowledge_menu.progress.locations_visited
            })

        return locations

    def show_location_list(self):
        """Display all locations with their status"""
        locations = self.get_available_locations()

        self.console.print(Text("\n🌌 SOLAR SYSTEM LOCATIONS:\n", style="bold cyan"))

        for loc in locations:
            if loc["can_visit"]:
                status = "→" if loc["id"] == self.current_location else "●"
                visited_mark = " ✓" if loc["visited"] else ""
                self.console.print(f"  {status} {loc['emoji']} {loc['name']}{visited_mark}")
            else:
                self.console.print(f"  ? {loc['emoji']} {loc['name']} - [dim]{loc['lock_reason']}[/dim]")

        self.console.print("\n")

    def get_current_location_name(self) -> str:
        """Get name of current location"""
        return self.location_data["locations"][self.current_location]["name"]
