from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.layout import Layout
from rich.text import Text

class UserInterface:
    def __init__(self, batch_drafter, batch_submitter, batch_monitor, batch_manager):
        self.batch_drafter = batch_drafter
        self.batch_submitter = batch_submitter
        self.batch_monitor = batch_monitor
        self.batch_manager = batch_manager
        self.console = Console()

    def run(self):
        """Main loop for the user interface."""
        while True:
            self.display_main_menu()
            choice = self.handle_user_input()
            if choice == "quit":
                break

    def display_main_menu(self):
        """Shows the main menu options."""
        menu = Table(title="Main Menu", box=None)
        menu.add_column("Option", style="cyan", no_wrap=True)
        menu.add_column("Description", style="magenta")
        menu.add_row("1", "Draft a new batch")
        menu.add_row("2", "Import prompts from file")  # New option
        menu.add_row("3", "Submit a batch")
        menu.add_row("4", "Monitor batch status")
        menu.add_row("5", "View batch results")
        menu.add_row("6", "List all batches")
        menu.add_row("7", "Cancel a batch")
        menu.add_row("q", "Quit")

        layout = Layout()
        
        # Ensure batch_monitor.display_batch_statuses() returns a renderable object
        batch_statuses = self.batch_monitor.display_batch_statuses()
        if batch_statuses is None:
            batch_statuses = Text("No active batches", style="yellow")

        layout.split_column(
            Layout(Panel(batch_statuses, title="Active Batches")),
            Layout(Panel(menu, title="Menu Options"))
        )
        self.console.print(layout)

    def handle_user_input(self):
        """Processes user input and calls appropriate methods."""
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "q"])
        if choice == "1":
            self.draft_batch()
        elif choice == "2":
            self.import_batch()  # New method
        elif choice == "3":
            self.submit_batch()
        elif choice == "4":
            self.monitor_batch()
        elif choice == "5":
            self.view_batch_results()
        elif choice == "6":
            self.list_all_batches()
        elif choice == "7":
            self.cancel_batch()
        elif choice.lower() == "q":
            return "quit"
        return choice

    def import_batch(self):
        """Handles batch import from file."""
        file_path = Prompt.ask("Enter the path to the file containing prompts")
        model = Prompt.ask("Enter model name")
        max_tokens = self.get_integer_input("Enter max tokens", default=100)
        self.batch_drafter.import_batch(file_path, model, max_tokens)
        self.console.print("[green]Batch import completed.[/green]")
        self.display_batch_draft()

    def draft_batch(self):
        """Handles batch drafting."""
        self.batch_drafter.create_new_batch()
        while True:
            self.display_batch_draft()
            action = Prompt.ask("Action", choices=["add", "edit", "remove", "done"])
            if action == "add":
                custom_id = Prompt.ask("Enter custom ID")
                model = Prompt.ask("Enter model name")
                max_tokens = self.get_integer_input("Enter max tokens", default=100)
                content = Prompt.ask("Enter message content")
                #file_path = Prompt.ask("Enter file path")
                self.batch_drafter.add_message(custom_id, model, max_tokens, content)
            elif action == "edit":
                index = self.get_integer_input("Enter message index to edit", default=0)
                field = Prompt.ask("Enter field to edit", choices=["custom_id", "model", "max_tokens", "content", "file_path"])
                if field == "max_tokens":
                    value = self.get_integer_input(f"Enter new value for {field}")
                else:
                    value = Prompt.ask(f"Enter new value for {field}")
                self.batch_drafter.edit_message(index, field, value)
            elif action == "remove":
                index = self.get_integer_input("Enter message index to remove", default=0)
                self.batch_drafter.remove_message(index)
            elif action == "done":
                break

    def submit_batch(self):
        """Handles batch submission."""
        batch = self.batch_drafter.get_batch()
        batch_id = self.batch_submitter.submit_batch(batch)
        if batch_id:
            self.batch_monitor.add_batch(batch_id)
            self.console.print(f"[green]Batch submitted successfully. Batch ID: {batch_id}[/green]")
        else:
            self.console.print("[red]Batch submission failed.[/red]")

    def monitor_batch(self):
        """Handles batch monitoring."""
        self.batch_monitor.update_all_statuses()
        statuses = self.batch_monitor.display_batch_statuses()
        if statuses:
            self.console.print(statuses)
        else:
            self.console.print("[yellow]No active batches to monitor.[/yellow]")

    def view_batch_results(self):
        """Handles viewing batch results."""
        batch_id = Prompt.ask("Enter batch ID to view results")
        results = self.batch_manager.retrieve_batch_results(batch_id)
        table = Table(title=f"Results for Batch {batch_id}")
        table.add_column("Custom ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Content", style="green")
        for result in results:
            table.add_row(
                result.get('custom_id', 'N/A'),
                result.get('status', 'N/A'),
                result.get('content', 'N/A')[:50] + '...'  # Truncate long content
            )
        self.console.print(table)

    def list_all_batches(self):
        """Handles listing all batches."""
        limit = int(Prompt.ask("Enter number of batches to list", default="20"))
        batches = self.batch_manager.list_all_batches(limit)
        table = Table(title="All Batches")
        table.add_column("Batch ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Created At", style="green")
        for batch in batches:
            table.add_row(
                batch.get('id', 'N/A'),
                batch.get('processing_status', 'N/A'),
                batch.get('created_at', 'N/A')
            )
        self.console.print(table)

    def cancel_batch(self):
        """Handles batch cancellation."""
        batch_id = Prompt.ask("Enter batch ID to cancel")
        success = self.batch_manager.cancel_batch(batch_id)
        if success:
            self.console.print(f"[green]Batch {batch_id} cancelled successfully.[/green]")
        else:
            self.console.print(f"[red]Failed to cancel batch {batch_id}.[/red]")

    def get_integer_input(self, prompt: str, default: int = 0) -> int:
        """Helper method to get integer input from the user."""
        while True:
            try:
                value = Prompt.ask(prompt, default=str(default))
                return int(value)
            except ValueError:
                self.console.print("[red]Please enter a valid integer.[/red]")

    def display_batch_draft(self):
        """Shows the current batch being drafted."""
        draft = self.batch_drafter.view_batch()
        if isinstance(draft, str):
            self.console.print(Panel(draft, title="Current Batch Draft"))
        elif isinstance(draft, Table):
            self.console.print(draft)
        else:
            self.console.print("[yellow]No current batch draft available.[/yellow]")
