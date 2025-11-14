"""
NPC Dialogue System
Handles short tutorial/context dialogues with 3 NPCs
"""

import json
from typing import Dict, List, Optional, Set
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time


class NPCSystem:
    """Manages NPC dialogues and interactions"""

    def __init__(self, console: Console, content_loader=None):
        self.console = console
        self.npc_data: Dict = {}
        self.dialogue_history: Set[str] = set()  # Track which dialogues have been seen
        self.content_loader = content_loader  # For displaying markdown entries

    def load_npc_data(self, npc_file_path: str = "content/data/npcs.json"):
        """Load NPC dialogue data from JSON"""
        npc_path = Path(npc_file_path)
        if npc_path.exists():
            with open(npc_path, 'r', encoding='utf-8') as f:
                self.npc_data = json.load(f)
        else:
            # Fallback to empty data
            self.npc_data = {"npcs": {}}

    def get_npc_info(self, npc_id: str) -> Optional[Dict]:
        """Get NPC data"""
        return self.npc_data.get("npcs", {}).get(npc_id)

    def has_dialogue_available(self, npc_id: str, knowledge_menu) -> bool:
        """Check if NPC has any available dialogue"""
        npc_info = self.get_npc_info(npc_id)
        if not npc_info:
            return False

        dialogues = npc_info.get("dialogues", [])
        for dialogue in dialogues:
            dialogue_id = dialogue.get("id")
            if self._can_access_dialogue(dialogue, knowledge_menu) and dialogue_id not in self.dialogue_history:
                return True

        return True  # Can always talk, even if just for flavor

    def has_new_dialogue(self, npc_id: str, knowledge_menu) -> bool:
        """Check if NPC has NEW dialogue that player hasn't seen yet AND can access now"""
        npc_info = self.get_npc_info(npc_id)
        if not npc_info:
            return False

        dialogues = npc_info.get("dialogues", [])
        for dialogue in dialogues:
            dialogue_id = dialogue.get("id")
            # Must not have been seen AND must be accessible
            if dialogue_id not in self.dialogue_history and self._can_access_dialogue(dialogue, knowledge_menu):
                return True

        return False  # No new accessible dialogue

    def _can_access_dialogue(self, dialogue: Dict, knowledge_menu) -> bool:
        """Check if dialogue prerequisites are met"""
        required_knowledge = dialogue.get("requires_knowledge", [])
        if required_knowledge:
            return knowledge_menu.progress.has_all_knowledge(required_knowledge)

        required_discoveries = dialogue.get("requires_discoveries", [])
        if required_discoveries:
            return all(d in knowledge_menu.progress.entries_discovered for d in required_discoveries)

        return True

    def talk_to_npc(self, npc_id: str, knowledge_menu, interactions=None) -> Optional[str]:
        """
        Initiate dialogue with NPC.
        Returns knowledge_id if dialogue grants knowledge, None otherwise.
        """
        npc_info = self.get_npc_info(npc_id)
        if not npc_info:
            self.console.print(f"\n[dim]That person isn't here...[/dim]\n")
            return None

        # Check if this NPC uses menu-based dialogue
        uses_menu = npc_info.get("dialogue_menu", False)

        if uses_menu and interactions:
            # Show menu of dialogue topics
            dialogue, granted = self._show_dialogue_menu(npc_info, knowledge_menu, interactions)
            return granted
        else:
            # Traditional priority-based dialogue
            dialogue = self._get_best_dialogue(npc_info, knowledge_menu)
            if not dialogue:
                self._show_default_dialogue(npc_info)
                return None

            # Show dialogue
            self._display_dialogue(npc_info, dialogue)

            # Mark as seen
            dialogue_id = dialogue.get("id")
            if dialogue_id:
                self.dialogue_history.add(dialogue_id)

            # Grant knowledge if applicable
            grants_knowledge = dialogue.get("grants_knowledge")
            if grants_knowledge:
                return grants_knowledge

            return None

    def _show_dialogue_menu(self, npc_info: Dict, knowledge_menu, interactions):
        """Show menu of dialogue topics for player to choose from"""
        npc_name = npc_info.get("name", "Unknown")
        dialogues = npc_info.get("dialogues", [])

        while True:
            # Get available dialogue topics
            available_topics = []
            available_dialogues = []

            for dialogue in dialogues:
                if self._can_access_dialogue(dialogue, knowledge_menu):
                    menu_text = dialogue.get("menu_text", dialogue.get("id", "Unknown topic"))
                    # Mark if already discussed
                    if dialogue.get("id") in self.dialogue_history:
                        menu_text = f"{menu_text} [discussed]"
                    available_topics.append(menu_text)
                    available_dialogues.append(dialogue)
                else:
                    # Show locked topics with hint
                    required = dialogue.get("requires_knowledge", [])
                    if required:
                        menu_text = dialogue.get("menu_text", "???")
                        available_topics.append(f"[LOCKED] {menu_text}")
                        available_dialogues.append(None)  # Placeholder

            if not available_topics:
                self._show_default_dialogue(npc_info)
                return None, None

            # Show menu
            choice = interactions.get_menu_choice(
                available_topics,
                title=f"💬 TALK TO {npc_name.upper()}",
                show_back=True
            )

            if choice is None:
                # Player backed out
                return None, None

            selected_dialogue = available_dialogues[choice]
            if selected_dialogue is None:
                # Locked dialogue
                self.console.print("\n[yellow]You need more knowledge to discuss this topic.[/yellow]\n")
                time.sleep(1)
                continue

            # Show the dialogue
            entry_ref = selected_dialogue.get("entry_reference")
            if entry_ref:
                # This dialogue references a full entry file - load and display it
                if self.content_loader:
                    # Build the full entry ID (location.entry_id format)
                    full_entry_id = f"quantum_moon.{entry_ref}"
                    # Create a minimal entry_data dict for display
                    entry_data = {
                        "title": selected_dialogue.get("menu_text", "Dialogue"),
                        "type": "dialogue",
                        "format": "conversational"
                    }
                    # Use content loader's method directly
                    self.content_loader.load_and_display_entry("quantum_moon", entry_ref, entry_data)
                else:
                    self.console.print(f"\n[yellow]Content loader not available[/yellow]\n")
                    time.sleep(0.3)
            else:
                # Regular dialogue with lines
                self._display_dialogue(npc_info, selected_dialogue)

            # Mark as seen
            dialogue_id = selected_dialogue.get("id")
            if dialogue_id:
                self.dialogue_history.add(dialogue_id)

            # Grant knowledge if applicable
            grants_knowledge = selected_dialogue.get("grants_knowledge")
            granted_this_turn = grants_knowledge

            # After showing dialogue, ask if they want to continue talking
            continue_choice = interactions.get_menu_choice(
                ["Ask another question", "End conversation"],
                title="",
                show_back=False
            )

            if continue_choice != 0:
                # End conversation
                return selected_dialogue, granted_this_turn

    def _get_best_dialogue(self, npc_info: Dict, knowledge_menu) -> Optional[Dict]:
        """Get the highest-priority dialogue that's available"""
        dialogues = npc_info.get("dialogues", [])

        # Filter to accessible dialogues
        available = []
        for dialogue in dialogues:
            dialogue_id = dialogue.get("id")
            if dialogue_id in self.dialogue_history:
                continue  # Already seen

            if self._can_access_dialogue(dialogue, knowledge_menu):
                available.append(dialogue)

        # Sort by priority (higher = more important)
        available.sort(key=lambda d: d.get("priority", 0), reverse=True)

        return available[0] if available else None

    def _display_dialogue(self, npc_info: Dict, dialogue: Dict):
        """Display a dialogue exchange"""
        npc_name = npc_info.get("name", "Unknown")
        lines = dialogue.get("lines", [])

        self.console.print()

        for line in lines:
            speaker = line.get("speaker")
            text = line.get("text")

            if speaker == "npc":
                # NPC speech
                speech = Text()
                speech.append(f"{npc_name.upper()}: ", style="bold cyan")
                speech.append(f'"{text}"', style="white")
                self.console.print(speech)
            elif speaker == "player":
                # Player response
                speech = Text()
                speech.append("YOU: ", style="bold yellow")
                speech.append(f'"{text}"', style="dim")
                self.console.print(speech)
            else:
                # Narration
                self.console.print(f"[dim]{text}[/dim]")

            time.sleep(1)
            self.console.print()

        # Show any teaching/hint
        teaching = dialogue.get("teaches")
        if teaching:
            hint = Text()
            hint.append("\n💡 ", style="yellow")
            hint.append(teaching, style="italic yellow")
            self.console.print(hint)
            time.sleep(1)

        self.console.print()

    def _show_default_dialogue(self, npc_info: Dict):
        """Show default/fallback dialogue when no special dialogue available"""
        npc_name = npc_info.get("name", "Unknown")
        fallback = npc_info.get("fallback_dialogue", "They seem busy.")

        dialogue_text = Text()
        dialogue_text.append(f"\n{npc_name.upper()}: ", style="bold cyan")
        dialogue_text.append(f'"{fallback}"', style="white")
        dialogue_text.append("\n", style="white")

        self.console.print(dialogue_text)
        time.sleep(0.8)

    def get_npc_description(self, npc_id: str) -> str:
        """Get brief description of NPC for scene-setting"""
        npc_info = self.get_npc_info(npc_id)
        if not npc_info:
            return ""

        return npc_info.get("description", "")

    def reset_dialogue_history(self):
        """Reset dialogue history (for loop resets)"""
        # In Outer Wilds, NPCs remember you've talked to them
        # We'll keep dialogue history persistent across loops
        # Only reset if needed for testing
        pass
