# 🧠 AI Meeting Scheduler – IIT-B Hackathon Submission  
**An Autonomous Scheduling Assistant Powered by LLMs & Google Calendar Integration**

---

## 🚀 Overview  
The **AI Meeting Scheduler** is an intelligent, end-to-end system that autonomously schedules meetings from email requests. It combines the power of **Large Language Models (LLMs)** and the **Google Calendar API** to extract key meeting details, resolve conflicts, and propose optimal time slots—**minimizing human coordination effort**.

---

## 🧩 Key Features  
- 🔍 **Natural Language Understanding**: Extracts date, time, duration from emails (e.g., “Thursday at 2 PM”)  
- 📅 **Google Calendar Integration**: Checks live availability of multiple attendees  
- 🧠 **LLM Agent + Rule-Based Fallback**: Reliable extraction even under model failure  
- ⏱️ **Timezone & Format Handling**: Supports IST, UTC, ISO 8601, DD-MM-YYYY  
- ✅ **JSON Format Compliance**: Exact output format as per specification  
- 🪵 **Comprehensive Logging**: Full visibility across all pipeline stages  

---

## 🛠️ Tech Stack  

| Component         | Technology               |
|------------------|--------------------------|
| Web Backend       | Flask (Python)           |
| AI Layer          | Qwen3-30B-A3B via `pydantic-ai` |
| Calendar API      | Google Calendar API v3   |
| Auth              | OAuth2 with token files  |
| Timezone Handling | `pytz`, `datetime`       |

---

## 🔄 System Architecture  
**Input Email ➝ LLM/Rule Engine ➝ Conflict Detection ➝ Google Calendar Check ➝ JSON Response**

- 📩 `Submission.ipynb`: Flask web server & input handling  
- 🤖 `meeting_scheduler_agent.py`: LLM-powered meeting detail extractor  
- ⚙️ `meeting_utils.py`: Core scheduling logic & slot scoring  
- 📅 `calendar_extractor.py`: Google Calendar integration & conflict detection  

---

## 📊 Performance  

- ⏱️ **Response Time**: ~5s (LLM), ~1s (Rule-based)  
- 🧪 **Testing**: Unit, Integration & System-level  
- 🌐 **Scalability**: Multi-user calendar access & concurrent request-ready  

---

## ✅ Demo-Ready Scenarios  
1. **“30-min meeting this Thursday at 2 PM”** → Scheduled with availability check  
2. **“1-hour review tomorrow afternoon”** → Parsed & matched to next-day PM slot  
3. **Conflict scenario** → Detected & resolved via optimal slot search  

---

## 📌 Highlights  
- 🤖 LLM + rule-based fallback = **robust hybrid AI system**  
- 📐 Schema-first design for **exact JSON output compliance**  
- 🔄 Real-time **Google Calendar integration**  
- 🎯 Fully functional and **demo-ready**  

---

*Built with ❤️ for the IIT-B Hackathon – Showcasing the future of autonomous productivity tools.*
