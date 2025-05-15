import streamlit as st
import google.generativeai as genai
import os
from git import Repo
import subprocess
from pathlib import Path
from datetime import datetime

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyCNX0JbZuCp-c3283WtCDpp5rJ_Q0sPfcs"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

def initialize_git_repo():
    """Initialize Git repository if not already initialized"""
    if not os.path.exists('.git'):
        Repo.init('.')
        st.success("Git repository initialized!")

def execute_git_command(command):
    """Execute Git command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

def get_current_branch():
    """Get the current branch name"""
    try:
        repo = Repo('.')
        return repo.active_branch.name
    except Exception as e:
        return str(e)

def list_branches():
    """List all branches"""
    try:
        repo = Repo('.')
        branches = [branch.name for branch in repo.heads]
        return branches
    except Exception as e:
        return str(e)

def push_to_repo(repo_url):
    """Push directly to the specified repository URL"""
    try:
        # Add all changes
        execute_git_command('git add .')
        
        # Commit changes
        commit_message = "Auto-commit: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_git_command(f'git commit -m "{commit_message}"')
        
        # First, try to add the remote
        execute_git_command(f'git remote add origin {repo_url}')
        
        # Try to push to main branch first
        try:
            result = execute_git_command('git push -u origin main')
            if "error" in result.lower():
                # If main fails, try master branch
                result = execute_git_command('git push -u origin master')
        except:
            # If both main and master fail, try current branch
            current_branch = get_current_branch()
            result = execute_git_command(f'git push -u origin {current_branch}')
        
        # Remove the remote after pushing
        execute_git_command('git remote remove origin')
        
        return f"Successfully pushed changes: {result}"
    except Exception as e:
        # Clean up remote if it exists
        execute_git_command('git remote remove origin')
        return f"Error pushing changes: {str(e)}"

def process_git_request(user_input):
    """Process user input and execute appropriate Git commands"""
    # Get Gemini's interpretation of the Git command
    prompt = f"""Given the following user request about Git operations, determine the exact Git command to execute.
    For Git operations, use these specific commands:
    
    Branch Operations:
    - Create and switch to new branch: git checkout -b <branch_name>
    - Switch to existing branch: git checkout <branch_name>
    - List all branches: git branch
    - Delete branch: git branch -d <branch_name>
    
    Push/Pull Operations:
    - Push to URL: git push <repository_url> HEAD:main
    - Pull from URL: git pull <repository_url>
    
    Commit Operations:
    - Add all files: git add .
    - Add specific file: git add <file_name>
    - Commit with message: git commit -m "<message>"
    - Add and commit in one command: git commit -am "<message>"
    
    Status Operations:
    - Check status: git status
    - View commit history: git log --oneline
    
    User request: {user_input}
    Return only the Git command without any explanation."""
    
    response = model.generate_content(prompt)
    git_command = response.text.strip()
    
    # Execute the Git command
    result = execute_git_command(git_command)
    return result

# Streamlit UI
st.title("🤖 Git Repository Agent with Gemini AI")

# Initialize Git repository
initialize_git_repo()

# Display repository information
col1, col2 = st.columns(2)
with col1:
    current_branch = get_current_branch()
    st.subheader(f"Current Branch: {current_branch}")
    
    # Display all branches
    st.subheader("Available Branches")
    branches = list_branches()
    st.code('\n'.join(branches), language="bash")

with col2:
    # Display current status
    st.subheader("Current Status")
    status = execute_git_command("git status")
    st.code(status, language="bash")

# Quick Push
st.subheader("Quick Push")
repo_url = st.text_input("Enter Repository URL to push:", 
                        placeholder="https://github.com/username/repository.git")

if st.button("Push to Repository"):
    if repo_url:
        with st.spinner("Pushing changes..."):
            result = push_to_repo(repo_url)
            st.code(result, language="bash")
    else:
        st.warning("Please enter a repository URL")

# User input
user_input = st.text_area("What would you like to do with your Git repository?", 
                         placeholder="Example: Push to https://github.com/username/repository.git")

if st.button("Execute"):
    if user_input:
        with st.spinner("Processing your request..."):
            result = process_git_request(user_input)
            st.code(result, language="bash")
            st.rerun()
    else:
        st.warning("Please enter a command or request.")

# Display recent commits
st.subheader("Recent Commits")
commits = execute_git_command("git log --oneline -n 5")
st.code(commits, language="bash")

# Quick Actions
st.subheader("Quick Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("Show All Branches"):
        result = execute_git_command("git branch -a")
        st.code(result, language="bash")

with col2:
    if st.button("Show Status"):
        result = execute_git_command("git status")
        st.code(result, language="bash")
