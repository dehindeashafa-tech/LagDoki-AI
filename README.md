# 🏥 LagDoki-AI
> **Multilingual Clinical Safety & Voice Triage Engine**

LagDoki-AI is an automated clinical safety and triage engine designed to lower healthcare barriers in low-resource and multilingual environments—with a special focus on the Nigerian healthcare ecosystem. It empowers patients to communicate symptoms via **voice notes or text** in **Nigerian Pidgin, English, or local languages** directly through a Web Dashboard or zero-cost **WhatsApp automation**.

---

## 📌 Project Overview

Accessing immediate clinical guidance during medical distress remains a challenge across emerging markets. **LagDoki-AI** bridges this gap by offering a 24/7 intelligent triage interface capable of processing spoken or written symptom descriptions.

The system transcribes incoming audio in real time using high-performance speech-to-text models (**Groq Whisper**), parses symptom severity through rule-based clinical red-flag algorithms, and returns immediate triage directives—ranging from self-care recommendations to critical emergency hospital dispatch alerts.

---

## 🎯 Objective

1. **Voice-First Healthcare Access:** Enable semi-literate or non-English-literate users to record native spoken audio (Pidgin/English) without filling out complex text forms.
2. **Zero-Cost WhatsApp Integration:** Leverage open-source browser automation (`whatsapp-web.js`) to provide unlimited, cost-free triage through a familiar, widely accessible messaging platform.
3. **Emergency Red-Flag Detection:** Rapidly screen symptoms for critical cardiovascular, respiratory, and neurological emergencies to prioritize high-risk patients.
4. **Seamless Dockerized Infrastructure:** Deliver a modular, containerized microservices stack ready for immediate local development or cloud deployment.

---

## 🏗️ Structure and Architecture

### Directory Layout

```text
LagDoki-AI/
├── docker-compose.yml               # Multi-container orchestration
├── .env.example                     # Environment variable template
├── README.md                        # Documentation
├── services/
│   ├── api/                         # FastAPI Python Backend
│   │   ├── Dockerfile
│   │   ├── main.py                  # API entry point & router mounting
│   │   ├── requirements.txt         # Python dependencies
│   │   └── routers/
│   │       ├── triage.py            # Web UI voice & text triage routes
│   │       └── whatsapp.py          # WhatsApp webhook handler
│   └── whatsapp_bot/                # Node.js WhatsApp Automation Bridge
│       ├── Dockerfile               # Headless Chromium & Node environment
│       ├── index.js                 # whatsapp-web.js client script
│       └── package.json             # Node dependencies
└── frontend/                        # Next.js Web Dashboard
    ├── package.json
    └── src/                         # Next.js UI components & pages


## System Architecture & Data Flow


 ┌────────────────────────────────────────────────────────────────────────┐
 │                              PATIENT INTERFACES                        │
 └────────────────────────────────────────────────────────────────────────┘
            │                                             │
   (Web Dashboard Voice/Text)                    (WhatsApp Voice/Text)
            │                                             │
            ▼                                             ▼
 ┌───────────────────────┐                    ┌─────────────────────────┐
 │ Next.js UI (Port 3000)│                    │ whatsapp_bot Container  │
 └───────────────────────┘                    │ (whatsapp-web.js Node)  │
            │                                 └─────────────────────────┘
            │                                             │
            └──────────────────────┬──────────────────────┘
                                   │ HTTP Multipart / JSON
                                   ▼
                   ┌───────────────────────────────┐
                   │   lagdoki_backend Container   │
                   │   (FastAPI REST Engine)       │
                   └───────────────────────────────┘
                                   │
                                   ├──► [Groq API] Whisper-Large-v3
                                   │    (Ultra-fast Speech-to-Text)
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │    Clinical Safety Engine     │
                   │   (Red Flag Keyword Parser)   │
                   └───────────────────────────────┘
                                   │
            ┌──────────────────────┴──────────────────────┐
            ▼                                             ▼
 🚨 EMERGENCY ALERT RED                           🟢 NON-EMERGENCY
 Proceed to ER immediately                        Rest, hydrate & monitor

## ⚙️ Set-up Environment
Prerequisites
Docker Desktop installed and running.
# Groq Cloud API Key
GROQ_API_KEY=gsk_your_actual_groq_api_key_here

# FastAPI Backend Configuration
PYTHONPATH=/app:/app/services/api
# FastAPI Backend Configuration
PYTHONPATH=/app:/app/services/api
🚀 Set-up
StepsStep 1: Clone the Repository
Bash
git clone [https://github.com/your-username/LagDoki-AI.git](https://github.com/your-username/LagDoki-AI.git)
cd LagDoki-AI
Step 2: Configure Environment
Variables Copy .env.example to .env and add your Groq API Key:
Bash
cp .env.example .env
Step 3: Build and Launch Docker Containers
Run Docker Compose to build and start the backend and whatsapp_bot services:
Bash
docker compose up --build -d
Step 4: Link Your WhatsApp Account
Attach to the WhatsApp bot container logs to scan the generated QR code:
Bash
docker logs -f lagdoki_whatsapp_bot
Open WhatsApp on your smartphone.
Go to Settings
Linked Device
Link a Device.
Scan the terminal QR code.Once you see ✅ WhatsApp Web Client is connected and active!, your bot is live!Step
5: (Optional) Launch Frontend Web Dashboard
Navigate to the frontend directory and start the Next.js development server:
Bashcd frontend
npm install
npm run dev
Open http://localhost:3000 in Google Chrome or Edge to test web voice recording.
🔮 Future Improvements[ ] LLaMA 3 Clinical Conversational Dialogue:
Integrate Groq-hosted LLaMA 3 models into triage.py and whatsapp.py to support dynamic multi-turn medical assessments in Pidgin.
[ ] Expanded Local Emergency Lexicon: Add indigenous language emergency red flag dictionaries (Yoruba, Hausa, Igbo) for enhanced sensitivity.[ ] Interactive Severity Gauge: Implement a 5-tier clinical severity score visualizer (ESI Level 1–5) on the web dashboard.[ ] Database & Patient History: Integrate PostgreSQL/MongoDB with Redis caching to retain encrypted multi-turn session history per patient phone number.[ ] Health Ministry Dashboard Integration: Export aggregated, anonymized regional symptom trends to primary healthcare dashboards for epidemiological decision-making.
