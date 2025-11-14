"""
Knowledge Menu System - Persistent Log
Tracks discovered entries, knowledge gained, and provides Rumor Mode UI
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.text import Text


@dataclass
class KnowledgeEntry:
    """Represents a single discoverable piece of knowledge"""
    entry_id: str
    location_id: str
    title: str
    entry_type: str  # wall_text, audio_log, dialogue, interface, ending
    format_type: str  # academic, conversational, synthesis, system, emotional
    is_quantum: bool
    knowledge_grants: List[str]
    discovered: bool = False
    discovered_loop: int = 0
    # New fields for progressive discovery and visual design
    importance: str = "optional"  # critical, important, optional
    short_desc: str = ""
    adds_to_log: bool = True
    appears_after: List[str] = field(default_factory=list)  # Knowledge IDs required for entry to appear
    key_info: str = ""  # Important info displayed in log (e.g., "Code: EPISTEMIC")


@dataclass
class KnowledgeProgress:
    """Tracks overall exploration progress"""
    entries_discovered: Set[str] = field(default_factory=set)
    knowledge_gained: Set[str] = field(default_factory=set)
    locations_visited: Set[str] = field(default_factory=set)
    current_loop: int = 1
    total_visits: int = 0
    dialogue_topics_asked: int = 0
    new_entries_since_last_view: int = 0  # Track new entries for "!" indicator
    discovered_commands: Set[str] = field(default_factory=lambda: {
        "explore", "visit", "locations", "check log", "help", "quit"
    })

    def add_entry(self, entry: KnowledgeEntry, loop: int) -> bool:
        """Add discovered entry. Returns True if newly discovered."""
        if entry.entry_id in self.entries_discovered:
            return False

        self.entries_discovered.add(entry.entry_id)
        entry.discovered = True
        entry.discovered_loop = loop

        # Add knowledge grants
        for knowledge in entry.knowledge_grants:
            self.knowledge_gained.add(knowledge)

        # Increment new entries counter for "!" indicator
        self.new_entries_since_last_view += 1

        return True

    def has_knowledge(self, knowledge_id: str) -> bool:
        """Check if player has specific knowledge"""
        return knowledge_id in self.knowledge_gained

    def has_all_knowledge(self, knowledge_ids: List[str]) -> bool:
        """Check if player has all required knowledge"""
        return all(k in self.knowledge_gained for k in knowledge_ids)

    def get_completion_percentage(self, total_entries: int) -> float:
        """Calculate percentage of content discovered"""
        if total_entries == 0:
            return 0.0
        return (len(self.entries_discovered) / total_entries) * 100


class KnowledgeMenu:
    """Manages ship's log and rumor mode display"""

    def __init__(self, console: Console):
        self.console = console
        self.progress = KnowledgeProgress()
        self.all_entries: Dict[str, KnowledgeEntry] = {}
        self.location_data: Dict = {}

    def register_entries(self, location_data: Dict):
        """Register all entries from location data"""
        self.location_data = location_data

        for loc_id, loc_info in location_data["locations"].items():
            for entry_id, entry_data in loc_info["entries"].items():
                full_entry_id = f"{loc_id}.{entry_id}"

                # Only register entries that should appear in log
                if not entry_data.get("adds_to_log", True):
                    continue

                entry = KnowledgeEntry(
                    entry_id=full_entry_id,
                    location_id=loc_id,
                    title=entry_data["title"],
                    entry_type=entry_data["type"],
                    format_type=entry_data["format"],
                    is_quantum=entry_data.get("quantum", False),
                    knowledge_grants=entry_data.get("knowledge_grants", []),
                    importance=entry_data.get("importance", "optional"),
                    short_desc=entry_data.get("short_desc", ""),
                    adds_to_log=entry_data.get("adds_to_log", True),
                    appears_after=entry_data.get("appears_after", []),
                    key_info=entry_data.get("key_info", "")
                )
                self.all_entries[full_entry_id] = entry

    def discover_entry(self, entry_id: str) -> bool:
        """Mark entry as discovered. Returns True if newly discovered."""
        if entry_id not in self.all_entries:
            return False

        entry = self.all_entries[entry_id]
        was_new = self.progress.add_entry(entry, self.progress.current_loop)

        return was_new

    def can_access_entry(self, entry_id: str) -> tuple[bool, str]:
        """Check if entry can be accessed. Returns (can_access, reason_if_not)"""
        if entry_id not in self.all_entries:
            return False, "Something's missing..."

        entry_data = self._get_entry_data(entry_id)
        if not entry_data:
            return False, "Can't find what you're looking for..."

        # Check knowledge requirements
        required_knowledge = entry_data.get("requires_knowledge", [])
        if required_knowledge:
            if not self.progress.has_all_knowledge(required_knowledge):
                missing = [k for k in required_knowledge if not self.progress.has_knowledge(k)]

                # Special messages for key gates
                if "quantum_stabilization_ability" in missing:
                    return False, "⟁ QUANTUM TEXT - You need to learn stabilization"
                elif "ship_operation" in missing:
                    return False, "You need to access the ship first"
                else:
                    missing_readable = [k.replace("_", " ") for k in missing]
                    return False, f"Not yet... ({', '.join(missing_readable)})"

        # Check dialogue count requirement
        required_dialogue = entry_data.get("requires_dialogue_count", 0)
        if required_dialogue > 0 and self.progress.dialogue_topics_asked < required_dialogue:
            remaining = required_dialogue - self.progress.dialogue_topics_asked
            return False, f"Talk more with Solanum first ({remaining} questions)"

        # Check exploration percentage
        required_pct = entry_data.get("requires_exploration_percentage", 0)
        if required_pct > 0:
            total_entries = len(self.all_entries)
            current_pct = self.progress.get_completion_percentage(total_entries) / 100
            if current_pct < required_pct:
                needed = int((required_pct - current_pct) * 100)
                return False, f"Explore more before this reveals itself ({needed}% needed)"

        return True, ""

    def _get_entry_data(self, entry_id: str) -> Optional[Dict]:
        """Get raw entry data from location config"""
        parts = entry_id.split(".")
        if len(parts) != 2:
            return None

        loc_id, ent_id = parts
        return self.location_data["locations"].get(loc_id, {}).get("entries", {}).get(ent_id)

    def _should_entry_appear(self, entry: KnowledgeEntry) -> bool:
        """Check if entry should appear in rumor mode based on progressive discovery"""
        # Check if all prerequisites are met
        for knowledge_id in entry.appears_after:
            if not self.progress.has_knowledge(knowledge_id):
                return False
        return True

    def _get_visible_entries(self) -> List[KnowledgeEntry]:
        """Get all entries that should be visible in rumor mode"""
        visible = []
        for entry in self.all_entries.values():
            # ALL entries must pass progressive discovery check (appears_after gates)
            # This creates gradual knowledge revelation regardless of importance
            if not self._should_entry_appear(entry):
                continue

            # Smart filter: Show if accessible OR discovered
            can_access, _ = self.can_access_entry(entry.entry_id)
            if can_access or entry.discovered:
                visible.append(entry)

        return visible

    def _get_importance_style(self, entry: KnowledgeEntry, is_discovered: bool) -> tuple[str, str, str]:
        """Get (marker, color, text_style) for entry based on importance"""
        if is_discovered:
            return "✓", "green", "green"

        # Undiscovered styling based on importance
        if entry.importance == "critical":
            return "[!!!]", "bold red", "bold red"
        elif entry.importance == "important":
            return "[!]", "yellow", "yellow"
        else:  # optional
            return "?", "dim white", "dim white"

    def show_rumor_mode(self):
        """Display clean, progressive rumor mode UI"""
        table = Table(title="📖 LOG", show_header=False, border_style="cyan")
        table.add_column("Content", style="white")

        # Get all visible entries
        visible_entries = self._get_visible_entries()

        # Organize entries by importance for progressive sections
        critical_entries = [e for e in visible_entries if e.importance == "critical"]
        important_entries = [e for e in visible_entries if e.importance == "important"]
        optional_entries = [e for e in visible_entries if e.importance == "optional"]

        # SECTION 1: Critical Path (always shown if any exist)
        if critical_entries:
            section = Text()
            section.append("\n━━━ CRITICAL PATH ━━━\n", style="bold red")

            for entry in sorted(critical_entries, key=lambda e: (e.discovered, e.title)):
                marker, color, text_style = self._get_importance_style(entry, entry.discovered)
                if entry.discovered:
                    section.append(f"  {marker} {entry.title}\n", style=text_style)
                    # Show key info if available
                    if entry.key_info:
                        section.append(f"    → {entry.key_info}\n", style="cyan")
                else:
                    # Don't show location - encourages exploration
                    section.append(f"  {marker} {entry.title}\n", style=text_style)

            table.add_row(section)

        # SECTION 2: Important Discoveries (shown after getting ship)
        if important_entries and self.progress.has_knowledge("ship_operation"):
            section = Text()
            section.append("\n━━━ INVESTIGATION ━━━\n", style="bold yellow")

            for entry in sorted(important_entries, key=lambda e: (e.discovered, e.title)):
                marker, color, text_style = self._get_importance_style(entry, entry.discovered)
                if entry.discovered:
                    section.append(f"  {marker} {entry.title}\n", style=text_style)
                    # Show key info if available
                    if entry.key_info:
                        section.append(f"    → {entry.key_info}\n", style="cyan")
                else:
                    # Don't show location - encourages exploration
                    section.append(f"  {marker} {entry.title}\n", style=text_style)

            table.add_row(section)

        # SECTION 3: Optional Lore (shown after quantum ability OR if player has discovered any)
        show_optional = (
            self.progress.has_knowledge("quantum_stabilization_ability") or
            any(e.discovered for e in optional_entries)
        )

        if optional_entries and show_optional:
            section = Text()
            section.append("\n━━━ DEEP LORE ━━━\n", style="bold cyan")

            for entry in sorted(optional_entries, key=lambda e: (e.discovered, e.title)):
                marker, color, text_style = self._get_importance_style(entry, entry.discovered)
                if entry.discovered:
                    section.append(f"  {marker} {entry.title}\n", style=text_style)
                    # Show key info if available
                    if entry.key_info:
                        section.append(f"    → {entry.key_info}\n", style="cyan")
                else:
                    # Don't show location - encourages exploration
                    section.append(f"  {marker} {entry.title}\n", style=text_style)

            table.add_row(section)

        # Footer: Just progress
        total_entries = len(self.all_entries)
        discovered_count = len(self.progress.entries_discovered)
        completion_pct = self.progress.get_completion_percentage(total_entries)

        footer = Text()
        footer.append(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", style="dim")
        footer.append(f"Progress: {completion_pct:.0f}% ", style="bold")
        footer.append(f"({discovered_count}/{total_entries})  ", style="white")
        footer.append(f"│  Loop {self.progress.current_loop}\n", style="cyan")
        table.add_row(footer)

        self.console.print(table)

    def show_quick_summary(self):
        """Show compact progress summary"""
        total = len(self.all_entries)
        discovered = len(self.progress.entries_discovered)
        pct = self.progress.get_completion_percentage(total)

        summary = Text()
        summary.append(f"Progress: {pct:.0f}% ", style="cyan")
        summary.append(f"({discovered}/{total}) | ", style="white")
        summary.append(f"Loop {self.progress.current_loop} | ", style="yellow")
        summary.append(f"Visits: {self.progress.total_visits % 4}/4", style="red" if self.progress.total_visits % 4 == 3 else "white")

        self.console.print(Panel(summary, border_style="dim"))

    def increment_loop(self):
        """Increment loop counter (called on supernova reset)"""
        self.progress.current_loop += 1

    def increment_visit(self):
        """Increment visit counter"""
        self.progress.total_visits += 1

    def get_discovered_count(self) -> int:
        """Get number of discovered entries"""
        return len(self.progress.entries_discovered)

    def get_total_entries(self) -> int:
        """Get total number of entries"""
        return len(self.all_entries)

    def has_knowledge(self, knowledge_id: str) -> bool:
        """Check if player has specific knowledge"""
        return self.progress.has_knowledge(knowledge_id)

    def add_knowledge(self, knowledge_id):
        """Manually add knowledge (for special cases)"""
        # Handle both single strings and lists for flexibility
        if isinstance(knowledge_id, list):
            for kid in knowledge_id:
                self.progress.knowledge_gained.add(kid)
        else:
            self.progress.knowledge_gained.add(knowledge_id)

    def increment_dialogue_asked(self):
        """Increment dialogue topics asked counter"""
        self.progress.dialogue_topics_asked += 1

    def unlock_command(self, command: str):
        """Unlock a new command for the player"""
        self.progress.discovered_commands.add(command)

    def has_command(self, command: str) -> bool:
        """Check if player has discovered a command"""
        return command in self.progress.discovered_commands

    def get_discovered_commands(self) -> Set[str]:
        """Get all discovered commands"""
        return self.progress.discovered_commands

    def has_new_entries(self) -> bool:
        """Check if there are new entries since last viewing log"""
        return self.progress.new_entries_since_last_view > 0

    def clear_new_entries(self):
        """Clear new entries counter (called when viewing ship's log)"""
        self.progress.new_entries_since_last_view = 0
