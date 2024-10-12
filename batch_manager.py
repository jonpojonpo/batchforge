from typing import List, Dict, Iterator
from rich.console import Console

class BatchManager:
    def __init__(self, api_client):
        self.api_client = api_client
        self.console = Console()

    def list_all_batches(self, limit: int = 20) -> List[Dict]:
        """
        Lists all batches in the workspace.

        :param limit: Number of batches to retrieve (default 20)
        :return: List of batch dictionaries
        """
        try:
            batches = self.api_client.list_batches(limit)
            return batches
        except Exception as e:
            self.console.print(f"[red]Error listing batches: {str(e)}[/red]")
            return []

    def get_batch_details(self, batch_id: str) -> Dict:
        """
        Retrieves detailed information about a specific batch.

        :param batch_id: ID of the batch to retrieve details for
        :return: Dictionary containing batch details
        """
        try:
            details = self.api_client.get_batch_status(batch_id)
            return details
        except Exception as e:
            self.console.print(f"[red]Error retrieving batch details: {str(e)}[/red]")
            return {}

    def cancel_batch(self, batch_id: str) -> bool:
        """
        Cancels a specific batch.

        :param batch_id: ID of the batch to cancel
        :return: Boolean indicating success or failure
        """
        try:
            response = self.api_client.cancel_batch(batch_id)
            if response['processing_status'] == 'canceling':
                self.console.print(f"[green]Batch {batch_id} is being canceled.[/green]")
                return True
            else:
                self.console.print(f"[yellow]Unexpected status after cancellation: {response['processing_status']}[/yellow]")
                return False
        except Exception as e:
            self.console.print(f"[red]Error canceling batch: {str(e)}[/red]")
            return False

    def retrieve_batch_results(self, batch_id: str) -> Iterator[Dict]:
        """
        Retrieves and yields results for a completed batch.

        :param batch_id: ID of the batch to retrieve results for
        :return: Iterator of result dictionaries
        """
        try:
            batch_status = self.get_batch_details(batch_id)
            if batch_status.get('processing_status') != 'ended':
                self.console.print(f"[yellow]Batch {batch_id} is not completed. Current status: {batch_status.get('processing_status')}[/yellow]")
                return iter([])  # Return an empty iterator

            return self.api_client.get_batch_results(batch_id)
        except Exception as e:
            self.console.print(f"[red]Error retrieving batch results: {str(e)}[/red]")
            return iter([])  # Return an empty iterator

    def get_batch_status_summary(self, batch_id: str) -> str:
        """
        Provides a summary of the batch status.

        :param batch_id: ID of the batch to summarize
        :return: String summary of batch status
        """
        try:
            details = self.get_batch_details(batch_id)
            status = details.get('processing_status', 'Unknown')
            counts = details.get('request_counts', {})
            total = sum(counts.values())
            summary = f"Batch {batch_id} - Status: {status}\n"
            summary += f"Total requests: {total}\n"
            for key, value in counts.items():
                percentage = (value / total) * 100 if total > 0 else 0
                summary += f"{key.capitalize()}: {value} ({percentage:.1f}%)\n"
            return summary
        except Exception as e:
            return f"Error getting batch summary: {str(e)}"

    def monitor_batch_progress(self, batch_id: str) -> None:
        """
        Monitors and displays the progress of a batch.

        :param batch_id: ID of the batch to monitor
        """
        try:
            with self.console.status(f"[bold green]Monitoring batch {batch_id}...") as status:
                while True:
                    details = self.get_batch_details(batch_id)
                    status.update(self.get_batch_status_summary(batch_id))
                    if details.get('processing_status') in ['ended', 'canceled']:
                        break
                    time.sleep(5)  # Wait for 5 seconds before checking again
            self.console.print(f"[bold]Final status for batch {batch_id}:[/bold]")
            self.console.print(self.get_batch_status_summary(batch_id))
        except Exception as e:
            self.console.print(f"[red]Error monitoring batch: {str(e)}[/red]")
