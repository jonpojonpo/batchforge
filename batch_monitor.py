from typing import Dict
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

class BatchMonitor:
    def __init__(self, api_client):
        self.api_client = api_client
        self.active_batches = {}
        self.console = Console()

    def add_batch(self, batch_id: str) -> None:
        """
        Adds a new batch to monitor.

        :param batch_id: ID of the batch to be monitored
        """
        if batch_id not in self.active_batches:
            self.active_batches[batch_id] = {"status": "Added", "request_counts": {}}
            self.console.print(f"[green]Batch {batch_id} added to monitoring.[/green]")
        else:
            self.console.print(f"[yellow]Batch {batch_id} is already being monitored.[/yellow]")

    def update_status(self, batch_id: str) -> None:
        """
        Updates the status of a specific batch.

        :param batch_id: ID of the batch to update
        """
        if batch_id in self.active_batches:
            try:
                batch_status = self.api_client.get_batch_status(batch_id)
                self.active_batches[batch_id] = {
                    "status": batch_status.get("processing_status", "Unknown"),
                    "request_counts": batch_status.get("request_counts", {})
                }
                self.console.print(f"[blue]Status updated for batch {batch_id}.[/blue]")
            except Exception as e:
                self.console.print(f"[red]Error updating status for batch {batch_id}: {str(e)}[/red]")
        else:
            self.console.print(f"[yellow]Batch {batch_id} is not being monitored.[/yellow]")

    def get_batch_status(self, batch_id: str) -> Dict:
        """
        Returns the current status of a batch.

        :param batch_id: ID of the batch to get status for
        :return: Dictionary containing status and request counts
        """
        if batch_id in self.active_batches:
            return self.active_batches[batch_id]
        else:
            self.console.print(f"[yellow]Batch {batch_id} is not being monitored.[/yellow]")
            return {"status": "Not monitored", "request_counts": {}}

    def remove_completed_batch(self, batch_id: str) -> None:
        """
        Removes a completed batch from monitoring.

        :param batch_id: ID of the batch to remove
        """
        if batch_id in self.active_batches:
            status = self.active_batches[batch_id]["status"]
            if status in ["ended", "canceled"]:
                del self.active_batches[batch_id]
                self.console.print(f"[green]Batch {batch_id} removed from monitoring.[/green]")
            else:
                self.console.print(f"[yellow]Batch {batch_id} is not completed (status: {status}). Not removing.[/yellow]")
        else:
            self.console.print(f"[yellow]Batch {batch_id} is not being monitored.[/yellow]")

    def display_batch_statuses(self):
        """
        Displays a table of all monitored batch statuses.
        """
        if not self.active_batches:
            return Text("No active batches", style="yellow")

        table = Table(title="Monitored Batches")
        table.add_column("Batch ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Processing", style="blue")
        table.add_column("Succeeded", style="green")
        table.add_column("Errored", style="red")
        table.add_column("Canceled", style="yellow")
        table.add_column("Expired", style="dim")

        for batch_id, data in self.active_batches.items():
            status = data["status"]
            counts = data["request_counts"]
            table.add_row(
                batch_id,
                status,
                str(counts.get("processing", 0)),
                str(counts.get("succeeded", 0)),
                str(counts.get("errored", 0)),
                str(counts.get("canceled", 0)),
                str(counts.get("expired", 0))
            )

        return table

    def update_all_statuses(self) -> None:
        """
        Updates the status of all monitored batches.
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]Updating batch statuses...", total=len(self.active_batches))
            for batch_id in list(self.active_batches.keys()):
                self.update_status(batch_id)
                progress.update(task, advance=1)

        self.display_batch_statuses()
