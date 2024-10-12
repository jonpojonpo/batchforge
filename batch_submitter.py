from typing import List, Dict
from rich.console import Console
from rich.panel import Panel

class BatchSubmitter:
    def __init__(self, api_client):
        self.api_client = api_client
        self.console = Console()

    def submit_batch(self, batch: List[Dict]) -> str:
        """
        Submits a batch and returns the batch ID.

        :param batch: List of message dictionaries to be submitted
        :return: Batch ID returned by the API
        """
        try:
            self.console.print(Panel("Submitting batch to API...", style="blue"))
            response = self.api_client.create_batch(batch)
            batch_id = response.get('id')
            if batch_id:
                self.console.print(Panel(f"Batch submitted successfully. Batch ID: {batch_id}", style="green"))
                return batch_id
            else:
                raise ValueError("API response did not contain a batch ID")
        except Exception as e:
            self.handle_submission_error(e)
            return ""

    def handle_submission_error(self, error: Exception) -> None:
        """
        Handles any errors during submission.

        :param error: The exception that was raised during submission
        """
        error_message = str(error)
        self.console.print(Panel(f"Error submitting batch: {error_message}", style="bold red"))

        if isinstance(error, ValueError):
            self.console.print("The API response was not in the expected format. Please check the API documentation.")
        elif isinstance(error, ConnectionError):
            self.console.print("There was a problem connecting to the API. Please check your internet connection and try again.")
        elif isinstance(error, TimeoutError):
            self.console.print("The API request timed out. The server might be overloaded, please try again later.")
        else:
            self.console.print("An unexpected error occurred. Please contact support if this problem persists.")

        # Log the error for debugging purposes
        # In a real-world application, you might want to use a proper logging system
        self.console.print(f"[dim]Debug information: {repr(error)}[/dim]")

        # Optionally, you could implement retry logic here
        # self.retry_submission(batch)

    # Additional helper methods could be added here, such as:
    # def retry_submission(self, batch: List[Dict], max_retries: int = 3) -> str:
    #     ...

    # def validate_batch(self, batch: List[Dict]) -> bool:
    #     ...
