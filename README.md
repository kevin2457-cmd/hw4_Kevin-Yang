# Campus Customs: Yale apparel store with an AI shopping assistant

MGT 409 (AI Foundations for Managers), Homework 4.

A working e-commerce site for **Campus Customs**, a Yale apparel shop, with an AI shopping assistant built into every page.

- **Storefront:** React + Vite + TypeScript. Home, Products (search, category, size-in-stock and price filters, sort), product detail pages with live stock by size, About, Log in, and Create account.
- **Backend:** FastAPI serving products, images, accounts and chat, on top of the course SQLite database.
- **AI assistant:** a PydanticAI agent on the course model (`gpt-6-astra` via Portkey). It uses database tools for search, details, price, stock by size, and comparisons, so it never makes up products, prices or inventory. It answers with clickable **product cards**, remembers logged-in shoppers' chats (saved in the DB), understands "do you have *this* in pink?" on a product page, and appends every run to an **audit trail**.

```
SQLite (data/campus_customs.db) → FastAPI (backend/) → PydanticAI agent + tools → React site (frontend/)
```

## Repository layout

```
hw4/
├── AI_prompts.md            # the prompts I gave my AI coding assistant, per problem
├── README.md
├── requirements.txt         # backend Python dependencies
├── .env.example             # environment variable names (placeholders only)
├── .gitignore
├── backend/
│   ├── main.py              # FastAPI app: product, auth, chat, chat-history routes
│   ├── agent.py             # PydanticAI agent (model, prompt, tools, deps, audit hook)
│   ├── tools.py             # database-backed agent tools
│   ├── models.py            # Pydantic models (API, agent output/deps, tool results)
│   ├── prompts/prompt.md    # system prompt (voice + safety rules)
│   ├── auth.py              # sign-up / login (PBKDF2 hashes, signed tokens)
│   ├── memory.py            # saved chat history (chat_messages table)
│   ├── audit.py             # append-only audit trail writer
│   └── db.py                # shared SQLite helpers
├── frontend/                # React + Vite + TypeScript app (src/, index.html, vite.config.ts)
├── data/                    # ← put the course data pack here (NOT in Git, see below)
└── output/
    ├── harness.md           # database analysis, architecture, models, tools, safety, specs
    ├── usability.md         # 4 usability improvements
    ├── design.md            # visual design decisions
    ├── app_check.html       # screenshots proving key features (open by double-clicking)
    ├── app_check_images/
    └── audit_trail.json     # append-only log of agent runs
```

## 1. Add the local data pack

The database and product images come from the course data pack and are **not** committed. Place them exactly here:

```
hw4/data/campus_customs.db
hw4/data/products/          (the 102 .jpg product images)
```

The backend finds them relative to its own folder (`backend/db.py` → `<hw4>/data/campus_customs.db`), so no path configuration is needed.

## 2. Create `.env`

Copy the example and put in your Portkey API key:

```bash
cp .env.example .env
```

(Windows PowerShell: `Copy-Item .env.example .env`)

| Variable | Required | Meaning |
|---|---|---|
| `PORTKEY_API_KEY` | **yes** | Portkey key for the course model |
| `MODEL_NAME` | no | defaults to `gpt-6-astra` |
| `PORTKEY_BASE_URL` | no | defaults to `https://api.portkey.ai/v1` |
| `AUTH_SECRET` | recommended | any long random string. It signs login tokens. If unset, a built-in development value is used. |

The backend reads `hw4/.env` first, then a `.env` one folder above `hw4` as a fallback.

## 3. Run the backend (FastAPI, port 8000)

Requires Python 3.10+.

```bash
# from the hw4 folder
python -m venv .venv
# macOS/Linux:  source .venv/bin/activate
# Windows:      .venv\Scripts\activate
pip install -r requirements.txt

cd backend
uvicorn main:app --reload --port 8000
```

Run `uvicorn` **from inside `backend/`**, because the modules import each other by name. Check it's up at http://127.0.0.1:8000/api/health; interactive API docs are at http://127.0.0.1:8000/docs.

## 4. Run the frontend (Vite, port 5173)

Requires Node.js 20+. In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The Vite dev server forwards `/api` and `/media` requests to the backend on `127.0.0.1:8000` (`frontend/vite.config.ts`), so keep both running.

## 5. Try it

- **Test account** (already in the course database): `test@campuscustoms.yale.edu` / `password`. You can also create a new account.
- Click **Ask us** (bottom right) and try:
  - "What hoodies do you have?" → reply + product cards
  - on a product page: "Do you have this in medium?" or "Do you have this in pink?"
  - "Hoodies under $50 in XL" or "Compare the Basic Hoodie Big Yale and the Champion Full Zip Hood"
- Log in, chat, refresh: your conversation (with its cards) is restored.
- Every agent run is appended to `output/audit_trail.json`.

## API summary

| Method & path | Purpose |
|---|---|
| `GET /api/health` | health check |
| `GET /api/products` | all products (with total stock and in-stock sizes) |
| `GET /api/products/{product_id}` | one product with stock by size |
| `GET /media/products/<file>.jpg` | product images |
| `POST /api/auth/register` · `POST /api/auth/login` · `GET /api/auth/me` | accounts |
| `POST /api/chat` | chat with the assistant (optional `Authorization: Bearer <token>`) |
| `GET /api/chat/history` | the logged-in user's saved chat |

Full details (models, tools, safety rules, limits): `output/harness.md`.
