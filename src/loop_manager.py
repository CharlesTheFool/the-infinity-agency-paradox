"""
Loop Manager - Handles Time Loop Mechanics
Manages action-based supernova timer, reset mechanics, and knowledge persistence
"""

import time
from typing import Callable, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from src.visualizer import Visualizer


class LoopManager:
    """Manages time loop resets and action-based supernova mechanics"""

    def __init__(self, console: Console, visualizer: Visualizer, actions_until_supernova: int = 22):
        self.console = console
        self.visualizer = visualizer
        self.actions_until_supernova = actions_until_supernova
        self.current_actions = 0
        self.loop_count = 1
        self.is_first_loop = True
        self.minutes_per_action = 1  # Each action costs 1 minute
        self.cavern_has_collapsed = False  # Track quantum cavern collapse

    def increment_action(self, action_cost: int = 1):
        """
        Increment action counter by specified cost.
        Returns:
        - "quantum_cavern_collapse" if cavern collapses (action 14)
        - "supernova" if supernova triggers (action 22+)
        - False otherwise
        """
        self.current_actions += action_cost

        # Check for quantum cavern collapse at action 14
        if self.current_actions == 14 and not self.cavern_has_collapsed:
            self.cavern_has_collapsed = True
            return "quantum_cavern_collapse"

        # Show warning at 18/22 actions
        warning_threshold = self.actions_until_supernova - 4
        if self.current_actions == warning_threshold:
            self._show_supernova_warning()

        # Check for supernova
        if self.current_actions >= self.actions_until_supernova:
            return "supernova"

        return False

    def get_timer_bar(self) -> str:
        """
        Get visual progress bar for action timer.
        Returns colored string like: [████████░░░░░░░░░░░░] 8/22 min
        """
        progress = self.current_actions / self.actions_until_supernova
        filled_blocks = int(progress * 20)
        empty_blocks = 20 - filled_blocks

        # Color based on urgency
        if progress >= 0.9:
            style = "bold red"
        elif progress >= 0.75:
            style = "yellow"
        else:
            style = "green"

        bar_filled = "█" * filled_blocks
        bar_empty = "░" * empty_blocks
        current_minutes = self.current_actions * self.minutes_per_action
        total_minutes = self.actions_until_supernova * self.minutes_per_action
        timer_text = f"{current_minutes}/{total_minutes} min"

        return f"[{style}][{bar_filled}{bar_empty}][/{style}] {timer_text}"

    def get_timer_text(self) -> Text:
        """Get colored Text object for timer display"""
        progress = self.current_actions / self.actions_until_supernova
        filled_blocks = int(progress * 20)
        empty_blocks = 20 - filled_blocks

        # Color based on urgency
        if progress >= 0.9:
            style = "bold red"
            bar_style = "red"
        elif progress >= 0.75:
            style = "yellow"
            bar_style = "yellow"
        else:
            style = "white"
            bar_style = "green"

        bar_filled = "█" * filled_blocks
        bar_empty = "░" * empty_blocks

        timer = Text()
        timer.append("[", style="dim")
        timer.append(bar_filled, style=bar_style)
        timer.append(bar_empty, style="dim")
        timer.append("]", style="dim")
        current_minutes = self.current_actions * self.minutes_per_action
        total_minutes = self.actions_until_supernova * self.minutes_per_action
        timer.append(f" {current_minutes}/{total_minutes} min", style=style)

        return timer

    def _show_supernova_warning(self):
        """Display warning that sun is becoming unstable"""
        warning = Text()
        warning.append("\n⚠️  WARNING ⚠️\n\n", style="bold red")
        warning.append("The sun grows brighter. Hotter.\n", style="yellow")
        warning.append("You feel it in your bones. Something is changing.\n", style="yellow")

        self.console.print(Panel(warning, border_style="red", title="THE SUN"))
        time.sleep(2)

    def trigger_supernova(self, knowledge_menu) -> bool:
        """
        Execute supernova sequence.
        Returns True if should continue (loop), False if should end.
        """
        self.visualizer.clear_screen()

        # Special handling for first loop
        if self.is_first_loop:
            self._first_supernova_sequence(knowledge_menu)
            self.is_first_loop = False
        else:
            self._standard_supernova_sequence()

        # Reset action counter and collapse state
        self.current_actions = 0
        self.cavern_has_collapsed = False

        # Increment loop counter
        self.loop_count += 1
        knowledge_menu.increment_loop()

        return True  # Continue looping

    def _first_supernova_sequence(self, knowledge_menu):
        """Special narrative sequence for first supernova"""
        sequences = [
            ("", "The sun grows brighter."),
            ("yellow", "The temperature rises."),
            ("", "You feel a deep rumbling beneath your feet."),
            ("red", "\nTHE SUN IS COLLAPSING!"),
        ]

        for style, text in sequences:
            self.console.print(Text(text, style=style or "white"))
            time.sleep(1.5)

        time.sleep(1)

        # Supernova flash
        self.console.print("\n\n")
        self.console.print(Panel(
            Text("███████████████████████████████████████", style="bold white on red"),
            border_style="red"
        ))
        time.sleep(0.5)

        self.visualizer.clear_screen()
        time.sleep(1)

        # Awakening
        awakening = Text()
        awakening.append("You wake beside the campfire.\n\n", style="cyan")
        awakening.append("Wait... you were just in space.\n", style="white")
        awakening.append("The sun exploded.\n", style="white")
        awakening.append("You died.\n\n", style="white")
        awakening.append("But you're alive. Back at Timber Hearth.\n\n", style="cyan")
        awakening.append("And you remember ", style="yellow")
        awakening.append("everything", style="bold yellow")
        awakening.append(".\n\n", style="yellow")

        self.console.print(Panel(awakening, border_style="cyan", title="LOOP 2 BEGINS"))
        time.sleep(3)

        # Show what persisted
        if knowledge_menu.progress.knowledge_gained:
            knowledge_text = Text()
            knowledge_text.append("You Still Remember:\n\n", style="bold green")

            # Show key knowledge
            key_knowledge = []
            if knowledge_menu.has_knowledge("launch_code_epistemic"):
                key_knowledge.append("✓ Launch code: EPISTEMIC")
            if knowledge_menu.has_knowledge("quantum_stabilization_ability"):
                key_knowledge.append("✓ Quantum stabilization technique")
            if knowledge_menu.has_knowledge("jenkins_framework"):
                key_knowledge.append("✓ Jenkins' four architectures")
            if knowledge_menu.has_knowledge("time_loop_understanding"):
                key_knowledge.append("✓ Time loop mechanics")

            for item in key_knowledge:
                knowledge_text.append(f"{item}\n", style="green")

            knowledge_text.append(f"\nTotal entries discovered: {knowledge_menu.get_discovered_count()}\n", style="cyan")
            knowledge_text.append("\nYour understanding remains, even as the universe resets.\n", style="yellow italic")

            self.console.print(Panel(knowledge_text, border_style="green", title="LOG"))
            time.sleep(3)

        # Tutorial about epistemic shortcuts
        if knowledge_menu.has_knowledge("launch_code_epistemic"):
            skip_text = Text()
            skip_text.append("You already know the launch code.\n", style="white")
            skip_text.append("You can go ", style="white")
            skip_text.append("directly to your ship", style="bold cyan")
            skip_text.append(" now.\n\n", style="white")
            skip_text.append("Knowledge enables shortcuts.\n", style="yellow italic")
            skip_text.append("Understanding creates new paths.\n", style="yellow italic")

            self.console.print(Panel(skip_text, border_style="yellow"))
            time.sleep(3)

        input("\n[Press Enter to continue...]")

    def _standard_supernova_sequence(self):
        """Standard supernova sequence for subsequent loops"""
        self.console.print(Text("\nTHE SUN EXPLODES!", style="bold red"))
        time.sleep(1)

        # Quick flash
        self.console.print(Panel(
            Text("████████████████████████", style="white on red"),
            border_style="red"
        ))
        time.sleep(0.3)

        self.visualizer.clear_screen()
        time.sleep(0.5)

        # Quick awakening
        self.console.print(Text(f"\nYou wake at the campfire. Loop {self.loop_count + 1} begins.\n", style="cyan"))
        time.sleep(1.5)

    def get_actions_remaining(self) -> int:
        """Get number of actions before supernova"""
        return self.actions_until_supernova - self.current_actions

    def get_current_loop(self) -> int:
        """Get current loop number"""
        return self.loop_count
