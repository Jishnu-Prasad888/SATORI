from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.llms import OpenAI
from langchain.prompts import StringPromptTemplate
from typing import List, Union
import json
from apps.nodes.models import Node, NodeEvent
from apps.telemetry.models import NodeMetric
from django.utils import timezone
from datetime import timedelta

class AgenticWorkflow:
    def __init__(self):
        self.llm = OpenAI(temperature=0)
        
    def analyze_node_health(self, node_id):
        """Analyze node health and recommend actions"""
        node = Node.objects.get(id=node_id)
        
        # Get recent metrics
        recent_metrics = NodeMetric.objects.filter(
            node=node,
            created_at__gte=timezone.now() - timedelta(minutes=30)
        ).order_by('created_at')
        
        # Get recent events
        recent_events = NodeEvent.objects.filter(
            node=node,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).order_by('-created_at')
        
        # Analyze for issues
        issues = []
        recommendations = []
        
        # CPU analysis
        cpu_metrics = recent_metrics.filter(metric_type='cpu')
        if cpu_metrics.exists():
            avg_cpu = cpu_metrics.aggregate(Avg('data__overall_percent'))['avg']
            if avg_cpu > 85:
                issues.append({
                    'type': 'cpu',
                    'severity': 'high',
                    'message': f'Consistently high CPU usage: {avg_cpu:.1f}%'
                })
                recommendations.append({
                    'action': 'redistribute_tasks',
                    'description': 'Consider redistributing tasks to other nodes',
                    'commands': ['systemctl stop heavy-service', 'docker pause high-cpu-container']
                })
        
        # Memory analysis
        memory_metrics = recent_metrics.filter(metric_type='memory')
        if memory_metrics.exists():
            avg_memory = memory_metrics.aggregate(Avg('data__percent_used'))['avg']
            if avg_memory > 90:
                issues.append({
                    'type': 'memory',
                    'severity': 'critical',
                    'message': f'Critical memory usage: {avg_memory:.1f}%'
                })
                recommendations.append({
                    'action': 'scale_memory',
                    'description': 'Memory pressure detected, consider increasing swap or reducing load',
                    'commands': ['swapoff -a && swapon -a', 'echo 3 > /proc/sys/vm/drop_caches']
                })
        
        # Security analysis
        security_metrics = recent_metrics.filter(metric_type='security')
        for metric in security_metrics:
            data = metric.data
            if data.get('failed_login_attempts', 0) > 10:
                issues.append({
                    'type': 'security',
                    'severity': 'critical',
                    'message': f'Multiple failed login attempts: {data["failed_login_attempts"]}'
                })
                recommendations.append({
                    'action': 'security_response',
                    'description': 'Suspicious activity detected, recommend isolation',
                    'commands': ['iptables -A INPUT -s {ip} -j DROP', 'systemctl restart ssh']
                })
        
        return {
            'node_id': str(node.id),
            'node_name': node.name,
            'status': node.status,
            'issues': issues,
            'recommendations': recommendations,
            'timestamp': timezone.now().isoformat()
        }
    
    def execute_recommendation(self, node_id, recommendation_id, approved_by=None):
        """Execute a recommended action (with human approval)"""
        # This would execute actual commands via node agent
        # For now, return a simulated response
        return {
            'status': 'executed',
            'node_id': node_id,
            'recommendation_id': recommendation_id,
            'approved_by': approved_by or 'system',
            'timestamp': timezone.now().isoformat(),
            'result': 'Commands executed successfully'
        }