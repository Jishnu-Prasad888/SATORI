from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.core.models import TimeStampedModel, Organization
import uuid

class Node(TimeStampedModel):
    STATUS_CHOICES = (
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('offline', 'Offline'),
        ('maintenance', 'Maintenance'),
    )
    
    OS_CHOICES = (
        ('linux', 'Linux'),
        ('windows', 'Windows'),
        ('macos', 'macOS'),
        ('raspbian', 'Raspbian'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='nodes')
    name = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17)
    
    os_type = models.CharField(max_length=20, choices=OS_CHOICES)
    os_version = models.CharField(max_length=100)
    kernel_version = models.CharField(max_length=100)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    api_key = models.CharField(max_length=255, unique=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    
    tags = ArrayField(models.CharField(max_length=100), default=list)
    
    cpu_cores = models.IntegerField(default=0)
    total_memory = models.BigIntegerField(default=0)  # in bytes
    total_disk = models.BigIntegerField(default=0)    # in bytes
    
    transmission_interval = models.IntegerField(default=30)  # seconds
    
    class Meta:
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['last_heartbeat']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.hostname})"

class NodeMetric(TimeStampedModel):
    METRIC_TYPES = (
        ('cpu', 'CPU'),
        ('memory', 'Memory'),
        ('disk', 'Disk'),
        ('network', 'Network'),
        ('process', 'Process'),
        ('security', 'Security'),
        ('kernel', 'Kernel'),
        ('container', 'Container'),
        ('service', 'Service'),
    )
    
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='metrics')
    timestamp = models.DateTimeField(auto_now_add=True)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    data = models.JSONField()
    
    class Meta:
        indexes = [
            models.Index(fields=['node', 'timestamp']),
            models.Index(fields=['metric_type', 'timestamp']),
        ]

class NodeEvent(TimeStampedModel):
    SEVERITY_CHOICES = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    )
    
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='events')
    timestamp = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['node', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
        ]

class NodeProcess(TimeStampedModel):
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='processes')
    timestamp = models.DateTimeField(auto_now_add=True)
    pid = models.IntegerField()
    ppid = models.IntegerField()
    name = models.CharField(max_length=255)
    cpu_percent = models.FloatField()
    memory_percent = models.FloatField()
    status = models.CharField(max_length=50)
    command = models.TextField()
    
    class Meta:
        indexes = [
            models.Index(fields=['node', 'timestamp']),
            models.Index(fields=['cpu_percent']),
            models.Index(fields=['memory_percent']),
        ]