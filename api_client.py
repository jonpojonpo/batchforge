import requests
from typing import List, Dict, Iterator
import json

class APIClient:
    BASE_URL = "https://api.anthropic.com/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "message-batches-2024-09-24",
            "content-type": "application/json"
        }

    def create_batch(self, batch: List[Dict]) -> Dict:
        """
        Sends a request to create a new batch.

        :param batch: List of message dictionaries to be submitted
        :return: API response containing the created batch details
        """
        url = f"{self.BASE_URL}/messages/batches"
        payload = {"requests": batch}
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def get_batch_status(self, batch_id: str) -> Dict:
        """
        Retrieves the status of a batch.

        :param batch_id: ID of the batch to get status for
        :return: API response containing the batch status
        """
        url = f"{self.BASE_URL}/messages/batches/{batch_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_batch_results(self, batch_id: str) -> Iterator[Dict]:
        """
        Retrieves and yields batch results.

        :param batch_id: ID of the batch to get results for
        :return: Iterator of batch result dictionaries
        """
        url = f"{self.BASE_URL}/messages/batches/{batch_id}/results"
        response = requests.get(url, headers=self.headers, stream=True)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield json.loads(line)

    def list_batches(self, limit: int = 20) -> List[Dict]:
        """
        Lists all batches in the workspace.

        :param limit: Number of batches to retrieve (default 20)
        :return: List of batch dictionaries
        """
        url = f"{self.BASE_URL}/messages/batches"
        params = {"limit": limit}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])

    def cancel_batch(self, batch_id: str) -> Dict:
        """
        Cancels a batch.

        :param batch_id: ID of the batch to cancel
        :return: API response containing the canceled batch details
        """
        url = f"{self.BASE_URL}/messages/batches/{batch_id}/cancel"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

class APIError(Exception):
    """Custom exception for API-related errors."""
    pass