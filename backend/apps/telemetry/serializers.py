from rest_framework import serializers
from apps.nodes.models import NodeMetric, NodeEvent, NodeProcess

class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeMetric
        fields = '__all__'

class CPUMetricSerializer(serializers.Serializer):
    overall_percent = serializers.FloatField()
    per_core = serializers.ListField(child=serializers.FloatField())
    user_time = serializers.FloatField()
    system_time = serializers.FloatField()
    idle_time = serializers.FloatField()

class MemoryMetricSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    used = serializers.IntegerField()
    free = serializers.IntegerField()
    available = serializers.IntegerField()
    percent_used = serializers.FloatField()

class DiskMetricSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    used = serializers.IntegerField()
    free = serializers.IntegerField()
    mount_point = serializers.CharField()
    fs_type = serializers.CharField()
    iops = serializers.FloatField(required=False)
    latency_ms = serializers.FloatField(required=False)

class NetworkMetricSerializer(serializers.Serializer):
    interface = serializers.CharField()
    speed = serializers.IntegerField()
    status = serializers.CharField()
    bytes_sent = serializers.IntegerField()
    bytes_recv = serializers.IntegerField()
    packets_sent = serializers.IntegerField()
    packets_recv = serializers.IntegerField()
    errors_in = serializers.IntegerField()
    errors_out = serializers.IntegerField()

class NodeMetricBatchSerializer(serializers.Serializer):
    node_id = serializers.UUIDField()
    timestamp = serializers.DateTimeField()
    cpu = CPUMetricSerializer(required=False)
    memory = MemoryMetricSerializer(required=False)
    disk = serializers.ListField(child=DiskMetricSerializer(), required=False)
    network = serializers.ListField(child=NetworkMetricSerializer(), required=False)
    processes = serializers.ListField(child=serializers.DictField(), required=False)
    security = serializers.DictField(required=False)
    kernel = serializers.DictField(required=False)
    containers = serializers.ListField(child=serializers.DictField(), required=False)
    services = serializers.ListField(child=serializers.DictField(), required=False)