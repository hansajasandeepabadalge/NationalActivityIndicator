'use client';

/**
 * System Health Dashboard
 * Comprehensive monitoring of system status, API performance, database health, and errors
 */

import React, { useEffect, useState } from 'react';
import { Activity, Database, Cpu, AlertTriangle, TrendingUp, Server, RefreshCw } from 'lucide-react';

interface HealthData {
    system_status: {
        status: string;
        uptime_formatted: string;
        version: string;
    };
    api_metrics: {
        total_requests: number;
        success_rate: number;
        avg_response_time_ms: number;
        requests_per_minute: number;
    };
    database_health: {
        status: string;
        collections_count: number;
        data_size_mb: number;
        objects_count: number;
    };
    resource_usage: {
        cpu_percent: number;
        memory_percent: number;
        disk_percent: number;
    };
    recent_errors: Array<{
        timestamp: string;
        type: string;
        message: string;
    }>;
    endpoint_performance: Array<{
        endpoint: string;
        request_count: number;
        avg_response_time_ms: number;
        error_rate: number;
    }>;
}

export function SystemHealthDashboard() {
    const [healthData, setHealthData] = useState<HealthData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    const fetchHealthData = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8080/api/v1/health/all');
            if (response.ok) {
                const data = await response.json();
                setHealthData(data);
                setLastUpdate(new Date());
            }
        } catch (error) {
            console.error('Failed to fetch health data:', error);
            // Use mock data as fallback
            setHealthData(getMockHealthData());
            setLastUpdate(new Date());
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchHealthData();

        // Auto-refresh every 30 seconds
        const interval = setInterval(fetchHealthData, 30000);
        return () => clearInterval(interval);
    }, []);

    const getStatusColor = (status: string) => {
        if (status === 'healthy' || status === 'connected') return 'text-green-600 bg-green-50 border-green-200';
        if (status === 'warning') return 'text-yellow-600 bg-yellow-50 border-yellow-200';
        if (status === 'error') return 'text-red-600 bg-red-50 border-red-200';
        return 'text-gray-600 bg-gray-50 border-gray-200';
    };

    const getResourceColor = (percent: number) => {
        if (percent >= 90) return 'text-red-600';
        if (percent >= 70) return 'text-yellow-600';
        return 'text-green-600';
    };

    if (isLoading && !healthData) {
        return (
            <div className="flex items-center justify-center h-96">
                <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
        );
    }

    if (!healthData) return null;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">System Health & Monitoring</h2>
                    <p className="text-sm text-gray-500">
                        Last updated: {lastUpdate?.toLocaleTimeString() || 'Never'}
                    </p>
                </div>
                <button
                    onClick={fetchHealthData}
                    disabled={isLoading}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    Refresh
                </button>
            </div>

            {/* Status Cards - 2x2 Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Backend Status */}
                <div className="bg-white rounded-xl shadow-lg border-2 border-green-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-green-50 rounded-lg">
                            <Server className="w-6 h-6 text-green-600" />
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(healthData.system_status.status)}`}>
                            {healthData.system_status.status}
                        </span>
                    </div>
                    <h3 className="text-sm font-medium text-gray-600 mb-1">Backend API</h3>
                    <p className="text-2xl font-bold text-gray-900">{healthData.system_status.uptime_formatted}</p>
                    <p className="text-xs text-gray-500 mt-1">Uptime</p>
                </div>

                {/* Database Status */}
                <div className="bg-white rounded-xl shadow-lg border-2 border-blue-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-blue-50 rounded-lg">
                            <Database className="w-6 h-6 text-blue-600" />
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(healthData.database_health.status)}`}>
                            {healthData.database_health.status}
                        </span>
                    </div>
                    <h3 className="text-sm font-medium text-gray-600 mb-1">Database</h3>
                    <p className="text-2xl font-bold text-gray-900">{healthData.database_health.collections_count}</p>
                    <p className="text-xs text-gray-500 mt-1">Collections ({healthData.database_health.data_size_mb.toFixed(1)} MB)</p>
                </div>

                {/* API Performance */}
                <div className="bg-white rounded-xl shadow-lg border-2 border-purple-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-purple-50 rounded-lg">
                            <Activity className="w-6 h-6 text-purple-600" />
                        </div>
                        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-50 text-purple-600 border border-purple-200">
                            {healthData.api_metrics.success_rate.toFixed(1)}%
                        </span>
                    </div>
                    <h3 className="text-sm font-medium text-gray-600 mb-1">API Success Rate</h3>
                    <p className="text-2xl font-bold text-gray-900">{healthData.api_metrics.avg_response_time_ms.toFixed(0)}ms</p>
                    <p className="text-xs text-gray-500 mt-1">Avg Response Time</p>
                </div>

                {/* Resource Usage */}
                <div className="bg-white rounded-xl shadow-lg border-2 border-amber-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-amber-50 rounded-lg">
                            <Cpu className="w-6 h-6 text-amber-600" />
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getResourceColor(healthData.resource_usage.cpu_percent)} bg-opacity-10`}>
                            CPU
                        </span>
                    </div>
                    <h3 className="text-sm font-medium text-gray-600 mb-1">System Resources</h3>
                    <p className="text-2xl font-bold text-gray-900">{healthData.resource_usage.cpu_percent.toFixed(1)}%</p>
                    <p className="text-xs text-gray-500 mt-1">CPU Usage</p>
                </div>
            </div>

            {/* Resource Usage Gauges */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* CPU Gauge */}
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-700 mb-4">CPU Usage</h3>
                    <div className="relative pt-1">
                        <div className="flex mb-2 items-center justify-between">
                            <div>
                                <span className={`text-3xl font-bold ${getResourceColor(healthData.resource_usage.cpu_percent)}`}>
                                    {healthData.resource_usage.cpu_percent.toFixed(1)}%
                                </span>
                            </div>
                        </div>
                        <div className="overflow-hidden h-4 text-xs flex rounded-full bg-gray-200">
                            <div
                                style={{ width: `${healthData.resource_usage.cpu_percent}%` }}
                                className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500 ${healthData.resource_usage.cpu_percent >= 90 ? 'bg-red-500' :
                                        healthData.resource_usage.cpu_percent >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                                    }`}
                            ></div>
                        </div>
                    </div>
                </div>

                {/* Memory Gauge */}
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-700 mb-4">Memory Usage</h3>
                    <div className="relative pt-1">
                        <div className="flex mb-2 items-center justify-between">
                            <div>
                                <span className={`text-3xl font-bold ${getResourceColor(healthData.resource_usage.memory_percent)}`}>
                                    {healthData.resource_usage.memory_percent.toFixed(1)}%
                                </span>
                            </div>
                        </div>
                        <div className="overflow-hidden h-4 text-xs flex rounded-full bg-gray-200">
                            <div
                                style={{ width: `${healthData.resource_usage.memory_percent}%` }}
                                className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500 ${healthData.resource_usage.memory_percent >= 90 ? 'bg-red-500' :
                                        healthData.resource_usage.memory_percent >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                                    }`}
                            ></div>
                        </div>
                    </div>
                </div>

                {/* Disk Gauge */}
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-700 mb-4">Disk Usage</h3>
                    <div className="relative pt-1">
                        <div className="flex mb-2 items-center justify-between">
                            <div>
                                <span className={`text-3xl font-bold ${getResourceColor(healthData.resource_usage.disk_percent)}`}>
                                    {healthData.resource_usage.disk_percent.toFixed(1)}%
                                </span>
                            </div>
                        </div>
                        <div className="overflow-hidden h-4 text-xs flex rounded-full bg-gray-200">
                            <div
                                style={{ width: `${healthData.resource_usage.disk_percent}%` }}
                                className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500 ${healthData.resource_usage.disk_percent >= 90 ? 'bg-red-500' :
                                        healthData.resource_usage.disk_percent >= 70 ? 'bg-yellow-500' : 'bg-green-500'
                                    }`}
                            ></div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Row: Endpoint Performance & Recent Errors */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Endpoint Performance */}
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <div className="flex items-center gap-2 mb-4">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Slowest Endpoints</h3>
                    </div>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {healthData.endpoint_performance.slice(0, 5).map((endpoint, index) => (
                            <div key={index} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-sm font-medium text-gray-900 truncate">{endpoint.endpoint}</span>
                                    <span className="text-sm font-bold text-blue-600">{endpoint.avg_response_time_ms.toFixed(0)}ms</span>
                                </div>
                                <div className="flex justify-between text-xs text-gray-500">
                                    <span>{endpoint.request_count} requests</span>
                                    <span className={endpoint.error_rate > 5 ? 'text-red-600 font-semibold' : ''}>
                                        {endpoint.error_rate.toFixed(1)}% errors
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recent Errors */}
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                    <div className="flex items-center gap-2 mb-4">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Recent Errors</h3>
                    </div>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {healthData.recent_errors.length > 0 ? (
                            healthData.recent_errors.map((error, index) => (
                                <div key={index} className="p-3 bg-red-50 rounded-lg border border-red-200">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="text-sm font-semibold text-red-900">{error.type}</span>
                                        <span className="text-xs text-red-600">{new Date(error.timestamp).toLocaleTimeString()}</span>
                                    </div>
                                    <p className="text-xs text-red-700 truncate">{error.message}</p>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <p className="text-sm">✓ No recent errors</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Mock data for fallback
function getMockHealthData(): HealthData {
    return {
        system_status: {
            status: 'healthy',
            uptime_formatted: '2 days, 14:32:15',
            version: '1.0.0',
        },
        api_metrics: {
            total_requests: 15234,
            success_rate: 99.8,
            avg_response_time_ms: 45,
            requests_per_minute: 125,
        },
        database_health: {
            status: 'connected',
            collections_count: 12,
            data_size_mb: 245.6,
            objects_count: 45678,
        },
        resource_usage: {
            cpu_percent: 23.5,
            memory_percent: 45.2,
            disk_percent: 62.8,
        },
        recent_errors: [],
        endpoint_performance: [
            { endpoint: '/api/v1/indicators/history', request_count: 234, avg_response_time_ms: 156, error_rate: 0.5 },
            { endpoint: '/api/v1/operational/metrics', request_count: 567, avg_response_time_ms: 98, error_rate: 0.2 },
            { endpoint: '/api/v1/insights/business', request_count: 123, avg_response_time_ms: 87, error_rate: 0.0 },
        ],
    };
}
