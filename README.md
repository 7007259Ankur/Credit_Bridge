# CreditBridge

Explainable multi-agent credit scoring platform. Scores applicants 300–850 using 7 specialized AI agents, with full per-agent explanation and consent-driven data collection.

## Quick Start

### 1. Prerequisites
- Docker Desktop
- Node.js 20+ + pnpm
- Python 3.11+ + uv
- Ollama (optional, for LLM features)

### 2. Start infrastructure
```bash
cd Credit_Bridge
cp .env.example .env
docker compose up -d
```

### 3. Backend
```bash
cd backend
uv pip install -e .
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
# API at http://localhost:8000/docs
```

### 4. Frontend
```bash
cd frontend
pnpm install
pnpm dev
# UI at http://localhost:5173
```

## Demo Accounts
| Role | Email | Password |
|------|-------|----------|
| Applicant | applicant@demo.com | Demo1234! |
| Bank Officer | bank@demo.com | Demo1234! |
| Admin | admin@demo.com | Demo1234! |

## Architecture

```
Frontend (React+Vite :5173)
    ↓ REST
Backend (FastAPI :8000)
    ↓ Celery task
Neuro SAN Agent Network  ← credit_scoring_network.hocon
  CreditCoordinator (frontman / LLM via Ollama)
    ├── CashflowAgent   → CashflowTool   (CodedTool)
    ├── PhoneBillAgent  → PhoneBillTool  (CodedTool)
    ├── EcommerceAgent  → EcommerceTool  (CodedTool)
    ├── PsychometricAgent → PsychometricTool (CodedTool)
    ├── MerchantAgent   → MerchantTool   (CodedTool)
    └── GeolocationAgent → GeolocationTool (CodedTool)
    └── RiskSynthesizerTool → final 300–850 score
    ↓
PostgreSQL + Redis
```

## Neuro SAN Integration

The agent layer is built on [Neuro SAN](https://github.com/cognizant-ai-lab/neuro-san) — a data-driven multi-agent framework from Cognizant AI Labs.

Key files:
- `agents/neuro_san/credit_scoring_network.hocon` — declarative HOCON config defining the full agent network topology
- `agents/neuro_san/coded_tools/` — 7 deterministic Python CodedTools (one per agent + risk synthesizer)
- `agents/coordinator.py` — loads the HOCON network, invokes via Neuro SAN, falls back to direct execution

How it works:
1. Neuro SAN reads the HOCON file and spins up the `CreditCoordinator` frontman agent (powered by Ollama/llama3 locally)
2. The coordinator fans out to 6 specialist LLM agents via AAOSA protocol
3. Each specialist calls its CodedTool (pure Python, no LLM) for deterministic scoring
4. `RiskSynthesizerTool` aggregates all sub-scores → final 300–850 score
5. Sensitive data (user_id, run_id, agent results) flows through `sly_data` — never exposed to the LLM

If Ollama is not running, the coordinator automatically falls back to running the CodedTools directly in parallel.

## Agents & Weights
| Agent | Default Weight |
|-------|---------------|
| Cashflow | 25% |
| Phone Bill | 15% |
| E-commerce | 15% |
| Psychometric | 15% |
| Merchant | 10% |
| Geolocation | 10% |
| Risk Synthesizer | 10% |

Weights are configurable from the Admin Panel.

## Score Formula
```
final_score = 300 + (weighted_avg_sub_score / 100) × 550
```
