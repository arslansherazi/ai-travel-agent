# AI Travel Agent System

A multi-agent travel planning system with async support and intelligent handoff mechanisms.

## Architecture

The system consists of:
- **Controller Agent**: Main orchestrator that routes requests to specialized agents
- **Weather Agent**: Handles weather-related queries and forecasts
- **Booking Agent**: Manages accommodation searches and bookings
- **Places Agent**: Discovers attractions, restaurants, and activities
- **Trip Planner Agent**: Creates comprehensive travel itineraries

## Setup Local Project
~~~
uv venv .venv
~~~
~~~
source .venv/bin/activate
~~~
~~~
pip install -r requirements.txt
~~~

## Setup Docker Project
### Run Services
~~~
docker-compose up
~~~

### Access Project
~~~
0.0.0.0:7860
~~~

## Check Logs
~~~
https://platform.openai.com/logs
~~~

