import React, { useState } from 'react';
import { Search, Bell, User, Moon, Sun, Wifi } from 'lucide-react';
import { Command } from 'cmdk';
import { useTheme } from '../../hooks/useTheme';

export function TopCommandBar() {
    const [open, setOpen] = useState(false);
    const { theme, toggleTheme } = useTheme();

    React.useEffect(() => {
        const down = (e) => {
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setOpen((open) => !open);
            }
        };
        document.addEventListener('keydown', down);
        return () => document.removeEventListener('keydown', down);
    }, []);

    return (
        <>
            <div className="h-16 bg-bg-secondary border-b border-border-primary fixed top-0 left-64 right-0 z-10">
                <div className="flex items-center justify-between h-full px-6">
                    <div className="flex-1 max-w-2xl">
                        <button
                            onClick={() => setOpen(true)}
                            className="w-full flex items-center space-x-3 px-4 py-2 bg-bg-tertiary rounded-lg border border-border-subtle text-text-muted hover:text-text-secondary transition-colors"
                        >
                            <Search className="w-4 h-4" />
                            <span className="text-sm">Search anything... (Cmd+K)</span>
                        </button>
                    </div>

                    <div className="flex items-center space-x-4">
                        <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-bg-tertiary rounded-lg transition-colors">
                            <Wifi className="w-5 h-5" />
                        </button>
                        <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-bg-tertiary rounded-lg transition-colors relative">
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-1 right-1 w-2 h-2 bg-status-critical rounded-full" />
                        </button>
                        <button
                            onClick={toggleTheme}
                            className="p-2 text-text-secondary hover:text-text-primary hover:bg-bg-tertiary rounded-lg transition-colors"
                        >
                            {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                        </button>
                        <button className="flex items-center space-x-3 px-3 py-2 hover:bg-bg-tertiary rounded-lg transition-colors">
                            <div className="w-8 h-8 bg-brand-primary rounded-full flex items-center justify-center">
                                <User className="w-4 h-4" />
                            </div>
                            <div className="text-left">
                                <p className="text-sm font-medium">Admin User</p>
                                <p className="text-xs text-text-muted">admin@satori.io</p>
                            </div>
                        </button>
                    </div>
                </div>
            </div>

            <Command.Dialog open={open} onOpenChange={setOpen} label="Global Command Menu">
                <div className="fixed inset-0 bg-black/50 z-50">
                    <div className="fixed top-20 left-1/2 -translate-x-1/2 w-full max-w-2xl">
                        <div className="bg-bg-secondary rounded-lg border border-border-primary shadow-elevated">
                            <Command.Input
                                placeholder="Search commands, nodes, metrics..."
                                className="w-full px-6 py-4 bg-transparent border-b border-border-primary text-text-primary placeholder-text-muted focus:outline-none"
                            />
                            <Command.List className="max-h-96 overflow-y-auto p-2">
                                <Command.Empty className="py-6 text-center text-text-muted">
                                    No results found.
                                </Command.Empty>

                                <Command.Group heading="Navigation" className="text-text-secondary">
                                    <Command.Item className="px-4 py-2 hover:bg-bg-tertiary rounded cursor-pointer">
                                        Go to Dashboard
                                    </Command.Item>
                                    <Command.Item className="px-4 py-2 hover:bg-bg-tertiary rounded cursor-pointer">
                                        View Nodes
                                    </Command.Item>
                                    <Command.Item className="px-4 py-2 hover:bg-bg-tertiary rounded cursor-pointer">
                                        AI Query Interface
                                    </Command.Item>
                                </Command.Group>

                                <Command.Group heading="Actions" className="text-text-secondary mt-2">
                                    <Command.Item className="px-4 py-2 hover:bg-bg-tertiary rounded cursor-pointer">
                                        Run Health Check
                                    </Command.Item>
                                    <Command.Item className="px-4 py-2 hover:bg-bg-tertiary rounded cursor-pointer">
                                        Generate Report
                                    </Command.Item>
                                    <Command.Item className="px-4 py-2 hover:bg-bg-tertiary rounded cursor-pointer">
                                        Isolate Node
                                    </Command.Item>
                                </Command.Group>
                            </Command.List>
                        </div>
                    </div>
                </div>
            </Command.Dialog>
        </>
    );
}