from celery import shared_task
import requests
import logging
from .models import PriceAlert, NotificationLog

logger = logging.getLogger(__name__)


@shared_task
def check_prices():
    """
    Celery Beat task that runs every 60 seconds.
    Checks prices for all active alerts and triggers notifications.
    """
    logger.info('check_prices task started')

    active_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.ACTIVE)
    routes = active_alerts.values_list('origin', 'destination').distinct()

    for origin, destination in routes:
        route = f'{origin}-{destination}'

        try:
            # Call internal price endpoint
            response = requests.get(
                'http://localhost:8000/api/flights/price/',
                params={'route': route},
                timeout=5
            )

            if response.status_code != 200:
                logger.warning(f'Price fetch failed for {route}: {response.status_code}')
                continue

            current_price = response.json().get('price')
            logger.info(f'Price for {route}: ₹{current_price}')

            # Check each active alert for this route
            route_alerts = active_alerts.filter(
                origin=origin, destination=destination
            )

            for alert in route_alerts:
                if current_price <= float(alert.threshold_price):
                    logger.info(f'Alert triggered for {alert.id}: {route} @ ₹{current_price}')
                    send_notification.delay(alert.id, current_price)

        except Exception as e:
            logger.error(f'Error checking prices for {route}: {str(e)}')

    logger.info('check_prices task completed')


@shared_task
def send_notification(alert_id, triggered_price):
    """
    Async task that creates a NotificationLog entry and marks alert as triggered.
    Called via .delay() so check_prices doesn't wait for it.
    """
    try:
        alert = PriceAlert.objects.get(id=alert_id)

        message = (
            f'Price alert triggered! {alert.origin}-{alert.destination} '
            f'is now ₹{triggered_price}  -  below your threshold of '
            f'₹{alert.threshold_price}'
        )

        NotificationLog.objects.create(
            alert=alert,
            triggered_price=triggered_price,
            message=message
        )

        # Mark alert as triggered so it doesn't fire again
        alert.status = PriceAlert.Status.TRIGGERED
        alert.save()

        logger.info(f'Notification created for alert {alert_id}')

    except PriceAlert.DoesNotExist:
        logger.error(f'Alert {alert_id} not found')
    except Exception as e:
        logger.error(f'Error sending notification: {str(e)}')
