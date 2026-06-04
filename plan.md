CreditBridge — MVP Master Plan
Multi-Agent Credit Scoring System | Localhost-First | Minimum Cost | Production-Ready Architecture


1. Product Vision
CreditBridge is a modular, explainable, and bias-resilient credit scoring platform built on a 4-layer architecture orchestrated by 9 specialized AI agents. It replaces black-box credit models with a transparent, consent-driven, multi-signal system that scores applicants between 300–850.

Core Value Proposition:

Explainable scores (not a black box)
Consent-first data collection
Multi-signal analysis (bank data, telecom, e-commerce, geolocation, merchant, psychometric)
Built for underbanked and thin-file applicants


2. System Architecture Overview
┌─────────────────────────────────────────────────────────┐

│  Layer 1: Frontend (React + Vite)                        │

│  ├── Applicant Portal  (consent + psychometric form)     │

│  ├── Bank Dashboard    (score view + loan recommendation) │

│  └── Admin Panel       (weight config + analytics)       │

├─────────────────────────────────────────────────────────┤

│  Layer 2: Backend API (FastAPI)                          │

│  ├── Auth Service      (JWT + AES-256)                   │

│  ├── Consent Engine    (per-source consent logging)      │

│  └── Scoring API       (triggers agent pipeline)         │

├─────────────────────────────────────────────────────────┤

│  Layer 3: Multi-Agent Network (Neuro SAN)                │

│  ├── Credit Coordinator   (orchestrates all agents)      │

│  ├── Phone Bill Agent     (payment consistency scoring)  │

│  ├── E-commerce Agent     (purchase behavior analysis)   │

│  ├── Geolocation Agent    (location stability scoring)   │

│  ├── Psychometric Agent   (behavioral analysis)          │

│  ├── Merchant Agent       (business reputation scoring)  │

│  ├── Cashflow Agent       (bank pattern analysis)        │

│  └── Risk Synthesizer     (combines scores → 300–850)    │

├─────────────────────────────────────────────────────────┤

│  Layer 4: Data Storage                                   │

│  ├── PostgreSQL           (users, consents, scores)      │

│  ├── Redis                (session cache, rate limiting) │

│  └── Local File Storage   (documents, mock data CSVs)    │

└─────────────────────────────────────────────────────────┘


3. Tech Stack Selection (Minimum Cost, Localhost-First)
3.1 Frontend
Tool
Choice
Reason
Framework
React 18 + Vite
Fastest DX, zero cost, HMR
Language
TypeScript
Type safety, catches bugs early
Styling
Tailwind CSS
No designer needed, utility-first
UI Components
shadcn/ui
Free, accessible, copy-paste components
State Management
Zustand
Lightweight, no boilerplate
Data Fetching
TanStack Query
Caching, loading states, minimal code
Charts
Recharts
Free, React-native charting
Forms
React Hook Form + Zod
Validation without overhead
Routing
React Router v6
Industry standard

3.2 Backend
Tool
Choice
Reason
Framework
FastAPI (Python)
Auto-docs, async, fast to build
Language
Python 3.11+
AI/ML ecosystem, free
Auth
python-jose + passlib
JWT + bcrypt, zero cost
Encryption
cryptography (AES-256)
Standard library
ORM
SQLAlchemy 2.0 + Alembic
Migrations, type-safe
Validation
Pydantic v2
Built-in to FastAPI
Task Queue
Celery + Redis
Async agent pipeline
Testing
pytest + httpx
Fast, async-compatible

3.3 AI / Agent Layer
Tool
Choice
Reason
LLM
Ollama (llama3 / mistral)
100% local, zero API cost
Agent Framework
LangGraph
Graph-based multi-agent orchestration
Embeddings
sentence-transformers
Local, CPU-compatible
ML Scoring
scikit-learn
Tabular scoring models, lightweight
Data
pandas + numpy
Agent data processing


MVP Cost for AI = $0/month — everything runs on localhost via Ollama
3.4 Data Layer
Tool
Choice
Reason
Primary DB
PostgreSQL 16
Free, robust, JSONB support
Cache
Redis 7
Session management, task broker
Migrations
Alembic
Version-controlled schema
DB Client
DBeaver (GUI)
Free GUI for local dev

3.5 DevOps (Localhost)
Tool
Choice
Reason
Containerization
Docker + Docker Compose
Single command startup
API Docs
FastAPI /docs (Swagger)
Auto-generated, zero cost
Env Management
python-dotenv / .env
Standard practice
Package Manager
uv (Python) + pnpm (Node)
Fastest, modern



4. Design Patterns
4.1 Backend Patterns
Repository Pattern — data access layer abstracted from business logic
Service Layer Pattern — business logic separate from API routes
Dependency Injection — FastAPI's Depends() for clean DI
Command Pattern — each agent action is a discrete command object
Observer Pattern — consent events trigger audit log observers
4.2 Agent Orchestration Pattern
CreditCoordinator (Supervisor Agent)

  │

  ├── Fan-Out: dispatch all 7 sub-agents in parallel

  │     ├── PhoneBillAgent

  │     ├── EcommerceAgent

  │     ├── GeolocationAgent

  │     ├── PsychometricAgent

  │     ├── MerchantAgent

  │     ├── CashflowAgent

  │     └── (each returns a sub-score 0–100 + explanation)

  │

  └── Fan-In: RiskSynthesizer aggregates → final 300–850 score

LangGraph implements this as a directed acyclic graph (DAG) with a supervisor node.
4.3 Frontend Patterns
Feature-Folder Structure — /features/applicant, /features/bank, /features/admin
Container/Presenter Pattern — smart containers fetch data, dumb components just render
Custom Hooks — useScoring(), useConsent(), useAuth()
Error Boundary — global React error boundary with fallback UI
4.4 Security Patterns
Zero-Trust Consent — each data source requires explicit per-user consent
JWT + Refresh Token Rotation — short-lived access tokens (15 min), rotating refresh
AES-256 Encryption at Rest — PII fields encrypted before DB insert
Rate Limiting — Redis-backed sliding window limiter on all endpoints


5. Project Structure
creditbridge/

├── docker-compose.yml

├── .env.example

│

├── frontend/

│   ├── src/

│   │   ├── features/

│   │   │   ├── applicant/     # Consent flow + psychometric form

│   │   │   ├── bank/          # Score dashboard + loan recommendations

│   │   │   └── admin/         # Weight config + analytics

│   │   ├── components/        # Shared UI (shadcn wrappers)

│   │   ├── hooks/             # useAuth, useScoring, useConsent

│   │   ├── lib/               # API client, utils

│   │   └── stores/            # Zustand stores

│   ├── package.json

│   └── vite.config.ts

│

├── backend/

│   ├── app/

│   │   ├── api/               # FastAPI routers

│   │   │   ├── auth.py

│   │   │   ├── consent.py

│   │   │   └── scoring.py

│   │   ├── services/          # Business logic

│   │   │   ├── auth_service.py

│   │   │   ├── consent_service.py

│   │   │   └── scoring_service.py

│   │   ├── repositories/      # DB access layer

│   │   ├── models/            # SQLAlchemy models

│   │   ├── schemas/           # Pydantic schemas

│   │   ├── core/              # Config, security, encryption

│   │   └── main.py

│   ├── alembic/               # DB migrations

│   ├── tests/

│   └── pyproject.toml

│

├── agents/

│   ├── coordinator.py         # CreditCoordinator (LangGraph supervisor)

│   ├── phone_bill_agent.py

│   ├── ecommerce_agent.py

│   ├── geolocation_agent.py

│   ├── psychometric_agent.py

│   ├── merchant_agent.py

│   ├── cashflow_agent.py

│   ├── risk_synthesizer.py

│   └── tools/                 # Shared agent tools

│

└── data/

    └── mock/                  # Mock CSVs for local testing


6. Database Schema (Core Tables)
-- Users (Applicants + Bank Officers + Admins)

users (id, email_encrypted, role, created_at)

-- Consent Records (per-source)

consents (id, user_id, source_type, granted_at, revoked_at)

-- source_type: ENUM('phone', 'ecommerce', 'bank', 'merchant', 'geo', 'psychometric')

-- Scoring Runs

scoring_runs (id, user_id, status, created_at, completed_at)

-- Agent Sub-Scores

agent_scores (id, run_id, agent_name, raw_score, explanation, data_snapshot_jsonb)

-- Final Credit Scores

credit_scores (id, run_id, user_id, final_score, score_band, recommendation, created_at)

-- Audit Log

audit_log (id, user_id, action, metadata_jsonb, timestamp)


7. API Design (Key Endpoints)
POST   /api/auth/register

POST   /api/auth/login

POST   /api/auth/refresh

POST   /api/consent/{source_type}        # Grant consent

DELETE /api/consent/{source_type}        # Revoke consent

GET    /api/consent/status               # All consent statuses

POST   /api/scoring/initiate             # Trigger agent pipeline (async)

GET    /api/scoring/{run_id}/status      # Poll run status

GET    /api/scoring/{run_id}/result      # Get final score + explanations

GET    /api/admin/weights                # Get agent weights

PUT    /api/admin/weights                # Update agent weights

GET    /api/admin/analytics              # Dashboard stats


8. Agent Scoring Logic
Each agent returns a structured result:

{

  "agent": "PhoneBillAgent",

  "sub_score": 78,          # 0–100

  "weight": 0.15,           # configurable from Admin Panel

  "explanation": "12 of 12 months consecutive payment, no late bills",

  "signals": ["payment_consistency", "bill_regularity"],

  "confidence": 0.91

}

Risk Synthesizer formula:

final_score = 300 + (weighted_avg_of_sub_scores / 100) * 550

# Range: 300 (worst) → 850 (best)

Default Weights (Admin-configurable): | Agent | Default Weight | |-------|--------------| | Cashflow Agent | 0.25 | | Phone Bill Agent | 0.15 | | E-commerce Agent | 0.15 | | Psychometric Agent | 0.15 | | Merchant Agent | 0.10 | | Geolocation Agent | 0.10 | | Risk Synthesizer | 0.10 |


9. MVP Feature Scope (Phase 1)
✅ Must Have (MVP)
User registration & JWT auth (3 roles: applicant, bank officer, admin)
Consent flow UI — applicants grant/revoke per-source consent
Psychometric questionnaire (20 questions → Psychometric Agent)
Mock data injection for all 6 agent sources (CSV-based for localhost)
Full agent pipeline execution (all 7 agents + synthesizer)
Score result display with per-agent explanation breakdown
Bank officer dashboard — view applicant score + recommendation
Admin panel — weight configuration per agent
Audit log for all consent and scoring events
🔄 Phase 2 (Post-MVP)
Real data source connectors (bank API, telecom API)
PDF score report generation
Loan product recommendation engine
Re-scoring on consent change
Multi-language support (Hindi + English)
❌ Out of Scope (MVP)
Mobile app
Payment processing
Third-party credit bureau integration
Real-time fraud detection


10. Local Development Setup
Prerequisites
# Required tools

Docker Desktop (includes Docker Compose)

Node.js 20+ + pnpm

Python 3.11+ + uv

Ollama (https://ollama.ai)
One-Command Startup
# Clone and start everything

git clone <repo>

cd creditbridge

cp .env.example .env

# Pull LLM model (one-time, ~4GB)

ollama pull llama3

# Start all services

docker compose up -d        # PostgreSQL + Redis

pnpm install && pnpm dev    # Frontend on :5173

uv run uvicorn app.main:app --reload  # Backend on :8000
docker-compose.yml (Core Services)
version: '3.9'

services:

  postgres:

    image: postgres:16-alpine

    environment:

      POSTGRES_DB: creditbridge

      POSTGRES_USER: cb_user

      POSTGRES_PASSWORD: cb_pass

    ports: ["5432:5432"]

    volumes: [pgdata:/var/lib/postgresql/data]

  redis:

    image: redis:7-alpine

    ports: ["6379:6379"]

  celery_worker:

    build: ./backend

    command: celery -A app.celery worker --loglevel=info

    depends_on: [postgres, redis]

volumes:

  pgdata:


11. Development Phases & Timeline
Phase 0 — Foundation (Week 1)
Docker Compose setup (Postgres + Redis)
FastAPI boilerplate with auth endpoints
React + Vite + Tailwind + shadcn setup
Database schema + Alembic migrations
JWT auth working end-to-end
Phase 1 — Core Flow (Week 2–3)
Consent Engine (backend + frontend UI)
Mock data loading scripts (CSV → DB)
LangGraph agent skeleton (Coordinator + 1 agent)
All 7 agents implemented with mock data
Risk Synthesizer + final score calculation
Scoring API endpoint (async with Celery)
Phase 2 — Dashboards (Week 4)
Applicant Portal (consent flow + score view)
Bank Officer Dashboard (score cards + explanations)
Admin Panel (weight sliders + analytics charts)
Full end-to-end user journey working
Phase 3 — Polish (Week 5)
Error handling + loading states
Audit log UI
Basic test coverage (>60%)
README + API docs
Demo data seeding script


12. Cost Analysis (Localhost MVP)
Item
Cost
LLM (Ollama/local)
$0/month
PostgreSQL (Docker)
$0/month
Redis (Docker)
$0/month
React/Vite/Tailwind
$0/month
FastAPI + Python libs
$0/month
LangGraph
$0/month
Domain (optional)
~$10/year
Total MVP Cost
$0–$10

Cloud Upgrade Path (Post-MVP)
When ready to deploy:

Render.com (backend + DB) — free tier → ~$25/month
Vercel (frontend) — free tier
OpenAI/Anthropic API (replace Ollama) — ~$50–100/month at scale
Total cloud cost at launch — ~$25–125/month


13. Key Engineering Decisions
Decision
Choice
Why Not Alternative
Agents via LangGraph
LangGraph DAG
CrewAI is heavier, harder to debug
Local LLM via Ollama
llama3 local
Avoids $0 → $$$ API surprise costs
FastAPI not Django
FastAPI
Django is overkill for an API-first app
Celery for agents
Celery+Redis
FastAPI BackgroundTasks lacks retry logic
Zustand not Redux
Zustand
90% less boilerplate for same result
shadcn not MUI
shadcn
Full control, no vendor lock-in, free
Postgres not MongoDB
Postgres
ACID compliance critical for financial data



14. Security Checklist (MVP)
All PII fields AES-256 encrypted before DB insert
JWT secret in .env, never hardcoded
CORS restricted to localhost:5173 in dev
Rate limiting on auth endpoints (5 req/min via Redis)
SQL injection prevention via SQLAlchemy ORM (no raw SQL)
Consent revocation immediately blocks agent data access
Audit log is append-only (no UPDATE/DELETE on audit table)
Passwords hashed with bcrypt (min 12 rounds)


15. Success Metrics (MVP Validation)
Metric
Target
Full scoring pipeline end-to-end
< 10 seconds
Score explainability
Per-agent breakdown visible
Consent revocation propagation
Immediate
API response time (non-scoring)
< 200ms
Test coverage
> 60%
Demo-ready
1 complete applicant journey working




CreditBridge MVP Master Plan — v1.0 | Built for localhost-first, zero-cost development

