from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Max, Min, Count
from cryptography.fernet import Fernet
import base64
import hashlib
from apps.nodes.models import Node, NodeMetric, NodeEvent
from apps.nodes.authentication import NodeAPIAuthentication
from .serializers import NodeMetricBatchSerializer
from django.conf import settings
import json

class MetricIngestionViewSet(viewsets.GenericViewSet):
    permission_classes = []
    authentication_classes = [NodeAPIAuthentication]
    
    def get_encryption_key(self):
        """Derive Fernet key from fixed password"""
        key = hashlib.sha256(settings.NODE_ENCRYPTION_KEY.encode()).digest()
        return base64.urlsafe_b64encode(key)
    
    def decrypt_payload(self, encrypted_data):
        """Decrypt node agent data"""
        fernet = Fernet(self.get_encryption_key())
        decrypted = fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted)
    
    @action(detail=False, methods=['post'])
    def ingest_batch(self, request):
        """Ingest batch of metrics from node agent"""
        try:
            # Decrypt if encrypted
            if request.headers.get('X-Encrypted') == 'true':
                data = self.decrypt_payload(request.data.get('data'))
            else:
                data = request.data
            
            serializer = NodeMetricBatchSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            node = request.auth  # Set by NodeAPIAuthentication
            
            # Update node heartbeat
            node.last_heartbeat = timezone.now()
            node.save(update_fields=['last_heartbeat'])
            
            # Process different metric types
            if 'cpu' in validated_data:
                NodeMetric.objects.create(
                    node=node,
                    metric_type='cpu',
                    data=validated_data['cpu']
                )
            
            if 'memory' in validated_data:
                NodeMetric.objects.create(
                    node=node,
                    metric_type='memory',
                    data=validated_data['memory']
                )
            
            if 'disk' in validated_data:
                for disk_data in validated_data['disk']:
                    NodeMetric.objects.create(
                        node=node,
                        metric_type='disk',
                        data=disk_data
                    )
            
            if 'network' in validated_data:
                for net_data in validated_data['network']:
                    NodeMetric.objects.create(
                        node=node,
                        metric_type='network',
                        data=net_data
                    )
            
            if 'processes' in validated_data:
                NodeMetric.objects.create(
                    node=node,
                    metric_type='process',
                    data={'processes': validated_data['processes']}
                )
            
            if 'security' in validated_data:
                NodeMetric.objects.create(
                    node=node,
                    metric_type='security',
                    data=validated_data['security']
                )
            
            if 'kernel' in validated_data:
                NodeMetric.objects.create(
                    node=node,
                    metric_type='kernel',
                    data=validated_data['kernel']
                )
            
            if 'containers' in validated_data:
                NodeMetric.objects.create(
                    node=node,
                    metric_type='container',
                    data={'containers': validated_data['containers']}
                )
            
            if 'services' in validated_data:
                NodeMetric.objects.create(
                    node=node,
                    metric_type='service',
                    data={'services': validated_data['services']}
                )
            
            # Check for anomalies and create events if needed
            self.check_for_anomalies(node, validated_data)
            
            return Response({'status': 'success', 'received': len(validated_data)})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def check_for_anomalies(self, node, data):
        """Check for anomalies in the data and create events"""
        events = []
        
        # CPU anomalies
        if 'cpu' in data:
            cpu = data['cpu']
            if cpu.get('overall_percent', 0) > 90:
                events.append({
                    'severity': 'warning',
                    'title': 'High CPU Usage',
                    'message': f"CPU usage is at {cpu['overall_percent']}%",
                    'data': {'cpu': cpu}
                })
        
        # Memory anomalies
        if 'memory' in data:
            memory = data['memory']
            if memory.get('percent_used', 0) > 90:
                events.append({
                    'severity': 'warning',
                    'title': 'High Memory Usage',
                    'message': f"Memory usage is at {memory['percent_used']}%",
                    'data': {'memory': memory}
                })
        
        # Create events
        for event_data in events:
            NodeEvent.objects.create(node=node, **event_data)