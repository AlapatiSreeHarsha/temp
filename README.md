# Git Repository Agent with Gemini AI

This Streamlit application integrates with Google's Gemini AI to provide an intelligent Git repository management interface. The agent can understand natural language commands and execute appropriate Git operations.

## Features

- Natural language processing of Git commands using Gemini AI
- Automatic Git repository initialization
- Real-time repository status display
- Recent commits history
- Interactive command execution

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

## Usage

1. Open the application in your web browser
2. Enter your Git command in natural language in the text area
3. Click "Execute" to process your request
4. View the results and repository status below

## Example Commands

- "Add all files and commit with message 'Initial commit'"
- "Create a new branch called 'feature' and switch to it"
- "Push all changes to the remote repository"
- "Show me the difference between current and last commit"

## Security Note

The application uses a Gemini API key for AI processing. Make sure to keep your API key secure and never share it publicly. 