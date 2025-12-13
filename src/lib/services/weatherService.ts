/**
 * Weather Service
 * 
 * Fetches weather data from OpenWeatherMap API for Sri Lankan cities
 */

import { WeatherData, SriLankanCity } from '@/types/weather';

const API_KEY = process.env.NEXT_PUBLIC_OPENWEATHER_API_KEY || '';
const BASE_URL = 'https://api.openweathermap.org/data/2.5/weather';

// Cache to avoid hitting API limits
const weatherCache = new Map<string, { data: WeatherData; timestamp: number }>();
const CACHE_DURATION = 10 * 60 * 1000; // 10 minutes

export class WeatherService {
    /**
     * Fetch weather data for a specific city
     */
    static async getWeatherForCity(city: SriLankanCity): Promise<WeatherData | null> {
        // Check cache first
        const cacheKey = city.name;
        const cached = weatherCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
            return cached.data;
        }

        // If no API key, return mock data
        if (!API_KEY) {
            console.warn('OpenWeatherMap API key not found, using mock data');
            return this.getMockWeatherData(city);
        }

        try {
            const url = `${BASE_URL}?lat=${city.lat}&lon=${city.lng}&units=metric&appid=${API_KEY}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`Weather API error: ${response.status}`);
            }

            const data = await response.json();

            const weatherData: WeatherData = {
                city: city.name,
                lat: city.lat,
                lng: city.lng,
                temperature: Math.round(data.main.temp),
                feelsLike: Math.round(data.main.feels_like),
                condition: data.weather[0].main,
                description: data.weather[0].description,
                humidity: data.main.humidity,
                windSpeed: data.wind.speed,
                icon: data.weather[0].icon,
                timestamp: Date.now(),
            };

            // Cache the result
            weatherCache.set(cacheKey, { data: weatherData, timestamp: Date.now() });

            return weatherData;
        } catch (error) {
            console.error(`Failed to fetch weather for ${city.name}:`, error);
            // Return mock data as fallback
            return this.getMockWeatherData(city);
        }
    }

    /**
     * Fetch weather data for multiple cities
     */
    static async getWeatherForCities(cities: SriLankanCity[]): Promise<WeatherData[]> {
        const promises = cities.map(city => this.getWeatherForCity(city));
        const results = await Promise.all(promises);
        return results.filter((data): data is WeatherData => data !== null);
    }

    /**
     * Generate mock weather data (for development/fallback)
     */
    private static getMockWeatherData(city: SriLankanCity): WeatherData {
        // Generate consistent but varied mock data based on city name
        const hash = city.name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        const baseTemp = 26 + (hash % 6); // 26-32°C range
        const conditions = ['Clear', 'Clouds', 'Rain', 'Drizzle'];
        const icons = ['01d', '02d', '03d', '09d', '10d'];

        return {
            city: city.name,
            lat: city.lat,
            lng: city.lng,
            temperature: baseTemp,
            feelsLike: baseTemp + 2,
            condition: conditions[hash % conditions.length],
            description: 'partly cloudy',
            humidity: 70 + (hash % 20),
            windSpeed: 3 + (hash % 5),
            icon: icons[hash % icons.length],
            timestamp: Date.now(),
        };
    }

    /**
     * Get weather icon URL
     */
    static getIconUrl(iconCode: string): string {
        return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
    }

    /**
     * Get temperature color (for visual coding)
     */
    static getTemperatureColor(temp: number): string {
        if (temp >= 32) return '#ef4444'; // red-500 - hot
        if (temp >= 28) return '#f97316'; // orange-500 - warm
        if (temp >= 24) return '#eab308'; // yellow-500 - mild
        return '#3b82f6'; // blue-500 - cool
    }

    /**
     * Clear cache (useful for manual refresh)
     */
    static clearCache(): void {
        weatherCache.clear();
    }
}
