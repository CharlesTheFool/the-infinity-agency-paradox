"""
Configuration constants for the mini-map system.
Defines icons, colors, and display settings.
"""

# === POI State Icons (ASCII) ===
ICON_PLAYER = "@"           # Current player position
ICON_SHIP = "*"             # Ship docked here
ICON_NPC = "~"              # NPC present
ICON_ENTRY_AVAILABLE = "+"  # Entries to discover
ICON_ENTRY_LOCKED = "#"     # Locked entries
ICON_COMPLETED = "x"        # All entries found
ICON_VISITED = "."          # Been here, nothing left
ICON_UNKNOWN = "?"          # Unknown/undiscovered
ICON_LOCKED_POI = "⚠"       # POI requires knowledge to access
ICON_CONNECTION = "|"       # Vertical connection line

# === Trail/Path Connectors ===
TRAIL_CONNECTOR = "─"       # Horizontal trail between POIs
TRAIL_VERTICAL = "│"        # Vertical trail (if needed)

# === Location Prefixes (ASCII) ===
LOCATION_PREFIXES = {
    "timber_hearth": "[H]",      # Home
    "the_attlerock": "[A]",      # Attlerock
    "brittle_hollow": "[B]",     # Brittle Hollow
    "the_quantum_moon": "[Q]"    # Quantum Moon
}

# === Colors (Rich markup) ===
COLOR_CURRENT = "yellow"
COLOR_VISITED = "green"
COLOR_UNVISITED = "dim white"
COLOR_LOCKED = "red"
COLOR_PARTIAL = "cyan"
COLOR_COMPLETE = "bright_green"
COLOR_HEADER = "bold bright_white"
COLOR_BORDER = "blue"

# === Display Settings ===
MAP_WIDTH = 35  # Panel width in characters
MAP_COMPACT_WIDTH = 30  # Fallback for smaller terminals
MAP_MIN_TERMINAL_WIDTH = 80  # Minimum recommended terminal width

# === Progress Display ===
SHOW_PERCENTAGES = True
SHOW_POI_COUNT = True
SHOW_ENTRY_COUNT = True

# === State Display Priorities ===
# Order matters - first matching state shows its icon
POI_STATE_PRIORITY = [
    "current",      # Player is here
    "ship",         # Ship is here
    "completed",    # All entries discovered
    "has_npc",      # NPC present
    "has_entries",  # Undiscovered entries
    "has_locked",   # Locked entries
    "visited",      # Been here before
    "unvisited"     # Never been here
]

# === Text Templates ===
TEXT_PROGRESS_POI = "{current}/{total} POIs"
TEXT_PROGRESS_ENTRIES = "{current}/{total} entries"
TEXT_PROGRESS_PERCENT = "({percent}%)"
TEXT_DISTANCE = "{distance} actions"
TEXT_NO_CONNECTIONS = "No other POIs nearby"
TEXT_IN_FLIGHT = "In Flight"
TEXT_IN_SHIP = "In Ship (grounded)"
