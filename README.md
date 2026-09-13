# 🌳 Family Historical Tree — Backend API (वंशावली प्रणाली)

A robust, enterprise-ready Django REST Framework backend powering the **Family Historical Tree** platform — a cultural and genealogical archive designed for preserving multi-generational family lineages, rich media archives, oral histories, and historical milestone timelines.

---

## 🚀 Key Features

* **Multi-Generational Tree Engine**:
  * Graph traversal algorithm calculating generational hierarchy, biological parents, spousal ties, and descendant lines.
  * Optimized subtree retrieval with configurable traversal depth (`/api/v1/families/{id}/tree/?depth=10`).
* **Role-Based Access Control (RBAC) & Approvals**:
  * Distinct permission levels: `OWNER`, `ADMIN`, `EDITOR`, `VIEWER`.
  * Integrated approval lifecycle (`PENDING` ➔ `APPROVED` / `REJECTED`) for secure public or invite-only lineages.
  * Server-enforced mutation permissions (`IsFamilyEditor`, `IsFamilyAdmin`, `IsFamilyOwner`).
* **Media & Digital Archive**:
  * High-resolution photo and document management with person tagging.
  * Automatic fallback avatar generation and customizable profile portraits.
* **Oral Histories & Narrative Stories**:
  * Rich-text storytelling with multiple tagged lineage members and draft/published workflows.
* **Chronological Milestones & Timeline Events**:
  * Historical records (births, migrations, achievements, cultural traditions) linked to individual ancestors or entire family branches.
* **Authentication & Collaboration**:
  * Stateless JWT authentication (`SimpleJWT`).
  * Email invitations for onboarding family members into collaborator roles.

---

## 🛠️ Tech Stack

* **Language**: Python 3.12+
* **Framework**: Django 6.1+ / Django REST Framework
* **Authentication**: `djangorestframework-simplejwt`
* **CORS**: `django-cors-headers`
* **Package Management**: [`uv`](https://docs.astral.sh/uv/) (or standard `pip`)
* **Containerization**: Docker

---

## 📁 Repository Structure

```text
backend/
├── apps/
│   ├── users/           # Custom User model, JWT registration & login
│   ├── families/        # Lineage metadata, memberships, approvals & roles
│   ├── members/         # Person records, dates, biographies, avatar links
│   ├── relationships/   # Kinship graph engine (Parent-Child, Spouse, Tree Builder)
│   ├── media/           # Digital assets, photos, documents, and uploads
│   ├── stories/         # Historical narratives and oral traditions
│   ├── events/          # Timeline events and historical milestones
│   ├── invitations/     # Collaboration tokens and invite links
│   └── notifications/   # Real-time and persistent user notifications
├── config/
│   ├── settings.py      # Django configuration (CORS, JWT, DB, Media)
│   ├── urls.py          # Master URL dispatcher
│   └── wsgi.py          # Production WSGI entry point
├── Dockerfile           # Production container build
├── manage.py            # Django management utility
├── pyproject.toml       # Dependencies & project metadata
└── .env.example         # Environment template
```

---

## ⚙️ Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone git@github.com:Prakash617/family-history-backend.git
cd family-history-backend
```

### 2. Environment Configuration
Copy the sample environment file and adjust variables if needed:
```bash
cp .env.example .env
```

Default local `.env`:
```ini
DEBUG=True
SECRET_KEY=django-insecure-family-tree-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Install Dependencies

**Using `uv` (Recommended - fast):**
```bash
uv sync
```

**Or using standard `pip`:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 4. Run Migrations
```bash
# Using uv:
uv run python manage.py migrate

# Or with activated venv:
python manage.py migrate
```

### 5. Seed Sample & Demo Data (Optional)
Populate realistic multi-generational Nepali lineages, timeline events, stories, and sample portraits:
```bash
uv run python manage.py seed_family_tree
uv run python manage.py seed_demo_content
uv run python manage.py generate_sample_avatars
```

### 6. Create a Superuser
```bash
uv run python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
uv run python manage.py runserver 0.0.0.0:8000
```

The API will now be accessible at `http://localhost:8000/api/v1/`.

---

## 📡 Core API Endpoints

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/v1/auth/register/` | Register new user account |
| **Auth** | `POST` | `/api/v1/auth/token/` | Obtain JWT access and refresh tokens |
| **Auth** | `POST` | `/api/v1/auth/token/refresh/` | Refresh expired access token |
| **Families** | `GET` / `POST` | `/api/v1/families/` | List or create family trees |
| **Families** | `GET` | `/api/v1/families/{id}/tree/` | Retrieve hierarchical lineage graph |
| **Families** | `POST` | `/api/v1/families/{id}/request_access/` | Request collaborator permission |
| **Approvals**| `POST` | `/api/v1/families/{family_id}/memberships/{id}/approve/` | Approve access (`EDITOR` / `VIEWER`) |
| **Approvals**| `POST` | `/api/v1/families/{family_id}/memberships/{id}/reject/` | Reject access request |
| **Members** | `GET` / `POST` | `/api/v1/people/` | Query or add individual family members |
| **Relations**| `GET` / `POST` | `/api/v1/relationships/` | Manage parent-child and spousal edges |
| **Media** | `GET` / `POST` | `/api/v1/media/` | Upload and list family photos/documents |
| **Stories** | `GET` / `POST` | `/api/v1/stories/` | Family articles and written histories |
| **Events** | `GET` / `POST` | `/api/v1/events/` | Milestone and timeline occurrences |

---

## 🐳 Running with Docker

Build and start the containerized backend:
```bash
docker build -t family-history-backend .
docker run -p 8000:8000 family-history-backend
```

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
