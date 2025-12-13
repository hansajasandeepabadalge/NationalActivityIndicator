// Traffic data types for Sri Lanka

export interface TrafficRoute {
    id: string;
    name: string;
    highway: string; // e.g., "A1", "A2"
    from: string;
    to: string;
    coordinates: [number, number][]; // Array of [lat, lng] points
    congestionLevel: 'free' | 'light' | 'moderate' | 'heavy' | 'blocked';
    avgSpeed: number; // km/h
    incidents: number;
}

export interface TrafficIncident {
    id: string;
    type: 'accident' | 'construction' | 'closure' | 'congestion';
    location: [number, number];
    description: string;
    severity: 'low' | 'medium' | 'high';
    timestamp: number;
}

// Major highways in Sri Lanka
export const SRI_LANKA_HIGHWAYS: TrafficRoute[] = [
    // A1 - Colombo to Kandy (Main route)
    {
        id: 'a1-colombo-kandy',
        name: 'Colombo - Kandy Road',
        highway: 'A1',
        from: 'Colombo',
        to: 'Kandy',
        coordinates: [
            [6.9271, 79.8612], // Colombo
            [7.0833, 79.9167], // Kadawatha
            [7.1667, 80.0000], // Gampaha
            [7.2906, 80.6337], // Kandy
        ],
        congestionLevel: 'moderate',
        avgSpeed: 45,
        incidents: 2,
    },
    // A2 - Colombo to Galle (Southern Expressway route)
    {
        id: 'a2-colombo-galle',
        name: 'Galle Road',
        highway: 'A2',
        from: 'Colombo',
        to: 'Galle',
        coordinates: [
            [6.9271, 79.8612], // Colombo
            [6.8333, 79.8500], // Mount Lavinia
            [6.5833, 79.9667], // Kalutara
            [6.0535, 80.2210], // Galle
        ],
        congestionLevel: 'light',
        avgSpeed: 60,
        incidents: 0,
    },
    // A3 - Colombo to Negombo
    {
        id: 'a3-colombo-negombo',
        name: 'Negombo Road',
        highway: 'A3',
        from: 'Colombo',
        to: 'Negombo',
        coordinates: [
            [6.9271, 79.8612], // Colombo
            [7.0500, 79.8500], // Ja-Ela
            [7.2008, 79.8358], // Negombo
        ],
        congestionLevel: 'heavy',
        avgSpeed: 30,
        incidents: 3,
    },
    // A4 - Colombo to Batticaloa
    {
        id: 'a4-colombo-batticaloa',
        name: 'Batticaloa Road',
        highway: 'A4',
        from: 'Colombo',
        to: 'Batticaloa',
        coordinates: [
            [6.9271, 79.8612], // Colombo
            [7.2906, 80.6337], // Kandy
            [7.7310, 81.6747], // Batticaloa
        ],
        congestionLevel: 'free',
        avgSpeed: 70,
        incidents: 0,
    },
    // A6 - Ambepussa to Trincomalee
    {
        id: 'a6-trincomalee',
        name: 'Trincomalee Road',
        highway: 'A6',
        from: 'Kurunegala',
        to: 'Trincomalee',
        coordinates: [
            [7.4863, 80.3623], // Kurunegala
            [8.3114, 80.4037], // Anuradhapura
            [8.5874, 81.2152], // Trincomalee
        ],
        congestionLevel: 'light',
        avgSpeed: 65,
        incidents: 1,
    },
    // A9 - Kandy to Jaffna
    {
        id: 'a9-kandy-jaffna',
        name: 'Jaffna Road',
        highway: 'A9',
        from: 'Kandy',
        to: 'Jaffna',
        coordinates: [
            [7.2906, 80.6337], // Kandy
            [8.3114, 80.4037], // Anuradhapura
            [8.7542, 80.4982], // Vavuniya
            [9.6615, 80.0255], // Jaffna
        ],
        congestionLevel: 'moderate',
        avgSpeed: 50,
        incidents: 1,
    },
];

// Mock traffic incidents
export const MOCK_TRAFFIC_INCIDENTS: TrafficIncident[] = [
    {
        id: 'inc1',
        type: 'accident',
        location: [7.0833, 79.9167],
        description: 'Minor accident on A1 near Kadawatha',
        severity: 'medium',
        timestamp: Date.now() - 30 * 60 * 1000,
    },
    {
        id: 'inc2',
        type: 'construction',
        location: [7.1500, 79.8500],
        description: 'Road work on A3, expect delays',
        severity: 'low',
        timestamp: Date.now() - 2 * 60 * 60 * 1000,
    },
    {
        id: 'inc3',
        type: 'congestion',
        location: [6.9271, 79.8612],
        description: 'Heavy traffic in Colombo city center',
        severity: 'high',
        timestamp: Date.now() - 15 * 60 * 1000,
    },
];
