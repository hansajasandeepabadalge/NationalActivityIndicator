# Environment Variables Setup

## OpenWeatherMap API Key

To enable real-time weather data on the Sri Lanka Weather Map, you need to get a free API key from OpenWeatherMap.

### Steps to Get Your API Key:

1. **Sign Up** (Free):
   - Go to https://openweathermap.org/api
   - Click "Sign Up" in the top right
   - Create a free account

2. **Get Your API Key**:
   - After signing in, go to https://home.openweathermap.org/api_keys
   - Copy your default API key (or create a new one)
   - The key takes ~10 minutes to activate

3. **Add to Your Project**:
   - Create or edit `.env.local` in the project root
   - Add this line:
     ```
     NEXT_PUBLIC_OPENWEATHER_API_KEY=your_api_key_here
     ```
   - Replace `your_api_key_here` with your actual key

4. **Restart Dev Server**:
   ```bash
   # Stop the current server (Ctrl+C)
   npm run dev
   ```

### Free Tier Limits:
- **1,000 API calls per day** (more than enough for this dashboard)
- Weather updates every 10 minutes
- 8 cities = ~1,152 calls/day (within limit)

### Without API Key:
The map will still work with **mock weather data** for development/testing purposes.

## Example `.env.local` File:
```
NEXT_PUBLIC_OPENWEATHER_API_KEY=abc123def456ghi789jkl012mno345pq
```

**Note**: Never commit `.env.local` to Git (it's already in `.gitignore`)
