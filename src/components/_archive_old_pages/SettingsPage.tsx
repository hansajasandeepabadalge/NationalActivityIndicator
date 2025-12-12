"use client";
import { Activity, Mail, MessageSquare, Plus, Edit2 } from 'lucide-react';
import { useState } from "react";

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState('Company Profile');
    const [notifications, setNotifications] = useState({
        dashboard: true,
        email: true,
        sms: true
    });

    const tabs = ['Company Profile', 'Alert Settings', 'Team', 'Integrations'];

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Company Settings</h1>

            {/* Tabs */}
            <div className="flex items-center gap-1 p-1 bg-slate-800/50 rounded-xl border border-slate-700/50 w-fit">
                {tabs.map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            activeTab === tab
                                ? 'bg-indigo-600 text-white'
                                : 'text-slate-400 hover:text-white'
                        }`}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'Company Profile' && (
                <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                    <h2 className="text-lg font-semibold text-white mb-6">Company Profile</h2>
                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <p className="text-sm text-slate-500 mb-1">Company Name</p>
                            <p className="text-white font-medium">ABC Retail Pvt Ltd</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500 mb-1">Industry</p>
                            <p className="text-white font-medium">Retail & E-commerce</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500 mb-1">Business Scale</p>
                            <p className="text-white font-medium">Medium (51-250 employees)</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-500 mb-1">Location</p>
                            <p className="text-white font-medium">Western Province, Colombo</p>
                        </div>
                    </div>
                    <button className="mt-6 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-2">
                        <Edit2 className="w-4 h-4" />
                        Edit Profile
                    </button>
                </div>
            )}

            {activeTab === 'Alert Settings' && (
                <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                    <h2 className="text-lg font-semibold text-white mb-6">Alert Configuration</h2>

                    <div className="mb-6">
                        <p className="text-sm text-slate-400 mb-3">Notification Channels</p>
                        <div className="space-y-3">
                            <label className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                                <div className="flex items-center gap-3">
                                    <Activity className="w-5 h-5 text-slate-400" />
                                    <span className="text-white">Dashboard</span>
                                    <span className="text-xs text-slate-500">(always on)</span>
                                </div>
                                <div className="w-10 h-6 bg-indigo-600 rounded-full relative">
                                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                                </div>
                            </label>
                            <label className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg cursor-pointer">
                                <div className="flex items-center gap-3">
                                    <Mail className="w-5 h-5 text-slate-400" />
                                    <span className="text-white">Email</span>
                                    <span className="text-xs text-slate-500">(owner@company.com)</span>
                                </div>
                                <button
                                    onClick={() => setNotifications({ ...notifications, email: !notifications.email })}
                                    className={`w-10 h-6 rounded-full relative transition-colors ${notifications.email ? 'bg-indigo-600' : 'bg-slate-600'}`}
                                >
                                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${notifications.email ? 'right-1' : 'left-1'}`} />
                                </button>
                            </label>
                            <label className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg cursor-pointer">
                                <div className="flex items-center gap-3">
                                    <MessageSquare className="w-5 h-5 text-slate-400" />
                                    <span className="text-white">SMS</span>
                                    <span className="text-xs text-slate-500">(+94 77 123 4567)</span>
                                </div>
                                <button
                                    onClick={() => setNotifications({ ...notifications, sms: !notifications.sms })}
                                    className={`w-10 h-6 rounded-full relative transition-colors ${notifications.sms ? 'bg-indigo-600' : 'bg-slate-600'}`}
                                >
                                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${notifications.sms ? 'right-1' : 'left-1'}`} />
                                </button>
                            </label>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6 mb-6">
                        <div>
                            <p className="text-sm text-slate-400 mb-2">Frequency</p>
                            <p className="text-white font-medium">Daily digest at 8:00 AM</p>
                        </div>
                        <div>
                            <p className="text-sm text-slate-400 mb-2">Minimum Severity</p>
                            <p className="text-white font-medium">High and above</p>
                        </div>
                    </div>

                    <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-medium">
                        Update Settings
                    </button>
                </div>
            )}

            {activeTab === 'Team' && (
                <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                    <h2 className="text-lg font-semibold text-white mb-6">Team Management</h2>

                    <div className="overflow-hidden rounded-lg border border-slate-700">
                        <table className="w-full">
                            <thead className="bg-slate-900/50">
                            <tr>
                                <th className="text-left text-sm font-medium text-slate-400 px-4 py-3">Name</th>
                                <th className="text-left text-sm font-medium text-slate-400 px-4 py-3">Role</th>
                                <th className="text-left text-sm font-medium text-slate-400 px-4 py-3">Status</th>
                                <th className="text-right text-sm font-medium text-slate-400 px-4 py-3">Actions</th>
                            </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-700">
                            {[
                                { name: 'John Doe', role: 'Owner', status: 'Active' },
                                { name: 'Jane Smith', role: 'Manager', status: 'Active' },
                                { name: 'Bob Wilson', role: 'Viewer', status: 'Active' }
                            ].map((member, i) => (
                                <tr key={i} className="hover:bg-slate-800/50 transition-colors">
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold text-xs">
                                                {member.name.split(' ').map(n => n[0]).join('')}
                                            </div>
                                            <span className="text-white font-medium">{member.name}</span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3 text-slate-400">{member.role}</td>
                                    <td className="px-4 py-3">
                                            <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-full font-medium">
                                                {member.status}
                                            </span>
                                    </td>
                                    <td className="px-4 py-3 text-right">
                                        <button className="p-2 text-slate-400 hover:text-white transition-colors">
                                            <Edit2 className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>

                    <button className="mt-4 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Invite Team Member
                    </button>
                </div>
            )}

            {activeTab === 'Integrations' && (
                <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                    <h2 className="text-lg font-semibold text-white mb-6">Integrations</h2>
                    <p className="text-slate-400">Integration settings coming soon...</p>
                </div>
            )}
        </div>
    );
}
