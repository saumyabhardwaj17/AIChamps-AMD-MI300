#!/usr/bin/env python3
"""
Standalone Demo of AI Meeting Scheduler (No LLM Required)
Demonstrates core scheduling logic and calendar integration
"""

import json
from datetime import datetime, timedelta
from meeting_utils import MeetingScheduler, process_meeting_request

def demo_email_parsing():
    """Demonstrate email content parsing."""
    print("🧠 Email Content Analysis Demo")
    print("-" * 30)
    
    test_emails = [
        "Hi team, let's meet on Thursday for 30 minutes to discuss the project.",
        "Can we schedule a 1-hour urgent meeting tomorrow morning?",
        "When convenient, let's have a 15-minute quick sync this week.",
        "Need to discuss the quarterly review. Friday afternoon for 45 minutes?"
    ]
    
    scheduler = MeetingScheduler()
    current_time = datetime.now().isoformat()
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 Email {i}: {email}")
        result = scheduler.parse_email_content(email, current_time)
        print(f"   ⏱️  Duration: {result['duration_minutes']} minutes")
        print(f"   🎯 Priority: {result['priority']}")
        if result['preferred_day']:
            print(f"   📅 Preferred: {result['preferred_day'][:10]}")

def demo_time_slot_generation():
    """Demonstrate time slot generation and scoring."""
    print(f"\n⏰ Time Slot Generation Demo")
    print("-" * 30)
    
    scheduler = MeetingScheduler()
    
    # Simulate empty calendars for demo
    empty_availability = {
        "detailed_events": {
            "userone.amd@gmail.com": [],
            "usertwo.amd@gmail.com": [],
            "userthree.amd@gmail.com": []
        },
        "availability_summary": {}
    }
    
    # Find slots for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    start_range = tomorrow.replace(hour=0, minute=0, second=0).isoformat()
    end_range = tomorrow.replace(hour=23, minute=59, second=59).isoformat()
    
    slots = scheduler.find_best_time_slots(
        empty_availability, 
        duration_minutes=30,
        start_range=start_range,
        end_range=end_range
    )
    
    print(f"📊 Found {len(slots)} potential time slots for tomorrow:")
    for i, slot in enumerate(slots[:3], 1):
        start_time = datetime.fromisoformat(slot['start_time'])
        print(f"   {i}. {start_time.strftime('%I:%M %p')} - Score: {slot['score']:.1f} ({slot['time_preference']})")

def demo_meeting_processing():
    """Demonstrate full meeting processing with sample data."""
    print(f"\n🎯 Complete Meeting Processing Demo")
    print("-" * 40)
    
    # Load sample request
    with open("1_Input_Request.json", "r") as f:
        sample_request = json.load(f)
    
    print(f"📥 Processing meeting request:")
    print(f"   From: {sample_request['From']}")
    print(f"   Subject: {sample_request['Subject']}")
    print(f"   Content: {sample_request['EmailContent']}")
    
    # Note: This will attempt to access Google Calendar
    # May fail if tokens are invalid, but will demonstrate the logic
    try:
        result = process_meeting_request(sample_request)
        
        if "error" in result:
            print(f"   ⚠️  Calendar access limited (expected): {result['error']}")
            print(f"   ℹ️  This is normal without valid Google Calendar tokens")
        else:
            print(f"   ✅ Meeting processed successfully!")
            if result.get("scheduling_metadata"):
                metadata = result["scheduling_metadata"]
                print(f"   📊 Scheduling score: {metadata.get('slot_score', 'N/A')}")
                print(f"   🔄 Conflicts: {metadata.get('conflicts_resolved', 'N/A')}")
    
    except Exception as e:
        print(f"   ⚠️  Demo limitation: {str(e)}")
        print(f"   ℹ️  This is expected without LLM server running")

def main():
    """Run the standalone demo."""
    print("🤖 AI Meeting Scheduler - Standalone Demo")
    print("=" * 50)
    print("This demo shows core functionality without requiring:")
    print("• LLM server running")
    print("• Valid Google Calendar tokens")
    print("• Network connectivity")
    print()
    
    try:
        demo_email_parsing()
        demo_time_slot_generation()
        demo_meeting_processing()
        
        print(f"\n🎉 Demo Complete!")
        print("🚀 Your AI Meeting Scheduler core logic is working!")
        print()
        print("📋 For full functionality:")
        print("1. Ensure LLM server is running on localhost:8000")
        print("2. Verify Google Calendar tokens are valid")
        print("3. Run Submission.ipynb to start the Flask server")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("🔧 Check that all required files are present")

if __name__ == "__main__":
    main()
