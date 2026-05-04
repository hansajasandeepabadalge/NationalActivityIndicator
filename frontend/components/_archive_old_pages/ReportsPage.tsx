"use client";
import {
    Plus,
    Edit2,
    FileText,
    Download,
    Eye,
    RefreshCw,
    Clock,
    Trash2, Calendar
} from 'lucide-react';
import {useState} from "react";

export default function ReportsPage() {
    const [reportType, setReportType] = useState('complete');
    const [includeOptions, setIncludeOptions] = useState({
        executiveSummary: true,
        keyInsights: true,
        trendCharts: true,
        recommendations: true,
        detailedData: false,
        appendix: false
    });
    const [format, setFormat] = useState('pdf');

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Reports & Analytics</h1>

            {/* Quick Reports */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Quick Reports (Pre-configured)</h2>
                <div className="grid grid-cols-3 gap-4">
                    {[
                        { name: 'Daily Summary', desc: '1-2 page overview' },
                        { name: 'Weekly Report', desc: '5-7 page analysis' },
                        { name: 'Monthly Overview', desc: '10-15 page report' }
                    ].map((report, i) => (
                        <div key={i} className="p-6 bg-slate-900/50 rounded-xl border border-slate-700 hover:border-slate-600 transition-colors">
                            <h3 className="font-semibold text-white mb-1">{report.name}</h3>
                            <p className="text-sm text-slate-500 mb-4">{report.desc}</p>
                            <div className="flex gap-2">
                                <button className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors text-sm font-medium">
                                    Generate
                                </button>
                                <button className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-1">
                                    <Calendar className="w-3 h-3" />
                                    Schedule
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Custom Report Builder */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                <h2 className="text-lg font-semibold text-white mb-6">Custom Report Builder</h2>

                <div className="grid grid-cols-2 gap-8">
                    <div>
                        <h3 className="text-sm font-medium text-slate-400 mb-3">Report Type</h3>
                        <div className="space-y-2">
                            {[
                                { id: 'risk', label: 'Risk Analysis' },
                                { id: 'opportunity', label: 'Opportunity Summary' },
                                { id: 'indicators', label: 'Indicator Trends' },
                                { id: 'complete', label: 'Complete Business Health' }
                            ].map(type => (
                                <label key={type.id} className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg cursor-pointer hover:bg-slate-900 transition-colors">
                                    <input
                                        type="radio"
                                        name="reportType"
                                        checked={reportType === type.id}
                                        onChange={() => setReportType(type.id)}
                                        className="w-4 h-4 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-0 bg-slate-700 border-slate-600"
                                    />
                                    <span className="text-white">{type.label}</span>
                                </label>
                            ))}
                        </div>

                        <h3 className="text-sm font-medium text-slate-400 mt-6 mb-3">Time Period</h3>
                        <div className="flex gap-3">
                            <input
                                type="date"
                                className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-indigo-500"
                            />
                            <span className="text-slate-500 self-center">to</span>
                            <input
                                type="date"
                                className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-indigo-500"
                            />
                        </div>
                    </div>

                    <div>
                        <h3 className="text-sm font-medium text-slate-400 mb-3">Include</h3>
                        <div className="space-y-2">
                            {[
                                { key: 'executiveSummary', label: 'Executive Summary' },
                                { key: 'keyInsights', label: 'Key Insights' },
                                { key: 'trendCharts', label: 'Trend Charts' },
                                { key: 'recommendations', label: 'Recommendations' },
                                { key: 'detailedData', label: 'Detailed Data Tables' },
                                { key: 'appendix', label: 'Appendix (Raw Data)' }
                            ].map(opt => (
                                <label key={opt.key} className="flex items-center gap-3 p-3 bg-slate-900/50 rounded-lg cursor-pointer hover:bg-slate-900 transition-colors">
                                    <input
                                        type="checkbox"
                                        checked={includeOptions[opt.key as keyof typeof includeOptions]}
                                        onChange={e => setIncludeOptions({ ...includeOptions, [opt.key]: e.target.checked })}
                                        className="w-4 h-4 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-0 bg-slate-700 border-slate-600 rounded"
                                    />
                                    <span className="text-white">{opt.label}</span>
                                </label>
                            ))}
                        </div>

                        <h3 className="text-sm font-medium text-slate-400 mt-6 mb-3">Format</h3>
                        <div className="flex gap-3">
                            {['pdf', 'excel', 'csv'].map(f => (
                                <button
                                    key={f}
                                    onClick={() => setFormat(f)}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium uppercase transition-colors ${
                                        format === f
                                            ? 'bg-indigo-600 text-white'
                                            : 'bg-slate-700 text-slate-400 hover:text-white'
                                    }`}
                                >
                                    {f}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <button className="mt-6 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors font-medium flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Generate Report
                </button>
            </div>

            {/* Recent Reports */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Recent Reports</h2>
                <div className="space-y-3">
                    {[
                        { date: 'Dec 5, 2025', name: 'Weekly Report', format: 'PDF', time: '2 hours ago' },
                        { date: 'Dec 4, 2025', name: 'Daily Summary', format: 'PDF', time: '1 day ago' },
                        { date: 'Dec 1, 2025', name: 'Monthly Overview', format: 'Excel', time: '5 days ago' }
                    ].map((report, i) => (
                        <div key={i} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-lg bg-indigo-600/20 flex items-center justify-center">
                                    <FileText className="w-5 h-5 text-indigo-400" />
                                </div>
                                <div>
                                    <p className="font-medium text-white">{report.date} | {report.name}</p>
                                    <p className="text-sm text-slate-500">Generated {report.time}</p>
                                </div>
                                <span className="px-2 py-0.5 bg-slate-700 text-slate-400 text-xs rounded font-medium">
                  {report.format}
                </span>
                            </div>
                            <div className="flex items-center gap-2">
                                <button className="p-2 text-slate-400 hover:text-white transition-colors">
                                    <Download className="w-4 h-4" />
                                </button>
                                <button className="p-2 text-slate-400 hover:text-white transition-colors">
                                    <Eye className="w-4 h-4" />
                                </button>
                                <button className="p-2 text-slate-400 hover:text-white transition-colors">
                                    <RefreshCw className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Scheduled Reports */}
            <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Scheduled Reports</h2>
                <div className="p-4 bg-slate-900/50 rounded-lg flex items-center justify-between">
                    <div>
                        <p className="font-medium text-white">Daily Summary - Every day at 8:00 AM</p>
                        <p className="text-sm text-slate-500">Email to: owner@company.com</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <button className="p-2 text-slate-400 hover:text-white transition-colors">
                            <Edit2 className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-slate-400 hover:text-yellow-400 transition-colors">
                            <Clock className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-slate-400 hover:text-red-400 transition-colors">
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>
                <button className="mt-4 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Add New Schedule
                </button>
            </div>
        </div>
    );
};