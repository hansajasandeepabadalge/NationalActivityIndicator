"use client";
import {useState} from "react";
import SeverityBadge from "@/components/utility/SeverityBadge";
import {Check, ChevronDown, Settings} from "lucide-react";
import { mockAlerts } from "@/data/mockAlerts";

export default function AlertsPage(){
    const [alerts, setAlerts] = useState(mockAlerts);
    const [filter, setFilter] = useState('all');

    const markAsRead = (id: string) => {
        setAlerts(alerts.map(a => a.id === id ? { ...a, read: true } : a));
    };

    const markAllAsRead = () => {
        setAlerts(alerts.map(a => ({ ...a, read: true })));
    };

    const unreadCount = alerts.filter(a => !a.read).length;
    const criticalCount = alerts.filter(a => a.severity === 'critical').length;
    const highCount = alerts.filter(a => a.severity === 'high').length;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Alerts & Notifications</h1>
                <button
                    onClick={markAllAsRead}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
                >
                    <Check className="w-4 h-4" />
                    Mark All as Read
                </button>
            </div>

            {/* Alert Filters */}
            <div className="flex items-center gap-2 p-2 bg-slate-800/50 rounded-xl border border-slate-700/50 w-fit">
                <button
                    onClick={() => setFilter('all')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        filter === 'all' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                >
                    All ({alerts.length})
                </button>
                <button
                    onClick={() => setFilter('unread')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        filter === 'unread' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                >
                    Unread ({unreadCount})
                </button>
                <button
                    onClick={() => setFilter('critical')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        filter === 'critical' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                >
                    Critical ({criticalCount})
                </button>
                <button
                    onClick={() => setFilter('high')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        filter === 'high' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                    }`}
                >
                    High ({highCount})
                </button>
            </div>

            {/* Active Alerts */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white">Active Alerts</h2>

                {alerts
                    .filter(alert => {
                        if (filter === 'unread') return !alert.read;
                        if (filter === 'critical') return alert.severity === 'critical';
                        if (filter === 'high') return alert.severity === 'high';
                        return true;
                    })
                    .map(alert => (
                        <div
                            key={alert.id}
                            className={`rounded-xl border p-6 transition-colors ${
                                alert.read
                                    ? 'bg-slate-800/30 border-slate-700/50'
                                    : 'bg-slate-800/50 border-slate-600/50'
                            }`}
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-3">
                                    <SeverityBadge severity={alert.severity} />
                                    <span className="text-sm text-slate-500">{alert.time}</span>
                                    {!alert.read && (
                                        <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-400 text-xs rounded-full font-medium">
                      UNREAD
                    </span>
                                    )}
                                </div>
                            </div>

                            <h3 className={`text-lg font-semibold mb-2 ${alert.read ? 'text-slate-300' : 'text-white'}`}>
                                {alert.title}
                            </h3>
                            <p className="text-slate-400 mb-4">{alert.description}</p>

                            {alert.recommendations && (
                                <div className="mb-4 p-4 bg-slate-900/50 rounded-lg">
                                    <p className="text-sm font-medium text-white mb-2">Recommended Actions:</p>
                                    <ol className="space-y-1">
                                        {alert.recommendations.map((rec, i) => (
                                            <li key={i} className="text-sm text-slate-400 flex items-start gap-2">
                                                <span className="text-indigo-400 font-medium">{i + 1}.</span>
                                                {rec}
                                            </li>
                                        ))}
                                    </ol>
                                </div>
                            )}

                            <div className="flex items-center gap-3">
                                <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-medium">
                                    View Full Details
                                </button>
                                {!alert.read && (
                                    <button
                                        onClick={() => markAsRead(alert.id)}
                                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium"
                                    >
                                        Mark as Read
                                    </button>
                                )}
                                <button className="px-4 py-2 text-slate-400 hover:text-white transition-colors text-sm">
                                    Dismiss
                                </button>
                            </div>
                        </div>
                    ))}
            </div>

            {/* Alert History */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">Alert History</h3>
                    <div className="relative">
                        <select className="appearance-none bg-slate-700 text-white px-4 py-2 pr-10 rounded-lg border border-slate-600 focus:outline-none focus:border-indigo-500 text-sm">
                            <option>Last 7 days</option>
                            <option>Last 30 days</option>
                            <option>Last 90 days</option>
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-slate-900/50 rounded-lg">
                        <p className="text-2xl font-bold text-white">23</p>
                        <p className="text-sm text-slate-400">Resolved Alerts</p>
                    </div>
                    <div className="p-4 bg-slate-900/50 rounded-lg">
                        <p className="text-2xl font-bold text-white">12</p>
                        <p className="text-sm text-slate-400">Dismissed Alerts</p>
                    </div>
                </div>
                <button className="mt-4 text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">
                    View History →
                </button>
            </div>

            {/* Notification Settings */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Notification Settings</h3>
                <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-2">
                    <Settings className="w-4 h-4" />
                    Configure Alert Preferences
                </button>
            </div>
        </div>
    );
};