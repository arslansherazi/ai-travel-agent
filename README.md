# AI Travel Agent System

A multi-agent travel planning system with async support and intelligent handoff mechanisms.

## Architecture

The system consists of:
- **Controller Agent**: Main orchestrator that routes requests to specialized agents
- **Weather Agent**: Handles weather-related queries and forecasts
- **Booking Agent**: Manages accommodation searches and bookings
- **Places Agent**: Discovers attractions, restaurants, and activities
- **Trip Planner Agent**: Creates comprehensive travel itineraries

## Features

### 🔄 Async Support
- All agents and MCP servers support asynchronous operations
- Improved performance and responsiveness
- Non-blocking operations for better user experience

### 🤝 Intelligent Handoff
- Automatic request routing based on content analysis
- Seamless transfer between specialized agents
- Context-aware agent selection

### 🌤️ Weather Integration
- Real-time weather data and forecasts
- Weather-optimized trip planning
- Severe weather alerts and recommendations

### 🏨 Accommodation Booking
- Hotel and accommodation search
- Price and rating filters
- Availability checking

### 🗺️ Places Discovery
- Local attractions and activities
- Restaurant recommendations
- Weather-appropriate suggestions

### 📅 Trip Planning
- Multi-day itinerary creation
- Budget-conscious planning
- Activity coordination

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file with:
   ```
   # MCP Server URLs
   WEATHER_SERVER_URL=http://localhost:5004
   BOOKING_SERVER_URL=http://localhost:5001
   PLACES_SERVER_URL=http://localhost:5002
   PLANNER_SERVER_URL=http://localhost:5003
   
   # API Keys
   BOOKING_API_KEY=your_booking_api_key
   GOOGLE_PLACES_API_KEY=your_google_places_api_key
   ```

3. **Start MCP Servers**
   ```bash
   docker-compose up -d
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

## Usage

### Interactive Mode
```bash
python main.py
```

Then enter natural language requests like:
- "What's the weather like in Paris?"
- "Find hotels in Tokyo for next week"
- "Show me attractions in London"
- "Plan a 3-day trip to New York"

## Agent Capabilities

### Weather Agent
- Current weather conditions
- Weather forecasts (up to 14 days)
- Severe weather alerts
- Travel-optimized weather recommendations

### Booking Agent
- Hotel and accommodation search
- Price and rating filters
- Availability checking
- Detailed property information

### Places Agent
- Attraction discovery
- Restaurant recommendations
- Activity suggestions
- Weather-appropriate recommendations

### Trip Planner Agent
- Multi-day itinerary creation
- Weather-optimized planning
- Budget considerations
- Activity coordination

### Controller Agent
- Request analysis and routing
- Multi-agent coordination
- Context management
- Unified response generation

## Handoff Mechanism

The system uses an intelligent handoff mechanism:

1. **Request Analysis**: The controller analyzes user input to determine the appropriate agent
2. **Capability Matching**: Matches request content with agent capabilities
3. **Multi-Agent Detection**: Identifies requests requiring multiple agents
4. **Routing**: Routes requests to the most appropriate agent
5. **Fallback**: Uses controller for complex or ambiguous requests

## Development

### Adding New Agents

1. Create agent file in `_agents/`
2. Add agent configuration to `_agents/constants.py`
3. Update controller to include new agent
4. Create corresponding MCP server

### Extending Capabilities

1. Add new capabilities to `AGENT_CAPABILITIES` in constants
2. Update handoff instructions
3. Implement new tools in MCP servers
4. Update agent instructions

## Docker Services

The system uses Docker for MCP servers:
- **booking**: Port 5001
- **places**: Port 5002
- **trip_planner**: Port 5003
- **weather**: Port 5004

## API Dependencies

- **Weather**: Open-Meteo API (free)
- **Booking**: Booking.com API (requires key)
- **Places**: Google Places API (requires key)

## Error Handling

The system includes comprehensive error handling:
- API failures gracefully handled
- Agent initialization errors reported
- Request routing fallbacks
- User-friendly error messages

## Performance

- Async operations for improved responsiveness
- Intelligent caching where applicable
- Efficient request routing
- Parallel processing capabilities
