import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Server,
    Activity,
    FileText,
    Bot,
    AlertTriangle,
    Database,
    Shield,
    Settings,
    Users
} from 'lucide-react';
import clsx from 'clsx';

const navigation = [
    { name: 'Mission Control', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Nodes', href: '/nodes', icon: Server },
    { name: 'Telemetry Explorer', href: '/telemetry', icon: Activity },
    { name: 'Log Search', href: '/logs', icon: FileText },
    { name: 'AI Query', href: '/ai', icon: Bot },
    { name: 'Agent Mode', href: '/agent', icon: Bot },
    { name: 'Alerts & Incidents', href: '/alerts', icon: AlertTriangle },
    { name: 'Storage', href: '/storage', icon: Database },
    { name: 'Security', href: '/settings/security', icon: Shield },
    { name: 'Configuration', href: '/settings/system', icon: Settings },
    { name: 'Organization', href: '/settings/org', icon: Users },
];

export function Sidebar() {
    return (
        <div className="w-64 bg-bg-secondary border-r border-border-primary h-screen fixed left-0 top-0 overflow-y-auto">
            <div className="p-6">
                <h1 className="text-2xl font-bold text-brand-accent">SATORI</h1>
                <p className="text-xs text-text-muted mt-1">System Analysis & Response</p>
            </div>

            <nav className="px-4 space-y-1">
                {navigation.map((item) => (
                    <NavLink
                        key={item.name}
                        to={item.href}
                        className={({ isActive }) =>
                            clsx(
                                'flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors',
                                isActive
                                    ? 'bg-bg-tertiary text-brand-accent'
                                    : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary'
                            )
                        }
                    >
                        <item.icon className="w-5 h-5 mr-3" />
                        {item.name}
                    </NavLink>
                ))}
            </nav>

            <div className="absolute bottom-0 left-0 right-0 p-4">
                <div className="flex items-center space-x-3 px-4 py-3 bg-bg-tertiary rounded-lg">
                    <div className="w-2 h-2 bg-status-healthy rounded-full animate-pulse" />
                    <div className="flex-1">
                        <p className="text-xs text-text-secondary">Connected</p>
                        <p className="text-sm font-medium">System Online</p>
                    </div>
                </div>
            </div>
        </div>
    );
}