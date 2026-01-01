# 🧠 AI-Powered Resume Screener — Worker

**Python + Redis + RQ | Stage 4 (Phase 4–6 Complete)**

This repository contains the **distributed worker system** responsible for all heavy processing in the AI-Powered Resume Screener platform.

The worker is deliberately isolated from the Node.js backend and owns the **entire intelligence pipeline**:

- Resume parsing
- Embedding generation
- Pre-filtering
- Ranking
- Explanation generation
- On-demand deep LLM analysis

The backend (Node) acts only as an **orchestrator** and data exposer.

---

## 🎯 Worker Responsibilities (Non-Negotiable)

The worker:

- Owns **all AI / ML logic**
- Writes deterministic results to MongoDB
- Is idempotent and retry-safe
- Never exposes APIs directly to clients
- Never depends on frontend behavior

The worker does **not**:

- Serve HTTP to users
- Handle authentication
- Own business workflows
- Make UI decisions

---

## 🏗️ Architecture Overview

```
Node Backend
   ↓ (enqueue jobs)
Redis Queue
   ↓
Python RQ Worker
   ↓
MongoDB (ResumeProcessing)
   ↓
Node Callback Handler
```

### Core Design Principles

- ResumeProcessing is the **single source of truth** per resume × job
- Each resume is processed independently
- Failures are isolated to a single resume
- All updates are atomic and idempotent

---

## ⚙️ Tech Stack

- Python 3.10+
- Redis
- RQ (Redis Queue)
- MongoDB (pymongo / motor)
- Gemini API (LLM)
- Local embedding model (MiniLM)

---

## 🧩 Processing Pipeline (Stage 4)

Each resume goes through the following deterministic pipeline:

### 1️⃣ Parsing

- Fetch resume from Cloudinary URL
- Extract structured text
- Normalize resume content

### 2️⃣ Text Engineering

- Build deterministic embedding text
- Normalize job description text

### 3️⃣ Embedding Generation

- Generate resume and job embeddings
- Store embeddings on ResumeProcessing
- Retry-safe and idempotent

### 4️⃣ Pre-Filtering

- Required skills check
- Experience mismatch detection
- Set `preFilter.passed` + rejection reasons

### 5️⃣ Ranking

- Compute cosine similarity
- Apply weighted scoring (skills, experience, etc.)
- Assign `finalScore` and deterministic `rank`

### 6️⃣ Explanation (Phase 5A)

- Generate **non-LLM**, deterministic explanation
- Works for both passed and failed resumes

### 7️⃣ Deep Analysis (Phase 5B – On Demand)

- Triggered only via API
- Single combined Gemini call (parse + analyze)
- JSON-only guarded output
- Stored under `analysis`

---

## 🔄 Job Types Handled

### 🟦 Batch Processing Jobs

- Triggered by `POST /api/v1/batch/create`
- One job per resume
- Queue: `batch-processing`

Payload includes:

- resumeProcessingId
- jobDescriptionId
- resumeUrl

---

### 🟨 Analysis Jobs (On Demand)

- Triggered by `POST /api/v1/processing/:resumeProcessingId/analyze`
- Queue: `analysis-processing`
- Completely isolated from batch flow

---

## 🔁 Retry & Idempotency Model

### Retry Strategy

- Exponential backoff
- Redis ZSET–based retry scheduler
- Configurable retry limits

### Idempotency Guarantees

- ResumeProcessing guards prevent duplicate work
- Embeddings and analysis do not rerun if completed
- `batchAccounted` prevents double-counting

---

## 🧾 Data Written by Worker

Worker updates **only** `ResumeProcessing` fields:

- embeddings
- preFilter
- passFail
- finalScore
- rank
- explanation
- analysisStatus
- analysis
- timestamps

The worker **never** updates Job or Batch documents directly.

---

## 🚦 Error Handling

- Resume-level failures are captured
- Errors stored on ResumeProcessing
- Failed resumes do not block batches
- Node callback updates batch/job counters

---

## 🔐 Security & Safety

- No secrets logged
- LLM responses stripped of markdown fences
- JSON-only parsing guards
- Timezone-aware UTC timestamps

---

## 🧪 Testing Status

- End-to-end tested with:

  - Large batches
  - Multiple workers
  - Forced failures
  - Retry exhaustion

- Deterministic ranking verified

- Analysis idempotency verified

---

## 📌 Current Status

✅ Stage 4 Phase 4–6 complete
✅ Worker logic frozen
✅ Backend consumes worker output only
⏸ Phase 8–11 deferred (cost controls, observability, hardening)

---

## 🔮 Future Work (Deferred)

- Cost telemetry hooks
- Worker-level metrics export
- GPU-backed embeddings
- Multi-language resume support

---

## 👨‍💻 Ownership

This worker is part of the **AI-Powered Resume Screener** project.

Owner: **Shekh Aalim**
