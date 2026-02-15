from django.urls import re_path
from .consumers import TelemetryConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/telemetry/(?P<node_id>[^/]+)/$', TelemetryConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]