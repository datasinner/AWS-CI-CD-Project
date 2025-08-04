#!/usr/bin/env python3
"""
Status Check Script for CI/CD Pipeline
Reads status_check.txt and validates if CI is approved
Polls continuously every 5 seconds until decision is made
"""
import sys
import os
import time

def check_ci_status_once():
    """
    Check CI status from status_check.txt file once
    Returns: 'approved', 'declined', 'waiting', or 'error'
    """
    status_file = "status_check.txt"
    
    # Check if status file exists
    if not os.path.exists(status_file):
        print(f"❌ Error: {status_file} not found!")
        print("Please create status_check.txt with 'ci approved' or 'ci declined'")
        return 'error'
    
    try:
        # Read the status file
        with open(status_file, 'r', encoding='utf-8') as file:
            content = file.read().strip().lower()
        
        print(f"📄 Status file content: '{content}'")
        
        # Check if content matches decision text
        if content == "ci approved":
            print("✅ CI Status: APPROVED - Proceeding with build...")
            return 'approved'
        elif content == "ci declined":
            print("❌ CI Status: DECLINED - Stopping pipeline...")
            return 'declined'
        else:
            print(f"⏳ Waiting for decision... Found: '{content}'")
            print("Expected: 'ci approved' or 'ci declined' (case insensitive)")
            return 'waiting'
            
    except Exception as e:
        print(f"❌ Error reading {status_file}: {str(e)}")
        return 'error'

def poll_for_decision(max_attempts=None):
    """
    Continuously poll status_check.txt every 5 seconds until decision is made
    Args:
        max_attempts: Maximum number of attempts (None for unlimited)
    Returns:
        True if approved, False if declined or error
    """
    print("🔄 Starting continuous polling (every 5 seconds)...")
    print("💡 Update status_check.txt with 'ci approved' or 'ci declined' to proceed")
    
    attempt = 0
    start_time = time.time()
    
    while True:
        attempt += 1
        elapsed_time = time.time() - start_time
        
        print(f"\n🔍 Check #{attempt} (elapsed: {elapsed_time:.1f}s)")
        
        status = check_ci_status_once()
        
        if status == 'approved':
            print("🎉 Decision received: APPROVED!")
            return True
        elif status == 'declined':
            print("🛑 Decision received: DECLINED!")
            return False
        elif status == 'error':
            print("💥 Error occurred during status check!")
            return False
        elif status == 'waiting':
            # Check max attempts if specified
            if max_attempts and attempt >= max_attempts:
                print(f"⏰ Maximum attempts ({max_attempts}) reached. Stopping...")
                return False
            
            print("⏰ Waiting 5 seconds before next check...")
            time.sleep(5)
        
        # Safety check to prevent infinite loops (24 hours max)
        if elapsed_time > 86400:  # 24 hours
            print("🛑 Maximum polling time (24 hours) reached. Stopping...")
            return False

def main():
    """Main function to run the status check with continuous polling"""
    print("🔍 Starting CI Status Check with Continuous Polling...")
    
    # Start polling for decision
    if poll_for_decision():
        print("🚀 Status check passed! Continuing with CI/CD pipeline...")
        sys.exit(0)  # Success
    else:
        print("🛑 Status check failed! Stopping CI/CD pipeline...")
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
