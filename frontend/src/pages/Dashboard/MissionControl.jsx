import React, { useState, useEffect } from 'react';
import {
    LineChart, Line, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { Activity, Cpu, HardDrive, AlertTriangle, Zap, Wifi } from 'lucide-react';

const mockMetrics = [
    { time: '00:00', cpu: 45, memory: 62, network: 78 },
    { time: '00:05', cpu: 52, memory: 65, network: 82 },
    { time: '00:10', cpu: 48, memory: 63, network: 75 },
    { time: '00:15', cpu: 61, memory: 71, network: 88 },
    { time: '00:20', cpu: 55, memory: 68, network: 84 },
    { time: '00:25', cpu: 47, memory: 64, network: 79 },
];

const clusterHealth = [
    { name: 'Healthy', value: 8, color: '#22c55e' },
    { name: 'Warning', value: 2, color: '#f59e0b' },
    { name: 'Critical', value: 1, color: '#ef4444' },
    { name: 'Offline', value: 1, color: '#6b7280' },
];

export function MissionControl() {
    const [metrics, setMetrics] = useState(mockMetrics);
    const [lastUpdated, setLastUpdated] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => {
            // Simulate real-time updates
            setMetrics(prev => {
                const newMetrics = [...prev.slice(1), {
                    time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
                    cpu: Math.floor(Math.random() * 40) + 40,
                    memory: Math.floor(Math.random() * 30) + 50,
                    network: Math.floor(Math.random() * 30) + 60,
                }];
                return newMetrics;
            });
            setLastUpdated(new Date());
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Mission Control</h1>
                    <p className="text-text-muted mt-1">
                        Last updated: {lastUpdated.toLocaleTimeString()}
                    </p>
                </div>
                <div className="flex items-center space-x-3">
                    <span className="flex items-center text-status-healthy">
                        <Wifi className="w-4 h-4 mr-2" />
                        12 Nodes Online
                    </span>
                </div>
            </div>

            {/* Cluster Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-text-muted text-sm">Total Nodes</p>
                            <p className="text-3xl font-bold mt-1">12</p>
                        </div>
                        <div className="p-3 bg-brand-primary/10 rounded-lg">
                            <Server className="w-6 h-6 text-brand-primary" />
                        </div>
                    </div>
                    <div className="mt-4 flex items-center text-xs text-text-muted">
                        <span className="text-status-healthy">+2</span>
                        <span className="ml-1">new this hour</span>
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-text-muted text-sm">Active Alerts</p>
                            <p className="text-3xl font-bold mt-1">4</p>
                        </div>
                        <div className="p-3 bg-status-critical/10 rounded-lg">
                            <AlertTriangle className="w-6 h-6 text-status-critical" />
                        </div>
                    </div>
                    <div className="mt-4 flex items-center text-xs">
                        <span className="text-status-critical">2 critical</span>
                        <span className="text-status-warning ml-2">2 warning</span>
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-text-muted text-sm">Avg CPU Usage</p>
                            <p className="text-3xl font-bold mt-1">54%</p>
                        </div>
                        <div className="p-3 bg-chart-1/10 rounded-lg">
                            <Cpu className="w-6 h-6 text-chart-1" />
                        </div>
                    </div>
                    <div className="mt-4">
                        <div className="w-full h-1 bg-bg-tertiary rounded-full overflow-hidden">
                            <div className="h-full bg-chart-1 rounded-full" style={{ width: '54%' }} />
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-text-muted text-sm">Anomaly Score</p>
                            <p className="text-3xl font-bold mt-1">23</p>
                        </div>
                        <div className="p-3 bg-chart-2/10 rounded-lg">
                            <Zap className="w-6 h-6 text-chart-2" />
                        </div>
                    </div>
                    <div className="mt-4 text-xs text-text-muted">
                        <span className="text-status-healthy">↓ 12%</span> from baseline
                    </div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Metrics Chart */}
                <div className="card lg:col-span-2">
                    <h3 className="text-lg font-medium mb-4">Real-Time Telemetry</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={metrics}>
                            <defs>
                                <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                            <XAxis dataKey="time" stroke="#6b7280" />
                            <YAxis stroke="#6b7280" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1f2937',
                                    border: '1px solid #374151',
                                    borderRadius: '6px'
                                }}
                            />
                            <Area type="monotone" dataKey="cpu" stroke="#06b6d4" fillOpacity={1} fill="url(#colorCpu)" />
                            <Area type="monotone" dataKey="memory" stroke="#7c3aed" fillOpacity={1} fill="url(#colorMemory)" />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Cluster Health Pie */}
                <div className="card">
                    <h3 className="text-lg font-medium mb-4">Cluster Health</h3>
                    <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                            <Pie
                                data={clusterHealth}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {clusterHealth.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="mt-4 grid grid-cols-2 gap-2">
                        {clusterHealth.map((item) => (
                            <div key={item.name} className="flex items-center justify-between text-sm">
                                <div className="flex items-center">
                                    <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: item.color }} />
                                    <span className="text-text-muted">{item.name}</span>
                                </div>
                                <span className="font-medium">{item.value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Alerts */}
            <div className="card">
                <h3 className="text-lg font-medium mb-4">Recent Alerts</h3>
                <div className="space-y-3">
                    {[
                        { severity: 'critical', node: 'node-03', message: 'High CPU usage (94%)', time: '2 min ago' },
                        { severity: 'warning', node: 'node-07', message: 'Memory pressure detected', time: '5 min ago' },
                        { severity: 'warning', node: 'node-12', message: 'Network latency spike', time: '12 min ago' },
                        { severity: 'info', node: 'node-04', message: 'System updated successfully', time: '25 min ago' },
                    ].map((alert, i) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                            <div className="flex items-center space-x-3">
                                <div className={`w-2 h-2 rounded-full bg-status-${alert.severity}`} />
                                <span className="text-sm font-medium">{alert.node}</span>
                                <span className="text-sm text-text-secondary">{alert.message}</span>
                            </div>
                            <span className="text-xs text-text-muted">{alert.time}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* AI Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="ai-panel">
                    <h3 className="text-lg font-medium mb-4 flex items-center">
                        <Bot className="w-5 h-5 mr-2 text-brand-accent" />
                        AI Insight Summary
                    </h3>
                    <p className="text-text-secondary">
                        Detected correlation between CPU spikes on node-03 and node-07.
                        Both nodes are running the same batch processing job. Consider
                        staggering job schedules to reduce load.
                    </p>
                    <div className="mt-4 flex items-center justify-between">
                        <span className="text-xs text-text-muted">Confidence: 87%</span>
                        <button className="btn-secondary text-sm py-1.5">View Details</button>
                    </div>
                </div>

                <div className="card">
                    <h3 className="text-lg font-medium mb-4">Agent Recommendations</h3>
                    <div className="space-y-3">
                        {[
                            { action: 'Redistribute tasks', impact: 'Reduce CPU load', risk: 'low' },
                            { action: 'Scale down logging', impact: 'Free up disk space', risk: 'low' },
                            { action: 'Isolate suspicious process', impact: 'Security', risk: 'high' },
                        ].map((rec, i) => (
                            <div key={i} className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
                                <div>
                                    <p className="text-sm font-medium">{rec.action}</p>
                                    <p className="text-xs text-text-muted">{rec.impact}</p>
                                </div>
                                <span className={`text-xs px-2 py-1 rounded-full ${rec.risk === 'high' ? 'bg-status-critical/10 text-status-critical' : 'bg-status-info/10 text-status-info'
                                    }`}>
                                    {rec.risk} risk
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}