"""
POI (Point of Interest) Navigation System
Handles spatial movement, POI discovery, and context-sensitive actions
"""

from typing import Dict, List, Set, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time


class POISystem:
    """Manages spatial navigation between points of interest"""

    def __init__(self, console: Console, location_data: Dict):
        self.console = console
        self.location_data = location_data

        # Current state
        self.current_location = "timber_hearth"
        self.current_poi = None  # Will be set to starting_poi
        self.in_ship = False
        self.ship_flying = False

        # Discovery tracking
        self.discovered_pois: Set[str] = set()

        # Visit tracking (for showing "visited" labels)
        self.visited_pois: Set[str] = set()

        # Initialize at starting POI
        self._initialize_starting_position()

    def _initialize_starting_position(self):
        """Set player at the starting POI of current location"""
        loc_data = self.location_data["locations"][self.current_location]
        self.current_poi = loc_data.get("starting_poi", "village_center")
        self._discover_poi(self.current_location, self.current_poi)
        # Mark as visited
        full_poi_id = f"{self.current_location}.{self.current_poi}"
        self.visited_pois.add(full_poi_id)

    def _discover_poi(self, location: str, poi: str):
        """Mark a POI as discovered"""
        full_poi_id = f"{location}.{poi}"
        self.discovered_pois.add(full_poi_id)

    def is_poi_discovered(self, location: str, poi: str) -> bool:
        """Check if POI has been discovered"""
        full_poi_id = f"{location}.{poi}"
        return full_poi_id in self.discovered_pois

    def get_current_poi_data(self) -> Dict:
        """Get data for current POI"""
        # Handle invalid location gracefully
        if self.current_location not in self.location_data.get("locations", {}):
            return {}

        loc_data = self.location_data["locations"][self.current_location]
        pois = loc_data.get("points_of_interest", {})
        return pois.get(self.current_poi, {})

    def _strip_articles(self, name: str) -> str:
        """Remove articles (the, a, an, your) from name for command display"""
        name_lower = name.lower()
        for article in ["the ", "your ", "a ", "an "]:
            if name_lower.startswith(article):
                return name_lower[len(article):]
        return name_lower

    def _has_accessible_entries(self, entry_ids: List[str], knowledge_menu) -> bool:
        """Check if any entries at current POI are accessible"""
        for entry_id in entry_ids:
            full_entry_id = f"{self.current_location}.{entry_id}"
            if full_entry_id in knowledge_menu.all_entries:
                entry = knowledge_menu.all_entries[full_entry_id]
                can_access, _ = knowledge_menu.can_access_entry(full_entry_id)

                # Show if accessible OR already discovered (can re-read)
                if can_access or entry.discovered:
                    return True

        return False

    def get_available_pois(self) -> List[Dict]:
        """Get list of POIs connected to current position"""
        current_poi_data = self.get_current_poi_data()
        connections = current_poi_data.get("connections", [])

        # Handle invalid location gracefully
        if self.current_location not in self.location_data.get("locations", {}):
            return []

        loc_data = self.location_data["locations"][self.current_location]
        pois = loc_data.get("points_of_interest", {})

        available = []
        for poi_id in connections:
            if poi_id in pois:
                poi_data = pois[poi_id]
                distance = current_poi_data.get("distance_to", {}).get(poi_id, 1)
                discovered = self.is_poi_discovered(self.current_location, poi_id)

                available.append({
                    "id": poi_id,
                    "name": poi_data.get("name", poi_id.replace("_", " ").title()),
                    "distance": distance,
                    "discovered": discovered,
                    "description": poi_data.get("description", "")
                })

        return available

    def move_to_poi(self, poi_id: str) -> Tuple[bool, int, str]:
        """
        Move to a connected POI.
        Returns (success, action_cost, message)
        """
        current_poi_data = self.get_current_poi_data()
        connections = current_poi_data.get("connections", [])

        if poi_id not in connections:
            return False, 0, f"You can't reach {poi_id} from here."

        # Get distance (action cost)
        distance = current_poi_data.get("distance_to", {}).get(poi_id, 1)

        # Move to POI
        self.current_poi = poi_id
        self._discover_poi(self.current_location, poi_id)

        # Mark as visited
        full_poi_id = f"{self.current_location}.{poi_id}"
        self.visited_pois.add(full_poi_id)

        # Get POI name
        loc_data = self.location_data["locations"][self.current_location]
        pois = loc_data.get("points_of_interest", {})
        poi_name = pois.get(poi_id, {}).get("name", poi_id)

        return True, distance, f"You travel to {poi_name}..."



    def enter_ship(self) -> Tuple[bool, str]:
        """
        Attempt to enter ship.
        Returns (success, message)
        """
        poi_data = self.get_current_poi_data()
        if not poi_data.get("has_ship", False):
            return False, "Your ship isn't here."

        if self.in_ship:
            return False, "You're already in the ship."

        self.in_ship = True
        return True, "You climb into the ship's cockpit."

    def exit_ship(self) -> Tuple[bool, str]:
        """Exit the ship"""
        if not self.in_ship:
            return False, "You're not in the ship."

        if self.ship_flying:
            return False, "You can't exit while flying! Land first."

        self.in_ship = False
        return True, "You step out of the ship."

    def launch_ship(self) -> Tuple[bool, str]:
        """Take off from current location"""
        if not self.in_ship:
            return False, "You need to be in the ship."

        if self.ship_flying:
            return False, "You're already flying."

        self.ship_flying = True
        return True, "The ship lifts off into space..."

    def land_at_location(self, location_id: str, knowledge_menu) -> Tuple[bool, int, str]:
        """
        Land ship at a new location.
        Returns (success, action_cost, message)
        """
        if not self.ship_flying:
            return False, 0, "You need to launch first."

        if location_id not in self.location_data["locations"]:
            return False, 0, f"Unknown location: {location_id}"

        # Check if location is accessible
        loc_info = self.location_data["locations"][location_id]
        required_knowledge = loc_info.get("requires_knowledge", [])

        if required_knowledge:
            if not knowledge_menu.progress.has_all_knowledge(required_knowledge):
                missing = [k for k in required_knowledge if not knowledge_menu.has_knowledge(k)]
                return False, 0, f"Cannot access this location: requires {', '.join(missing)}"

        # Land at location
        self.current_location = location_id
        self.ship_flying = False

        # Move to starting POI
        starting_poi = loc_info.get("starting_poi", "landing_site")
        self.current_poi = starting_poi
        self._discover_poi(location_id, starting_poi)

        # Mark as visited
        full_poi_id = f"{location_id}.{starting_poi}"
        self.visited_pois.add(full_poi_id)

        loc_name = loc_info.get("name", location_id)

        return True, 2, f"You land on {loc_name}..."

    def get_contextual_actions(self, knowledge_menu, frequency_entered=False, npc_system=None, quantum_system=None) -> List[str]:
        """Get list of available actions based on current context with icons"""
        actions = []

        if self.ship_flying:
            # In ship, flying - navigation requires signal scope frequencies
            if not knowledge_menu.has_knowledge("signal_scope_frequencies"):
                # No frequencies logged - cannot navigate
                actions.append("• Navigation Unavailable - Log frequencies at radio station")
            else:
                # Has frequencies - show all locations with lock status
                locations = self.location_data.get("locations", {})
                for loc_id, loc_data in locations.items():
                    if loc_id == self.current_location:
                        continue

                    loc_name = loc_data.get("name", loc_id)

                    # Check if location is accessible
                    always_accessible = loc_data.get("always_accessible", False)
                    requires_knowledge = loc_data.get("requires_knowledge", [])

                    # Special gate for Quantum Moon - requires frequency entry THIS LOOP
                    if loc_id == "quantum_moon":
                        if frequency_entered:
                            # Frequency entered - accessible
                            actions.append(f"→ Visit {loc_name}")
                        elif knowledge_menu.has_knowledge("quantum_moon_frequency"):
                            # Know frequency exists but haven't entered it yet
                            actions.append(f"→ Visit {loc_name} (insert frequency at radio station)")
                        else:
                            # Don't know frequency yet - show as unknown
                            actions.append(f"→ Visit ??? (quantum interference detected)")
                    elif always_accessible or knowledge_menu.progress.has_all_knowledge(requires_knowledge):
                        # Accessible - show normally
                        actions.append(f"→ Visit {loc_name}")
                    else:
                        # Locked - show with requirement
                        missing = [k.replace("_", " ") for k in requires_knowledge
                                  if not knowledge_menu.has_knowledge(k)]
                        lock_reason = ", ".join(missing) if missing else "requirements"
                        actions.append(f"→ Visit {loc_name} (requires: {lock_reason})")
        elif self.in_ship:
            # In ship, on ground
            # Check for ship_operation knowledge directly (epistemic gate on launch, not entry)
            if knowledge_menu.has_knowledge("ship_operation"):
                actions.append("→ Launch")
            else:
                actions.append("• Enter Launch Code")
            actions.append("• Exit Ship")
        else:
            # Outside ship
            current_poi_data = self.get_current_poi_data()

            # Movement options - ALWAYS show all connected POIs
            available_pois = self.get_available_pois()
            for poi in available_pois:
                poi_name = self._strip_articles(poi['name'])

                # Add (visited) label if player has been there
                full_poi_id = f"{self.current_location}.{poi['id']}"
                visited_label = " (visited)" if full_poi_id in self.visited_pois else ""

                actions.append(f"→ Go to {poi_name}{visited_label}")

            # Ship option - add shortcut label if launch code known
            if current_poi_data.get("has_ship", False):
                shortcut_label = ""
                if knowledge_menu.has_knowledge("launch_code_epistemic"):
                    shortcut_label = " (shortcut)"
                actions.append(f"→ Enter Ship{shortcut_label}")

            # NPCs
            npcs = current_poi_data.get("npcs", [])
            for npc in npcs:
                # Format NPC name nicely from ID
                npc_name = npc.replace("_", " ").title()

                # Check if NPC has new dialogue and add "!" indicator
                new_indicator = ""
                if npc_system and npc_system.has_new_dialogue(npc, knowledge_menu):
                    new_indicator = " !"

                actions.append(f"• Talk to {npc_name}{new_indicator}")

            # Entries/objects - ALWAYS show if entries exist
            entries = current_poi_data.get("entries", [])
            has_quantum_entries = False
            if entries:
                # Count accessible vs locked entries
                accessible_count = 0
                locked_count = 0

                for entry_id in entries:
                    full_entry_id = f"{self.current_location}.{entry_id}"
                    if full_entry_id in knowledge_menu.all_entries:
                        entry = knowledge_menu.all_entries[full_entry_id]
                        can_access, _ = knowledge_menu.can_access_entry(full_entry_id)

                        if can_access or entry.discovered:
                            accessible_count += 1
                        else:
                            locked_count += 1

                        # Check if any entry is quantum
                        if entry.is_quantum:
                            has_quantum_entries = True

                # Show examine with status indicator
                if accessible_count > 0 and locked_count > 0:
                    actions.append(f"• Examine ({locked_count} locked)")
                elif accessible_count == 0:
                    actions.append(f"• Examine ({locked_count} locked)")
                else:
                    actions.append("• Examine")

            # Quantum observation - add if there are quantum entries at this location
            if has_quantum_entries and quantum_system:
                actions.append("• Close Eyes")

            # Special radio station frequency insertion
            if self.current_location == "timber_hearth" and self.current_poi == "radio_station":
                if knowledge_menu.has_knowledge("signal_scope_frequencies"):
                    if not frequency_entered:
                        # Frequency not entered yet - show as incomplete action
                        actions.append("• Insert Frequency ⚠")
                    else:
                        # Frequency already entered this loop
                        actions.append("• Insert Frequency ✓")

            # Special grove ending action (after all content exhausted)
            if self.current_location == "quantum_moon" and self.current_poi == "grove":
                if knowledge_menu.has_knowledge("complete_understanding"):
                    actions.append("Witness the End")

        return actions

    def get_current_location_name(self) -> str:
        """Get display name of current location"""
        loc_data = self.location_data["locations"][self.current_location]
        return loc_data.get("name", self.current_location.replace("_", " ").title())

    def get_current_poi_name(self) -> str:
        """Get display name of current POI"""
        current_poi_data = self.get_current_poi_data()
        return current_poi_data.get("name", self.current_poi.replace("_", " ").title())

    def show_current_scene(self, knowledge_menu=None, frequency_entered=False):
        """Display current POI description and context"""
        # Check ship states first
        if self.ship_flying:
            self._show_space_view()
            return
        elif self.in_ship:
            self._show_ship_interior(knowledge_menu, frequency_entered)
            return

        # Normal POI display
        poi_data = self.get_current_poi_data()
        poi_name = poi_data.get("name", self.current_poi.replace("_", " ").title())
        description = poi_data.get("description", "")

        # Build scene text
        scene = Text()
        scene.append(f"\n{poi_name.upper()}", style="bold cyan")

        # Show location context if not at home
        if self.current_location != "timber_hearth":
            loc_name = self.get_current_location_name()
            scene.append(f" - {loc_name}", style="dim")

        scene.append("\n\n", style="white")
        scene.append(description, style="white")
        scene.append("\n", style="white")

        self.console.print(scene)
        time.sleep(0.3)

    def _show_ship_interior(self, knowledge_menu=None, frequency_entered=False):
        """Show ship cockpit view with knowledge-based console states"""
        scene = Text()
        scene.append("\n━━━ SHIP COCKPIT ━━━\n\n", style="bold cyan")

        loc_name = self.get_current_location_name()
        scene.append(f"📍 Location: {loc_name}\n", style="dim")
        scene.append(f"🎯 POI: {self.get_current_poi_name()}\n\n", style="dim")

        scene.append("You sit at the ship's controls. The console glows before you:\n\n", style="white")

        # Determine console state based on knowledge
        has_frequencies = knowledge_menu and knowledge_menu.has_knowledge("signal_scope_frequencies")
        has_launch_code = knowledge_menu and knowledge_menu.has_knowledge("ship_operation")
        has_qm_frequency = knowledge_menu and knowledge_menu.has_knowledge("quantum_moon_frequency")

        # Ship console display
        scene.append("╔══════════════════════════════╗\n", style="cyan")
        scene.append("║  🖥️  SHIP CONSOLE            ║\n", style="cyan")
        scene.append("║                              ║\n", style="cyan")

        if not has_frequencies:
            # State 1: No signal scope frequencies logged
            scene.append("║  ⚠️  SIGNAL SCOPE OFFLINE    ║\n", style="yellow")
            scene.append("║                              ║\n", style="cyan")
            scene.append("║  Visit radio station to      ║\n", style="dim")
            scene.append("║  log navigation frequencies  ║\n", style="dim")
        else:
            # State 2+: Has frequencies
            # Show launch code status
            if has_launch_code:
                scene.append("║  STATUS: READY ✓             ║\n", style="green")
                scene.append("║  CODE: EPISTEMIC             ║\n", style="green")
            else:
                scene.append("║  STATUS: LOCKED              ║\n", style="yellow")
                scene.append("║  LAUNCH CODE: [________]     ║\n", style="yellow")

            scene.append("║                              ║\n", style="cyan")

            # Show navigation frequencies
            scene.append("║  📡 NAVIGATION SIGNALS       ║\n", style="cyan")
            scene.append("║  [2841] Timber Hearth        ║\n", style="dim")
            scene.append("║  [2847] The Attlerock        ║\n", style="dim")
            scene.append("║  [2857] Brittle Hollow       ║\n", style="dim")

            # Show Quantum Moon status based on frequency entry
            if frequency_entered:
                # Frequency entered this loop - accessible
                scene.append("║  [5555] Quantum Moon         ║\n", style="bold magenta")
            elif has_qm_frequency:
                # Know frequency but haven't entered it yet
                scene.append("║  [5555] Quantum Moon         ║\n", style="dim yellow")
                scene.append("║   └─ Insert at radio station ║\n", style="dim yellow")
            elif knowledge_menu and knowledge_menu.has_knowledge("quantum_signal_detected"):
                scene.append("║  [????] Unknown Signal       ║\n", style="yellow")
                scene.append("║   └─ Quantum interference    ║\n", style="dim yellow")

        scene.append("║                              ║\n", style="cyan")
        scene.append("╚══════════════════════════════╝\n", style="cyan")

        self.console.print(scene)
        time.sleep(0.3)

    def _show_space_view(self):
        """Show space/orbit view"""
        scene = Text()
        scene.append("\n━━━ IN ORBIT ━━━\n\n", style="bold cyan")

        scene.append("You float in the darkness of space. Stars drift past the cockpit window.\n", style="white")
        scene.append("The planets of the solar system beckon below.\n\n", style="white")

        self.console.print(scene)
        time.sleep(0.3)
