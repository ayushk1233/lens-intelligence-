# 🧠 PULSE Intelligence Engine
**Project Understanding & Live Status Engine**

An enterprise-grade, asynchronous decision-intelligence layer that converts raw Google Meet transcripts into structured operational memory, mathematically scores project health, and surfaces delivery risks before they happen.

## 📖 Overview

Standard meeting bots generate passive summaries. **PULSE is an active operating system for project management.** It listens to meetings, extracts strict data contracts (promises, blockers, confusion signals), routes them to physical storage, tracks the passage of time, and acts as a ruthless executive auditor to score project health.

### What is the "Pipeline"?

A pipeline is an automated sequence of data processing steps where the output of one step becomes the input for the next. In PULSE, the pipeline flows like this:

1. **Capture (Layer 0):** A Runpod GPU turns meeting audio into a diarized transcript.
2. **Extraction (LENS):** An AI agent converts the text into structured JSON schemas.
3. **Orchestration (NERVE):** A web server physically saves those JSONs to disk.
4. **Aging (CRONS):** Nightly scripts age open blockers by +1 day.
5. **Evaluation (CORE):** An executive AI reads the history and outputs a Health Score out of 100.

## 🏗️ Architecture Stack

PULSE is divided into three highly decoupled operational layers:

### 1. LENS (Live Event & Notes Synthesizer) - The Brain
A deterministic, LangGraph workflow that extracts intelligence using strict Pydantic schemas.

* **Extracts:** Commitments (promises + dates), Blockers (dependencies + severity).
* **Temporal Linking:** Calculates "Delivery Drift" by comparing current dialogue against previous meeting commitments.
* **Behavioral Analytics:** Scores speaker initiative (1-10) and flags "Intern Confusion."
* **Data Compression:** Generates a highly compressed <85 token YAML summary.

### 2. NERVE (Network Event Router & Variable Engine) - The Nervous System
An asynchronous FastAPI orchestration layer.

* **Non-Blocking Webhooks:** Instantly responds `200 OK` to the recording server while handing LLM extraction to background tasks.
* **Intelligent File Router:** Routes data to `data/projects/{id}/warm` (JSON metrics) and `data/projects/{id}/cold` (YAML summaries).
* **Nightly Sweeper:** A simulated cron job that increments `days_open` on unresolved blockers to track aging risks.

### 3. CORE (Continuous Operations & Risk Evaluator) - The Executive
An aggregation agent that reads the entire project history.

* **Context Loader:** Scans the `project_index.json` to compile all past YAMLs and JSONs.
* **Health Scoring:** Applies penalties for drift, aged blockers, and team confusion.
* **Markdown Output:** Generates a brutal, objective executive summary and a 1-100 Project Health Score.

## 📂 Repository Structure

```text
.
├── README.md
├── pyproject.toml
├── requirements.txt
├── deploy/
│   ├── docker/
│   └── k8s/
├── src/
│   ├── core/
│   │   ├── graph.py
│   │   └── prompts.py
│   ├── lens/
│   │   ├── graph.py
│   │   ├── prompts.py
│   │   └── nodes/
│   ├── nerve/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── webhook.py
│   │   ├── crons/
│   │   │   └── nightly_sweeper.py
│   │   └── routers/
│   │       └── file_router.py
│   └── shared/
│       ├── database/
│       ├── schemas/
│       │   ├── core_outputs.py
│       │   └── lens_outputs.py
│       └── utils/
│           └── llm_client.py
└── tests/
    ├── simulate_runpod.py
    ├── test_core_score.py
    ├── test_lens_extraction.py
    └── test_nerve_routing.py
```

## ⚙️ Technical Specifications

* **Language:** Python 3.10+
* **Frameworks:** FastAPI, Uvicorn, LangGraph, LangChain, Pydantic
* **AI Providers:** Primary OpenRouter (`openai/gpt-4o-mini`) via resilient fallback client.
* **Storage Pattern:** Local File System (JSON/YAML) structured by `Project_ID -> WARM/COLD -> Meeting_ID`.

### The Benefits

* **Zero Hallucination Routing:** By forcing the LLM to map names to a biometric `attendees.json`, the AI cannot invent commitments for people who weren't there.
* **Cost Efficiency:** CORE only reads the 85-token COLD summaries instead of 10,000-token raw transcripts, saving massive API costs at scale.
* **Proactive Risk Mitigation:** It mathematically penalizes projects when people say "I'll do it tomorrow" but the task was originally due Tuesday.

## 🚀 How to Run Locally

### 1. Prerequisites & Setup

Ensure you have Python installed, then set up your virtual environment and dependencies:

```bash
# Clone the repo and navigate to the directory
cd pulse-intelligence-engine

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file at the root of the repository and add your API keys:

```env
OPENAI_API_KEY="sk-proj-your-openai-key"
OPENROUTER_API_KEY="sk-or-v1-your-openrouter-key"
```

### 2. Start the NERVE Server

Run the FastAPI orchestration server. Leave this terminal window open.

```bash
uvicorn src.nerve.main:app --reload
```
*(The server will boot up and listen on http://127.0.0.1:8000)*

### 3. Simulate a Meeting (Trigger LENS)

Open a second terminal window, activate your venv, and fire a simulated Runpod payload at the server.

```bash
python tests/simulate_runpod.py
```
*Watch the NERVE server terminal. You will see LENS extract the commitments, calculate the drift, and save the files into the `data/projects/PROJ-Alpha/` directory.*

### 4. Run the Nightly Sweeper (Trigger CRON)

Simulate the passage of time. This script scans the data directory, ages any open blockers by +1 day, and builds the `project_index.json` required by CORE.

```bash
python src/nerve/crons/nightly_sweeper.py
```

### 5. Generate the Final Health Report (Trigger CORE)

Now that the data is extracted and aged, run the CORE agent to evaluate the project.

```bash
export PYTHONPATH=$PYTHONPATH:.
python tests/test_core_score.py
```
*The terminal will output a full Markdown report, complete with the final 1-100 score, a dimension breakdown, and critical risks.*

## 🗺️ Roadmap & Next Steps

* [ ] **Layer 0 Migration:** Transition flat-file JSON/YAML storage into a secure PostgreSQL/SQLAlchemy database to protect biometric data.
* [ ] **Layer 4 Distribution:** Integrate a Slack webhook client to automatically push the CORE Health Report to team channels.
* [ ] **Human-in-the-Loop (HITL):** Build a basic frontend dashboard to manually resolve blockers so the Nightly Sweeper stops aging them.