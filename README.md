# SAHAYA (सहाय / சகாயா)
### Multilingual Cooperative Governance & Legal Assistance Chatbot
**Core Doctrine: NO EVIDENCE → NO ANSWER → HUMAN ESCALATION**

SAHAYA is a public-service civic-tech web application designed for cooperative members, farmers, and citizens across India. Unlike generic conversational chatbots that risk hallucinating legal, financial, or regulatory claims, SAHAYA enforces a **Citation-Gated Retrieval-Augmented Generation (RAG)** pipeline backed by an automated **Confidence-Triggered Human Escalation Gate**.

---

## 1. Problem Statement

In rural cooperative governance, Primary Agricultural Credit Societies (PACS), and agricultural welfare schemes (like the Pradhan Mantri Fasal Bima Yojana — PMFBY), providing incorrect legal or procedural information can cause severe financial loss, forfeiture of insurance claims, or loss of voting rights.

Generic LLMs frequently hallucinate deadlines, eligibility amounts, and statutory procedures. **SAHAYA solves this by enforcing a zero-unsupported-claims principle:**
- An answer is generated **strictly from verified gazettes, operational guidelines, and by-laws**.
- Every single factual assertion is stamped with verifiable **document, page, and section citations**.
- If the retrieved evidence is insufficient, outdated, or falls below confidence thresholds (0.75 for general queries, 0.85 for sensitive legal/claim matters), the generated answer is **strictly discarded**, and an official **Grievance Ticket (`GRV-2026-XXXXX`)** is automatically dispatched to the human Cooperative Officer queue.

---

## 2. Safety Architecture & Grounding Formula

### Verification Gate Pipeline
```
Citizen Query (EN / TA / HI)
       │
       ▼
Language Detection & Pivot Translation (EN)
       │
       ▼
Domain Intent Classification & Sensitivity Check
(PMFBY_CLAIM, COOPERATIVE_BYLAW, SCHEME_ELIGIBILITY, GRIEVANCE)
       │
       ▼
Hybrid Retrieval Engine
┌───────────────────────┐   ┌──────────────────────────┐
│  Sparse BM25 Keyword  │ + │ Dense Semantic Embeddings│
│ (Clauses, Terms, Sec) │   │ (Conceptual Alignment)   │
└───────────────────────┘   └──────────────────────────┘
       │
       ▼
Reciprocal Rank Fusion (RRF) & Relevance Scoring
       │
       ▼
Strict Citation-Gated Generation (JSON Contract)
       │
       ▼
Citation Verification & Groundedness Gate
Confidence = 0.4 * Retrieval + 0.4 * Entailment + 0.2 * Source Quality
       │
       ├─── Confidence >= Threshold (75% / 85%) ──► Verified Answer + Source Citations
       │
       └─── Confidence < Threshold (or Insufficient Evidence)
                   │
                   ▼
       Answer Discarded ──► Auto-create Grievance Ticket (GRV-2026-XXXXX)
                                 │
                                 ▼
                     Officer Portal Dashboard Queue
```

### Mathematical Formula
$$\text{final\_confidence} = 0.4 \times \text{retrieval\_score} + 0.4 \times \text{entailment\_score} + 0.2 \times \text{source\_quality\_score}$$

- **`retrieval\_score`**: Hybrid score combining BM25 keyword matching and dense vector similarity.
- **`entailment\_score`**: NLI groundedness layer verifying that numeric entities, deadlines (e.g., "72 hours", "Rs. 100", "4.0%"), and legal terms in the answer exist in the retrieved evidence.
- **`source\_quality\_score`**: Verified gazette integrity and presence of structured page and section metadata.

---

## 3. Tech Stack

- **Frontend**:
  - React 18
  - Vite 6
  - Tailwind CSS (Government public-service design palette)
  - Lucide React icons
  - Web Speech API integration with backend voice fallback
- **Backend**:
  - Python 3.13 / FastAPI
  - Uvicorn ASGI
  - SQLAlchemy ORM with SQLite database
  - Pydantic v2
  - PyMuPDF (fitz) for PDF text extraction & page-number preservation
- **AI / RAG**:
  - BM25 Okapi (`rank-bm25`) for exact legal keywords, sections, and scheme codes
  - Dense semantic retrieval with cosine similarity over document embeddings
  - Configurable LLM Provider: Google Gemini (`gemini-1.5-flash`), OpenAI, or local Ollama (`qwen2.5-7b`, `llama-3-8b`)
  - Grounded deterministic synthesis fallback when API key is not supplied (out-of-the-box demo mode)
  - Multilingual pivot translation (English, Tamil, Hindi)

---

## 4. Project Structure

```
sahaya/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── components/
│       │   ├── Header.jsx                 # Public-service header, language switcher, trust badge
│       │   ├── TrustBanner.jsx            # "No Evidence -> No Answer" architecture doctrine
│       │   ├── ChatInterface.jsx          # Interactive chat, mic input, demo questions
│       │   ├── MessageBubble.jsx          # Verified answer & confidence gauge
│       │   ├── CitationCard.jsx           # Verifiable citation cards with excerpt viewer
│       │   ├── EscalationCard.jsx         # "Verified Info Not Found" card with Ticket ID
│       │   ├── OfficerDashboard.jsx       # Officer portal with KPI metrics & grievance table
│       │   ├── TicketDetailModal.jsx      # Inspection drawer with candidate chunks & action logs
│       │   └── DocumentManager.jsx        # PDF/TXT repository & re-indexer
│       └── services/
│           ├── api.js                     # API client
│           └── localFaq.js                # Offline kiosk cache
├── backend/
│   ├── run.py                             # Server launch script
│   ├── test_api.py                        # Automated end-to-end API test suite
│   ├── requirements.txt
│   ├── .env.example
│   ├── .env
│   ├── app/
│   │   ├── main.py                        # FastAPI application & route registration
│   │   ├── config.py                      # Thresholds and settings
│   │   ├── database.py                    # SQLite engine & session maker
│   │   ├── models/
│   │   │   ├── ticket.py                  # Grievance ticket model
│   │   │   └── document.py                # Document metadata model
│   │   ├── routes/
│   │   │   ├── chat.py                    # POST /api/chat (Citation-Gated RAG)
│   │   │   ├── tickets.py                 # GET/PATCH /api/tickets
│   │   │   ├── documents.py               # GET/POST /api/documents
│   │   │   ├── stats.py                   # GET /api/stats (KPI metrics)
│   │   │   ├── voice.py                   # POST /api/voice (Speech-to-text)
│   │   │   └── faq.py                     # GET /api/faq (Offline kiosk cache)
│   │   ├── services/
│   │   │   ├── ingestion.py               # PDF/TXT parser & page-aware chunker
│   │   │   ├── retrieval.py               # Hybrid BM25 + dense semantic search
│   │   │   ├── rag.py                     # Strict system prompt with JSON contract
│   │   │   ├── verification.py            # Safety verification gate & confidence scorer
│   │   │   ├── translation.py             # Multilingual detection & pivot translator
│   │   │   └── intent.py                  # Cooperative intent classifier
│   │   └── utils/
│   │       └── seed_data.py               # Ingestion runner & demo seed data
│   └── data/
│       ├── documents/                     # Verified government documents (PDF / TXT)
│       │   ├── PMFBY_Operational_Guidelines_2024.txt
│       │   ├── Model_Cooperative_Societies_Bylaws.txt
│       │   ├── PACS_Grievance_Redressal_Protocol.txt
│       │   └── Kisan_Credit_Scheme_Norms.txt
│       └── index/
│           └── chunks.json                # Serialized chunk store
└── README.md
```

---

## 5. Getting Started & Installation

### Prerequisites
- **Python 3.10+** (Python 3.13 tested and verified)
- **Node.js 18+** (Node.js 24 tested and verified)

### 1. Backend Setup
```bash
cd backend

# Install Python requirements
python -m pip install -r requirements.txt

# Initialize database and index demo documents
python run.py --seed

# Start backend server
python run.py --host 127.0.0.1 --port 8000
```
Backend API will be accessible at: `http://127.0.0.1:8000`  
Swagger API Documentation: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend web application will be accessible at: `http://localhost:5173`

---

## 6. Where to Add Your Real Government PDFs and API Key

### Adding Real Government PDFs
1. Place your official `.pdf` or `.txt` files directly into:
   ```
   backend/data/documents/
   ```
   *(Example: `PMFBY_Circular_2026.pdf`, `TamilNadu_Cooperative_Act_1983.pdf`)*
2. Either click the **"Re-index Knowledge Base"** button in the **Verified Documents** tab of the web application, or run:
   ```bash
   python backend/run.py --seed
   ```
   The ingestion engine will automatically extract text page-by-page, chunk it, and rebuild the BM25 and vector indices.

### Adding Your LLM API Key (Optional)
Open `backend/.env` and configure your API key:
```env
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash
```
*Note: SAHAYA includes an out-of-the-box Grounded Synthesis Engine so the application works immediately for demo purposes even without an external API key!*

---

## 7. Interactive Demo Questions

Try these prompts to test the core features:

| Prompt | Expected Result | Why? |
|---|---|---|
| **"What is the PMFBY claim settlement procedure and 72-hour deadline?"** | ✓ **VERIFIED ANSWER** (94% Confidence)<br>Citations: *PMFBY Guidelines (Page 42, Section 11)* | Exact grounding found in operational guidelines. |
| **"Who is eligible to become an ordinary member of a Primary Agricultural Credit Society (PACS)?"** | ✓ **VERIFIED ANSWER** (92% Confidence)<br>Citations: *PACS Model By-laws (Page 12, Rule 14)* | Fully supported by cooperative statutory rules. |
| **"What is the net interest rate for prompt repayment under Kisan Credit Card?"** | ✓ **VERIFIED ANSWER** (91% Confidence)<br>Citations: *KCC Norms (Page 16, Norm 12)* | Supported by RBI/NABARD Interest Subvention norms. |
| **"Can I get a loan waiver of 10 lakh rupees without land records under government scheme?"** | ⚠️ **VERIFIED INFORMATION NOT FOUND**<br>Generated ticket: `GRV-2026-XXXXX` | Answer discarded. Query escalated to Officer Portal. |

---

## 8. Officer Grievance Portal (`/officer`)

When queries are escalated:
1. Navigate to the **Officer Portal** tab in the navigation bar.
2. View real-time KPI cards: **Total Grievances**, **Pending Action**, **Under Review**, **Escalated**, and **Resolved**.
3. Click **"Inspect"** on any ticket to view:
   - The citizen's verbatim question and detected language.
   - The exact confidence score and verification gate rejection reason.
   - The candidate chunks retrieved from the knowledge base.
   - Officer action buttons: `[Mark Resolved]`, `[Request Info]`, `[Escalate to District Registrar]`.
   - Action log / remarks saved directly to the SQLite database.

---

## 9. Offline / Kiosk Mode

In rural PACS kiosks with unreliable internet connectivity:
1. Toggle the **"Online Mode / Offline Kiosk"** button in the header.
2. Frequently Asked Questions (FAQ) are served directly from a high-speed local static cache.
3. If an uncached or complex legal question is asked, the system **refuses to fabricate an answer** and displays an offline guidance prompt directing the farmer to the on-duty society secretary.

---

## 10. Automated Test Suite

To verify all 7 API endpoints:
```bash
python backend/test_api.py
```
Outputs:
```
--- 1. Testing /health --- 200 OK
--- 2. Testing /stats --- 200 OK
--- 3. Testing /documents --- 200 OK (4 documents, 17 chunks)
--- 4. Testing Supported Query --- 200 OK (Status: SUPPORTED, Confidence: 94%)
--- 5. Testing Unsupported Query --- 200 OK (Status: ESCALATED, Ticket ID: GRV-2026-XXXXX)
--- 6. Verifying Created Grievance Ticket --- 200 OK
--- 7. Testing Officer Status Resolution --- 200 OK (Status: UNDER_REVIEW)
=======================================================
ALL 7 API VERIFICATION TESTS PASSED SUCCESSFULLY!
=======================================================
```
