"""
Content Loader - Loads and displays entry content from markdown files
"""

import os
import time
import random
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text


class ContentLoader:
    """Loads and displays content for location entries"""

    def __init__(self, console: Console, content_dir: str):
        self.console = console
        self.content_dir = Path(content_dir)

    def load_and_display_entry(self, location_id: str, entry_id: str, entry_data: dict, quantum_state: Optional[int] = None):
        """
        Load content file and display with appropriate formatting.

        Args:
            location_id: Location identifier
            entry_id: Entry identifier
            entry_data: Entry metadata
            quantum_state: Optional quantum state (1-6). If not 6, scrambles content.
        """

        # Map entry IDs to content files
        content_map = {
            # Timber Hearth
            "timber_hearth.deontic_critique": "timber_hearth_deontic_critique.md",
            "timber_hearth.epistemic_intro": "timber_hearth_epistemic_intro.md",
            "timber_hearth.launch_code_discovery": "observatory_launch_code.md",
            "timber_hearth.ship_access_tutorial": "ship_access_tutorial.md",
            "timber_hearth.signal_frequencies_log": "timber_hearth_signal_frequencies.md",
            "timber_hearth.cardinal_directions_poem": "timber_hearth_cardinal_directions.md",
            "timber_hearth.quantum_moon_rumor": "timber_hearth_quantum_moon_rumor.md",

            # Attlerock
            "attlerock.jenkins_overview": "attlerock_jenkins_overview.md",
            "attlerock.quantum_stabilization": "attlerock_quantum_stabilization.md",
            "attlerock.evocative_spaces": "attlerock_evocative_spaces.md",
            "attlerock.embedded_narratives": "attlerock_embedded_narratives.md",
            "attlerock.enacting_stories": "attlerock_enacting_stories.md",
            "attlerock.emergent_narratives": "attlerock_emergent_narratives.md",
            "attlerock.frequency_codes": "attlerock_frequency_codes.md",

            # Brittle Hollow
            "brittle_hollow.time_loop_intro": "brittle_hollow_time_loop_intro.md",
            "brittle_hollow.majora_comparison": "brittle_hollow_majora_comparison.md",
            "brittle_hollow.quantum_moon_frequency": "brittle_hollow_quantum_moon_frequency.md",
            "brittle_hollow.quantum_research_notes": "brittle_hollow_quantum_research_notes.md",

            # Quantum Moon (2 entries + ending)
            "quantum_moon.solanum_location": "quantum_moon_arrival.md",
            "quantum_moon.guidance_dialogue": "solanum_guidance_dialogue.md",
            "quantum_moon.thesis_ending": "ending_sequence.md",
        }

        full_entry_id = f"{location_id}.{entry_id}"

        # Try to load content file
        if full_entry_id in content_map:
            content_file = self.content_dir / content_map[full_entry_id]
            if content_file.exists():
                self._display_from_file(content_file, entry_data, quantum_state)
                return True

        # Fallback: display placeholder
        self._display_placeholder(entry_data)
        return False

    def _display_from_file(self, file_path: Path, entry_data: dict, quantum_state: Optional[int] = None):
        """
        Display content from markdown file.

        Args:
            file_path: Path to content file
            entry_data: Entry metadata
            quantum_state: Optional quantum state. If provided and not 6, scrambles content.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply quantum scrambling if needed
        if quantum_state is not None and quantum_state != 6:
            content = self._scramble_text(content, quantum_state)

        # Clear screen for immersion
        self.console.clear()
        time.sleep(0.3)

        # Display based on entry type
        entry_type = entry_data.get("type", "wall_text")
        format_type = entry_data.get("format", "academic")

        if entry_type == "audio_log":
            self._display_audio_log(content, entry_data["title"])
        elif entry_type == "interface":
            self._display_interface(content, entry_data["title"])
        elif entry_type == "dialogue":
            self._display_dialogue(content, entry_data["title"])
        elif entry_type == "ending":
            self._display_ending(content)
        else:  # wall_text or default
            self._display_wall_text(content, entry_data["title"])

        input("\n[Press Enter to continue...]")

    def _scramble_text(self, content: str, state: int) -> str:
        """
        Scramble text content by shuffling word order.
        Uses quantum state as seed for reproducible scrambling.

        Args:
            content: Original text content
            state: Quantum state (1-5 for scrambling)

        Returns:
            Scrambled text with words in gibberish order
        """
        # Use state as seed for reproducible scrambling
        rng = random.Random(state)

        # Split into lines and scramble each line
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

    def _display_wall_text(self, content: str, title: str):
        """Display Nomai wall inscription"""
        md = Markdown(content)
        self.console.print(Panel(
            md,
            title=f"📜 {title}",
            border_style="cyan",
            padding=(1, 2)
        ))

    def _display_audio_log(self, content: str, title: str):
        """Display audio log with appropriate styling"""
        md = Markdown(content)
        self.console.print(Panel(
            md,
            title=f"🔊 AUDIO LOG - {title}",
            border_style="yellow",
            padding=(1, 2)
        ))

    def _display_interface(self, content: str, title: str):
        """Display computer interface"""
        md = Markdown(content)
        self.console.print(Panel(
            md,
            title=f"💻 {title}",
            border_style="green",
            padding=(1, 2)
        ))

    def _display_dialogue(self, content: str, title: str):
        """Display Solanum dialogue"""
        md = Markdown(content)
        self.console.print(Panel(
            md,
            title=f"🌙 SOLANUM - {title}",
            border_style="magenta",
            padding=(1, 2)
        ))

    def _display_ending(self, content: str):
        """Display ending sequence"""
        # Parse and display with dramatic pacing
        lines = content.split('\n')

        for line in lines:
            if line.strip():
                if line.startswith('**SOLANUM'):
                    # Dialogue
                    self.console.print(Text(line.replace('**', ''), style="bold magenta"))
                    time.sleep(1.5)
                elif line.startswith('```'):
                    # Screen effects
                    continue
                elif '[WHITE SCREEN]' in line or '[Fade to campfire]' in line:
                    self.console.clear()
                    time.sleep(2)
                elif line.startswith('#'):
                    # Headers
                    self.console.print(Text(line.replace('#', '').strip(), style="bold cyan"))
                    time.sleep(1)
                else:
                    # Regular text
                    self.console.print(line)
                    time.sleep(0.5)
            else:
                time.sleep(0.3)

    def _display_placeholder(self, entry_data: dict):
        """Display placeholder for content not yet created"""
        title = entry_data.get("title", "Unknown Entry")
        entry_type = entry_data.get("type", "wall_text")

        placeholder = Text()
        placeholder.append(f"\n[This text is not yet written]\n\n", style="yellow")
        placeholder.append(f"Entry: {title}\n", style="white")
        placeholder.append(f"Type: {entry_type}\n\n", style="dim")
        placeholder.append("The words here are still forming.\n", style="dim")
        placeholder.append("They will appear in time.\n\n", style="dim")

        self.console.print(Panel(placeholder, border_style="yellow", title="⚠️ Incomplete"))
        time.sleep(1)
        input("\n[Press Enter to continue...]")

    def display_ending_with_stats(self, knowledge_menu, loop_manager):
        """Display ending sequence with player statistics"""
        ending_file = self.content_dir / "ending_sequence.md"

        if not ending_file.exists():
            self.console.print("[red]Ending file not found![/red]")
            return

        with open(ending_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace placeholders with actual stats
        stats = {
            "{{LOOP_COUNT}}": str(loop_manager.loop_count),
            "{{FIRST_LOCATION}}": "Timber Hearth",  # Could track this
            "{{FIRST_QUANTUM}}": "Unknown",  # Could track this
            "{{MOST_VISITED}}": "Unknown",  # Could track this
            "{{COMPLETION_PCT}}": f"{knowledge_menu.progress.get_completion_percentage(knowledge_menu.get_total_entries()):.0f}",
            "{{DISCOVERED}}": str(knowledge_menu.get_discovered_count()),
            "{{TOTAL}}": str(knowledge_menu.get_total_entries())
        }

        for placeholder, value in stats.items():
            content = content.replace(placeholder, value)

        # Display ending
        self._display_ending(content)
