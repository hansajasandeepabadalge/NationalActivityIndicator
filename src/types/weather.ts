// Weather data types for OpenWeatherMap API

export interface WeatherData {
    city: string;
    lat: number;
    lng: number;
    temperature: number; // Celsius
    feelsLike: number;
    condition: string; // e.g., "Clear", "Clouds", "Rain"
    description: string; // e.g., "clear sky", "few clouds"
    humidity: number; // percentage
    windSpeed: number; // m/s
    icon: string; // weather icon code
    timestamp: number;
}

export interface SriLankanCity {
    name: string;
    lat: number;
    lng: number;
    district?: string;
}

export const SRI_LANKAN_CITIES: SriLankanCity[] = [
    // Major Cities
    { name: 'Colombo', lat: 6.9271, lng: 79.8612, district: 'Western' },
    { name: 'Kandy', lat: 7.2906, lng: 80.6337, district: 'Central' },
    { name: 'Galle', lat: 6.0535, lng: 80.2210, district: 'Southern' },
    { name: 'Jaffna', lat: 9.6615, lng: 80.0255, district: 'Northern' },
    { name: 'Trincomalee', lat: 8.5874, lng: 81.2152, district: 'Eastern' },
    { name: 'Batticaloa', lat: 7.7310, lng: 81.6747, district: 'Eastern' },
    { name: 'Anuradhapura', lat: 8.3114, lng: 80.4037, district: 'North Central' },
    { name: 'Ratnapura', lat: 6.6828, lng: 80.4036, district: 'Sabaragamuwa' },

    // Additional Cities
    { name: 'Negombo', lat: 7.2008, lng: 79.8358, district: 'Western' },
    { name: 'Matara', lat: 5.9549, lng: 80.5550, district: 'Southern' },
    { name: 'Kurunegala', lat: 7.4863, lng: 80.3623, district: 'North Western' },
    { name: 'Badulla', lat: 6.9934, lng: 81.0550, district: 'Uva' },
    { name: 'Nuwara Eliya', lat: 6.9497, lng: 80.7891, district: 'Central' },
    { name: 'Hambantota', lat: 6.1429, lng: 81.1212, district: 'Southern' },
    { name: 'Vavuniya', lat: 8.7542, lng: 80.4982, district: 'Northern' },
    { name: 'Ampara', lat: 7.2974, lng: 81.6722, district: 'Eastern' },
    { name: 'Polonnaruwa', lat: 7.9403, lng: 81.0188, district: 'North Central' },
    { name: 'Kegalle', lat: 7.2513, lng: 80.3464, district: 'Sabaragamuwa' },
    { name: 'Chilaw', lat: 7.5759, lng: 79.7953, district: 'North Western' },
    { name: 'Monaragala', lat: 6.8728, lng: 81.3507, district: 'Uva' },
];

// Sri Lanka map bounds
export const SRI_LANKA_BOUNDS = {
    center: { lat: 7.8731, lng: 80.7718 } as [number, number],
    zoom: 7,
    minZoom: 7,
    maxZoom: 12,
};
