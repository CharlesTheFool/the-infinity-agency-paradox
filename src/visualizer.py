"""
Visualization Engine

Handles all visual display using Rich library for terminal formatting.
Creates ASCII art, panels, progress bars, and formatted text.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, BarColumn, TextColumn
from rich.tree import Tree
from rich.table import Table
from typing import Dict, List, Optional
import time


class Visualizer:
    """
    Creates visual elements using Rich library.

    Implements the visual specifications from VISUAL_SPECIFICATIONS.md
    including color palette, typography, and ASCII art.
    """

    def __init__(self):
        # Force UTF-8 encoding for Windows compatibility
        import sys
        import io
        if sys.platform == 'win32':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

        self.console = Console(legacy_windows=False)

        # Color palette (from VISUAL_SPECIFICATIONS.md)
        self.colors = {
            "interactive": "cyan",
            "question": "yellow",
            "understood": "green",
            "locked": "red",
            "meta": "magenta",
            "dim": "dim"
        }

    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()

    def show_title_card(self, title: str, subtitle: str = "", act_number: Optional[int] = None):
        """
        Display act title card with border.

        Args:
            title: Main title text
            subtitle: Optional subtitle
            act_number: Optional act number (1-5)
        """
        border = "═" * 70
        self.console.print(f"\n{border}", style="bold")

        if act_number:
            self.console.print(f"ACT {act_number} OF 5".center(70), style="bold cyan")
            self.console.print()

        self.console.print(title.center(70), style="bold cyan")

        if subtitle:
            self.console.print(subtitle.center(70), style="cyan")

        self.console.print(f"{border}\n", style="bold")

    def show_panel(self, content: str, title: str = "", border_style: str = "white"):
        """
        Display content in a bordered panel.

        Args:
            content: Text to display
            title: Optional panel title
            border_style: Color of border
        """
        panel = Panel(content, title=title, border_style=border_style)
        self.console.print(panel)

    def show_markdown(self, md_text: str):
        """
        Render markdown content with rich formatting.

        Used for displaying analysis sections.
        """
        md = Markdown(md_text)
        self.console.print(md)

    def show_progress_bar(self, total: int, description: str = "Progress"):
        """
        Show progress bar (returns Progress context manager).

        Used for loop timer simulation.
        """
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        )

    def show_solar_system(self, discovered_planets: List[str]):
        """
        Display ASCII solar system with discovered planets.

        Builds progressively as player discovers locations.
        """
        ascii_art = "\n"

        # Always show sun
        ascii_art += "                    ☀️\n"
        ascii_art += "                  [SUN]\n\n"

        # Show discovered planets
        if "timber_hearth" in discovered_planets:
            ascii_art += "        🌍\n"
            ascii_art += "   [Timber Hearth]\n"
            ascii_art += "    Home Planet\n\n"

        if "brittle_hollow" in discovered_planets:
            ascii_art += "    🌑\n"
            ascii_art += " [Brittle Hollow]\n"
            ascii_art += "  Fragmenting\n\n"

        if "giants_deep" in discovered_planets:
            ascii_art += "       💨\n"
            ascii_art += "  [Giant's Deep]\n"
            ascii_art += "   Storm World\n\n"

        if "dark_bramble" in discovered_planets:
            ascii_art += "      🌿\n"
            ascii_art += " [Dark Bramble]\n"
            ascii_art += "  Maze of Vines\n\n"

        if "ash_twin" in discovered_planets:
            ascii_art += "     🏜️\n"
            ascii_art += "  [Ash Twin]\n"
            ascii_art += " Sand Transfer\n\n"

        if "interloper" in discovered_planets:
            ascii_art += "       ❄️\n"
            ascii_art += "  [Interloper]\n"
            ascii_art += "  Ghost Matter\n\n"

        if "quantum_moon" in discovered_planets:
            ascii_art += "      🔮\n"
            ascii_art += " [Quantum Moon]\n"
            ascii_art += " Superposition\n\n"

        self.console.print(ascii_art, style="cyan")

    def show_knowledge_tree(self, understood: List[str], accessible: List[str], locked: List[str]):
        """
        Display knowledge graph as tree structure.

        Shows epistemic state: what's understood, accessible, and locked.
        """
        tree = Tree("📚 [bold]Your Epistemic State[/bold]")

        if understood:
            understood_branch = tree.add("[green]✓ Understood[/green]")
            for item in understood:
                understood_branch.add(f"[green]{item}[/green]")

        if accessible:
            accessible_branch = tree.add("[cyan]→ Available to Investigate[/cyan]")
            for item in accessible:
                accessible_branch.add(f"[cyan]{item}[/cyan]")

        if locked:
            locked_branch = tree.add("[red]🔒 Locked (Prerequisites Needed)[/red]")
            for item in locked[:3]:  # Show max 3 to avoid clutter
                locked_branch.add(f"[red]{item}[/red]")

        self.console.print(tree)

    def show_comparison_table(self, title: str, rows: List[Dict[str, str]]):
        """
        Display comparison table.

        Used for comparing games, frameworks, systems, etc.
        """
        table = Table(title=title, show_header=True, header_style="bold cyan")

        # Add columns from first row keys
        if rows:
            for col_name in rows[0].keys():
                table.add_column(col_name)

            # Add data rows
            for row in rows:
                table.add_row(*row.values())

        self.console.print(table)

    def show_loop_timer(self, minutes: int, total_minutes: int = 22):
        """
        Display time loop counter.

        Shows current time in loop (MM:SS) with progress bar.
        """
        progress = (minutes / total_minutes) * 100
        filled = int(progress / 5)
        empty = 20 - filled

        bar = "▓" * filled + "░" * empty

        time_str = f"{minutes:02d}:00 / 22:00"

        self.console.print("╔" + "═" * 48 + "╗")
        self.console.print(f"║  ⏱️  LOOP TIME: {time_str}".ljust(48) + "  ║")
        self.console.print(f"║  {bar}                          ║")
        self.console.print("╚" + "═" * 48 + "╝")

    def show_fragment_discovery(self, fragment_title: str, fragment_content: str):
        """
        Display fragment discovery with special formatting.

        Creates "aha moment" feeling when understanding is achieved.
        """
        self.console.print("\n[bold yellow]✨ UNDERSTANDING ACHIEVED ✨[/bold yellow]\n")

        panel_content = f"[bold]{fragment_title}[/bold]\n\n{fragment_content}"
        self.show_panel(panel_content, border_style="yellow")

    def show_locked_message(self, prerequisites: List[str]):
        """
        Display message when content is locked by prerequisites.
        """
        prereq_list = "\n".join(f"  • {p}" for p in prerequisites)

        message = f"[red]🔒 INSUFFICIENT KNOWLEDGE[/red]\n\n"
        message += f"This information requires understanding:\n{prereq_list}\n\n"
        message += "[dim]Continue exploring to gain prerequisites.[/dim]"

        self.show_panel(message, border_style="red")

    def show_stats(self, stats: Dict):
        """
        Display progress statistics.

        Shows discoveries, understanding, questions raised, etc.
        """
        stats_text = f"""
[cyan]Discoveries:[/cyan] {stats.get('discovered', 0)} fragments
[green]Understood:[/green] {stats.get('understood', 0)} / {stats.get('total', 0)} ({stats.get('percentage', 0)}%)
[yellow]Questions Raised:[/yellow] {stats.get('questions_raised', 0)}
[magenta]Locations Visited:[/magenta] {stats.get('locations_visited', 0)}
        """.strip()

        self.show_panel(stats_text, title="📊 Your Progress", border_style="cyan")

    def typewriter_effect(self, text: str, delay: float = 0.03):
        """
        Print text with typewriter effect.

        Used sparingly for dramatic moments.
        """
        for char in text:
            self.console.print(char, end="", style="bold")
            time.sleep(delay)
        self.console.print()  # New line at end

    def show_convergence(self, choice: str):
        """
        Show convergence moment for Act 1.

        Demonstrates that all paths lead to same outcome.
        """
        self.console.print("\n[dim]Analyzing your choice...[/dim]\n")
        time.sleep(1)

        border = "═" * 60
        self.console.print(f"\n{border}", style="red")
        self.console.print("RESULT: IMPOSSIBLE".center(60), style="bold red")
        self.console.print(f"{border}\n", style="red")

        message = f"""
You chose: [cyan]{choice}[/cyan]

But the Nomai died 280,000 years ago.
Nothing you chose could change this outcome.

[bold]This is DEONTIC AGENCY[/bold] : choosing actions with the
illusion of affecting outcomes.

Notice how constrained that felt?
        """.strip()

        self.console.print(message)
