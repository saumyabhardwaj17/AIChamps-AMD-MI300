#!/usr/bin/env python3
"""
AI Meeting Scheduler Setup Script
Validates environment and dependencies for the hackathon submission
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_files():
    """Check if required files exist."""
    required_files = [
        "calendar_extractor.py",
        "meeting_scheduler_agent.py", 
        "meeting_utils.py",
        "Submission.ipynb",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ Found: {file}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def check_keys_directory():
    """Check if authentication keys are available."""
    keys_dir = Path("Keys")
    if not keys_dir.exists():
        print("❌ Keys directory not found")
        return False
    
    token_files = list(keys_dir.glob("*.token"))
    if len(token_files) < 3:
        print(f"⚠️  Expected 3 token files, found {len(token_files)}")
        return False
    
    print(f"✅ Found {len(token_files)} authentication tokens")
    for token in token_files:
        print(f"   📄 {token.name}")
    
    return True

def install_requirements():
    """Install required Python packages."""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def validate_imports():
    """Test if all critical imports work."""
    try:
        print("🔍 Validating imports...")
        
        # Test basic imports
        import flask
        import requests
        print("✅ Flask and requests available")
        
        # Test Google Calendar imports
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        print("✅ Google Calendar API available")
        
        # Test our modules
        from calendar_extractor import retrive_calendar_events
        from meeting_utils import process_meeting_request, MeetingScheduler
        print("✅ Custom modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup validation."""
    print("🚀 AI Meeting Scheduler - Setup Validation")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_files),
        ("Authentication Keys", check_keys_directory),
        ("Package Installation", install_requirements),
        ("Import Validation", validate_imports)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔧 {check_name}:")
        if not check_func():
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 Setup validation PASSED!")
        print("✅ Your AI Meeting Scheduler is ready to run")
        print("📝 Next steps:")
        print("   1. Open Submission.ipynb in Jupyter")
        print("   2. Run all cells to start the server")
        print("   3. Test with POST requests to /receive endpoint")
    else:
        print("❌ Setup validation FAILED!")
        print("🔧 Please fix the issues above before proceeding")
    
    return all_passed

if __name__ == "__main__":
    main()
