from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def print_welcome():
    """Print welcome message."""
    welcome = """
# Welcome to Beavs! 🦫

Your friendly Canadian shop assistant for Maple Leaf Makers.

**Commands:**
- Type naturally to interact (e.g., "Bin A1 has M3 screws")
- `/help` - Show this help
- `/clear` - Clear conversation history
- `/quit` or `/exit` - Exit Beavs

Let's get organized, eh!
"""
    console.print(Panel(Markdown(welcome), title="Beavs", border_style="green"))

def print_response(text: str):
    """Print Beavs' response."""
    console.print(Panel(text, title="Beavs", border_style="blue"))

def print_error(text: str):
    """Print an error message."""
    console.print(Panel(text, title="Error", border_style="red"))

def run_repl():
    """Run the interactive REPL."""
    # Import here to avoid circular imports and ensure Django is set up
    from assistant.processor import InputProcessor

    processor = InputProcessor()
    print_welcome()

    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ['/quit', '/exit']:
                console.print("[yellow]See ya later! 👋[/yellow]")
                break

            if user_input.lower() == '/help':
                print_welcome()
                continue

            if user_input.lower() == '/clear':
                processor.clear_history()
                console.print("[yellow]Conversation cleared![/yellow]")
                continue

            # Process natural language input
            response = processor.process(user_input)
            print_response(response)

        except KeyboardInterrupt:
            console.print("\n[yellow]See ya later! 👋[/yellow]")
            break
        except Exception as e:
            print_error(str(e))

if __name__ == '__main__':
    run_repl()
