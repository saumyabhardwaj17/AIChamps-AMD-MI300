import os
import json
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from pydantic_ai import Agent, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from calendar_extractor import retrive_calendar_events
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class TimeSlot(BaseModel):
    start: str
    end: str
    available: bool

class MeetingRequest(BaseModel):
    attendees: List[str]
    duration_minutes: int
    preferred_day: Optional[str] = None
    start_range: str
    end_range: str
    subject: str

class ScheduledMeeting(BaseModel):
    start_time: str
    end_time: str
    attendees: List[str]
    subject: str
    status: str
    conflict_resolution: Optional[str] = None

@Tool
def get_current_datetime() -> str:
    """Get the current date and time in ISO format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@Tool
def extract_meeting_details(email_content: str, current_time: str) -> Dict[str, Any]:
    """Extract meeting details from email content including timing, duration, and context."""
    # This will be enhanced by LLM to parse natural language
    return {
        "parsed_content": email_content,
        "current_time": current_time,
        "extraction_status": "success"
    }

@Tool
def get_user_calendar_events(user_email: str, start_time: str, end_time: str) -> List[Dict[str, Any]]:
    """Retrieve calendar events for a specific user within the given time range."""
    try:
        events = retrive_calendar_events(user_email, start_time, end_time)
        return events
    except Exception as e:
        return {"error": f"Failed to retrieve calendar for {user_email}: {str(e)}"}

@Tool
def get_all_attendees_availability(attendees: List[str], start_time: str, end_time: str) -> Dict[str, List[Dict[str, Any]]]:
    """Get calendar events for all meeting attendees to check availability."""
    all_events = {}
    for attendee in attendees:
        try:
            events = retrive_calendar_events(attendee, start_time, end_time)
            all_events[attendee] = events
        except Exception as e:
            all_events[attendee] = {"error": f"Could not fetch calendar: {str(e)}"}
    return all_events

@Tool
def find_optimal_time_slot(attendees_events: Dict[str, List[Dict]], duration_minutes: int, 
                          start_range: str, end_range: str, business_hours_only: bool = True) -> Dict[str, Any]:
    """Find the optimal time slot when all attendees are available."""
    from datetime import datetime, timedelta
    import pytz
    
    # Parse time range
    start_dt = datetime.fromisoformat(start_range.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_range.replace('Z', '+00:00'))
    
    # Generate time slots (15-minute intervals during business hours)
    time_slots = []
    current = start_dt.replace(hour=9, minute=0, second=0, microsecond=0)  # Start at 9 AM
    day_end = start_dt.replace(hour=18, minute=0, second=0, microsecond=0)  # End at 6 PM
    
    while current <= end_dt:
        if current.hour >= 9 and current.hour < 18:  # Business hours
            slot_end = current + timedelta(minutes=duration_minutes)
            if slot_end.hour <= 18:  # Ensure meeting ends within business hours
                time_slots.append({
                    "start": current.isoformat(),
                    "end": slot_end.isoformat()
                })
        current += timedelta(minutes=15)  # 15-minute intervals
        if current.hour >= 18:  # Move to next day
            current = current.replace(hour=9, minute=0) + timedelta(days=1)
    
    # Check availability for each slot
    available_slots = []
    for slot in time_slots:
        slot_start = datetime.fromisoformat(slot["start"])
        slot_end = datetime.fromisoformat(slot["end"])
        
        # Check if all attendees are free
        all_free = True
        conflicts = []
        
        for attendee, events in attendees_events.items():
            if isinstance(events, dict) and "error" in events:
                continue  # Skip if calendar couldn't be fetched
                
            for event in events:
                event_start = datetime.fromisoformat(event["StartTime"])
                event_end = datetime.fromisoformat(event["EndTime"])
                
                # Check for overlap
                if (slot_start < event_end and slot_end > event_start):
                    all_free = False
                    conflicts.append({
                        "attendee": attendee,
                        "conflicting_event": event["Summary"],
                        "event_time": f"{event['StartTime']} - {event['EndTime']}"
                    })
                    break
        
        if all_free:
            available_slots.append({
                "start_time": slot["start"],
                "end_time": slot["end"],
                "confidence": "high"
            })
        
        # If we found a good slot, return it
        if len(available_slots) >= 3:  # Return top 3 options
            break
    
    return {
        "available_slots": available_slots[:3],
        "total_slots_checked": len(time_slots),
        "conflicts_found": len([s for s in time_slots if s not in [a for a in available_slots]])
    }

@Tool
def create_calendar_event(organizer_email: str, attendees: List[str], start_time: str, 
                         end_time: str, subject: str, description: str = "") -> Dict[str, Any]:
    """Create a calendar event for all attendees."""
    try:
        # Use organizer's credentials to create the event
        token_path = os.path.join("Keys", organizer_email.split("@")[0] + ".token")
        user_creds = Credentials.from_authorized_user_file(token_path)
        calendar_service = build("calendar", "v3", credentials=user_creds)
        
        event = {
            'summary': subject,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': [{'email': email} for email in attendees],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        
        created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()
        return {
            "status": "success",
            "event_id": created_event.get('id'),
            "event_link": created_event.get('htmlLink'),
            "created_at": created_event.get('created')
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@Tool 
def resolve_scheduling_conflicts(conflicts: List[Dict], meeting_priority: str = "high") -> Dict[str, Any]:
    """Analyze conflicts and suggest resolution strategies."""
    resolution_strategies = []
    
    for conflict in conflicts:
        if "1:1" in conflict.get("conflicting_event", "").lower():
            resolution_strategies.append({
                "conflict": conflict,
                "suggestion": "Request to reschedule 1:1 meeting as group meeting has higher priority",
                "action": "send_reschedule_request"
            })
        elif "optional" in conflict.get("conflicting_event", "").lower():
            resolution_strategies.append({
                "conflict": conflict,
                "suggestion": "Attendee can skip optional meeting",
                "action": "mark_as_resolved"
            })
        else:
            resolution_strategies.append({
                "conflict": conflict,
                "suggestion": "Find alternative time slot or negotiate priority",
                "action": "find_alternative"
            })
    
    return {
        "resolution_strategies": resolution_strategies,
        "auto_resolvable": len([s for s in resolution_strategies if s["action"] != "find_alternative"]),
        "requires_human_intervention": len([s for s in resolution_strategies if s["action"] == "find_alternative"])
    }

# Initialize the LLM model
BASE_URL = "http://localhost:8000/v1"
os.environ["BASE_URL"] = BASE_URL
os.environ["OPENAI_API_KEY"] = "abc-123"

agent_model = OpenAIModel(
    'Qwen3-30B-A3B',
    provider=OpenAIProvider(
        base_url=os.environ["BASE_URL"], 
        api_key=os.environ["OPENAI_API_KEY"]
    ),
)

# Create the meeting scheduler agent
meeting_scheduler_agent = Agent(
    model=agent_model,
    tools=[
        get_current_datetime,
        extract_meeting_details,
        get_user_calendar_events,
        get_all_attendees_availability,
        find_optimal_time_slot,
        create_calendar_event,
        resolve_scheduling_conflicts
    ],
    system_prompt=(
        "You are an AI Meeting Scheduler Assistant. Your primary goal is to autonomously schedule meetings with minimal human intervention.\n\n"
        "CORE CAPABILITIES:\n"
        "1. Parse natural language meeting requests from emails\n"
        "2. Extract meeting details (attendees, duration, preferred time)\n"
        "3. Check calendar availability for all attendees\n"
        "4. Find optimal meeting times avoiding conflicts\n"
        "5. Create calendar events automatically\n"
        "6. Resolve scheduling conflicts intelligently\n\n"
        "SCHEDULING RULES:\n"
        "- Business hours: 9 AM to 6 PM IST\n"
        "- Minimum meeting duration: 15 minutes\n"
        "- Default duration: 30 minutes if not specified\n"
        "- Prefer morning slots (9-12 PM) for important meetings\n"
        "- Avoid lunch hours (12-1 PM) when possible\n"
        "- Buffer 15 minutes between back-to-back meetings\n\n"
        "CONFLICT RESOLUTION:\n"
        "- Prioritize team meetings over 1:1s\n"
        "- Suggest rescheduling optional meetings\n"
        "- Propose alternative times for conflicts\n"
        "- Auto-resolve when possible, escalate when needed\n\n"
        "RESPONSE FORMAT:\n"
        "Always provide structured responses with:\n"
        "- Meeting details extracted\n"
        "- Availability analysis\n"
        "- Recommended time slots\n"
        "- Conflict resolution if any\n"
        "- Final scheduling decision\n\n"
        "Be proactive, accurate, and user-friendly in your responses."
    )
)

async def schedule_meeting_async(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main async function to handle meeting scheduling requests."""
    try:
        async with meeting_scheduler_agent.run_mcp_servers():
            # Create a comprehensive prompt with all the request data
            prompt = f"""
            I need to schedule a meeting based on this request:
            
            Request ID: {request_data.get('Request_id')}
            From: {request_data.get('From')}
            Attendees: {request_data.get('Attendees')}
            Subject: {request_data.get('Subject')}
            Email Content: {request_data.get('EmailContent')}
            Requested Start: {request_data.get('Start')}
            Requested End: {request_data.get('End')}
            Duration: {request_data.get('Duration_mins', 30)} minutes
            Location: {request_data.get('Location')}
            
            Please:
            1. Extract meeting details from the email content
            2. Get availability for all attendees
            3. Find the best time slot
            4. Handle any conflicts
            5. Provide the final meeting schedule
            
            Return a comprehensive response with the optimal meeting time.
            """
            
            result = await meeting_scheduler_agent.run(prompt)
            return {"status": "success", "response": result.output}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def schedule_meeting(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for the async meeting scheduling function."""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(schedule_meeting_async(request_data))
        loop.close()
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}
