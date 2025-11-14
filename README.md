# Epistemic Agency: An Interactive Analysis of Outer Wilds

## Intro

Hi! Welcome to "The Infinity Agency Paradox," an interactive experience that explores how agency and progression work in the 2019 Mobius Entertainment hit video game Outer Wilds (not to be confused with Outer Worlds, 2019). The objective of this approach, as opposed to an essay, is the ability to show first hand how the epistemic systems at work in outer Wilds shape gameplay, offering an interesting, multimedia alternative approach to analytical writing. For those who have played Outer Wilds, forgive my lax take on adapting the game's story and characters, as I had to make sure that they would somehow fit into this toy-sized version of the entire experience. So, if you want the full depth and accurancy of Outer Wilds... Play the game!

Anyway, feel free to read the guide below to understand how this entire thing works, and thank you for taking your time to indulge this little experiement!

## Running the Experience

**Requirements**: Python 3.8 or higher installed on your system.

Simply double-click the launcher for your platform:

### Windows
Double-click `launch.bat`

### Linux
Double-click `launch.sh`

*First time only*: You may need to make it executable:
```bash
chmod +x launch.sh
```

*Note for Ubuntu/Debian users*: If you see an error about `python3-venv`, run:
```bash
sudo apt install python3-venv
```
Then run the launcher again.

### macOS
Double-click `launch.command`

*First time only*: You may need to make it executable:
```bash
chmod +x launch.command
```

No manual setup, terminal commands, or configuration required.

## How to Play (SPOILERS)

1. **Follow the tutorial**: Hornfels and the first few entries provides initial guidance at the Observatory
2. **Find the launch code**: Read all entries to trigger ship code dialogue with Hornfels
3. **Explore the solar system**: Visit locations, examine entries, gain knowledge
4. **Check your Ship's Log**: Press "Check Ship's Log" to track progress and discovered entries
5. **Check your Ship's Log**: Press "Check Ship's Log" to track progress and discovered entries

**Key mechanics**: Knowledge enables action. The ship is always accessible, but launching requires the code. Quantum texts require stabilization. Every 22 actions trigger a supernova reset, but knowledge persists across loops.

**If you are lazy**: If you are interested in reading all the entries in a more traditionally academic fashion, please direct yourself to the path at "content/entries/." and have fun with all those markdown files! You may, and should, ignore non-analytical entries if you go on that route.

## Author

**Charles Belanger**
FMS 394 - 2025

## References

### Books

Crawford, Chris. *The Art of Interactive Design.* Chapter 28: "Interactive Storytelling," 2003, pp. 339-346.

Domsch, Sebastian. *Storyplaying: Agency and Narrative in Video Games.* "Narrative Forms [extract]," 2013, pp. 31-52.

Koster, Raph. *A Theory of Fun.* Chapters 2-3: "How the Brain Works" and "What Games Are," 2004, pp. 12-47.

Lebowitz, Josiah, and Chris Klug. *Interactive Storytelling for Video Games.* Chapter 3: "The Hero's Journey and the Structure of Game Stories," 2011, pp. 39-69.

Rogers, Scott. *Level Up!: The Guide to Great Video Game Design.* Chapter 3: "Writing the Story," 2014, pp. 43-56.

Salen, Katie, and Eric Zimmerman. *Rules of Play.* Chapter 6: "Interactivity," 2004, pp. 1-14.

Salen, Katie, and Eric Zimmerman. *Rules of Play.* Chapter 7: "Defining Games," 2004, pp. 1-14.

Walton, Mark, and Maurice Suckling. *Video Game Writing.* Chapter 5: "Narrative Design," pp. 3-12.

### Articles

Bartle, Richard. Referenced in: Zenn. "Understanding Your Audience: Bartle Player Taxonomy." GameAnalytics.com.

Boller. "Game Design Fundamentals" (blog series). TheKnowledgeGuru.com.

Jenkins, Henry. "Game Design as Narrative Architecture." HenryJenkins.com, 2005.

Larsen, Bjørn Petter, and Henrik Schoenau-Fog. "The Narrative Quality of Game Mechanics," 2016, pp. 61-72.

Narain. "The 9 Types of Player Choice (with Examples)." BlackShellMedia.com, 2016.

Picucci. "When Video Games Tell Stories: A Model of Video Game Narrative Architectures," 2014, pp. 105-113.

### Videos

"Death to the Three Act Structure! Towards a Unique Structure for Game Narratives," 25:30.

Extra Credits. "How to Start Your Narrative - Design Mechanics First," Season 7, Episode 6, 4:59.

Extra Credits. "The Feeling of Agency - What Makes Choice Meaningful?" Season 7, Episode 6, 5:18.

### Games

*Deathloop.* (2021). Arkane Studios. Bethesda Softworks.

*Detroit: Become Human.* (2018). Quantic Dream. Sony Interactive Entertainment.

*Life is Strange.* (2015). Dontnod Entertainment. Square Enix.

*Outer Wilds.* (2019). Mobius Digital. Annapurna Interactive.

*Returnal.* (2021). Housemarque. Sony Interactive Entertainment.

*The Legend of Zelda: Majora's Mask.* (2000). Nintendo. Nintendo.

---

## Troubleshooting

### "Python is not installed" Error

Download and install Python 3.8 or higher:
- **Windows**: https://www.python.org/downloads/ (check "Add Python to PATH" during installation)
- **macOS**: https://www.python.org/downloads/macos/ or `brew install python3`
- **Linux**: `sudo apt install python3 python3-venv` (Ubuntu/Debian)

### Manual Installation (Advanced)

If the launcher doesn't work for some reason, you can run manually:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main_outerwilds.py
```
