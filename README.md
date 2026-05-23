# WhatsApp Bulk Sender

A full-stack Django application for sending bulk WhatsApp messages via the **WhatsApp Cloud API**. Features contact management, group segmentation, campaign scheduling, and real-time delivery tracking.

## Features

- **Contact Management** — Import, organize, and tag contacts with CSV upload
- **Smart Groups** — Segment contacts into groups for targeted campaigns
- **Campaign Engine** — Create, schedule, and send text/template/media campaigns
- **Real-time Tracking** — Monitor sent, delivered, and read status per recipient
- **REST API** — Full API surface for programmatic access
- **Async-ready** — Celery + Redis architecture (optional, runs synchronously without)
- **WebSocket Support** — Channels/Daphne for live progress updates
- **Secure** — Fernet-encrypted API tokens, CSRF protection

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, Django REST Framework |
| Database | PostgreSQL (SQLite for local dev) |
| Queue | Celery + Redis (optional) |
| Async | Channels + Daphne (WebSockets) |
| API | WhatsApp Cloud API (Meta) |
| Frontend | Bootstrap 5, crispy forms |
| Auth | Session-based with encrypted token storage |

## Quick Start

```bash
# Clone
git clone https://github.com/Sahil-TRCAC/whatsapp-bulk-sender.git
cd whatsapp-bulk-sender

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python manage.py migrate
python manage.py runserver
```

### WhatsApp API Setup

1. Go to [Meta Developer Console](https://developers.facebook.com)
2. Create a **Business App** → add **WhatsApp** product
3. Claim a **test number** (or use a production number after verification)
4. Copy **Phone Number ID**, **WABA ID**, and **Access Token**
5. Paste into the app at **Settings** → **WhatsApp Configuration**

## Project Structure

```
whatsapp_bulk_sender/
├── apps/
│   ├── accounts/       # Auth, profiles, WhatsApp config
│   ├── analytics/      # Dashboard, reports, REST API
│   ├── campaigns/      # Campaign CRUD, sending logic
│   ├── contacts/       # Contacts, groups, CSV import
│   ├── messaging/      # WhatsApp API client service
│   ├── templates_mgr/  # Message template management
│   └── webhooks/       # Meta webhook receiver
├── config/             # Django settings (base/dev)
├── templates/          # Bootstrap 5 frontend
├── static/             # Static assets
├── docker-compose.yml  # Production deployment
└── Dockerfile
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/campaigns/` | List all campaigns |
| GET | `/api/campaigns/:id/` | Campaign details |
| GET | `/api/contacts/` | List contacts |
| GET | `/api/groups/` | List contact groups |
| GET | `/api/dashboard/` | Aggregate statistics |

## Development

```bash
# Run with SQLite (no Docker needed)
python manage.py runserver

# Run with PostgreSQL + Redis (Docker required)
docker-compose up
```

## Resume Highlights

- Full-stack Django application with **real third-party API integration**
- **Database design** with complex relationships (M2M, foreign keys)
- **Async architecture** planned with Celery/Redis + Channels
- **Security-first** approach (encrypted secrets, CSRF, auth)
- Clean **MVC architecture** across 7+ modular Django apps
- **Working end-to-end** message delivery via Meta's WhatsApp Cloud API

## License

MIT
