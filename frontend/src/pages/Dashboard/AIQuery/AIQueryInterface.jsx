import React, { useState } from 'react';
import { Send, Bot, FileText, TrendingUp, Shield, Clock, CheckCircle, XCircle } from 'lucide-react';

export function AIQueryInterface() {
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);

        // Simulate API call
        setTimeout(() => {
            setResponse({
                answer: "Based on the telemetry data, the temperature spike at 14:23 UTC coincided with increased CPU activity from the data processing job on node-03. Battery voltage dropped from 12.4V to 11.8V during this period, which is within normal operating parameters. The anomaly appears to be related to the scheduled batch processing task.",
                confidence: 92,
                evidence: [
                    { type: 'metric', title: 'CPU Usage', value: '94% at 14:23', relevance: 'high' },
                    { type: 'metric', title: 'Temperature', value: '72°C at 14:23', relevance: 'high' },
                    { type: 'metric', title: 'Battery Voltage', value: '11.8V', relevance: 'medium' },
                    { type: 'log', title: 'System Log', value: 'CPU frequency scaled down due to thermal throttle', relevance: 'high' },
                ],
                timeWindow: '14:20 - 14:30 UTC',
                relatedNodes: ['node-03', 'node-07']
            });
            setIsLoading(false);
        }, 2000);
    };

    return (
        <div className="p-6 h-full flex flex-col">
            <div className="mb-6">
                <h1 className="text-3xl font-bold">AI Query Interface</h1>
                <p className="text-text-muted mt-1">
                    Ask questions about your telemetry data in natural language
                </p>
            </div>

            <div className="flex-1 flex flex-col lg:flex-row gap-6">
                {/* Query Section */}
                <div className="lg:w-1/2 space-y-4">
                    <div className="card">
                        <form onSubmit={handleSubmit}>
                            <div className="relative">
                                <textarea
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    placeholder="Ask a question... (e.g., 'What was the altitude and battery voltage when the temperature spike occurred?')"
                                    className="input min-h-[120px] pr-12"
                                />
                                <button
                                    type="submit"
                                    disabled={isLoading}
                                    className="absolute bottom-3 right-3 p-2 bg-brand-primary rounded-lg hover:bg-brand-primary/80 transition-colors disabled:opacity-50"
                                >
                                    <Send className="w-4 h-4" />
                                </button>
                            </div>
                        </form>

                        <div className="mt-4">
                            <h4 className="text-sm font-medium mb-2">Example Queries:</h4>
                            <div className="space-y-2">
                                {[
                                    "Show anomalies in the last flight",
                                    "What caused the memory spike on node-03?",
                                    "Compare CPU usage across all nodes",
                                    "Any security incidents in the last 24 hours?"
                                ].map((example, i) => (
                                    <button
                                        key={i}
                                        onClick={() => setQuery(example)}
                                        className="block w-full text-left p-2 text-sm text-text-secondary hover:text-text-primary hover:bg-bg-tertiary rounded transition-colors"
                                    >
                                        "{example}"
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Recent Queries */}
                    <div className="card">
                        <h3 className="text-lg font-medium mb-3">Recent Queries</h3>
                        <div className="space-y-2">
                            {[
                                { query: "CPU usage trends last 6 hours", time: "10 min ago" },
                                { query: "Failed login attempts", time: "25 min ago" },
                                { query: "Container performance metrics", time: "1 hour ago" },
                            ].map((item, i) => (
                                <div key={i} className="flex items-center justify-between p-2 hover:bg-bg-tertiary rounded cursor-pointer">
                                    <span className="text-sm">{item.query}</span>
                                    <span className="text-xs text-text-muted">{item.time}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Response Section */}
                <div className="lg:w-1/2">
                    {isLoading ? (
                        <div className="card flex items-center justify-center py-12">
                            <div className="text-center">
                                <Bot className="w-12 h-12 text-brand-accent animate-pulse mx-auto mb-4" />
                                <p className="text-text-secondary">Analyzing telemetry data...</p>
                            </div>
                        </div>
                    ) : response ? (
                        <div className="space-y-4">
                            {/* Answer Card */}
                            <div className="ai-panel">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center">
                                        <Bot className="w-5 h-5 text-brand-accent mr-2" />
                                        <h3 className="text-lg font-medium">Analysis Result</h3>
                                    </div>
                                    <div className="flex items-center px-3 py-1 bg-bg-tertiary rounded-full">
                                        <span className="text-sm mr-2">Confidence</span>
                                        <span className="font-medium text-status-healthy">{response.confidence}%</span>
                                    </div>
                                </div>
                                <p className="text-text-secondary leading-relaxed">{response.answer}</p>

                                <div className="mt-4 flex items-center space-x-4 text-sm">
                                    <span className="flex items-center text-text-muted">
                                        <Clock className="w-4 h-4 mr-1" />
                                        {response.timeWindow}
                                    </span>
                                    <span className="flex items-center text-text-muted">
                                        <TrendingUp className="w-4 h-4 mr-1" />
                                        {response.relatedNodes.length} nodes involved
                                    </span>
                                </div>
                            </div>

                            {/* Evidence Panel */}
                            <div className="card">
                                <h3 className="text-lg font-medium mb-4">Retrieved Evidence</h3>
                                <div className="space-y-3">
                                    {response.evidence.map((item, i) => (
                                        <div key={i} className="p-3 bg-bg-tertiary rounded-lg">
                                            <div className="flex items-center justify-between mb-2">
                                                <div className="flex items-center">
                                                    {item.type === 'metric' ? (
                                                        <TrendingUp className="w-4 h-4 text-chart-1 mr-2" />
                                                    ) : (
                                                        <FileText className="w-4 h-4 text-chart-2 mr-2" />
                                                    )}
                                                    <span className="text-sm font-medium">{item.title}</span>
                                                </div>
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${item.relevance === 'high'
                                                        ? 'bg-status-healthy/10 text-status-healthy'
                                                        : 'bg-status-info/10 text-status-info'
                                                    }`}>
                                                    {item.relevance} relevance
                                                </span>
                                            </div>
                                            <p className="text-sm text-text-secondary">{item.value}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Suggested Actions */}
                            <div className="card">
                                <h3 className="text-lg font-medium mb-4">Suggested Actions</h3>
                                <div className="space-y-2">
                                    <button className="w-full p-3 bg-bg-tertiary hover:bg-bg-tertiary/80 rounded-lg text-left transition-colors">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="font-medium">Adjust batch job schedule</p>
                                                <p className="text-sm text-text-muted">Move job to off-peak hours</p>
                                            </div>
                                            <CheckCircle className="w-5 h-5 text-status-healthy" />
                                        </div>
                                    </button>
                                    <button className="w-full p-3 bg-bg-tertiary hover:bg-bg-tertiary/80 rounded-lg text-left transition-colors">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="font-medium">Scale down logging verbosity</p>
                                                <p className="text-sm text-text-muted">Reduce I/O during peak loads</p>
                                            </div>
                                            <Shield className="w-5 h-5 text-status-warning" />
                                        </div>
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="card flex items-center justify-center py-12 text-center">
                            <div>
                                <Bot className="w-16 h-16 text-text-muted mx-auto mb-4" />
                                <h3 className="text-xl font-medium mb-2">Ready to help</h3>
                                <p className="text-text-muted">
                                    Ask a question about your telemetry data and I'll analyze it for you
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}