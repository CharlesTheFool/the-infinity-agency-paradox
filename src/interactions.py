"""
User Interaction Handler

Manages all user input with validation and error handling.
Ensures graceful UX with clear prompts and helpful feedback.
"""

from typing import List, Optional
from rich.console import Console
import questionary


class InteractionHandler:
    """
    Handles all user input interactions.

    Provides various input types:
    - Simple acknowledgment (ENTER)
    - Numbered choices (1, 2, 3)
    - Text input
    - Ratings (1-5 scale)
    """

    def __init__(self):
        # Force UTF-8 encoding for Windows compatibility
        import sys
        import io
        if sys.platform == 'win32':
            # Only set if not already wrapped
            if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

        self.console = Console(legacy_windows=False)

    def wait_for_enter(self, prompt: str = "\nPress ENTER to continue..."):
        """
        Wait for user to press ENTER to continue.

        Used for pacing - ensures user has time to read before proceeding.
        """
        self.console.print(f"[dim]{prompt}[/dim]")
        input()

    def get_choice(self, options: List[str], prompt: str = "Choose an option:") -> int:
        """
        Present numbered options and get user's choice.

        Args:
            options: List of option strings
            prompt: Question or instruction for user

        Returns:
            Integer index (1-based) of chosen option
        """
        self.console.print(f"\n[bold]{prompt}[/bold]")
        for i, option in enumerate(options, 1):
            self.console.print(f"  [cyan]{i}.[/cyan] {option}")

        while True:
            try:
                self.console.print()
                choice = input(f"Enter 1-{len(options)}: ")
                choice_int = int(choice)

                if 1 <= choice_int <= len(options):
                    return choice_int
                else:
                    self.console.print(f"[red]Please enter a number between 1 and {len(options)}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
            except KeyboardInterrupt:
                self.console.print("\n[red]Interrupted. Exiting...[/red]")
                raise

    def get_numbered_choice(self, min_val: int, max_val: int) -> Optional[int]:
        """
        Get a numeric choice from user (when options are already displayed).

        Args:
            min_val: Minimum valid number
            max_val: Maximum valid number

        Returns:
            Integer choice within range, or None if interrupted
        """
        while True:
            try:
                choice = input(f"\nEnter {min_val}-{max_val}: ").strip()
                choice_int = int(choice)

                if min_val <= choice_int <= max_val:
                    return choice_int
                else:
                    self.console.print(f"[red]Please enter a number between {min_val} and {max_val}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
            except KeyboardInterrupt:
                self.console.print("\n[red]Interrupted. Exiting...[/red]")
                raise

    def get_text_input(self, prompt: str, allow_empty: bool = False) -> str:
        """
        Get text input from user.

        Args:
            prompt: Question or instruction
            allow_empty: Whether to accept empty strings

        Returns:
            User's text input
        """
        while True:
            self.console.print(f"\n[bold]{prompt}[/bold]")
            text = input("> ").strip()

            if text or allow_empty:
                return text
            else:
                self.console.print("[red]Please enter some text[/red]")

    def get_rating(self, prompt: str, min_val: int = 1, max_val: int = 5) -> int:
        """
        Get numerical rating from user.

        Args:
            prompt: What to rate
            min_val: Minimum rating value
            max_val: Maximum rating value

        Returns:
            Integer rating within range
        """
        self.console.print(f"\n[bold]{prompt}[/bold]")

        while True:
            try:
                rating = int(input(f"Rate {min_val}-{max_val}: "))

                if min_val <= rating <= max_val:
                    return rating
                else:
                    self.console.print(f"[red]Please rate between {min_val} and {max_val}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")
            except KeyboardInterrupt:
                self.console.print("\n[red]Interrupted. Exiting...[/red]")
                raise

    def get_yes_no(self, prompt: str) -> bool:
        """
        Get yes/no response from user.

        Args:
            prompt: Yes/no question

        Returns:
            True for yes, False for no
        """
        self.console.print(f"\n[bold]{prompt}[/bold]")

        while True:
            response = input("(y/n): ").strip().lower()

            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                self.console.print("[red]Please enter 'y' or 'n'[/red]")

    def get_sequence(self, items: List[str], prompt: str) -> List[str]:
        """
        Get user-ordered sequence of items.

        Used for Act 4's fragment reconstruction puzzle.

        Args:
            items: List of items to arrange
            prompt: Instructions for arrangement

        Returns:
            List of items in user's chosen order
        """
        self.console.print(f"\n[bold]{prompt}[/bold]\n")

        for i, item in enumerate(items, 1):
            self.console.print(f"  [{chr(64+i)}] {item}")

        self.console.print("\n[dim]Enter the order as letters (e.g., EACBD)[/dim]")

        while True:
            order = input("Order: ").strip().upper()

            # Convert letters to indices
            expected_letters = set(chr(65+i) for i in range(len(items)))
            provided_letters = set(order)

            if provided_letters == expected_letters and len(order) == len(items):
                # Convert letters to ordered list of items
                ordered_items = []
                for letter in order:
                    index = ord(letter) - 65
                    ordered_items.append(items[index])
                return ordered_items
            else:
                self.console.print(f"[red]Please use each letter A-{chr(64+len(items))} exactly once[/red]")

    def show_error(self, message: str):
        """Display error message in red."""
        self.console.print(f"[red]⚠️  {message}[/red]")

    def show_success(self, message: str):
        """Display success message in green."""
        self.console.print(f"[green]✓ {message}[/green]")

    def show_info(self, message: str):
        """Display info message in cyan."""
        self.console.print(f"[cyan]ℹ {message}[/cyan]")

    def get_menu_choice(self, options: List[str], title: str = "Choose:", show_back: bool = False) -> Optional[int]:
        """
        Display interactive arrow key menu.

        Args:
            options: List of option strings to display
            title: Title/prompt above menu
            show_back: If True, adds "← Back" option at bottom

        Returns:
            Index of selected option (0-based), or None if back/cancelled
        """
        if show_back:
            menu_options = options + ["← Back"]
        else:
            menu_options = options

        try:
            # Use questionary for cross-platform arrow key support
            result = questionary.select(
                title,
                choices=menu_options,
                pointer="►",
                style=questionary.Style([
                    ('pointer', 'fg:cyan bold'),
                    ('highlighted', 'fg:cyan'),
                    ('selected', 'fg:cyan'),
                ])
            ).ask()

            # Add bottom buffer for visual breathing room
            if result is not None:
                self.console.print("\n\n\n")

            if result is None:
                return None

            # Find index of selected option
            choice_index = menu_options.index(result)

            # Handle back option
            if show_back and choice_index == len(options):
                return None

            return choice_index

        except KeyboardInterrupt:
            return None
