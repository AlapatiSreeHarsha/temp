import streamlit as st
import google.generativeai as genai
import os
from git import Repo
import subprocess
from pathlib import Path

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

def get_remote_url():
    """Get the remote repository URL"""
    try:
        repo = Repo('.')
        if repo.remotes:
            return repo.remotes.origin.url
        return "No remote repository configured"
    except Exception as e:
        return str(e)

def setup_remote_repo(repo_url):
    """Set up remote repository"""
    try:
        repo = Repo('.')
        if not repo.remotes:
            repo.create_remote('origin', repo_url)
            return True
        return False
    except Exception as e:
        return str(e)

def push_to_remote(branch_name=None, force=False):
    """Push changes to remote repository with proper error handling"""
    try:
        repo = Repo('.')
        
        # Check if remote exists
        if not repo.remotes:
            return "No remote repository configured. Please add a remote repository first."
        
        # Get the current branch if none specified
        if not branch_name:
            branch_name = repo.active_branch.name
        
        # Check if there are changes to commit
        if repo.is_dirty():
            return "You have uncommitted changes. Please commit your changes first."
        
        # Check if there are commits to push
        if not repo.head.is_valid():
            return "No commits to push."
        
        # Prepare push command
        push_command = f"git push origin {branch_name}"
        if force:
            push_command += " --force"
        
        # Execute push
        result = execute_git_command(push_command)
        
        # Check for common push errors
        if "rejected" in result.lower():
            return "Push rejected. You may need to pull changes first or use force push."
        elif "not found" in result.lower():
            return "Remote branch not found. You may need to set the upstream branch."
        
        return result
    except Exception as e:
        return f"Error during push: {str(e)}"

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
    - Push current branch: git push origin <current_branch>
    - Push all branches: git push --all origin
    - Pull latest changes: git pull origin <current_branch>
    - Set upstream branch: git push -u origin <branch_name>
    
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
    # Display remote repository information
    st.subheader("Remote Repository")
    remote_url = get_remote_url()
    st.code(remote_url, language="bash")

# Remote Repository Setup
st.subheader("Remote Repository Setup")
repo_url = st.text_input("Enter Remote Repository URL (if not configured):", 
                        placeholder="https://github.com/username/repository.git")
if st.button("Configure Remote"):
    if repo_url:
        result = setup_remote_repo(repo_url)
        if result is True:
            st.success("Remote repository configured successfully!")
        else:
            st.error(f"Error configuring remote: {result}")
        st.rerun()

# User input
user_input = st.text_area("What would you like to do with your Git repository?", 
                         placeholder="Example: Create a new branch called 'feature' and push it to remote")

if st.button("Execute"):
    if user_input:
        with st.spinner("Processing your request..."):
            result = process_git_request(user_input)
            st.code(result, language="bash")
            st.rerun()
    else:
        st.warning("Please enter a command or request.")

# Display current Git status
st.subheader("Current Repository Status")
status = execute_git_command("git status")
st.code(status, language="bash")

# Display recent commits
st.subheader("Recent Commits")
commits = execute_git_command("git log --oneline -n 5")
st.code(commits, language="bash")

# Quick Actions
st.subheader("Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Push Current Branch"):
        result = push_to_remote()
        st.code(result, language="bash")
        if "Error" not in result and "rejected" not in result:
            st.success("Push successful!")
        st.rerun()

with col2:
    if st.button("Pull Latest Changes"):
        current_branch = get_current_branch()
        result = execute_git_command(f"git pull origin {current_branch}")
        st.code(result, language="bash")
        st.rerun()

with col3:
    if st.button("Show All Branches"):
        result = execute_git_command("git branch -a")
        st.code(result, language="bash")

# Force Push Option
st.subheader("Advanced Push Options")
force_push = st.checkbox("Force Push (Use with caution!)")
if force_push:
    if st.button("Force Push Current Branch"):
        result = push_to_remote(force=True)
        st.code(result, language="bash")
        st.rerun()
