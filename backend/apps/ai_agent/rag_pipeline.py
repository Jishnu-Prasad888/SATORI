from sentence_transformers import SentenceTransformer
import numpy as np
from django.db import connection
import json
from apps.telemetry.models import NodeMetric, NodeEvent
from apps.nodes.models import Node
from datetime import datetime, timedelta

class RAGPipeline:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def generate_embedding(self, text):
        """Generate embedding for text"""
        return self.model.encode(text)
    
    def search_similar(self, query, limit=10):
        """Search for similar telemetry data using vector similarity"""
        query_embedding = self.generate_embedding(query)
        
        # Use pgvector for similarity search
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    nm.id,
                    nm.node_id,
                    nm.metric_type,
                    nm.data,
                    nm.created_at,
                    1 - (embedding <=> %s::vector) as similarity
                FROM telemetry_metricembeddings
                JOIN nodes_nodemetric nm ON telemetry_metricembeddings.metric_id = nm.id
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, [query_embedding.tolist(), query_embedding.tolist(), limit])
            
            results = cursor.fetchall()
        
        return results
    
    def query(self, natural_language_query):
        """Process natural language query"""
        # Find relevant metrics
        similar_metrics = self.search_similar(natural_language_query)
        
        # Get related events
        events = NodeEvent.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=7)
        ).order_by('-created_at')[:50]
        
        # Prepare context
        context = {
            'query': natural_language_query,
            'similar_metrics': [
                {
                    'node_id': r[1],
                    'metric_type': r[2],
                    'data': r[3],
                    'timestamp': r[4],
                    'similarity': r[5]
                }
                for r in similar_metrics
            ],
            'recent_events': [
                {
                    'node_id': e.node_id,
                    'severity': e.severity,
                    'title': e.title,
                    'message': e.message,
                    'timestamp': e.created_at
                }
                for e in events
            ]
        }
        
        return context