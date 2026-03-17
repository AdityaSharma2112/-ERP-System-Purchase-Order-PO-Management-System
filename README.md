# Purchase Order (PO) System

A full-stack Purchase Order management system with Google OAuth authentication, real-time notifications, and AI-powered product descriptions.

---

## Project Structure

```
po-system/
│
├── backend/               # FastAPI Python backend
│   ├── main.py            # API routes & business logic
│   ├── model.py           # SQLModel ORM models & Pydantic schemas
│   ├── database.py        # PostgreSQL engine & session factory
│   ├── mongoDB.py         # MongoDB connection for AI logs
│   ├── init_db.py         # Creates all tables from models
│   ├── migrate.py         # Incremental migration script
│   ├── seed.py            # Populates sample vendors & products
│   ├── requirements.txt   # Python dependencies
│   └── .env               # Environment variables (see setup)
│
├── notification/          # Node.js Socket.IO server
│   ├── index.js           # Express + Socket.IO notification server
│   └── package.json       # Node dependencies
│
└── frontend/              # Static HTML/JS frontend
    ├── dashboard.html     # Main PO dashboard
    ├── create-po.html     # Create Purchase Order form
    ├── create-product.html # Create Product form
    ├── create-vendor.html # Create Vendor form
    └── navbar.js          # Shared navbar, auth helpers, apiFetch()
```

---

## Tech Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Frontend     | HTML5, Bootstrap 5, Vanilla JS                  |
| Auth         | Google OAuth 2.0 (One Tap) + JWT                |
| Backend API  | FastAPI (Python)                                |
| ORM          | SQLModel (SQLAlchemy + Pydantic)                |
| Primary DB   | PostgreSQL                                      |
| Logging DB   | MongoDB                                         |
| Real-time    | Socket.IO (Node.js)                             |
| AI           | Gemini 2.5 Flash via OpenAI-compatible API      |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (running locally or remote)
- MongoDB Atlas or local MongoDB instance
- A Google Cloud project with OAuth 2.0 credentials
- A Gemini API key

---

## Setup & Installation

### 1. Clone / Download the Project

```bash
# Navigate into the project root
cd po-system
```

---

### 2. Backend Setup (FastAPI)

```bash
cd backend
```

#### a) Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### b) Install dependencies

```bash
pip install -r requirements.txt
```

#### c) Configure environment variables

Create a `.env` file inside `backend/` (a template is already provided):

```env
GEMINI_API=your_gemini_api_key_here
MONGO_URL=your_mongodb_connection_string_here
```

- **GEMINI_API** — Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **MONGO_URL** — Your MongoDB connection URI, e.g. `mongodb+srv://user:pass@cluster.mongodb.net/`

#### d) Update the PostgreSQL connection string

Open `backend/database.py` and replace with your credentials:

```python
DATABASE_URL = "postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DB_NAME"
```

#### e) Initialize the database

```bash
# Creates all tables from model.py
python init_db.py
```

#### f) (Optional) Run migrations for schema upgrades

```bash
python migrate.py           # apply all pending migrations
python migrate.py --status  # check what has been applied
python migrate.py --rollback # rollback the last migration
```

#### g) (Optional) Seed sample data

```bash
python seed.py
```

This populates 4 sample vendors and 8 sample products.

#### h) Start the FastAPI server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API is now available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

### 3. Notification Server Setup (Node.js)

```bash
cd notification
npm install
node index.js
```

The Socket.IO server runs on **port 3000**.

---

### 4. Frontend

The frontend is plain HTML — no build step needed.

Open `frontend/dashboard.html` directly in a browser, **or** serve with any static file server:

```bash
# Using Python (from the frontend/ directory)
cd frontend
python -m http.server 5500
```

Then visit `http://localhost:5500/dashboard.html`

> **Note:** Serving via `http://` is required for Google Sign-In to work (it won't work with `file://` URLs).

---

## Running the Full System

Start all three services in separate terminals:

```bash
# Terminal 1 — FastAPI backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 — Socket.IO notification server
cd notification && node index.js

# Terminal 3 — Frontend static server
cd frontend && python -m http.server 5500
```

Then open `http://localhost:5500/dashboard.html`.

---

## API Endpoints

| Method | Path                     | Auth Required | Description                          |
|--------|--------------------------|---------------|--------------------------------------|
| GET    | `/profile`               | ✅            | Returns current user info from JWT   |
| GET    | `/vendors`               | ❌            | List all vendors                     |
| GET    | `/products`              | ❌            | List all products                    |
| GET    | `/dashboard`             | ✅            | List all purchase orders             |
| POST   | `/create-vendor`         | ✅            | Create a new vendor                  |
| POST   | `/create-product`        | ✅            | Create a new product                 |
| POST   | `/create-purchase-order` | ✅            | Create a PO with line items          |
| POST   | `/auto-description`      | ✅            | AI-generate a product description    |
| POST   | `/auth/google`           | ❌            | Exchange Google token for JWT        |

---

## Database Design

### Relational (PostgreSQL)

The schema follows a normalized relational structure:

```
vendors (1) ──────────< purchase_orders (1) ──────────< purchase_order_items
                                                                  >──────── products
```

#### `vendors`
| Column   | Type         | Notes                  |
|----------|--------------|------------------------|
| id       | SERIAL PK    |                        |
| name     | VARCHAR(100) |                        |
| contact  | VARCHAR(100) |                        |
| rating   | INT          | 1–5, nullable          |

#### `products`
| Column      | Type         | Notes              |
|-------------|--------------|--------------------|
| id          | SERIAL PK    |                    |
| name        | VARCHAR(100) |                    |
| sku         | VARCHAR      | Unique, indexed    |
| unit_price  | FLOAT        |                    |
| stock_level | INT          | Default 0          |
| description | TEXT         |                    |

#### `purchase_orders`
| Column       | Type         | Notes                         |
|--------------|--------------|-------------------------------|
| id           | SERIAL PK    |                               |
| reference_no | VARCHAR      | Unique, indexed               |
| vendor_id    | INT FK       | → vendors.id                  |
| total_amount | FLOAT        | Subtotal + 5% tax, set by API |
| status       | VARCHAR      | Pending / Approved / Rejected |

#### `purchase_order_items` (junction / line-items)
| Column     | Type   | Notes               |
|------------|--------|---------------------|
| id         | SERIAL PK |                  |
| po_id      | INT FK | → purchase_orders.id |
| product_id | INT FK | → products.id       |
| quantity   | INT    |                     |
| price      | FLOAT  | Price at time of PO |

**Design decisions:**
- `price` is stored per line item (not referenced from `products.unit_price`) so historical PO values remain accurate even if the product price changes later.
- `total_amount` is computed server-side (subtotal × 1.05) and stored, avoiding recalculation on every dashboard read.
- `reference_no` has a unique index to prevent duplicate POs.
- `sku` on products has a unique index to enforce data integrity at the DB level.

---

### Document (MongoDB)

MongoDB is used exclusively for **AI description generation logs** — it is a natural fit here because:
- Each log entry is schema-free (prompt text, model name, output, user email, timestamp)
- It acts as an append-only audit trail with no relational joins needed
- The document structure can evolve without migrations

#### Collection: `ai_descriptions_logging`

```json
{
  "user_id": "user@example.com",
  "product_name": "Ergonomic Chair",
  "prompt": "Generate a professional marketing description...",
  "model": "gemini-2.5-flash",
  "generated_description": "...",
  "created_at": "2025-01-01T12:00:00Z"
}
```

---

## Authentication Flow

1. User clicks **Sign in with Google** in the navbar
2. Google returns a credential token to `handleCredentialResponse()` in `navbar.js`
3. The frontend POSTs the token to `POST /auth/google`
4. FastAPI verifies it with Google's servers using `google-auth` library
5. A signed JWT (HS256, 1-hour expiry) is returned and stored in `localStorage`
6. All protected API calls include `Authorization: Bearer <token>` header
7. `get_current_user()` dependency decodes and validates the JWT on every protected route

---

## Real-Time Notifications

1. When a PO is created, FastAPI calls `notify_node(reference_no)` which POSTs to `http://localhost:3000/notify`
2. The Node.js server emits a `po_created` Socket.IO event to all connected clients
3. The dashboard listens for `po_created` events, shows a toast notification, and refreshes the PO table automatically

---

## Google OAuth Configuration

The Google Client ID is currently hardcoded in `navbar.js` and `main.py`.  
To use your own Google project:

1. Go to [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Create an **OAuth 2.0 Client ID** (Web application)
3. Add `http://localhost:5500` to Authorized JavaScript origins
4. Replace the `client_id` in:
   - `backend/main.py` → `GOOGLE_CLIENT_ID`
   - `frontend/navbar.js` → `client_id` in both occurrences
