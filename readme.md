# Message Batch Terminal App

## Overview

The Message Batch Terminal App is a powerful command-line interface for managing and monitoring message batches using the Anthropic API. This application allows users to draft, submit, monitor, and manage batches of messages for processing through various Claude models.

## Features

- Draft message batches with custom configurations
- Submit batches to the Anthropic API
- Monitor the status of submitted batches
- Retrieve and display batch results
- Cancel ongoing batches
- List all batches in the workspace
- Interactive terminal user interface with rich formatting

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jonpojonpo/batchforge.git
   cd batchforge
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root directory.
2. Add your Anthropic API key to the `.env` file:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

To run the application, use the following command:

```
python main.py
```

Once launched, you'll be presented with a main menu offering the following options:

1. Draft a new batch
2. Submit a batch
3. Monitor batch status
4. View batch results
5. List all batches
6. Cancel a batch
q. Quit

Use the number keys to select an option, and follow the on-screen prompts to perform various actions.

## Drafting a Batch

When drafting a batch, you'll be asked to provide the following information for each message:

- Custom ID
- Model name (e.g., "claude-3-haiku-20240307")
- Maximum number of tokens
- Message content

You can add multiple messages to a batch, edit existing messages, or remove messages before submitting.

## Monitoring Batches

The application provides real-time updates on the status of your batches. You can view the progress of all active batches, including the number of processed, succeeded, errored, and canceled requests.

## Viewing Results

Once a batch is completed, you can view the results, which will show the output for each message in the batch. The results include the custom ID, status, and a preview of the content.

## Cancelling Batches

If needed, you can cancel an ongoing batch. The application will attempt to cancel the batch and provide feedback on the success of the cancellation.

## Error Handling

The application includes robust error handling to manage API errors, network issues, and invalid user inputs. Error messages will be displayed in red to alert you of any problems.

## Customization

You can customize the application by modifying the configuration files in the `config` directory. This allows you to set default models, token limits, and other parameters.

## Contributing

Contributions to the Message Batch Terminal App are welcome! Please feel free to submit pull requests, create issues, or suggest improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have any questions, please open an issue in the GitHub repository.

