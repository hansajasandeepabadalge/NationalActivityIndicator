'use client';

/**
 * Sri Lanka Weather Map Component
 * 
 * Interactive map showing real-time weather data for major Sri Lankan cities
 */

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { WeatherData, SRI_LANKAN_CITIES, SRI_LANKA_BOUNDS } from '@/types/weather';
import { WeatherService } from '@/lib/services/weatherService';
import { RefreshCw, MapPin, Thermometer } from 'lucide-react';

// Dynamically import map components (Leaflet doesn't work with SSR)
const MapContainer = dynamic(
    () => import('react-leaflet').then((mod) => mod.MapContainer),
    { ssr: false }
);
const TileLayer = dynamic(
    () => import('react-leaflet').then((mod) => mod.TileLayer),
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

// Import Leaflet CSS
import 'leaflet/dist/leaflet.css';

export function SriLankaWeatherMap() {
    const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
    const [L, setL] = useState<any>(null);

    // Load Leaflet library
    useEffect(() => {
        import('leaflet').then((leaflet) => {
            setL(leaflet.default);
            // Fix default marker icon issue
            delete (leaflet.default.Icon.Default.prototype as any)._getIconUrl;
            leaflet.default.Icon.Default.mergeOptions({
                iconRetinaUrl: '/leaflet/marker-icon-2x.png',
                iconUrl: '/leaflet/marker-icon.png',
                shadowUrl: '/leaflet/marker-shadow.png',
            });
        });
    }, []);

    const fetchWeatherData = async () => {
        setIsLoading(true);
        try {
            const data = await WeatherService.getWeatherForCities(SRI_LANKAN_CITIES);
            setWeatherData(data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error('Failed to fetch weather data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchWeatherData();

        // Auto-refresh every 10 minutes
        const interval = setInterval(fetchWeatherData, 10 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    const handleRefresh = () => {
        WeatherService.clearCache();
        fetchWeatherData();
    };

    // Create custom marker icon based on temperature
    const createCustomIcon = (weather: WeatherData) => {
        if (!L) return undefined;

        const color = WeatherService.getTemperatureColor(weather.temperature);
        const iconHtml = `
      <div style="
        background-color: ${color};
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 12px;
      ">
        ${weather.temperature}°
      </div>
    `;

        return L.divIcon({
            html: iconHtml,
            className: 'custom-weather-marker',
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -16],
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
                        <div className="p-2 bg-blue-50 rounded-lg border border-blue-100">
                            <MapPin className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-gray-900">Sri Lanka Weather Map</h3>
                            <p className="text-sm text-gray-500">
                                {lastUpdate ? `Last updated: ${lastUpdate.toLocaleTimeString()}` : 'Loading...'}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={handleRefresh}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </button>
                </div>

                {/* Legend */}
                <div className="mt-4 flex items-center gap-6 text-sm">
                    <div className="flex items-center gap-2">
                        <Thermometer className="w-4 h-4 text-gray-600" />
                        <span className="text-gray-600">Temperature:</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-blue-500"></div>
                        <span className="text-gray-600">&lt;24°C</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                        <span className="text-gray-600">24-28°C</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-orange-500"></div>
                        <span className="text-gray-600">28-32°C</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full bg-red-500"></div>
                        <span className="text-gray-600">&gt;32°C</span>
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

                    {weatherData.map((weather) => (
                        <Marker
                            key={weather.city}
                            position={[weather.lat, weather.lng]}
                            icon={createCustomIcon(weather)}
                        >
                            <Popup>
                                <div className="p-2 min-w-[200px]">
                                    <div className="flex items-center justify-between mb-3">
                                        <h4 className="font-bold text-lg text-gray-900">{weather.city}</h4>
                                        <img
                                            src={WeatherService.getIconUrl(weather.icon)}
                                            alt={weather.condition}
                                            className="w-12 h-12"
                                        />
                                    </div>

                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Temperature:</span>
                                            <span className="font-semibold text-gray-900">{weather.temperature}°C</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Feels like:</span>
                                            <span className="font-semibold text-gray-900">{weather.feelsLike}°C</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Condition:</span>
                                            <span className="font-semibold text-gray-900 capitalize">{weather.description}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Humidity:</span>
                                            <span className="font-semibold text-gray-900">{weather.humidity}%</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-600">Wind:</span>
                                            <span className="font-semibold text-gray-900">{weather.windSpeed} m/s</span>
                                        </div>
                                    </div>
                                </div>
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>

                {isLoading && (
                    <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-10">
                        <div className="text-center">
                            <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-2" />
                            <p className="text-gray-600">Loading weather data...</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
