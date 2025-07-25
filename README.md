# AI Travel Agent System

A multi-agent travel planning system with async support and intelligent handoff mechanisms.

## Architecture

The system consists of:
- **Controller Agent**: Main orchestrator that routes requests to specialized agents
- **Weather Agent**: Handles weather-related queries and forecasts
- **Booking Agent**: Manages accommodation searches and bookings
- **Places Agent**: Discovers attractions, restaurants, and activities
- **Trip Planner Agent**: Creates comprehensive travel itineraries

## Setup Project
~~~
uv venv .venv
~~~
~~~
source .venv/bin/activate
~~~
~~~
pip install -r requirements.txt
~~~

## Run Project
~~~
docker-compose up
~~~

