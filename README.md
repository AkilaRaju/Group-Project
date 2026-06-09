# 🎫 Ticket-to-FAQ Pipeline

An AI-powered Streamlit application that automatically converts closed support tickets into a structured, searchable FAQ knowledge base using ML clustering and the Google Gemini API.

---

## 📌 Overview

Support teams handle repetitive issues daily. This tool mines closed tickets, groups them by topic using unsupervised machine learning (TF-IDF + KMeans), generates FAQ drafts via Gemini AI, and routes them through an admin review workflow before publishing to a customer-facing knowledge base.

---

## 🗂️ Project Structure

```
FinalTicketFAQ/
├── app.py                        # Main entry point & multipage navigation
├── requirements.txt              # Python dependencies
├── tickets.db                    # SQLite database (auto-created)
├── tickets.sql                   # DB schema for tickets table
├── faq_drafts.sql                # DB schema for FAQ drafts table
├── published_faqs.sql            # DB schema for published FAQs table
├── .env                          # Environment variables (not committed)
├── .env.example                  # Example env config
├── .streamlit/
│   └── config.toml               # Streamlit configuration
├── static/
│   └── style.css                 # Custom dark-mode CSS
├── backend/
│   ├── db.py                     # SQLite CRUD helpers
│   ├── data_loader.py            # Load tickets from CSV into DB
│   ├── gemini_client.py          # Gemini API wrapper (with local fallback)
│   ├── processing.py             # TF-IDF vectorization & KMeans clustering
│   └── init_db.py                # Database initialization script
└── pages/
    ├── dashboard.py              # KPI metrics & pipeline analytics
    ├── customer_portal.py        # Ticket submission form
    ├── support_agent_panel.py    # Agent ticket resolution panel
    ├── closed_tickets.py         # View & manage closed tickets
    ├── clusters.py               # Visualize ML-generated clusters
    ├── faq_drafts.py             # Review AI-generated FAQ drafts
    ├── admin_review.py           # Admin approval/rejection workflow
    └── published_faqs.py         # Public-facing knowledge base
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd FinalTicketFAQ
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN_PASSWORD=your_admin_password
TICKETS_CSV_PATH=/path/to/your/closed_tickets.csv
DB_PATH=tickets.db          # optional, defaults to tickets.db
```

> **Note:** If `GEMINI_API_KEY` is not set or invalid, the app automatically falls back to a local rule-based FAQ generator.

### 4. Initialize the database

```bash
python backend/init_db.py
```

### 5. Load tickets from CSV

Your CSV must contain these columns: `ticket_id`, `issue`, `resolution`, `status`.

```bash
python backend/data_loader.py
```

### 6. Run the app

```bash
streamlit run app.py
```

---

## 🧭 Navigation & Pages

| Page | Description |
|---|---|
| 🏠 **Dashboard** | KPI cards (total tickets, clusters, drafts, published FAQs), pipeline workflow diagram, cluster distribution & top issues charts |
| 👤 **Customer Portal** | Form for customers to submit new support tickets |
| 🎧 **Support Panel** | Agent view to pick open tickets, enter resolutions, and mark them as closed |
| 🗄️ **Closed Tickets** | Browse and filter all closed tickets stored in the database |
| 🕸️ **Clusters** | Visualize ML-generated ticket clusters with topic labels |
| 📝 **FAQ Drafts** | View AI-generated FAQ drafts, edit questions/answers before review |
| 🛡️ **Admin Review** | Approve or reject FAQ drafts (password protected) |
| 📚 **Published FAQs** | Customer-facing knowledge base of all approved FAQs |

---

## 🔄 Pipeline Workflow

```
Customer Portal  →  Support Agent Resolution  →  Closed Ticket Database
       ↓
ML Clustering (TF-IDF + KMeans, scikit-learn)
       ↓
AI FAQ Generation (Google Gemini / local fallback)
       ↓
Admin Review (approve / reject / edit)
       ↓
Published Knowledge Base
```

---

## 🤖 ML & AI Details

### Clustering (`backend/processing.py`)
- Combines `issue` + `resolution` text per ticket
- Cleans and vectorizes using **TF-IDF** (`scikit-learn`)
- Selects optimal cluster count (k) automatically using **silhouette score** over a range of 2–10
- Runs **KMeans** with the best k to group similar tickets

### FAQ Generation (`backend/gemini_client.py`)
- Sends grouped issue/resolution text to **Google Gemini Pro** (`gemini-pro`)
- Returns a structured `{ question, answer }` JSON object with step-by-step guidance
- **Graceful fallback:** if the API key is missing or the call fails, a local rule-based generator produces a formatted FAQ using keyword extraction

---

## 📋 CSV Format

Your input CSV must have the following columns:

```csv
ticket_id,issue,resolution,status
101,VPN not connecting,Restart VPN client and verify credentials,Closed
102,Password reset link not working,Request a new reset link,Closed
```

---

## 🗄️ Database Schema

**`tickets`**
```sql
ticket_id INTEGER PRIMARY KEY
issue     TEXT NOT NULL
resolution TEXT NOT NULL
status    TEXT CHECK(status IN ('open', 'closed'))
raised_at TEXT
closed_at TEXT
```

**`faq_drafts`**
```sql
faq_id           INTEGER PRIMARY KEY
question         TEXT
answer           TEXT
source_ticket_ids TEXT
status           TEXT  -- pending | approved | rejected
cluster_id       INTEGER
confidence_score INTEGER
```

**`published_faqs`**
```sql
faq_id            INTEGER PRIMARY KEY
question          TEXT
answer            TEXT
source_ticket_ids TEXT
confidence_score  INTEGER
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web app framework |
| `pandas` | Data manipulation |
| `scikit-learn` | TF-IDF vectorization & KMeans clustering |
| `altair` | Interactive charts |
| `python-dotenv` | Environment variable management |
| `requests` | Gemini API HTTP calls |

---

## 🔐 Admin Access

The Admin Review page is password-protected. Set `ADMIN_PASSWORD` in your `.env` file. Default in `.env.example` is `admin123` — **change this before deploying**.

---

## 📝 License

This project is for internal/educational use. Add your license here as needed.
