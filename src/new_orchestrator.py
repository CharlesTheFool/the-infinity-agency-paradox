"""
New Orchestrator - Outer Wilds-Style Exploration with POI Navigation
Integrates POI system, NPC dialogues, action-based timer, context-sensitive commands
"""

import json
import random
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.visualizer import Visualizer
from src.knowledge_menu import KnowledgeMenu
from src.loop_manager import LoopManager
from src.poi_system import POISystem
from src.npc_system import NPCSystem
from src.quantum_system import QuantumSystem
from src.quantum_navigation import QuantumNavigator
from src.content_loader import ContentLoader
from src.interactions import InteractionHandler
from src.minimap import MiniMap


class OuterWildsOrchestrator:
    """Main game orchestrator with POI-based spatial navigation"""

    def __init__(self):
        self.visualizer = Visualizer()
        self.console = self.visualizer.console
        self.interactions = InteractionHandler()
        self.knowledge_menu = KnowledgeMenu(self.console)

        # Load location data
        self.location_data = self._load_location_data()

        # Initialize systems
        self.knowledge_menu.register_entries(self.location_data)
        self.loop_manager = LoopManager(
            self.console,
            self.visualizer,
            actions_until_supernova=self.location_data["supernova_config"]["actions_until_supernova"]
        )
        self.poi_system = POISystem(self.console, self.location_data)
        self.npc_system = NPCSystem(self.console)
        self.npc_system.load_npc_data()
        self.quantum_system = QuantumSystem(
            self.console,
            self.visualizer,
            self.knowledge_menu
        )
        self.quantum_navigator = QuantumNavigator(self.console)
        self.content_loader = ContentLoader(self.console, "content/entries")
        # Give NPC system access to content loader for dialogue entries
        self.npc_system.content_loader = self.content_loader

        # Initialize mini-map system
        self.minimap = MiniMap(self.console, self.poi_system, self.knowledge_menu, self.loop_manager)

        # Track intro and tutorial completion for UI flow
        self.intro_complete = False
        self.observatory_tutorial_shown = False

        # Track physical actions that reset each loop
        self.quantum_frequency_entered = False
        self.launch_code_entered = False

        # Track eye closing state for two-stage mechanics
        self.eyes_closed = False
        self.eyes_closed_at_location = None  # Track where eyes were closed (convergence/grove)

    def _load_location_data(self) -> dict:
        """Load location configuration"""
        location_file = Path("content/data/locations.json")
        with open(location_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run(self):
        """Main execution loop"""
        self.visualizer.show_title_card("EPISTEMIC AGENCY", "An Interactive Analysis of Outer Wilds")
        time.sleep(2)

        # Show intro
        self._show_intro()

        # Mark intro as complete
        self.intro_complete = True

        # Main exploration loop
        self._exploration_loop()

    def _show_intro(self):
        """Display immersive opening sequence"""
        self.visualizer.clear_screen()

        intro = Text()
        intro.append("\n" + "═" * 60 + "\n", style="dim")
        intro.append("\nYou wake beside a campfire on Timber Hearth, your home.\n\n", style="cyan")
        intro.append("Your unused ship rests nearby.\n", style="white")
        intro.append("The village is quiet. Above you, the stars turn in\n", style="white")
        intro.append("familiar patterns, but something feels... temporary.\n\n", style="white")
        intro.append("Like this moment won't last forever.\n\n", style="yellow")
        intro.append("═" * 60 + "\n", style="dim")

        self.console.print(intro)

        # Wait for user to continue
        input("\n[Press Enter to begin...]")

    def _exploration_loop(self):
        """Main gameplay loop with POI navigation"""
        running = True

        while running:
            # Show current scene
            self._show_current_scene()

            # Get command
            command = self._get_command()

            # Process command and get whether it should cost an action
            costs_action = True
            if command:
                costs_action = self._process_command(command)

            # Increment action timer for non-free actions (but not at grove - timeless space)
            at_grove = (self.poi_system.current_location == "quantum_moon" and
                       self.poi_system.current_poi == "grove")

            if costs_action and not at_grove:
                result = self.loop_manager.increment_action(1)

                # Handle quantum cavern collapse
                if result == "quantum_cavern_collapse":
                    self._handle_cavern_collapse()
                    continue

                # Handle supernova
                if result == "supernova":
                    self.loop_manager.trigger_supernova(self.knowledge_menu)
                    # Reset POI system to starting position
                    self.poi_system.current_location = "timber_hearth"
                    self.poi_system.in_ship = False
                    self.poi_system.ship_flying = False
                    self.poi_system._initialize_starting_position()

                    # Reset quantum navigator (in case player was on quantum moon)
                    self.quantum_navigator.reset_navigation()

                    # Reset physical actions (must repeat each loop)
                    self.quantum_frequency_entered = False
                    self.launch_code_entered = False

                    # Reset eye state
                    self.eyes_closed = False
                    self.eyes_closed_at_location = None

                    # Clear temporary same-loop knowledge flags
                    if "cavern_collapse_witnessed" in self.knowledge_menu.progress.knowledge_gained:
                        self.knowledge_menu.progress.knowledge_gained.remove("cavern_collapse_witnessed")

                    continue

    def _show_current_scene(self):
        """Display current POI"""
        self.visualizer.clear_screen()

        # If eyes are closed, show darkness scene instead
        if self.eyes_closed:
            self.console.print("\n" + "━" * 60 + "\n", style="dim")
            self.console.print("DARKNESS\n", style="bold dim")
            self.console.print("━" * 60 + "\n\n", style="dim")
            self.console.print("The universe holds its breath.\n\n", style="dim italic")
            return  # Skip normal rendering

        # Render mini-map HUD (hidden at grove - immersive ending space)
        at_grove = (self.poi_system.current_location == "quantum_moon" and
                   self.poi_system.current_poi == "grove")

        if not at_grove:
            self.minimap.render()

        # Check if we're at Quantum Moon surface and need navigation scene
        at_quantum_surface = (
            self.poi_system.current_location == "quantum_moon" and
            self.poi_system.current_poi == "surface" and
            not self.quantum_navigator.is_at_grove()
        )

        # Show appropriate scene
        if at_quantum_surface:
            # Show quantum navigation scene
            self.quantum_navigator.show_navigation_scene()
        else:
            # Show normal POI scene
            self.poi_system.show_current_scene(self.knowledge_menu, self.quantum_frequency_entered, self.launch_code_entered)

    def _get_command(self):
        """Get command from user via arrow key menu"""
        # If eyes are closed, only show "Open Eyes" option
        if self.eyes_closed:
            menu_actions = [
                "Open Eyes",
                "───────────────────",
                "• Help"
            ]
            choice = self.interactions.get_menu_choice(menu_actions, title="▸ ACTIONS", show_back=False)

            if choice is None:
                return "cancel"

            selected_action = menu_actions[choice]

            # Handle separator selection
            if selected_action.startswith("───"):
                return "cancel"

            return selected_action

        # Check if we're at Quantum Moon surface and need cardinal navigation
        at_quantum_surface = (
            self.poi_system.current_location == "quantum_moon" and
            self.poi_system.current_poi == "surface" and
            not self.quantum_navigator.is_at_grove()
        )

        # Get contextual actions
        if at_quantum_surface:
            # Use cardinal navigation instead of normal POI actions
            contextual_actions = self.quantum_navigator.get_available_directions()

            # Add ship access if at surface and not already in ship
            poi_data = self.poi_system.get_current_poi_data()
            if poi_data.get("has_ship", False) and not self.poi_system.in_ship:
                contextual_actions.append("Enter Ship")
        else:
            # Normal POI navigation
            contextual_actions = self.poi_system.get_contextual_actions(self.knowledge_menu, self.quantum_frequency_entered, self.launch_code_entered, self.npc_system, self.quantum_system, self.loop_manager.cavern_has_collapsed)

        # Build complete menu with contextual + persistent actions
        menu_actions = []

        # Add contextual actions first (movement, interaction, ship controls)
        for action in contextual_actions:
            menu_actions.append(action)

        # Add separator if we have contextual actions
        if menu_actions:
            menu_actions.append("───────────────────")

        # Add persistent commands
        # Add "!" indicator to Check Log if there are new entries
        log_label = "• Check Log"
        if self.knowledge_menu.has_new_entries():
            log_label = "• Check Log !"
        menu_actions.append(log_label)
        menu_actions.append("• Help")
        menu_actions.append("• Quit")

        # Show timer at bottom (hidden at grove - timeless space)
        at_grove = (self.poi_system.current_location == "quantum_moon" and
                   self.poi_system.current_poi == "grove")

        if not at_grove:
            timer = self.loop_manager.get_timer_text()
            self.console.print(f"\n{timer}\n")

        # Show menu
        choice = self.interactions.get_menu_choice(
            menu_actions,
            title="▸ ACTIONS",
            show_back=False
        )

        if choice is None:
            return "cancel"

        selected_action = menu_actions[choice]

        # Handle separator selection (shouldn't happen but just in case)
        if selected_action.startswith("───"):
            return "cancel"

        return selected_action

    def _strip_ui_labels(self, text: str) -> str:
        """Remove UI labels like !, (visited), (seen), (shortcut), ⭐, (requires: ...)"""
        # Remove leading icons/bullets
        text = text.lstrip('•→ ')

        # Remove trailing exclamation mark indicator
        if text.endswith(' !'):
            text = text[:-2]

        # Remove anything in parentheses at the end
        if '(' in text:
            text = text.split('(')[0]

        # Remove star emoji indicator
        if '⭐' in text:
            text = text.replace('⭐', '')

        return text.strip()

    def _strip_articles(self, name: str) -> str:
        """Remove articles (the, your, a, an) from location names for ID conversion"""
        name_lower = name.lower()
        for article in ["the ", "your ", "a ", "an "]:
            if name_lower.startswith(article):
                return name[len(article):]
        return name

    def _process_command(self, command: str) -> bool:
        """
        Process user command from menu selection.
        Returns True if command should cost an action, False if free.
        """
        # Normalize command (remove icons and extra whitespace)
        command_clean = command.strip()
        command_lower = command_clean.lower()

        # Handle signal scope unavailable message (free action)
        if "navigation unavailable" in command_lower:
            self.console.print("\n[yellow]⚠️  You need to log navigation frequencies first.[/yellow]")
            self.console.print("[dim]The radio station on Timber Hearth has the signal scope logs.[/dim]\n")
            time.sleep(1)
            return False

        # Handle persistent commands (with icons) - all free
        if "check ship's log" in command_lower or "log" in command_lower:
            self._show_ship_log()
            return False

        elif "help" in command_lower:
            self._show_help()
            return False

        elif "quit" in command_lower:
            self._quit_game()
            return False

        # Movement commands (cost actions)
        elif "go to " in command_lower:
            # Extract POI name (after "go to ") and strip UI labels
            poi_name_raw = command_lower.split("go to ")[1].strip()
            poi_name = self._strip_ui_labels(poi_name_raw)
            self._handle_movement(poi_name)
            return True

        elif "visit " in command_lower and not "revisit" in command_lower:
            # In space, visiting a location
            location_name_raw = command_clean.split("Visit ")[1].strip() if "Visit" in command_clean else ""
            location_name = self._strip_ui_labels(location_name_raw)
            location_name = self._strip_articles(location_name)
            if location_name:
                self._land_at_location(location_name.lower().replace(" ", "_"))
            return True

        # Quantum Moon cardinal navigation (costs actions)
        elif "look east" in command_lower or command_lower == "east":
            self._handle_cardinal_navigation("east")
            return True

        elif "look west" in command_lower or command_lower == "west":
            self._handle_cardinal_navigation("west")
            return True

        elif "look north" in command_lower or command_lower == "north":
            self._handle_cardinal_navigation("north")
            return True

        elif "look south" in command_lower or command_lower == "south":
            self._handle_cardinal_navigation("south")
            return True

        # Quantum Moon navigation puzzle - ONLY at Quantum Moon surface
        elif ("close eyes" in command_lower and
              self.poi_system.current_location == "quantum_moon" and
              self.poi_system.current_poi == "surface"):
            # Two-stage eye closing: close → darkness → open → transition
            # Check if at convergence (ready for grove)
            at_convergence = self.quantum_navigator.current_location == "convergence"

            if at_convergence:
                # At convergence: closing eyes enters darkness state (FREE - opening costs the action)
                self.eyes_closed = True
                self.eyes_closed_at_location = "convergence"
                self.console.print("\n[dim cyan]You close your eyes...[/dim cyan]\n")
                time.sleep(1)
                return False  # FREE - closing is just preparation
            else:
                # Not at convergence: reset to platform as before (COSTS ACTION - immediate teleport)
                success, message, reached_grove = self.quantum_navigator.close_eyes_reset()
                self.console.print(f"\n[cyan]{message}[/cyan]\n")
                time.sleep(0.5)
                return True  # COSTS ACTION - immediate reset/teleport

        # Open eyes - handle transitions based on where eyes were closed
        elif "open eyes" in command_lower and self.eyes_closed:
            if self.eyes_closed_at_location == "convergence":
                # Opening eyes at convergence → reach the grove!
                self.console.print("\n[cyan]You open your eyes and see: the weathered stone platform where you began "
                                 "And beyond it, impossible but certain, a grove of quantum trees that exists "
                                 "only because you walked this path.[/cyan]\n")
                time.sleep(2)

                # Show grove arrival sequence
                self.console.print("\n" + "━" * 60 + "\n", style="bold magenta")
                self.console.print("THE QUANTUM WAVEFORM STABILIZES\n", style="bold magenta")
                time.sleep(2)

                self.console.print("A grove materializes around you. At the center, a figure waits patiently.", style="white")
                time.sleep(2)

                self.console.print("Solanum turns toward you, existing and not existing,", style="dim italic")
                time.sleep(2)

                self.console.print("\n" + "━" * 60 + "\n", style="bold magenta")

                # Grant navigation complete knowledge
                self.knowledge_menu.add_knowledge("grove_navigation_complete")

                # Move player to grove POI
                self.poi_system.current_poi = "grove"
                self.poi_system._discover_poi("quantum_moon", "grove")
                full_poi_id = "quantum_moon.grove"
                self.poi_system.visited_pois.add(full_poi_id)

                # Update quantum navigator state
                self.quantum_navigator.current_location = "grove"

                # Reset eye state
                self.eyes_closed = False
                self.eyes_closed_at_location = None

                # Exit ship when arriving at grove via quantum navigation
                self.poi_system.in_ship = False

                self.console.print("\n[bold magenta]You've successfully navigated to the grove![/bold magenta]\n")
                time.sleep(1)

            elif self.eyes_closed_at_location == "grove":
                # Opening eyes at grove → return to quantum moon surface
                self.console.print("\n[cyan]You open your eyes...[/cyan]\n")
                time.sleep(1)
                self.console.print("[dim]The grove fades. Quantum superposition collapses.[/dim]\n")
                time.sleep(1)
                self.console.print("[white]You're back at the weathered stone platform on the Quantum Moon's surface.[/white]\n")
                time.sleep(1)

                # Move player back to surface
                self.poi_system.current_poi = "surface"

                # Reset quantum navigator to platform
                self.quantum_navigator.reset_navigation()

                # Reset eye state
                self.eyes_closed = False
                self.eyes_closed_at_location = None

            return True  # COSTS ACTION

        # Ship commands
        elif "enter ship" in command_lower:
            # FREE action - just entering ship
            self._handle_enter_ship()
            return False

        elif "exit ship" in command_lower:
            # FREE action - just exiting ship
            self._handle_exit_ship()
            return False

        elif "launch" in command_lower and "code" not in command_lower:
            self._handle_launch()
            return True

        elif "enter launch code" in command_lower or "launch code" in command_lower:
            # FREE action - just UI interaction
            self._handle_enter_launch_code()
            return False

        # NPC commands (cost actions)
        elif "talk to " in command_lower:
            npc_name_raw = command_lower.split("talk to ")[1].strip()
            npc_name = self._strip_ui_labels(npc_name_raw)
            self._handle_talk_to_npc(npc_name)
            return True

        # Examination commands
        elif "examine" in command_lower:
            # Opening menu is FREE, but reading an entry costs action
            entry_was_read = self._handle_examine()
            return entry_was_read

        # Close eyes at grove - return to quantum moon surface (conditional)
        elif ("close eyes" in command_lower and
              self.poi_system.current_location == "quantum_moon" and
              self.poi_system.current_poi == "grove"):
            # Player at grove closing eyes to return to surface
            # Only allowed if they can't end the game yet
            if not self.knowledge_menu.has_knowledge("complete_understanding"):
                self.eyes_closed = True
                self.eyes_closed_at_location = "grove"
                self.console.print("\n[dim cyan]You close your eyes...[/dim cyan]\n")
                time.sleep(1)
                return False  # FREE - closing is just preparation, opening costs the action
            else:
                # Player can end the game - Solanum reminds them
                self.console.print("\n[dim magenta]Solanum's voice reaches you across quantum states:[/dim magenta]\n")
                self.console.print("[magenta]'You've come so far. There is nothing left to find.'[/magenta]\n")
                self.console.print("[magenta]'When you're ready, witness the end.'[/magenta]\n")
                time.sleep(1)
                return False  # FREE action (cancelled)

        # Quantum observation (free) - unified atomic action
        elif "close eyes" in command_lower or "close eye" in command_lower:
            # Complete observation cycle: close → shift → open → reveal
            # Returns True if stabilized (unlocked), False if glitched or no quantum text
            # Player must manually examine entry to read content after stabilization
            self.quantum_system.quantum_observation(self.poi_system)
            return False  # FREE action

        # Quantum frequency entry (costs action)
        elif "insert frequency" in command_lower or "enter frequency" in command_lower:
            self._handle_insert_frequency()
            return True  # Costs action (attempting frequency entry)

        # Ending trigger (triggers final ending sequence)
        elif "witness the end" in command_lower:
            self._handle_witness_the_end()
            return True  # Doesn't matter, game ends after this

        # Cancel/back (free)
        elif command_clean == "cancel":
            return False

        # Invalid command (free)
        else:
            self.console.print(f"\n[dim]That doesn't seem right...[/dim]")
            self.console.print("[dim]Try 'help' if you're lost.[/dim]\n")
            time.sleep(1)
            return False

    def _handle_movement(self, poi_name: str):
        """Handle movement to a POI"""
        # Find matching POI
        available_pois = self.poi_system.get_available_pois()

        matching_poi = None
        for poi in available_pois:
            if poi_name in poi['name'].lower():
                matching_poi = poi
                break

        if not matching_poi:
            self.console.print(f"\n[red]Can't go to '{poi_name}' from here.[/red]\n")
            time.sleep(0.3)
            return

        # Move to POI
        success, cost, message = self.poi_system.move_to_poi(
            matching_poi['id'],
            cavern_has_collapsed=self.loop_manager.cavern_has_collapsed
        )

        if success:
            self.console.print(f"\n[cyan]{message}[/cyan]\n")
            time.sleep(0.5)

            # Movement costs 2 actions total (1 from this call + 1 from return True)
            self.loop_manager.increment_action(1)

            # Trigger Observatory tutorial if first visit
            if (self.poi_system.current_poi == "observatory" and
                not self.observatory_tutorial_shown and
                "hornfels" in self.poi_system.get_current_poi_data().get("npcs", [])):
                self._trigger_observatory_tutorial()
        else:
            # Movement failed - show reason (e.g., cavern collapsed)
            self.console.print(f"\n[yellow]{message}[/yellow]\n")
            time.sleep(0.5)

    def _handle_cardinal_navigation(self, direction: str):
        """Handle Quantum Moon cardinal direction navigation"""
        # Observe the direction and check if we progress
        success, message, reached_grove = self.quantum_navigator.observe_direction(direction)

        if reached_grove:
            # Grant navigation complete knowledge
            self.knowledge_menu.add_knowledge("grove_navigation_complete")

            # Move player to grove POI
            self.poi_system.current_poi = "grove"
            self.poi_system._discover_poi("quantum_moon", "grove")

            # Mark as visited
            full_poi_id = "quantum_moon.grove"
            self.poi_system.visited_pois.add(full_poi_id)

            self.console.print("\n[bold magenta]You've successfully navigated to the grove![/bold magenta]\n")
            time.sleep(1)

    def _trigger_observatory_tutorial(self):
        """Automatically trigger Hornfels tutorial on first Observatory visit"""
        self.observatory_tutorial_shown = True

        # Show a brief transition
        self.console.print("\n[dim italic]Hornfels notices you and waves you over...[/dim italic]\n")
        time.sleep(1.5)

        # Trigger Hornfels dialogue automatically
        granted_knowledge = self.npc_system.talk_to_npc("hornfels", self.knowledge_menu, self.interactions)

        if granted_knowledge:
            self.knowledge_menu.add_knowledge(granted_knowledge)

        input("\n[Press Enter to continue...]")

    def _handle_enter_ship(self):
        """Handle entering the ship"""
        success, message = self.poi_system.enter_ship()

        if not success:
            self.console.print(f"\n[yellow]{message}[/yellow]")
            time.sleep(0.3)
        else:
            self.console.print(f"\n[cyan]{message}[/cyan]\n")
            time.sleep(0.3)

            # Contextual hint if player doesn't have launch code yet
            if not self.knowledge_menu.has_knowledge("launch_code_epistemic"):
                self.console.print("[dim]💡 The ship won't respond. It needs something. A code?[/dim]")
                if not self.knowledge_menu.has_knowledge("hornfels_met"):
                    self.console.print("[dim]   Perhaps someone at the Observatory knows where it is?[/dim]\n")
                else:
                    self.console.print("[dim]   Hornfels mentioned it's in the Observatory...[/dim]\n")
                time.sleep(1)

    def _handle_exit_ship(self):
        """Handle exiting the ship"""
        success, message = self.poi_system.exit_ship()

        self.console.print(f"\n[cyan]{message}[/cyan]\n")
        time.sleep(0.3)

    def _handle_launch(self):
        """Handle ship launch"""
        # Check if frequencies are logged before allowing launch
        if not self.knowledge_menu.has_knowledge("signal_scope_frequencies"):
            self.console.print("\n[yellow]⚠️  The Stars Are Silent[/yellow]")
            self.console.print("[white]Without the frequencies, you can't navigate.[/white]")
            self.console.print("[dim]Perhaps the radio station has what you need?[/dim]\n")
            time.sleep(0.3)
            return

        success, message = self.poi_system.launch_ship()

        if success:
            self.console.print(f"\n[bold cyan]{message}[/bold cyan]\n")
            time.sleep(0.5)

            # Launch costs 2 actions total (1 from command return, 1 added here)
            self.loop_manager.increment_action(1)

            # Build menu of destinations (including current location)
            destinations = []
            destination_ids = []

            for loc_id, loc_data in self.location_data["locations"].items():
                # Check if accessible
                can_access, _ = self._can_access_location(loc_id)
                if can_access:
                    emoji = loc_data.get("emoji", "📍")
                    name = loc_data["name"]

                    # Mark current location
                    if loc_id == self.poi_system.current_location:
                        destinations.append(f"{emoji} {name} ⭐ (you're here!)")
                    else:
                        destinations.append(f"{emoji} {name}")

                    destination_ids.append(loc_id)

            # Filter out any empty or malformed entries
            destinations = [d for d in destinations if d and d.strip()]

            # Show navigation menu only if destinations exist
            if not destinations:
                self.console.print("\n[yellow]No destinations available. You need to activate the ship first.[/yellow]\n")
                time.sleep(1)
                return

            choice = self.interactions.get_menu_choice(
                destinations,
                title="NAVIGATION - WHERE DO YOU WANT TO GO?",
                show_back=False
            )

            if choice is not None:
                selected_location = destination_ids[choice]

                # Check if selecting current planet (cancel launch)
                if selected_location == self.poi_system.current_location:
                    self.poi_system.ship_flying = False
                    self.console.print("\n[cyan]You decide to stay. The ship settles back down.[/cyan]\n")
                    time.sleep(0.5)
                else:
                    # Normal landing at different planet
                    self._land_at_location(selected_location)
        else:
            self.console.print(f"\n[red]{message}[/red]\n")
            time.sleep(1)

    def _handle_land(self, location_name: str):
        """Handle landing at a location - DEPRECATED, use _land_at_location"""
        # This is now handled by the menu in _handle_launch
        pass

    def _land_at_location(self, location_id: str):
        """Land at a specific location"""
        # Attempt landing
        success, cost, message = self.poi_system.land_at_location(location_id, self.knowledge_menu, self.quantum_frequency_entered)

        if success:
            # If landing at quantum moon, reset quantum navigator to initial state
            if location_id == "quantum_moon":
                self.quantum_navigator.reset_navigation()

            self.console.print(f"\n[bold cyan]{message}[/bold cyan]\n")
            time.sleep(0.5)
            # Apply landing cost (travel + landing time)
            self.loop_manager.increment_action(cost)
        else:
            self.console.print(f"\n[red]{message}[/red]\n")
            time.sleep(0.3)

    def _show_location_arrival(self, location_id: str):
        """Show atmospheric arrival description"""
        # This is already handled by POI system's show_current_scene
        pass

    def _handle_cavern_collapse(self):
        """Handle quantum cavern collapse into black hole at action 14"""
        current_loc = self.poi_system.current_location
        current_poi = self.poi_system.current_poi

        # Case 1: Player is IN quantum cavern - DEATH
        if current_loc == "brittle_hollow" and current_poi == "quantum_cavern":
            self.console.print("\n[bold red]━━━ GRAVITATIONAL COLLAPSE ━━━[/bold red]\n")
            time.sleep(0.5)
            self.console.print("[red]The chunk of Brittle Hollow beneath you breaks away.[/red]")
            time.sleep(1)
            self.console.print("[red]You fall into the black hole's event horizon.[/red]")
            time.sleep(1)
            self.console.print("[dim red]Everything stretches... then nothing.[/dim red]\n")
            time.sleep(2)

            # Trigger loop reset (death instead of supernova)
            self.console.print("[bold yellow]━━━ TIME RESETS ━━━[/bold yellow]\n")
            time.sleep(1)
            self.knowledge_menu.increment_loop()

            # Reset physical state
            self.poi_system.current_location = "timber_hearth"
            self.poi_system.in_ship = False
            self.poi_system.ship_flying = False
            self.poi_system._initialize_starting_position()
            self.quantum_frequency_entered = False
            self.launch_code_entered = False
            self.loop_manager.current_actions = 0
            self.loop_manager.cavern_has_collapsed = False
            self.loop_manager.loop_count += 1

            # Reset eye state
            self.eyes_closed = False
            self.eyes_closed_at_location = None

            # Clear temporary same-loop knowledge flags
            if "cavern_collapse_witnessed" in self.knowledge_menu.progress.knowledge_gained:
                self.knowledge_menu.progress.knowledge_gained.remove("cavern_collapse_witnessed")

        # Case 2: Player is at Brittle Hollow (other POI) - CUTSCENE
        elif current_loc == "brittle_hollow":
            self.console.print("\n[bold yellow]━━━ PLANETARY COLLAPSE ━━━[/bold yellow]\n")
            time.sleep(0.5)
            self.console.print("[yellow]The ground shakes violently. You watch as the quantum cavern "
                             "chunk breaks away from the planet and spirals into the black hole "
                             "below. It's gone.[/yellow]\n")
            time.sleep(2)
            self.console.print("[dim]Maybe earlier next time?[/dim]\n")
            time.sleep(1.5)

            # Grant temporary knowledge flag for this loop (enables Riebeck dialogue)
            self.knowledge_menu.add_knowledge("cavern_collapse_witnessed")

        # Case 3: Player elsewhere - no immediate message
        # (They'll discover collapse when they try to access later)

    def _handle_enter_launch_code(self):
        """Interactive launch code entry"""
        if self.poi_system.in_ship and not self.launch_code_entered:
            self.console.print("\n[bold]SHIP CONSOLE[/bold]")
            self.console.print("Enter launch code: ", end="")
            code = input().strip().upper()

            if code == "EPISTEMIC":
                self.console.print("\n[bold green]✓ ACCESS GRANTED[/bold green]")
                time.sleep(0.5)
                self.console.print("\n[cyan]╔══════════════════════════════╗[/cyan]")
                self.console.print("[cyan]║  SHIP SYSTEMS: ONLINE       ║[/cyan]")
                self.console.print("[cyan]║  NAVIGATION: READY          ║[/cyan]")
                self.console.print("[cyan]║  LAUNCH AUTHORIZATION: OK   ║[/cyan]")
                self.console.print("[cyan]╚══════════════════════════════╝[/cyan]\n")
                self.console.print("[white]The ship hums to life. You can now launch into space.[/white]\n")
                # Grant epistemic knowledge (understanding the code)
                self.knowledge_menu.add_knowledge("launch_code_epistemic")
                # Also grant ship operation capability (enables navigation to other locations)
                self.knowledge_menu.add_knowledge("ship_operation")
                # Set physical state (code entered this loop)
                self.launch_code_entered = True
                time.sleep(2.5)
            else:
                self.console.print(f"\n[red]✗ Nothing happens. That's not it.[/red]")
                self.console.print("[dim]The launch code can be found somewhere on Timber Hearth...[/dim]\n")
                time.sleep(0.3)
        else:
            self.console.print("\n[dim]The ship is already activated. Or you're not inside yet.[/dim]\n")
            time.sleep(0.3)

    def _handle_insert_frequency(self):
        """Interactive frequency entry at radio station"""
        # Check if at radio station
        if self.poi_system.current_location != "timber_hearth" or self.poi_system.current_poi != "radio_station":
            self.console.print("\n[yellow]You need to be at the radio station to insert frequencies.[/yellow]\n")
            time.sleep(0.3)
            return

        # Check if player has discovered the frequency exists
        if not self.knowledge_menu.has_knowledge("signal_scope_frequencies"):
            self.console.print("\n[yellow]You need to log the navigation frequencies first.[/yellow]\n")
            time.sleep(0.3)
            return

        self.console.print("\n[bold]SIGNAL SCOPE - FREQUENCY INSERTION[/bold]")
        self.console.print("Enter 4-digit frequency: ", end="")

        frequency_input = input().strip()

        # Validate input (exactly 4 digits)
        if not frequency_input.isdigit() or len(frequency_input) != 4:
            self.console.print("\n[red]✗ INVALID INPUT - Must be exactly 4 digits[/red]\n")
            time.sleep(1)
            return

        # Check if correct frequency (5555 for Quantum Moon)
        if frequency_input == "5555":
            # Success!
            self.quantum_frequency_entered = True
            self.knowledge_menu.add_knowledge("quantum_moon_frequency")
            self.console.print("\n[bold green]✓ FREQUENCY LOCKED[/bold green]")
            time.sleep(0.5)
            self.console.print("\n[cyan]╔══════════════════════════════╗[/cyan]")
            self.console.print("[cyan]║  QUANTUM SIGNAL: STABLE     ║[/cyan]")
            self.console.print("[cyan]║  [5555] QUANTUM MOON        ║[/cyan]")
            self.console.print("[cyan]║  NAVIGATION: ENABLED        ║[/cyan]")
            self.console.print("[cyan]╚══════════════════════════════╝[/cyan]\n")
            self.console.print("[white]The quantum interference resolves into a stable signal.[/white]")
            self.console.print("[white]The Quantum Moon is now accessible for navigation.[/white]\n")
            time.sleep(2.5)
        else:
            # Wrong frequency
            self.console.print(f"\n[yellow]⚠️  FREQUENCY INCOMPATIBLE[/yellow]")
            self.console.print(f"[white]Signal [{frequency_input}] rejected - No matching quantum signature.[/white]\n")
            time.sleep(1.5)

    def _handle_talk_to_npc(self, npc_name: str):
        """Handle talking to an NPC"""
        # Get NPCs at current POI
        poi_data = self.poi_system.get_current_poi_data()
        npcs = poi_data.get("npcs", [])

        # Find matching NPC
        matching_npc = None
        for npc_id in npcs:
            if npc_name in npc_id or npc_name in self.npc_system.get_npc_info(npc_id).get("name", "").lower():
                matching_npc = npc_id
                break

        if not matching_npc:
            self.console.print(f"\n[red]{npc_name} isn't here.[/red]\n")
            time.sleep(0.3)
            return

        # Talk to NPC
        granted_knowledge = self.npc_system.talk_to_npc(matching_npc, self.knowledge_menu, self.interactions)

        if granted_knowledge:
            self.knowledge_menu.add_knowledge(granted_knowledge)

        input("\n[Press Enter to continue...]")

    def _handle_examine(self) -> bool:
        """
        Handle examining entries at current POI.
        Returns True if an entry was read (costs action), False if menu was just browsed (free).
        """
        poi_data = self.poi_system.get_current_poi_data()
        entries = poi_data.get("entries", [])

        if not entries:
            self.console.print("\n[dim]Nothing to examine here.[/dim]\n")
            time.sleep(0.3)
            return False  # Free - nothing to examine

        # Get accessible entries
        accessible = []
        for entry_id in entries:
            full_entry_id = f"{self.poi_system.current_location}.{entry_id}"
            if full_entry_id in self.knowledge_menu.all_entries:
                entry = self.knowledge_menu.all_entries[full_entry_id]
                can_access, reason = self.knowledge_menu.can_access_entry(full_entry_id)

                # Show quantum entries even if not accessible (they'll trigger stabilization)
                # Show non-quantum entries only if accessible or discovered
                if entry.is_quantum or can_access or entry.discovered:
                    accessible.append({
                        "id": entry_id,
                        "full_id": full_entry_id,
                        "title": entry.title,
                        "discovered": entry.discovered,
                        "quantum": entry.is_quantum
                    })

        if not accessible:
            self.console.print("\n[dim]Nothing accessible to examine here yet.[/dim]\n")
            time.sleep(0.3)
            return False  # Free - nothing accessible

        # Build menu options
        menu_options = []
        for entry in accessible:
            status = "✓" if entry["discovered"] else "●"

            # Show dynamic quantum symbol based on current state
            if entry["quantum"]:
                symbol = self.quantum_system.get_entry_symbol(entry["full_id"])
                quantum_mark = f" {symbol}"
            else:
                quantum_mark = ""

            seen_mark = " (seen)" if entry["discovered"] else ""
            menu_options.append(f"{status} {entry['title']}{quantum_mark}{seen_mark}")

        # Show menu
        choice = self.interactions.get_menu_choice(
            menu_options,
            title="WHAT DO YOU WANT TO EXAMINE?",
            show_back=True
        )

        if choice is not None:
            selected = accessible[choice]
            self._read_entry(self.poi_system.current_location, selected["id"])
            return True  # Entry was read - costs action
        else:
            return False  # Menu was cancelled - free

    def _read_entry(self, location_id: str, entry_id: str):
        """Read a specific entry"""
        full_id = f"{location_id}.{entry_id}"
        entry_data = self._get_entry_raw_data(full_id)
        entry_obj = self.knowledge_menu.all_entries.get(full_id)

        # Handle quantum entries - check encryption key state
        if entry_data.get("quantum", False):
            quantum_state = self.quantum_system.get_entry_state(full_id)

            if quantum_state == 6:
                # Encryption key state (⟐) - readable and can be discovered
                was_new = self.knowledge_menu.discover_entry(full_id)

                if was_new:
                    # Grant knowledge
                    for knowledge in entry_data.get("knowledge_grants", []):
                        self.knowledge_menu.add_knowledge(knowledge)

                    # Show notification
                    notif = Text()
                    notif.append("📝 NEW ENTRY ADDED TO LOG\n", style="bold green")
                    notif.append(f"{entry_data['title']}", style="cyan")
                    self.console.print(Panel(notif, border_style="green"))
                    time.sleep(0.8)

                # Display normally (unscrambled)
                self.content_loader.load_and_display_entry(location_id, entry_id, entry_data, quantum_state=6)
                return
            else:
                # States 1-5 - show scrambled content, don't mark as discovered
                self.content_loader.load_and_display_entry(location_id, entry_id, entry_data, quantum_state=quantum_state)
                return

        # Non-quantum entries: check requirements
        can_access, reason = self.knowledge_menu.can_access_entry(full_id)
        if not can_access:
            self.console.print(f"\n[red]Cannot access: {reason}[/red]\n")
            time.sleep(0.3)
            return

        # Mark as discovered
        was_new = self.knowledge_menu.discover_entry(full_id)

        if was_new:
            notif = Text()
            notif.append("📝 NEW ENTRY ADDED TO LOG\n", style="bold green")
            notif.append(f"{entry_data['title']}", style="cyan")
            self.console.print(Panel(notif, border_style="green"))
            time.sleep(0.8)

        # Load and display content
        self.content_loader.load_and_display_entry(location_id, entry_id, entry_data)

    def _get_entry_raw_data(self, full_entry_id: str) -> dict:
        """Get raw entry data from location config"""
        parts = full_entry_id.split(".")
        if len(parts) != 2:
            return {}

        loc_id, entry_id = parts
        return self.location_data["locations"].get(loc_id, {}).get("entries", {}).get(entry_id, {})

    def _show_ship_log(self):
        """Display ship's log (rumor mode)"""
        self.visualizer.clear_screen()
        self.knowledge_menu.show_rumor_mode()
        # Clear new entries indicator after viewing log
        self.knowledge_menu.clear_new_entries()
        input("\n[Press Enter to continue...]")

    def _show_help(self):
        """Display help screen"""
        self.visualizer.clear_screen()

        help_text = Text()
        help_text.append("\n📘 HELP\n\n", style="bold cyan")
        help_text.append("This is a spatial exploration experience. Move between locations,\n", style="white")
        help_text.append("talk to NPCs, examine objects, and piece together knowledge.\n\n", style="white")

        help_text.append("MOVEMENT:\n", style="bold")
        help_text.append("  go to <location>    - Move to a connected area\n", style="dim")
        help_text.append("  enter/exit ship     - Board or leave your ship\n", style="dim")
        help_text.append("  launch              - Take off into space\n", style="dim")
        help_text.append("  land at <planet>    - Land on a planet\n\n", style="dim")

        help_text.append("INTERACTION:\n", style="bold")
        help_text.append("  talk to <npc>       - Speak with someone\n", style="dim")
        help_text.append("  examine             - Investigate objects/texts\n", style="dim")
        help_text.append("                        (also: read, look, investigate)\n", style="dim")
        help_text.append("  close eyes          - Observe quantum phenomena\n", style="dim")
        help_text.append("                        (eyes open automatically)\n\n", style="dim")

        help_text.append("INFORMATION:\n", style="bold")
        help_text.append("  check log           - View your ship's log\n", style="dim")
        help_text.append("  help                - This screen\n", style="dim")
        help_text.append("  quit                - Exit game\n\n", style="dim")

        help_text.append("Remember: Every command costs time. The sun is unstable.\n", style="yellow italic")

        self.console.print(Panel(help_text, border_style="cyan", title="HELP"))
        input("\n[Press Enter to continue...]")

    def _handle_witness_the_end(self):
        """Trigger the final ending sequence"""
        self.visualizer.clear_screen()

        # Show player stats before ending
        from rich.text import Text
        stats = Text()
        stats.append("\n═══════════════════════════════════════\n", style="bold cyan")
        stats.append("         YOUR JOURNEY COMPLETE         \n", style="bold white")
        stats.append("═══════════════════════════════════════\n\n", style="bold cyan")

        stats.append(f"  Loops experienced: {self.loop_manager.loop_count}\n", style="white")
        completion = self.knowledge_menu.get_completion_percentage()
        stats.append(f"  Knowledge discovered: {completion:.1f}%\n", style="white")
        stats.append(f"  Locations visited: {len(self.poi_system.visited_pois)}\n\n", style="white")

        stats.append("═══════════════════════════════════════\n\n", style="bold cyan")

        self.console.print(stats)
        input("[Press Enter to witness the end...]")

        # Load and display ending sequence
        entry_data = self._get_entry_raw_data("quantum_moon.thesis_ending")
        self.content_loader.load_and_display_entry("quantum_moon", "thesis_ending", entry_data)

        # Exit to main menu after ending
        self._quit_game()

    def _quit_game(self):
        """Quit the game"""
        self.visualizer.clear_screen()
        self.console.print("\n[cyan]Thank you for exploring.[/cyan]\n")
        exit(0)

    def _can_access_location(self, location_id: str) -> tuple[bool, str]:
        """Check if location can be accessed"""
        loc_info = self.location_data["locations"][location_id]

        # Check knowledge requirements
        required_knowledge = loc_info.get("requires_knowledge", [])
        if required_knowledge:
            if not self.knowledge_menu.progress.has_all_knowledge(required_knowledge):
                return False, "Missing required knowledge"

        # SPECIAL: Quantum Moon requires frequency entry THIS LOOP (physical state)
        if location_id == "quantum_moon":
            if not self.quantum_frequency_entered:
                return False, "Frequency not entered this loop"

        return True, ""
