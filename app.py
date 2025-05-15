import streamlit as st
import google.generativeai as genai
import os
from git import Repo
import subprocess
from pathlib import Path
from datetime import datetime
import shutil
import base64

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

def get_remote_branches(repo_url):
    """Get available branches from remote repository"""
    try:
        # Add remote temporarily
        execute_git_command(f'git remote add temp_remote {repo_url}')
        
        # Fetch remote branches
        execute_git_command('git fetch temp_remote')
        
        # Get remote branches
        remote_branches = execute_git_command('git branch -r')
        
        # Remove temporary remote
        execute_git_command('git remote remove temp_remote')
        
        return remote_branches
    except Exception as e:
        return f"Error getting remote branches: {str(e)}"

def save_uploaded_files(uploaded_files):
    """Save uploaded files to the repository"""
    try:
        added_files = []
        status_messages = []
        
        # Initialize repository if needed
        if not os.path.exists('.git'):
            status_messages.append("Initializing Git repository...")
            Repo.init('.')
            status_messages.append("Git repository initialized!")
        
        # Create a temporary directory for uploaded files
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        for uploaded_file in uploaded_files:
            try:
                # Save file to temporary directory
                file_path = os.path.join(temp_dir, uploaded_file.name)
                status_messages.append(f"Saving file: {uploaded_file.name}")
                
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Move file to repository
                target_path = os.path.join('.', uploaded_file.name)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.move(file_path, target_path)
                
                added_files.append(target_path)
                status_messages.append(f"Successfully saved: {uploaded_file.name}")
            except Exception as e:
                status_messages.append(f"Error saving {uploaded_file.name}: {str(e)}")
        
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        # Add all files to git
        if added_files:
            status_messages.append("Adding files to Git...")
            execute_git_command('git add .')
            
            # Commit the changes
            commit_message = f"Added {len(added_files)} new file(s): " + ", ".join([os.path.basename(f) for f in added_files])
            status_messages.append("Committing changes...")
            execute_git_command(f'git commit -m "{commit_message}"')
            
            return True, "\n".join(status_messages + [f"Successfully added and committed: {', '.join([os.path.basename(f) for f in added_files])}"])
        return False, "No files were uploaded"
    except Exception as e:
        return False, f"Error: {str(e)}"

def push_to_github(repo_url, files_to_push=None):
    """Push files to GitHub repository"""
    try:
        status_messages = []
        
        # Initialize repository if needed
        if not os.path.exists('.git'):
            status_messages.append("Initializing Git repository...")
            Repo.init('.')
            status_messages.append("Git repository initialized!")
        
        # Add all changes or specific files
        if files_to_push:
            for file_path in files_to_push:
                status_messages.append(f"Adding file: {file_path}")
                execute_git_command(f'git add "{file_path}"')
        else:
            status_messages.append("Adding all changes...")
            execute_git_command('git add .')
        
        # Commit changes
        commit_message = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        status_messages.append("Committing changes...")
        execute_git_command(f'git commit -m "{commit_message}"')
        
        # Configure remote
        status_messages.append("Configuring remote repository...")
        execute_git_command(f'git remote add origin {repo_url}')
        
        # Try to push to different branches
        try:
            status_messages.append("Pushing to main branch...")
            result = execute_git_command('git push -u origin main')
            if "error" in result.lower():
                status_messages.append("Trying master branch...")
                result = execute_git_command('git push -u origin master')
        except:
            current_branch = get_current_branch()
            status_messages.append(f"Trying current branch: {current_branch}")
            result = execute_git_command(f'git push -u origin {current_branch}')
        
        # Clean up remote
        execute_git_command('git remote remove origin')
        
        return True, "\n".join(status_messages + [f"Successfully pushed changes: {result}"])
    except Exception as e:
        # Clean up remote if it exists
        execute_git_command('git remote remove origin')
        return False, f"Error pushing changes: {str(e)}"

def get_repository_status():
    """Get detailed repository status"""
    try:
        # Get status
        status = execute_git_command("git status")
        
        # Get list of tracked files
        tracked_files = execute_git_command("git ls-files")
        
        # Get list of untracked files
        untracked_files = execute_git_command("git ls-files --others --exclude-standard")
        
        # Get recent commits
        commits = execute_git_command("git log --oneline -n 5")
        
        return {
            "status": status,
            "tracked_files": tracked_files,
            "untracked_files": untracked_files,
            "commits": commits
        }
    except Exception as e:
        return {
            "status": f"Error getting status: {str(e)}",
            "tracked_files": "",
            "untracked_files": "",
            "commits": ""
        }

def display_repository_status():
    """Display current repository status"""
    repo_status = get_repository_status()
    
    # Display current status
    st.subheader("Current Status")
    st.code(repo_status["status"], language="bash")
    
    # Display tracked files
    if repo_status["tracked_files"]:
        st.subheader("Tracked Files")
        st.code(repo_status["tracked_files"], language="bash")
    
    # Display untracked files
    if repo_status["untracked_files"]:
        st.subheader("Untracked Files")
        st.code(repo_status["untracked_files"], language="bash")
    
    # Display recent commits
    st.subheader("Recent Commits")
    st.code(repo_status["commits"], language="bash")

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

# File Upload Section
st.subheader("Upload Files")
uploaded_files = st.file_uploader("Choose files to add to the repository", accept_multiple_files=True)

if uploaded_files:
    if st.button("Add Files to Repository"):
        with st.spinner("Processing files..."):
            success, message = save_uploaded_files(uploaded_files)
            if success:
                st.success(message)
                st.rerun()  # Refresh the page to show updated status
            else:
                st.error(f"Error adding files: {message}")

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
    display_repository_status()

# Quick Push
st.subheader("Quick Push")
repo_url = st.text_input("Enter Repository URL to push:", 
                        placeholder="https://github.com/username/repository.git")

# Show remote branches when URL is entered
if repo_url:
    st.subheader("Remote Repository Information")
    remote_branches = get_remote_branches(repo_url)
    st.code(remote_branches, language="bash")

if st.button("Push to Repository"):
    if repo_url:
        with st.spinner("Pushing changes..."):
            success, message = push_to_github(repo_url)
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()  # Refresh the page to show updated status
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
            st.rerun()  # Refresh the page to show updated status
    else:
        st.warning("Please enter a command or request.")

# Quick Actions
st.subheader("Quick Actions")
col1, col2 = st.columns(2)

with col1:
    if st.button("Show All Branches"):
        result = execute_git_command("git branch -a")
        st.code(result, language="bash")

with col2:
    if st.button("Show Status"):
        display_repository_status()
