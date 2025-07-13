#!/usr/bin/env python3
"""
Quick Test Script for AI Meeting Scheduler
Tests core functionality without requiring LLM server
"""

import json
import sys
import os
from datetime import datetime, timedelta

def test_calendar_extractor():
    """Test calendar extractor module."""
    try:
        from calendar_extractor import retrive_calendar_events
        print("✅ Calendar extractor imported successfully")
        return True
    except Exception as e:
        print(f"❌ Calendar extractor error: {e}")
        return False

def test_meeting_utils():
    """Test meeting utilities."""
    try:
        from meeting_utils import MeetingScheduler, process_meeting_request
        
        scheduler = MeetingScheduler()
        print("✅ Meeting scheduler initialized")
        
        # Test email parsing
        test_email = "Hi team, let's meet on Thursday for 30 minutes to discuss the project."
        current_time = datetime.now().isoformat()
        
        result = scheduler.parse_email_content(test_email, current_time)
        print(f"✅ Email parsing works: Duration={result['duration_minutes']}min")
        
        return True
    except Exception as e:
        print(f"❌ Meeting utils error: {e}")
        return False

def test_sample_data():
    """Test with sample JSON data."""
    try:
        # Load sample request
        with open("1_Input_Request.json", "r") as f:
            sample_request = json.load(f)
        
        print("✅ Sample data loaded")
        print(f"   From: {sample_request['From']}")
        print(f"   Subject: {sample_request['Subject']}")
        print(f"   Attendees: {len(sample_request['Attendees'])}")
        
        return True
    except Exception as e:
        print(f"❌ Sample data error: {e}")
        return False

def test_flask_setup():
    """Test Flask module availability."""
    try:
        import flask
        from flask import Flask, request, jsonify
        print("✅ Flask modules available")
        return True
    except Exception as e:
        print(f"❌ Flask error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 AI Meeting Scheduler - Quick Test")
    print("=" * 40)
    
    tests = [
        ("Calendar Extractor", test_calendar_extractor),
        ("Meeting Utils", test_meeting_utils), 
        ("Sample Data", test_sample_data),
        ("Flask Setup", test_flask_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All core tests PASSED!")
        print("✅ Your system is ready for the meeting scheduler")
    else:
        print("⚠️  Some tests failed, but core functionality may still work")
    
    print(f"\n📝 Next steps:")
    print("1. Open Submission.ipynb in Jupyter Notebook")
    print("2. Run all cells to start the Flask server")
    print("3. Test the /receive endpoint with sample data")
    
    return passed == total

if __name__ == "__main__":
    main()
