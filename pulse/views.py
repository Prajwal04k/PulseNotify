from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
import random
import json

from .models import PriceAlert, UserProfile, NotificationLog
from .serializers import RegisterSerializer, LoginSerializer, PriceAlertSerializer, NotificationLogSerializer
from .permissions import IsAdminUser


# ===== Auth Endpoints =====

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    POST /api/auth/register/
    Creates a new user and returns JWT token
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'username': user.username,
            'access': serializer.validated_data.get('access') or serializer.get_access(user),
            'role': 'user'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/auth/login/
    Validates credentials and returns JWT token
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user is not None:
            return Response({
                'username': user.username,
                'access': serializer.get_access({'user': user})
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===== Alert Endpoints =====

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_alert(request):
    """
    POST /api/alerts/
    Creates a new price alert for the authenticated user
    """
    data = request.data.copy()
    data['user'] = request.user.id

    serializer = PriceAlertSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_alerts(request):
    """
    GET /api/alerts/
    Returns all alerts for the authenticated user
    """
    alerts = PriceAlert.objects.filter(user=request.user).order_by('-created_at')
    serializer = PriceAlertSerializer(alerts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_alert(request, alert_id):
    """
    DELETE /api/alerts/<id>/
    Deactivates an alert (sets status to INACTIVE)
    """
    alert = get_object_or_404(PriceAlert, id=alert_id)

    if alert.user != request.user:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)

    alert.status = PriceAlert.Status.INACTIVE
    alert.save()

    return Response({'status': 'inactive'}, status=status.HTTP_200_OK)


# ===== Price Feed Endpoint =====

MOCK_PRICES = {
    'DEL-BOM': (3000, 7000),
    'BLR-HYD': (1500, 4000),
    'DEL-BLR': (4000, 9000),
    'BOM-GOA': (2000, 5000),
}


@api_view(['GET'])
@permission_classes([AllowAny])
def get_flight_price(request):
    """
    GET /api/flights/price/?route=DEL-BOM
    Returns mock flight price for a given route.
    Called internally by Celery check_prices task.
    """
    route = request.GET.get('route', '')
    price_range = MOCK_PRICES.get(route)

    if not price_range:
        return Response({'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

    price = random.randint(*price_range)
    return Response({'route': route, 'price': price}, status=status.HTTP_200_OK)


# ===== Admin Summary Endpoint =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_summary(request):
    """
    GET /api/admin/summary/
    Returns platform-wide statistics (admin only)
    """
    from django.db.models import Count

    # Get all counts
    total_alerts = PriceAlert.objects.count()
    active_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.ACTIVE).count()
    triggered_alerts = PriceAlert.objects.filter(status=PriceAlert.Status.TRIGGERED).count()
    total_notifications = NotificationLog.objects.count()

    # Get top routes
    top_routes = (
        PriceAlert.objects
        .values('origin', 'destination')
        .annotate(alert_count=Count('id'))
        .order_by('-alert_count')[:5]
    )

    routes_list = [
        {
            'route': f"{item['origin']}-{item['destination']}",
            'alert_count': item['alert_count']
        }
        for item in top_routes
    ]

    return Response({
        'total_alerts': total_alerts,
        'active_alerts': active_alerts,
        'triggered_alerts': triggered_alerts,
        'total_notifications': total_notifications,
        'top_routes': routes_list
    }, status=status.HTTP_200_OK)
