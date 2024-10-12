from typing import List, Dict, Any
import json
import os
import csv
from rich.console import Console
from rich.table import Table

class BatchDrafter:
    def __init__(self, config_manager=None):
        self.current_batch: List[Dict] = []
        self.config_manager = config_manager
        self.console = Console()

    def import_batch(self, file_path: str, model: str, max_tokens: int) -> None:
        """
        Imports prompts from a file to create a new batch.
        Supports .txt, .json, .jsonl, and .csv file formats.
        """
        file_name, file_extension = os.path.splitext(file_path)
        
        if file_extension.lower() == '.txt':
            self._import_from_txt(file_path, model, max_tokens)
        elif file_extension.lower() in ['.json', '.jsonl']:
            self._import_from_json(file_path, model, max_tokens)
        elif file_extension.lower() == '.csv':
            self._import_from_csv(file_path, model, max_tokens)
        else:
            self.console.print(f"[red]Unsupported file format: {file_extension}[/red]")

    def _import_from_csv(self, file_path: str, model: str, max_tokens: int) -> None:
        """
        Imports prompts from a CSV file, supporting multiline prompts.
        Expected CSV format: custom_id,content
        """
        try:
            with open(file_path, 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                headers = next(csv_reader)  # Read the header row
                
                if len(headers) != 2 or headers[0].lower() != 'custom_id' or headers[1].lower() != 'content':
                    raise ValueError("CSV file must have 'custom_id' and 'content' columns")

                for row in csv_reader:
                    if len(row) == 2:
                        custom_id, content = row
                        content = content.strip()
                        if content:
                            self.add_message(custom_id, model, max_tokens, content)
                    else:
                        self.console.print(f"[yellow]Skipping invalid row: {row}[/yellow]")

            self.console.print(f"[green]Successfully imported prompts from {file_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error importing from CSV file: {str(e)}[/red]")

    def _import_from_txt(self, file_path: str, model: str, max_tokens: int) -> None:
        """
        Imports prompts from a text file, using line numbers as part of the custom_id.
        """
        try:
            with open(file_path, 'r') as file:
                for line_number, content in enumerate(file, 1):
                    content = content.strip()
                    if content:
                        custom_id = f"{os.path.basename(file_path)}_{line_number}"
                        self.add_message(custom_id, model, max_tokens, content)
            self.console.print(f"[green]Successfully imported prompts from {file_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error importing from text file: {str(e)}[/red]")

    def _import_from_json(self, file_path: str, model: str, max_tokens: int) -> None:
        """
        Imports prompts from a JSON or JSONL file.
        """
        try:
            with open(file_path, 'r') as file:
                if file_path.lower().endswith('.jsonl'):
                    for line_number, line in enumerate(file, 1):
                        data = json.loads(line)
                        self._process_json_entry(data, file_path, line_number, model, max_tokens)
                else:
                    data = json.load(file)
                    if isinstance(data, list):
                        for index, entry in enumerate(data):
                            self._process_json_entry(entry, file_path, index + 1, model, max_tokens)
                    elif isinstance(data, dict):
                        self._process_json_entry(data, file_path, 1, model, max_tokens)
            self.console.print(f"[green]Successfully imported prompts from {file_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error importing from JSON/JSONL file: {str(e)}[/red]")

    def _process_json_entry(self, entry: Dict, file_path: str, index: int, model: str, max_tokens: int) -> None:
        """
        Processes a single JSON entry and adds it to the batch.
        """
        custom_id = entry.get('custom_id', f"{os.path.basename(file_path)}_{index}")
        content = entry.get('content', '')
        if content:
            self.add_message(custom_id, model, max_tokens, content)            

    def add_message(self, custom_id: str, model: str, max_tokens: int, content: str) -> None:
        """
        Adds a new message to the batch.
        """
        message = {
            "custom_id": custom_id,
            "params": {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": content}
                ]
            }
        }
        self.current_batch.append(message)
        self.console.print(f"[green]Message added to batch with custom_id: {custom_id}[/green]")

    def create_new_batch(self) -> None:
        """Initializes a new batch."""
        self.current_batch = []
        self.console.print("[green]New batch created.[/green]")

    def add_message(self, custom_id: str, model: str, max_tokens: int, content: str) -> None:
        """
        Adds a new message to the batch.
        """
        message = {
            "custom_id": custom_id,
            "params": {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": content}
                ]
            },
            #"file_path": file_path
        }
        self.current_batch.append(message)
        self.console.print(f"[green]Message added to batch with custom_id: {custom_id}[/green]")

    def edit_message(self, index: int, field: str, value: Any) -> None:
        """
        Edits a specific field of a message in the batch.
        """
        if 0 <= index < len(self.current_batch):
            message = self.current_batch[index]
            if field in ['custom_id', 'file_path']:
                message[field] = value
            elif field in ['model', 'max_tokens']:
                message['params'][field] = value
            elif field == 'content':
                message['params']['messages'][0]['content'] = value
            else:
                self.console.print(f"[red]Invalid field: {field}[/red]")
                return
            self.console.print(f"[green]Message at index {index} updated.[/green]")
        else:
            self.console.print("[red]Invalid message index.[/red]")

    def remove_message(self, index: int) -> None:
        """
        Removes a message from the batch.
        """
        if 0 <= index < len(self.current_batch):
            removed = self.current_batch.pop(index)
            self.console.print(f"[green]Message removed from batch: {removed['custom_id']}[/green]")
        else:
            self.console.print("[red]Invalid message index.[/red]")

    def view_batch(self) -> Table:
        """Returns a formatted table representation of the current batch."""
        table = Table(title="Current Batch")
        table.add_column("Index", style="cyan")
        table.add_column("Custom ID", style="magenta")
        table.add_column("Model", style="green")
        table.add_column("Max Tokens", style="yellow")
        table.add_column("Content", style="blue")
        #table.add_column("File Path", style="red")

        for index, message in enumerate(self.current_batch):
            table.add_row(
                str(index),
                message['custom_id'],
                message['params']['model'],
                str(message['params']['max_tokens']),
                message['params']['messages'][0]['content'][:50] + "...",
                #message['file_path']
            )

        return table

    def get_batch(self) -> List[Dict]:
        """Returns the current batch."""
        return self.current_batch
