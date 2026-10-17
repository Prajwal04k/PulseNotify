# PulseNotify - Quick Start Guide

Get PulseNotify running in 5 minutes!

## Prerequisites

- Python 3.9+
- Docker & Docker Compose installed
- 3 terminal windows ready

## Quick Setup

### 1. Clone & Install (1 min)

```bash
# Clone or extract project
cd pulsenotify

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (1 min)

```bash
# Copy example environment
cp .env.example .env

# Edit .env if needed (mostly pre-configured)
# For local development, defaults work fine
```

### 3. Start Docker Services (1 min)

```bash
# In any terminal, start containers
docker-compose up -d

# Verify they're running
docker-compose ps
# You should see: postgres and redis containers running
```

### 4. Initialize Database (1 min)

```bash
# Run migrations
python manage.py migrate

# Create admin user (optional for testing)
python manage.py createsuperuser
# Follow prompts or use:
# username: admin, email: admin@example.com, password: admin
```

### 5. Start All Services (1 min)

**Terminal 1: Django Server**
```bash
python manage.py runserver
# Runs on http://localhost:8000
```

**Terminal 2: Celery Worker**
```bash
celery -A pulsenotify worker -l info
# Processes background tasks
```

**Terminal 3: Celery Beat**
```bash
celery -A pulsenotify beat -l info
# Schedules price checks every 60 seconds
```

✅ **All done!** Your system is running.

---

## Test It Out

### Option 1: Using Postman (Recommended)

1. Open Postman
2. Import: `Postman_PulseNotify.postman_collection.json`
3. Set environment variable: `base_url = http://localhost:8000`
4. Try these in order:

```
1. POST Register User → Get token
2. POST Create Alert → Create DEL-BOM alert with threshold 4500
3. GET List Alerts → See your alert
4. GET Get Flight Price → Check current price
5. GET Admin Summary (if you set yourself as admin)
```

### Option 2: Using curl

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@example.com","password":"testpass123"}'

# Login and save token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"testpass123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Create alert
curl -X POST http://localhost:8000/api/alerts/create/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"origin":"DEL","destination":"BOM","threshold_price":4500}'

# List alerts
curl -X GET http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer $TOKEN"

# Get flight price
curl -X GET "http://localhost:8000/api/flights/price/?route=DEL-BOM"
```

---

## Key Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/auth/register/` | No | Create account |
| POST | `/api/auth/login/` | No | Get token |
| POST | `/api/alerts/create/` | JWT | Create price alert |
| GET | `/api/alerts/` | JWT | List your alerts |
| DELETE | `/api/alerts/<id>/` | JWT | Remove alert |
| GET | `/api/flights/price/?route=DEL-BOM` | No | Get current price |
| GET | `/api/admin/summary/` | JWT (Admin) | View stats |

---

## What's Happening

1. **Price Check**: Every 60 seconds, Celery Beat triggers `check_prices` task
2. **Alert Matching**: System fetches all active alerts and current prices
3. **Notification**: When price ≤ threshold, `send_notification` task runs
4. **History**: Notifications logged in NotificationLog for reference

Supported routes: DEL-BOM, BLR-HYD, DEL-BLR, BOM-GOA

---

## Run Tests

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test pulse.tests.AlertScopingTest

# Verbose output
python manage.py test -v 2
```

Tests include:
- ✅ Price threshold logic
- ✅ Notification creation
- ✅ User isolation (can't see other users' alerts)
- ✅ Profile auto-creation
- ✅ Role assignment

---

## Stop Everything

```bash
# When done, stop services

# Ctrl+C in Django terminal
# Ctrl+C in Celery terminal  
# Ctrl+C in Celery Beat terminal

# Stop containers
docker-compose down

# Deactivate virtual environment
deactivate
```

---

## Troubleshooting

**Port already in use?**
```bash
# Change port in Terminal 1
python manage.py runserver 8001
# Then update Postman/curl calls to http://localhost:8001
```

**Database connection error?**
```bash
# Restart Docker
docker-compose restart postgres
# Then retry migrations
python manage.py migrate
```

**Celery tasks not running?**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Restart Celery services
# Ctrl+C and re-run in Terminals 2 & 3
```

**Token expired?**
```bash
# Just login again to get new token
# Or use refresh_token endpoint
```

---

## Next Steps

- Read [README.md](README.md) for full documentation
- Explore Django admin at http://localhost:8000/admin/
- View API docs at http://localhost:8000/api/docs/
- Modify mock prices in `pulse/views.py` (get_flight_price function)
- Connect to real flight price API (replace mock endpoint)
- Deploy to production (see README.md)

---

**Happy monitoring! 🚀**
