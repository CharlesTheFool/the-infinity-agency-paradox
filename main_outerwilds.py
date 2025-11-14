"""
Outer Wilds-Style Interactive Analysis
Main entry point for the redesigned experience
"""

from src.new_orchestrator import OuterWildsOrchestrator


def main():
    """Main entry point"""
    try:
        orchestrator = OuterWildsOrchestrator()
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n\n[Exploration ended]\n")
    except Exception as e:
        print(f"\n\nError: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
