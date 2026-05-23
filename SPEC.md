# WhatsApp Bulk Sender - Technical Specification

## Project Overview

**Project Name:** WhatsApp Bulk Sender
**Project Type:** Full-stack Web Application
**Core Functionality:** A production-ready bulk messaging platform using WhatsApp Cloud API (Meta) for sending text, template, and media messages to large contact lists.
**Target Users:** Businesses, marketing teams, and organizations that need to send bulk WhatsApp messages to customers.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | Django 4.2+ (Main) + Flask (Webhook microservice) |
| Frontend | HTML5, Bootstrap 5, Vanilla JS |
| Database | PostgreSQL 15+ |
| Task Queue | Celery 5.3+ with Redis backend |
| API | WhatsApp Cloud API v18.0+ |
| Docker | Docker + Docker Compose |

---

## UI/UX Specification

### Color Palette

| Purpose | Color | Hex Code |
|---------|-------|----------|
| Primary | WhatsApp Green | #25D366 |
| Primary Dark | Dark Green | #128C7E |
| Secondary | Teal | #075E54 |
| Accent | Light Green | #DCF8C6 |
| Background | Off White | #F5F5F5 |
| Card Background | White | #FFFFFF |
| Text Primary | Dark Gray | #333333 |
| Text Secondary | Gray | #666666 |
| Danger | Red | #DC3545 |
| Warning | Orange | #FFC107 |
| Success | Green | #28A745 |
| Info | Blue | #17A2B8 |

### Typography

| Element | Font | Size |
|---------|------|------|
| Headings | Inter, sans-serif | 24-32px |
| Body Text | Inter, sans-serif | 14-16px |
| Small Text | Inter, sans-serif | 12px |
| Buttons | Inter, semi-bold | 14px |

### Layout Structure

1. **Sidebar Navigation** (240px width)
   - Logo at top
   - Navigation links with icons
   - User profile at bottom

2. **Main Content Area**
   - Top navbar with search and notifications
   - Content container with max-width 1400px
   - Responsive cards and tables

3. **Responsive Breakpoints**
   - Mobile: < 768px (sidebar collapses to hamburger)
   - Tablet: 768px - 1024px
   - Desktop: > 1024px

### Components

- **Buttons:** Rounded (8px), with hover effects
- **Cards:** White background, subtle shadow (0 2px 8px rgba(0,0,0,0.1))
- **Forms:** Clean inputs with floating labels
- **Tables:** Striped rows, hover effect, pagination
- **Modals:** Centered, with backdrop blur
- **Alerts:** Toast notifications (top-right)
- **Progress Bars:** Green gradient, animated

---

## Functionality Specification

### 1. Authentication & Multi-Tenancy

- **User Registration:** Email, password, name
- **Login/Logout:** Session-based with Django auth
- **User Profile:** Extend Django User with:
  - Phone Number ID (encrypted)
  - WhatsApp Business Account ID
  - Access Token (encrypted, AES-256)
  - Webhook verify token

### 2. WhatsApp API Integration

**Base URL:** `https://graph.facebook.com/v18.0/{phone_number_id}/messages`

**Methods:**
- `send_text_message(to, body)` - Send plain text
- `send_template_message(to, template_name, language, components)` - Send template
- `send_media_message(to, media_type, media_url, caption)` - Send media
- `get_templates()` - List approved templates
- `upload_media(file)` - Upload media to WhatsApp

**Webhook Events:**
- `messages` - Incoming messages
- `message_status` - Delivery status updates

### 3. Contact Management

- **Contact Model:** name, phone (E.164), tags, group, created_at
- **Group Model:** name, description, contacts (M2M)
- **Bulk Import:** CSV upload with headers (name, phone)
- **Validation:** E.164 phone format, duplicate detection

### 4. Campaign Management

**Campaign Model:**
- name, description
- message_type (text/template/media)
- message_body, template_name, media_url
- contact_groups (M2M)
- status (draft/queued/sending/completed/failed)
- schedule_time (nullable)
- created_by (FK to User)
- created_at, updated_at

**Campaign Flow:**
1. Draft → 2. Queued → 3. Sending → 4. Completed/Failed

### 5. Bulk Sending Engine

**Celery Tasks:**
- `process_campaign(campaign_id)` - Main orchestrator
- `send_single_message(campaign_id, contact_id)` - Per-message task
- `update_message_status(message_id, status)` - Status update task

**Rate Limiting:**
- Max 80 messages/second
- 12.5ms delay between messages
- Exponential backoff for retries (max 3 attempts)

**Message Statuses:**
- pending, sent, delivered, read, failed

### 6. Dashboard & Analytics

**Metrics:**
- Total messages sent (today/week/month/all-time)
- Delivery rate (delivered/sent %)
- Read rate (read/delivered %)
- Failed message count
- Campaign success rate

**Charts (Chart.js):**
- Line chart: Messages over time (7 days)
- Bar chart: Messages by campaign
- Pie chart: Status distribution
- Donut chart: Delivery rate

### 7. Webhook Handler

**Endpoints:**
- `POST /webhook/` - Receive WhatsApp webhooks
- `GET /webhook/` - Verify webhook (hub.challenge)

**Processing:**
- Parse webhook payload
- Extract message ID and status
- Update CampaignRecipient status in DB
- Log all events

### 8. Template Message Builder

**Template Model:**
- template_name
- language
- category (MARKETING/UTILITY/AUTHENTICATION)
- status (PENDING/APPROVED/REJECTED)
- components (JSON - header, body, footer, buttons)

**Components:**
- Header: text, image, video, document
- Body: text with variables {{1}}, {{2}}, etc.
- Footer: text
- Buttons: quick_reply, url, phone_number

---

## Database Schema

### Tables

```
accounts_userprofile
- id, user_id (FK), phone_number_id, waba_id, access_token, webhook_verify_token

contacts_contact
- id, user_id (FK), name, phone, tags, created_at

contacts_contactgroup
- id, user_id (FK), name, description, created_at

contacts_contact_groups (M2M)
- contact_id, contactgroup_id

campaigns_campaign
- id, user_id (FK), name, description, message_type, message_body, template_name, media_url, status, schedule_time, created_at, updated_at

campaigns_campaignrecipient
- id, campaign_id (FK), contact_id (FK), status, wam_id, sent_at, delivered_at, read_at, error_message

campaigns_campaign_groups (M2M)
- campaign_id, contactgroup_id

messaging_messagelog
- id, campaign_id (FK), contact_id (FK), request_data, response_data, status_code, created_at

templates_mgr_whatsapptemplate
- id, user_id (FK), template_name, language, category, status, components, meta_template_id, created_at, updated_at
```

---

## API Endpoints

### REST API (Django REST Framework)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/contacts/ | Create contact |
| GET | /api/contacts/ | List contacts |
| POST | /api/contacts/import/ | Import CSV |
| POST | /api/campaigns/ | Create campaign |
| GET | /api/campaigns/ | List campaigns |
| GET | /api/campaigns/{id}/ | Campaign detail |
| POST | /api/campaigns/{id}/send/ | Start campaign |
| GET | /api/analytics/dashboard/ | Dashboard stats |
| GET | /api/templates/ | List templates |
| POST | /api/templates/sync/ | Sync from Meta |

---

## Acceptance Criteria

### Authentication
- [ ] User can register with email/password
- [ ] User can login/logout
- [ ] User can configure WABA credentials
- [ ] Credentials are encrypted in database

### Contacts
- [ ] User can add contacts manually
- [ ] User can import contacts via CSV
- [ ] User can create and manage groups
- [ ] Duplicate contacts are detected

### Campaigns
- [ ] User can create campaigns (text/template/media)
- [ ] User can select contact groups as recipients
- [ ] User can schedule campaigns
- [ ] Campaign status is tracked correctly

### Bulk Sending
- [ ] Messages are sent asynchronously via Celery
- [ ] Rate limiting is enforced (80/sec max)
- [ ] Failed messages are retried
- [ ] Progress is tracked in real-time

### Analytics
- [ ] Dashboard shows accurate statistics
- [ ] Charts display correctly
- [ ] Reports can be exported as CSV

### Webhooks
- [ ] Webhook endpoint verifies correctly
- [ ] Delivery status updates in real-time
- [ ] All events are logged

### Templates
- [ ] Templates sync from Meta API
- [ ] User can create new templates
- [ ] Variables are supported

---

## File Structure

```
whatsapp_bulk_sender/
├── manage.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── celery_app.py
├── SPEC.md
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── admin.py
│   ├── contacts/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tasks.py
│   ├── campaigns/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tasks.py
│   ├── messaging/
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── admin.py
│   │   └── __init__.py
│   ├── webhooks/
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── __init__.py
│   ├── analytics/
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── serializers.py
│   └── templates_mgr/
│       ├── models.py
│       ├── views.py
│       ├── urls.py
│       └── admin.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── auth/
│   ├── contacts/
│   ├── campaigns/
│   └── includes/
├── static/
│   ├── css/
│   └── js/
└── webhook_service/
    └── app.py
```