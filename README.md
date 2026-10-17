# PulseNotify

**Flight Price Monitoring Service**

A robust Django REST Framework backend for monitoring flight prices and triggering automatic alerts when prices drop below user-defined thresholds. Built with Celery for async tasks, Redis for caching, and PostgreSQL for data persistence.

## Features

✅ **User Authentication & Authorization**
- JWT token-based authentication with django-rest-framework-simplejwt
- User registration and login endpoints
- Role-based access control (Admin/User)

✅ **Price Alert Management**
- Create price alerts for flight routes (origin-destination pairs)
- Set custom price thresholds
- List and manage your alerts
- Soft-delete alerts (mark as inactive)

✅ **Automated Price Monitoring**
- Scheduled price checking every 60 seconds using Celery Beat
- Mock price feed with randomized prices for testing
- Automatic notification generation when prices drop below threshold
- Notification history and logs

✅ **Admin Dashboard**
- Summary statistics (total alerts, active alerts, triggered alerts)
- Notification count tracking
- Top routes analysis
- Admin-only access

✅ **Task Queue & Scheduling**
- Celery + Redis for async task processing
- Celery Beat for scheduled price checks
- Separate notification tasks to prevent blocking

## Tech Stack

- **Backend:** Django 4.2 + Django REST Framework 3.14
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Database:** PostgreSQL 15
- **Message Broker:** Redis 7
- **Task Queue:** Celery 5.3 with Celery Beat
- **API Documentation:** drf-yasg (Swagger/OpenAPI)

## Project Structure

```
pulsenotify/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── QUICKSTART.md
├── Postman_PulseNotify.postman_collection.json
│
├── pulsenotify/              # Main project
│   ├── __init__.py
│   ├── celery.py            # Celery app configuration
│   ├── wsgi.py
│   ├── urls.py              # Main URL routing
│   └── settings/
│       ├── __init__.py
│       ├── base.py          # Shared settings
│       ├── local.py         # Development settings
│       └── production.py    # Production settings
│
└── pulse/                   # Main app
    ├── migrations/
    │   ├── __init__.py
    │   └── 0001_initial.py
    ├── __init__.py
    ├── admin.py             # Django admin configuration
    ├── apps.py
    ├── models.py            # Data models
    ├── serializers.py       # DRF serializers
    ├── views.py             # API endpoints (7 total)
    ├── urls.py              # App URL routing
    ├── permissions.py       # Custom permission classes
    ├── tasks.py             # Celery tasks
    ├── signals.py           # Django signals
    └── tests.py             # Unit tests
```

## Installation

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- pip (Python package manager)

### Step 1: Clone and Setup

```bash
# Clone repository (if from GitHub)
git clone https://github.com/Prajwal04k/PulseNotify.git
cd pulsenotify

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - DJANGO_SETTINGS_MODULE=pulsenotify.settings.local
# - SECRET_KEY=your-secret-key-here
# - DEBUG=True (for development)
# - PostgreSQL credentials
# - Redis connection strings
```

### Step 3: Start Docker Services

```bash
# Start PostgreSQL and Redis containers
docker-compose up -d

# Verify containers are running
docker-compose ps
```

### Step 4: Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser for Django admin
python manage.py createsuperuser
# Follow prompts to set username, email, and password
```

### Step 5: Start Services

**Terminal 1: Django Development Server**
```bash
python manage.py runserver
# Server runs on http://localhost:8000
```

**Terminal 2: Celery Worker**
```bash
celery -A pulsenotify worker -l info
```

**Terminal 3: Celery Beat (Scheduler)**
```bash
celery -A pulsenotify beat -l info
```

Once all three services are running, the system is ready to accept requests and automatically check prices every 60 seconds.

## API Endpoints

### Authentication (No Auth Required)

**Register User**
```
POST /api/auth/register/
Body: {"username": "user", "email": "user@example.com", "password": "pass"}
Response: {"username": "user", "access_token": "...", "role": "user"}
```

**Login User**
```
POST /api/auth/login/
Body: {"username": "user", "password": "pass"}
Response: {"username": "user", "access_token": "...", "refresh_token": "..."}
```

### Price Alerts (Requires Auth)

**Create Alert**
```
POST /api/alerts/create/
Headers: Authorization: Bearer <token>
Body: {"origin": "DEL", "destination": "BOM", "threshold_price": 4500}
Response: {alert object with id, status, created_at}
```

**List Alerts**
```
GET /api/alerts/
Headers: Authorization: Bearer <token>
Response: [list of user's alerts]
```

**Delete Alert**
```
DELETE /api/alerts/<alert_id>/
Headers: Authorization: Bearer <token>
Response: {"status": "inactive"}
```

### Flight Prices (No Auth Required)

**Get Price**
```
GET /api/flights/price/?route=DEL-BOM
Response: {"route": "DEL-BOM", "price": 4250}
```

Supported routes: DEL-BOM, BLR-HYD, DEL-BLR, BOM-GOA

### Admin (Admin Auth Required)

**Admin Summary**
```
GET /api/admin/summary/
Headers: Authorization: Bearer <token> (admin token)
Response: {
    "total_alerts": 10,
    "active_alerts": 7,
    "triggered_alerts": 2,
    "total_notifications": 5,
    "top_routes": [{"origin": "DEL", "destination": "BOM", "count": 3}]
}
```

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test pulse.tests.PriceThresholdTest

# Run with verbose output
python manage.py test -v 2
```

Test coverage includes:
- Price threshold comparison logic (3 tests)
- Notification log creation and storage (2 tests)
- User alert isolation/scoping (3 tests)
- User profile auto-creation and role assignment (3 tests)

## Using Postman

1. Import `Postman_PulseNotify.postman_collection.json` into Postman
2. Set environment variable `base_url` to `http://localhost:8000`
3. Start with Register User or Login User endpoint
4. The collection will automatically save the auth token for subsequent requests
5. Test each endpoint in sequence

## Data Models

### UserProfile
- Linked to Django User (OneToOne)
- Roles: admin, user (default: user)
- Auto-created when User is created
- Tracks created_at timestamp

### PriceAlert
- User (ForeignKey) - links to User model
- Origin/Destination (CharField) - flight route codes
- Threshold Price (DecimalField) - alert trigger price
- Status (CharField) - active, inactive, or triggered
- Created At (DateTimeField) - timestamp

### NotificationLog
- Alert (ForeignKey) - links to PriceAlert
- Triggered Price (DecimalField) - price at which alert fired
- Message (TextField) - formatted notification message
- Notified At (DateTimeField) - when notification was sent

## Background Tasks

### check_prices (Runs Every 60 Seconds)
1. Fetches all active price alerts
2. Groups by origin-destination route
3. Calls mock price API for each route
4. Compares current price to threshold
5. Triggers send_notification for matching alerts

### send_notification (Runs Async)
1. Fetches alert details
2. Creates NotificationLog entry with formatted message
3. Updates alert status to 'triggered'
4. Logs notification event

## Configuration

### Settings Split

**base.py** (Shared)
- Django apps and middleware
- REST Framework auth and permissions
- JWT token configuration (1h access, 1d refresh)
- Celery configuration
- Logging setup

**local.py** (Development)
- DEBUG=True
- SQLite/PostgreSQL database
- Reduced security settings

**production.py** (Production)
- DEBUG=False
- PostgreSQL database
- Hardened security settings
- Environment-based configuration

### Celery Beat Schedule

```python
CELERY_BEAT_SCHEDULE = {
    'check-flight-prices-every-minute': {
        'task': 'pulse.tasks.check_prices',
        'schedule': 60.0,  # Every 60 seconds
    },
}
```

## Troubleshooting

### Services Won't Start
```bash
# Check Docker is running
docker --version

# View container logs
docker-compose logs postgres
docker-compose logs redis

# Restart services
docker-compose restart
```

### Database Connection Error
```bash
# Verify PostgreSQL is accessible
psql -h localhost -U postgres -d pulsenotify -c "SELECT 1"

# Ensure .env has correct credentials
# Check DATABASE_URL in .env
```

### Celery Tasks Not Running
```bash
# Check Celery Beat is running (separate terminal)
# Verify Redis connection: redis-cli ping
# Check Celery worker logs for errors
# Restart services: celery worker, celery beat
```

### Token Expiration
- Access token expires in 1 hour
- Use refresh token endpoint to get new access token
- In Postman: POST /api/token/refresh/ with refresh_token

## Production Deployment

1. Switch to `production.py` settings
2. Set DEBUG=False
3. Configure ALLOWED_HOSTS
4. Use production database (managed service recommended)
5. Use managed Redis service
6. Set strong SECRET_KEY
7. Use HTTPS only
8. Configure CORS settings as needed
9. Deploy Celery worker and beat to production environment
10. Use process manager (Gunicorn, uWSGI) for Django
11. Use supervisor or systemd for Celery services

## Development Notes

- Token is automatically saved to Postman environment after login
- Mock prices use random ranges: DEL-BOM (₹3000-7000), BLR-HYD (₹1500-4000), etc.
- Signals auto-create UserProfile when User is created
- Notifications are soft-deleted (status changed to INACTIVE)
- Admin panel available at /admin/ (Django admin)
- API documentation at /api/docs/ (Swagger UI via drf-yasg)

## Support & Contribution

For issues, feature requests, or contributions, please create an issue or pull request on the GitHub repository.

## License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Django & Celery**
