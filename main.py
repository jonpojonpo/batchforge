import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from api_client import APIClient
from batch_drafter import BatchDrafter
from batch_submitter import BatchSubmitter
from batch_monitor import BatchMonitor
from batch_manager import BatchManager
from user_interface import UserInterface

def main():
    console = Console()

    try:
        # Load environment variables
        load_dotenv()

        # Check for API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            console.print(Panel("API key not found. Please set the ANTHROPIC_API_KEY environment variable.", 
                                title="Error", style="bold red"))
            sys.exit(1)

        # Initialize components
        api_client = APIClient(api_key)
        batch_drafter = BatchDrafter()  # Now this works without config_manager
        batch_submitter = BatchSubmitter(api_client)
        batch_monitor = BatchMonitor(api_client)
        batch_manager = BatchManager(api_client)

        # Create and run the user interface
        ui = UserInterface(batch_drafter, batch_submitter, batch_monitor, batch_manager)

        console.print(Panel("Welcome to the Message Batch Terminal App!", 
                            subtitle="Press Ctrl+C to exit at any time", 
                            style="bold green"))

        ui.run()

    except KeyboardInterrupt:
        console.print("\n[yellow]Application terminated by user.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {str(e)}[/bold red]")
        console.print_exception(show_locals=True)
    finally:
        console.print("[bold blue]Thank you for using the Message Batch Terminal App![/bold blue]")

if __name__ == "__main__":
    main()