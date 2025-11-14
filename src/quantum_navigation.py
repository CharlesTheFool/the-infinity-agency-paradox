"""
Quantum Moon Cardinal Navigation System
Five-location quantum superposition puzzle with randomized outcomes and stable paths
"""

from typing import Tuple
from rich.console import Console
from rich.text import Text
import time
import random


class QuantumNavigator:
    """Manages quantum moon navigation with quantum superposition mechanics"""

    def __init__(self, console: Console):
        self.console = console
        self.current_location = "platform"  # Starting location
        self.has_visited_platform = False  # Track if player has been reset

        # Define the 5 locations with their descriptions and observations
        self.locations = {
            "platform": {
                "name": "Weathered Stone Platform",
                "description": "You stand where ancient stone meets the quantum sky. The platform hums with quantum resonance beneath your feet.",
                "stable_path": {"east": "crystals"},  # Only East is deterministic
                "observations": {
                    "east": "To the EAST: Crystalline formations rise from the quantum surface, emitting harmonic resonances that shift frequency with each observation. Their tones create interference patterns in the air.",
                    "west": "To the WEST: Quantum fog obscures distant landmarks in probability mist, their forms uncertain and unstable.",
                    "north": "To the NORTH: Northward stretches an expanse of shifting quantum terrain, flickering between observable states.",
                    "south": "To the SOUTH: The southern horizon warps and bends, space folding into uncertain geometries that defy measurement."
                }
            },
            "crystals": {
                "name": "Singing Crystal Field",
                "description": "The crystalline formations surround you. Their quantum harmonics modulate with your presence, creating standing waves in local spacetime.",
                "stable_path": {"west": "tree"},  # Only West is deterministic
                "observations": {
                    "east": "To the EAST: More crystal formations extend endlessly eastward, their tones discordant and chaotic, threatening waveform collapse.",
                    "west": "To the WEST: The ancient silver tree towers nearby. Its bark exhibits quantum tunneling effects, phasing through observable states at irregular intervals.",
                    "north": "To the NORTH: Northern crystals resonate at unstable frequencies, creating destructive interference patterns that blur spacetime.",
                    "south": "To the SOUTH: Southward, the crystals fade into quantum uncertainty, their forms undefined and probability distributions overlapping."
                }
            },
            "tree": {
                "name": "Ancient Tree Grove",
                "description": "Massive silver branches arch overhead, their quantum-unstable bark creating localized probability fields. The tree's roots penetrate multiple dimensional planes.",
                "stable_path": {"north": "arch"},  # Only North is deterministic
                "observations": {
                    "east": "To the EAST: Smaller quantum-shifted vegetation struggles to maintain coherence, their molecular bonds flickering in and out of existence.",
                    "west": "To the WEST: The tree's shadow extends infinitely westward, folding through impossible angles that violate Euclidean geometry.",
                    "north": "To the NORTH: Northward, a natural stone archway refracts light like a prism constructed from pure possibility rather than matter.",
                    "south": "To the SOUTH: The southern approach shows quantum duplicates of the tree, each slightly out of phase with observable reality."
                }
            },
            "arch": {
                "name": "Prismatic Archway",
                "description": "Light bends through the natural stone arch in ways that violate conservation of energy. Photons split, merge, and interfere with themselves across temporal boundaries.",
                "stable_path": {"south": "convergence"},  # Only South is deterministic
                "observations": {
                    "east": "To the EAST: Eastward, refracted light creates false horizons and impossible angles, distance measurements becoming meaningless.",
                    "west": "To the WEST: To the west, prismatic distortions scatter photons into quantum noise, unable to maintain coherent wavefronts.",
                    "north": "To the NORTH: Northern light beams fragment into probability distributions, each photon existing in superposition across multiple paths.",
                    "south": "To the SOUTH: Behind you, looking south, faint disturbances in quantum dust mark the path you've walked. Each footstep exists in superposition, observed yet uncertain."
                }
            },
            "convergence": {
                "name": "Quantum Convergence",
                "description": "You've reached a point of perfect quantum coherence. The air thrums with potential, all possibilities converging toward a single inevitable truth. The grove exists here, waiting for observation to collapse it into reality.",
                "stable_path": {},  # No cardinal directions lead anywhere
                "observations": {
                    "east": "To the EAST: All directions show the same shimmering potential—the grove exists everywhere and nowhere until you choose to observe it.",
                    "west": "To the WEST: The boundaries between cardinal directions blur into quantum superposition, space itself awaiting your final choice.",
                    "north": "To the NORTH: Space itself seems to anticipate your decision, probability waves focused on this singular convergent point.",
                    "south": "To the SOUTH: Every direction leads to the same destination, once you choose to observe it beyond the limitations of sight."
                }
            }
        }

    def reset_navigation(self):
        """Reset to starting location"""
        self.current_location = "platform"

    def close_eyes_reset(self):
        """Player chooses to close eyes - either resets or reaches grove"""
        if self.current_location == "convergence":
            # At convergence, closing eyes leads to grove
            return self._reach_grove()
        else:
            # At any other location, closing eyes resets to platform
            self.has_visited_platform = True
            self.current_location = "platform"
            return (True, "You close your eyes. When you open them, you're back at the weathered platform.", False)

    def is_at_grove(self) -> bool:
        """Check if player has successfully reached the grove"""
        return self.current_location == "grove"

    def get_available_directions(self) -> list[str]:
        """Get list of cardinal directions player can observe"""
        return [
            "Look East",
            "Look West",
            "Look North",
            "Look South",
            "Close Eyes"
        ]

    def observe_direction(self, direction: str) -> Tuple[bool, str, bool]:
        """
        Observe a direction - either follow stable path or quantum teleport randomly.

        Returns:
            (success, message, reached_grove)
        """
        # Normalize direction
        direction_clean = direction.lower().strip()

        # Map command variations to canonical directions
        direction_map = {
            "look east": "east",
            "east": "east",
            "look west": "west",
            "west": "west",
            "look north": "north",
            "north": "north",
            "look south": "south",
            "south": "south",
            "close eyes": "close eyes"
        }

        canonical_dir = direction_map.get(direction_clean)

        if not canonical_dir:
            return False, "Invalid direction.", False

        # Check if we're already at the grove
        if self.is_at_grove():
            return True, "You're already at the grove.", True

        # Handle "close eyes" command
        if canonical_dir == "close eyes":
            return self.close_eyes_reset()

        # Get current location info
        loc_info = self.locations[self.current_location]
        observation = loc_info["observations"].get(canonical_dir, "You see nothing unusual in that direction.")

        # Show observation
        self._show_observation(loc_info["name"], canonical_dir, observation)

        # Check if this direction is the stable path
        if canonical_dir in loc_info["stable_path"]:
            # Stable path - deterministic outcome
            next_location = loc_info["stable_path"][canonical_dir]
            self.current_location = next_location
            next_name = self.locations[next_location]["name"]
            message = f"The quantum waveform shifts. You find yourself at: {next_name}"
            self.console.print(f"\n[bold green]{message}[/bold green]\n")
            time.sleep(1)
            return True, message, False
        else:
            # Quantum randomization - teleport to random location
            # Possible destinations: platform, crystals, tree, arch (excluding current and convergence)
            possible_locations = ["platform", "crystals", "tree", "arch"]
            possible_locations.remove(self.current_location)  # Can't stay at current

            random_location = random.choice(possible_locations)
            self.current_location = random_location
            random_name = self.locations[random_location]["name"]

            self.console.print("\n[bold red]The quantum waveform collapses![/bold red]\n")
            time.sleep(0.5)
            self.console.print(f"[yellow]You find yourself at: {random_name}[/yellow]\n")
            time.sleep(1)

            # Mark that player has experienced quantum collapse
            if random_location == "platform":
                self.has_visited_platform = True

            return True, f"Quantum teleport to {random_name}", False

    def _reach_grove(self) -> Tuple[bool, str, bool]:
        """Player successfully reaches the grove from convergence"""
        self.console.print(
            "\n[cyan]You close your eyes and see: the weathered stone platform where you began—"
            "and beyond it, impossible but certain, a grove of quantum trees that exists "
            "only because you walked this path.[/cyan]\n"
        )
        time.sleep(2)

        self._show_grove_arrival()
        self.current_location = "grove"
        return True, "You've reached Solanum's Grove!", True

    def _show_observation(self, current_location: str, direction: str, observation: str):
        """Display what the player observes in a direction"""
        scene = Text()
        scene.append(f"\n━━━ {current_location.upper()} ━━━\n\n", style="bold cyan")
        scene.append(f"You look {direction}...\n\n", style="dim")
        scene.append(f"{observation}\n", style="white")

        self.console.print(scene)
        time.sleep(0.8)

    def _show_grove_arrival(self):
        """Display the grove arrival sequence"""
        self.console.print("\n" + "━" * 60 + "\n", style="bold magenta")
        self.console.print("THE QUANTUM WAVEFORM STABILIZES\n", style="bold magenta")
        self.console.print("You step through into impossible space...\n\n", style="cyan")
        time.sleep(2)

        self.console.print("A grove materializes around you. Quantum trees shimmer with light", style="white")
        self.console.print("that shouldn't exist. At the center, a figure waits patiently.\n", style="white")
        time.sleep(2)

        self.console.print("Solanum turns toward you, existing and not existing,", style="dim italic")
        self.console.print("quantum superposition made manifest.\n", style="dim italic")
        time.sleep(2)

        self.console.print("\n" + "━" * 60 + "\n", style="bold magenta")

    def get_current_state_description(self) -> str:
        """Get description of current navigation location"""
        if self.is_at_grove():
            return "You are at Solanum's Grove."

        loc_info = self.locations[self.current_location]
        desc = loc_info["description"]

        # Add "walking in circles" message if they've been to platform after quantum collapse
        if self.current_location == "platform" and self.has_visited_platform:
            desc = "Wait, you've been here before... Are you walking around in circles?\n\n" + desc

        return desc

    def show_navigation_scene(self):
        """Display current quantum moon navigation scene"""
        if self.is_at_grove():
            # Show grove scene
            self.console.print("\n━━━ SOLANUM'S GROVE ━━━\n", style="bold magenta")
            self.console.print("Quantum trees shimmer with impossible light. Solanum stands among them,", style="white")
            self.console.print("a Nomai traveler in quantum superposition, patient as starlight.\n", style="white")
        else:
            # Show current navigation location
            loc_info = self.locations[self.current_location]

            # Get description with potential "walking in circles" message
            full_desc = self.get_current_state_description()

            self.console.print(f"\n━━━ {loc_info['name'].upper()} ━━━\n", style="bold cyan")
            self.console.print(f"{full_desc}\n", style="white")

        time.sleep(0.5)
