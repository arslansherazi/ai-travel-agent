"""
AI Travel Agent System

A multi-agent travel planning system with async support and intelligent handoff mechanisms.
"""

from .weather import (
    setup_weather_agent
)

from .booking import (
    setup_booking_agent
)

from .places import (
    setup_places_agent
)

from .planner import (
    setup_planner_agent
)

__all__ = [
    # Weather Agent
    "setup_weather_agent",
    
    # Booking Agent
    "setup_booking_agent",
    
    # Places Agent
    "setup_places_agent",
    
    # Planner Agent
    "setup_planner_agent",
]

# Version info
__version__ = "2.0.0"
__author__ = "AI Travel Agent System"
__description__ = "Multi-agent travel planning system with direct handoffs"
