#!/usr/bin/env python3
"""
Status Check Script for CD (Continuous Deployment) Pipeline
Reads status_check.txt from remote GitHub repository and validates if CD is approved
Polls continuously every 5 seconds until decision is made
"""
import sys
import os
import time
import urllib.request
import urllib.error
import json
import base64

def get_github_file_content(owner, repo, file_path, branch="main"):
    """
    Fetch file content directly from GitHub repository
    Args:
        owner: Repository owner
        repo: Repository name  
        file_path: Path to the file in repository
        branch: Branch name (default: main)
    Returns:
        File content as string or None if error
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    
    try:
        print(f"🌐 Fetching {file_path} from GitHub repository for CD approval...")
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            
            # Decode base64 content
            content = base64.b64decode(data['content']).decode('utf-8').strip()
            return content
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ File {file_path} not found in repository")
        else:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"❌ Error fetching file from GitHub: {str(e)}")
        return None

def check_cd_status_once():
    """
    Check CD status from remote status_check.txt file
    Returns: 'approved', 'declined', 'waiting', or 'error'
    """
    # Get repository information from environment variables (GitHub Actions provides these)
    owner = os.environ.get('GITHUB_REPOSITORY_OWNER', 'datasinner')
    repo_full = os.environ.get('GITHUB_REPOSITORY', 'datasinner/AWS-CI-CD-Project')
    repo = repo_full.split('/')[-1] if '/' in repo_full else 'AWS-CI-CD-Project'
    branch = os.environ.get('GITHUB_REF_NAME', 'test')
    
    print(f"📍 Repository: {owner}/{repo} (branch: {branch})")
    
    # Fetch file content from GitHub
    content = get_github_file_content(owner, repo, "status_check.txt", branch)
    
    if content is None:
        return 'error'
    
    content_lower = content.lower()
    print(f"📄 Remote status file content: '{content}'")
    
    # Check if content matches CD approval text
    if content_lower == "cd approved":
        print("✅ CD Status: APPROVED - Proceeding with deployment...")
        return 'approved'
    elif content_lower == "cd declined":
        print("❌ CD Status: DECLINED - Stopping deployment...")
        return 'declined'
    else:
        print(f"⏳ Waiting for CD decision... Found: '{content}'")
        print("Expected: 'cd approved' or 'cd declined' (case insensitive)")
        return 'waiting'

def poll_for_cd_decision(max_attempts=None):
    """
    Continuously poll status_check.txt every 5 seconds until CD decision is made
    Args:
        max_attempts: Maximum number of attempts (None for unlimited)
    Returns:
        True if approved, False if declined or error
    """
    print("🔄 Starting continuous polling for CD approval (every 5 seconds)...")
    print("💡 Update status_check.txt with 'cd approved' or 'cd declined' to proceed")
    
    attempt = 0
    start_time = time.time()
    
    while True:
        attempt += 1
        elapsed_time = time.time() - start_time
        
        print(f"\n🔍 CD Check #{attempt} (elapsed: {elapsed_time:.1f}s)")
        
        status = check_cd_status_once()
        
        if status == 'approved':
            print("🎉 CD Decision received: APPROVED!")
            return True
        elif status == 'declined':
            print("🛑 CD Decision received: DECLINED!")
            return False
        elif status == 'error':
            print("💥 Error occurred during CD status check!")
            return False
        elif status == 'waiting':
            # Check max attempts if specified
            if max_attempts and attempt >= max_attempts:
                print(f"⏰ Maximum attempts ({max_attempts}) reached. Stopping...")
                return False
            
            print("⏰ Waiting 5 seconds before next CD check...")
            time.sleep(5)
        
        # Safety check to prevent infinite loops (24 hours max)
        if elapsed_time > 86400:  # 24 hours
            print("🛑 Maximum polling time (24 hours) reached. Stopping...")
            return False

def main():
    """Main function to run the CD status check with continuous polling"""
    print("🔍 Starting CD (Continuous Deployment) Status Check with Continuous Polling...")
    
    # Start polling for CD decision
    if poll_for_cd_decision():
        print("🚀 CD Status check passed! Continuing with deployment...")
        sys.exit(0)  # Success
    else:
        print("🛑 CD Status check failed! Stopping deployment...")
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
