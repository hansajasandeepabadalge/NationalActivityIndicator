'use client';

/**
 * Sri Lanka Traffic Map Component
 * 
 * Interactive map showing real-time traffic conditions on major highways
 */

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { SRI_LANKA_HIGHWAYS, MOCK_TRAFFIC_INCIDENTS, TrafficRoute, TrafficIncident } from '@/types/traffic';
import { SRI_LANKA_BOUNDS } from '@/types/weather';
import { RefreshCw, Navigation, AlertTriangle, Construction, XCircle } from 'lucide-react';

// Dynamically import map components
const MapContainer = dynamic(
    () => import('react-leaflet').then((mod) => mod.MapContainer),
    { ssr: false }
);
const TileLayer = dynamic(
    () => import('react-leaflet').then((mod) => mod.TileLayer),
    { ssr: false }
);
const Polyline = dynamic(
    () => import('react-leaflet').then((mod) => mod.Polyline),
    { ssr: false }
);
const Marker = dynamic(
    () => import('react-leaflet').then((mod) => mod.Marker),
    { ssr: false }
);
const Popup = dynamic(
    () => import('react-leaflet').then((mod) => mod.Popup),
    { ssr: false }
);

import 'leaflet/dist/leaflet.css';

export function SriLankaTrafficMap() {
    const [trafficData, setTrafficData] = useState<TrafficRoute[]>(SRI_LANKA_HIGHWAYS);
    const [incidents, setIncidents] = useState<TrafficIncident[]>(MOCK_TRAFFIC_INCIDENTS);
    const [isLoading, setIsLoading] = useState(false);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const [L, setL] = useState<any>(null);

    // Load Leaflet library
    useEffect(() => {
        import('leaflet').then((leaflet) => {
            setL(leaflet.default);
        });
    }, []);

    const refreshTrafficData = () => {
        setIsLoading(true);
        // Simulate data refresh with random congestion changes
        setTimeout(() => {
            const updatedRoutes = trafficData.map(route => {
                const congestionLevels: TrafficRoute['congestionLevel'][] = ['free', 'light', 'moderate', 'heavy'];
                const randomLevel = congestionLevels[Math.floor(Math.random() * congestionLevels.length)];
                return {
                    ...route,
                    congestionLevel: randomLevel,
                    avgSpeed: randomLevel === 'free' ? 70 : randomLevel === 'light' ? 60 : randomLevel === 'moderate' ? 45 : 30,
                    incidents: Math.floor(Math.random() * 4),
                };
            });
            setTrafficData(updatedRoutes);
            setLastUpdate(new Date());
            setIsLoading(false);
        }, 1000);
    };

    // Get color based on congestion level
    const getCongestionColor = (level: TrafficRoute['congestionLevel']): string => {
        switch (level) {
            case 'free':
                return '#10b981'; // green-500
            case 'light':
                return '#3b82f6'; // blue-500
            case 'moderate':
                return '#f59e0b'; // amber-500
            case 'heavy':
                return '#ef4444'; // red-500
            case 'blocked':
                return '#991b1b'; // red-900
            default:
                return '#6b7280'; // gray-500
        }
    };

    // Get incident icon
    const getIncidentIcon = (type: TrafficIncident['type']) => {
        switch (type) {
            case 'accident':
                return <AlertTriangle className="w-4 h-4" />;
            case 'construction':
                return <Construction className="w-4 h-4" />;
            case 'closure':
                return <XCircle className="w-4 h-4" />;
            default:
                return <Navigation className="w-4 h-4" />;
        }
    };

    // Create custom incident marker
    const createIncidentIcon = (incident: TrafficIncident) => {
        if (!L) return undefined;

        const color = incident.severity === 'high' ? '#ef4444' : incident.severity === 'medium' ? '#f59e0b' : '#3b82f6';
        const iconHtml = `
      <div style="
        background-color: ${color};
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 16px;
      ">
        ⚠️
      </div>
    `;

        return L.divIcon({
            html: iconHtml,
            className: 'custom-incident-marker',
            iconSize: [28, 28],
            iconAnchor: [14, 14],
            popupAnchor: [0, -14],
        });
    };

    if (!L) {
        return (
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                <div className="flex items-center justify-center h-96">
                    <div className="text-gray-500">Loading map...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-orange-50 rounded-lg border border-orange-100">
                            <Navigation className="w-5 h-5 text-orange-600" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Sri Lanka Traffic Map</h3>
                            <p className="text-sm text-gray-500">
                                Last updated: {lastUpdate.toLocaleTimeString()}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={refreshTrafficData}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>

                {/* Legend */}
                <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-1 bg-green-500 rounded"></div>
                        <span className="text-gray-600">Free Flow</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-1 bg-blue-500 rounded"></div>
                        <span className="text-gray-600">Light Traffic</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-1 bg-amber-500 rounded"></div>
                        <span className="text-gray-600">Moderate</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-1 bg-red-500 rounded"></div>
                        <span className="text-gray-600">Heavy Traffic</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                        <span className="text-gray-600">Incidents</span>
                    </div>
                </div>
            </div>

            {/* Map */}
            <div className="relative h-[500px]">
                <MapContainer
                    center={SRI_LANKA_BOUNDS.center}
                    zoom={SRI_LANKA_BOUNDS.zoom}
                    minZoom={SRI_LANKA_BOUNDS.minZoom}
                    maxZoom={SRI_LANKA_BOUNDS.maxZoom}
                    style={{ height: '100%', width: '100%' }}
                    className="z-0"
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    {/* Traffic Routes */}
                    {trafficData.map((route) => (
                        <Polyline
                            key={route.id}
                            positions={route.coordinates}
                            pathOptions={{
                                color: getCongestionColor(route.congestionLevel),
                                weight: 6,
                                opacity: 0.8,
                            }}
                        >
                            <Popup>
                                <div className="p-2 min-w-[220px]">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div
                                            className="w-4 h-4 rounded-full"
                                            style={{ backgroundColor: getCongestionColor(route.congestionLevel) }}
                                        ></div>
                                        <h4 className="font-bold text-gray-900">{route.highway}</h4>
                                    </div>
                                    <p className="text-sm text-gray-700 mb-2">{route.name}</p>
                                    <div className="space-y-1 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Status:</span>
                                            <span className="font-semibold text-gray-900 capitalize">{route.congestionLevel}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Avg Speed:</span>
                                            <span className="font-semibold text-gray-900">{route.avgSpeed} km/h</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Incidents:</span>
                                            <span className="font-semibold text-gray-900">{route.incidents}</span>
                                        </div>
                                    </div>
                                </div>
                            </Popup>
                        </Polyline>
                    ))}

                    {/* Traffic Incidents */}
                    {incidents.map((incident) => (
                        <Marker
                            key={incident.id}
                            position={incident.location}
                            icon={createIncidentIcon(incident)}
                        >
                            <Popup>
                                <div className="p-2 min-w-[200px]">
                                    <div className="flex items-center gap-2 mb-2">
                                        {getIncidentIcon(incident.type)}
                                        <h4 className="font-bold text-gray-900 capitalize">{incident.type}</h4>
                                    </div>
                                    <p className="text-sm text-gray-700 mb-2">{incident.description}</p>
                                    <div className="flex items-center justify-between text-xs">
                                        <span className={`px-2 py-1 rounded-full ${incident.severity === 'high' ? 'bg-red-100 text-red-700' :
                                                incident.severity === 'medium' ? 'bg-amber-100 text-amber-700' :
                                                    'bg-blue-100 text-blue-700'
                                            }`}>
                                            {incident.severity} severity
                                        </span>
                                        <span className="text-gray-500">
                                            {Math.floor((Date.now() - incident.timestamp) / 60000)}m ago
                                        </span>
                                    </div>
                                </div>
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>

                {isLoading && (
                    <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10">
                        <div className="text-center">
                            <RefreshCw className="w-8 h-8 text-orange-600 animate-spin mx-auto mb-2" />
                            <p className="text-gray-600">Updating traffic data...</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Traffic Summary */}
            <div className="p-6 bg-gray-50 border-t border-gray-100">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Total Routes</p>
                        <p className="text-2xl font-bold text-gray-900">{trafficData.length}</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Active Incidents</p>
                        <p className="text-2xl font-bold text-orange-600">{incidents.length}</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Avg Speed</p>
                        <p className="text-2xl font-bold text-gray-900">
                            {Math.round(trafficData.reduce((sum, r) => sum + r.avgSpeed, 0) / trafficData.length)} km/h
                        </p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Heavy Traffic</p>
                        <p className="text-2xl font-bold text-red-600">
                            {trafficData.filter(r => r.congestionLevel === 'heavy' || r.congestionLevel === 'blocked').length}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
