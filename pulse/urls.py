from django.urls import path
from . import views

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),

    # Alert endpoints
    path('alerts/', views.list_alerts, name='list_alerts'),
    path('alerts/create/', views.create_alert, name='create_alert'),
    path('alerts/<int:alert_id>/', views.delete_alert, name='delete_alert'),

    # Price feed
    path('flights/price/', views.get_flight_price, name='get_flight_price'),

    # Admin
    path('admin/summary/', views.admin_summary, name='admin_summary'),
]
