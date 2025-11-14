"""
Quantum System - Quantum Text Observation Mechanics
POI-wide quantum state observation with word scrambling
"""

import time
import random
from typing import Dict, Optional, List, Tuple
from rich.console import Console
from rich.text import Text
from src.visualizer import Visualizer
from src.knowledge_menu import KnowledgeMenu


class QuantumSystem:
    """Manages quantum text observation puzzle mechanics"""

    def __init__(self, console: Console, visualizer: Visualizer, knowledge_menu: KnowledgeMenu):
        self.console = console
        self.visualizer = visualizer
        self.knowledge_menu = knowledge_menu
        self.eyes_closed = False

        # Track quantum state per entry (entry_id -> current_state: 1-6)
        self.quantum_states: Dict[str, int] = {}

        # Symbol mapping for each state (⟐ = state 6 = encryption key)
        self.state_symbols = {
            1: "⟁",
            2: "⧈",
            3: "◊",
            4: "∞",
            5: "◈",
            6: "⟐"  # Encryption key - readable state
        }

    def quantum_observation(self, location_system) -> bool:
        """
        Complete quantum observation cycle (atomic action):
        1. Close eyes (contemplative dark sequence)
        2. ALL quantum entries at POI re-roll to new random states
        3. Wait for any key press (implicit eye opening)
        4. Eyes open automatically, return to menu silently

        Returns False (free action, no announcements).
        Player must manually examine entries to see states/content.
        """
        if self.eyes_closed:
            self.console.print("\n[dim]Your eyes are already closed.[/dim]\n")
            return False

        # PHASE 1: Close eyes - show contemplative sequence
        self.eyes_closed = True
        self._show_contemplative_sequence()

        # PHASE 2: POI-wide quantum shift - re-roll ALL quantum entries at this POI
        quantum_entries = self._get_all_quantum_entries_at_poi(location_system)

        for full_entry_id, entry_data in quantum_entries:
            # Get old state (or 0 if first observation)
            old_state = self.quantum_states.get(full_entry_id, 0)

            # Roll new state (must differ from old)
            new_state = self._get_new_state(old_state)

            # Update state
            self.quantum_states[full_entry_id] = new_state

        # PHASE 3: Wait for any key (implicit eye opening)
        input("\n[Press any key to open your eyes...]")

        # PHASE 4: Eyes open automatically, return to menu silently
        self.eyes_closed = False
        self.visualizer.clear_screen()
        time.sleep(0.2)

        # No announcements - player discovers states by examining entries
        return False

    def _show_contemplative_sequence(self):
        """Show the dark contemplative message sequence"""
        # Contemplative message sequence - snippets that appear and disappear
        messages = [
            {
                "particles": "    ✦     ·  ∞    ·    ⟁     ·   ◊   ",
                "text": "Everything goes dark.",
                "style": "cyan",
                "duration": 1.0
            },
            {
                "particles": "  ·    ◈     ·    ⧈    ·     ⟐     · ",
                "text": "You breathe.\nThe universe breathes with you.",
                "style": "dim cyan",
                "duration": 1.5
            },
            {
                "particles": "    ✦     ·  ⟐    ·    ∞     ·   ◊   ",
                "text": "In the darkness,\nall possibilities exist.",
                "style": "dim white",
                "duration": 1.2
            },
            {
                "particles": "  ·    ⧈     ·    ⟁    ·     ◈     · ",
                "text": "Take your time.",
                "style": "yellow",
                "duration": 1.0
            }
        ]

        for msg in messages:
            self.visualizer.clear_screen()
            time.sleep(0.2)

            dark_screen = Text()
            dark_screen.append("\n" * 3)
            dark_screen.append(msg["particles"] + "\n", style="dim white")
            dark_screen.append("\n")
            dark_screen.append(f"         {msg['text']}\n", style=msg["style"])
            dark_screen.append("\n" * 3)

            self.console.print(dark_screen)
            time.sleep(msg["duration"])

    def _get_all_quantum_entries_at_poi(self, location_system) -> List[Tuple[str, Dict]]:
        """
        Find ALL quantum entries at current POI (discovered or not).
        Returns list of (full_entry_id, entry_data) tuples.
        """
        current_loc = location_system.current_location
        current_poi = location_system.current_poi

        # Get POI data
        loc_info = location_system.location_data["locations"].get(current_loc)
        if not loc_info:
            return []

        poi_info = loc_info["points_of_interest"].get(current_poi)
        if not poi_info:
            return []

        # Get entries at this POI
        entry_ids = poi_info.get("entries", [])

        quantum_entries = []
        for entry_id in entry_ids:
            full_entry_id = f"{current_loc}.{entry_id}"
            entry_data = loc_info["entries"].get(entry_id)

            if entry_data and entry_data.get("quantum", False):
                # Include ALL quantum entries (discovered or not)
                # This allows re-rolling all entries at POI
                quantum_entries.append((full_entry_id, entry_data))

        return quantum_entries

    def _get_new_state(self, old_state: int) -> int:
        """
        Get new random state (1-6) that differs from old_state.
        If old_state is 0 (first observation), any state 1-6 is valid.
        """
        if old_state == 0:
            # First observation - any state is fine
            return random.randint(1, 6)

        # Get list of valid new states (all except old_state)
        valid_states = [s for s in range(1, 7) if s != old_state]

        return random.choice(valid_states)

    def get_entry_state(self, full_entry_id: str) -> int:
        """
        Get current quantum state for an entry.
        Returns state 1-6, or 0 if never observed.
        """
        return self.quantum_states.get(full_entry_id, 0)

    def get_entry_symbol(self, full_entry_id: str) -> str:
        """
        Get current symbol for an entry.
        Returns symbol string or "?" if never observed.
        """
        state = self.get_entry_state(full_entry_id)
        if state == 0:
            return "?"
        return self.state_symbols.get(state, "?")

    def scramble_text(self, content: str, state: int) -> str:
        """
        Scramble text content based on quantum state.
        Uses state as seed for reproducible scrambling.
        States 1-5 scramble word order into gibberish.
        State 6 (encryption key) returns original text unscrambled.
        """
        if state == 6:
            # Encryption key state - return original text
            return content

        # Use state as seed for reproducible scrambling
        rng = random.Random(state)

        # Split into words while preserving some structure
        lines = content.split('\n')
        scrambled_lines = []

        for line in lines:
            if line.strip():
                # Split line into words
                words = line.split()
                # Shuffle words
                rng.shuffle(words)
                scrambled_lines.append(' '.join(words))
            else:
                # Preserve empty lines
                scrambled_lines.append(line)

        return '\n'.join(scrambled_lines)

    def reset_eyes(self):
        """Reset eyes to open state (for safety/cleanup)"""
        self.eyes_closed = False
