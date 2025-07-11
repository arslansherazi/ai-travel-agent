import panel as pn

from agents import Runner
from dotenv import load_dotenv
from _agents.weather import setup_weather_agent
from _agents.booking import setup_booking_agent
from _agents.places import setup_places_agent
from _agents.planner import setup_planner_agent

load_dotenv()


async def setup_agents():
    """
    Set up agents for UI mode
    """
    # Initialize all agents
    weather_agent = await setup_weather_agent()
    booking_agent = await setup_booking_agent()
    places_agent = await setup_places_agent()
    planner_agent = await setup_planner_agent()

    # Set up handoffs between agents
    weather_agent.handoffs = [booking_agent, places_agent, planner_agent]
    booking_agent.handoffs = [weather_agent, places_agent, planner_agent]
    places_agent.handoffs = [weather_agent, booking_agent, planner_agent]
    planner_agent.handoffs = [weather_agent, booking_agent, places_agent]

    return weather_agent


async def process_message(_input: str):
    """
    Process user message with agents and return response

    :param _input: user message
    """
    weather_agent = await setup_agents()

    try:
        response = await Runner.run(starting_agent=weather_agent, input=_input)
        return response
    except Exception as e:
        return f"Something went wrong. Please try again with a different request. Error: {str(e)}"


def run():
    """
    Run the application with Panel UI
    """
    pn.extension()

    # Create the chat interface
    chat_interface = pn.chat.ChatInterface(
        callback=process_message,
        callback_user="Travel Assistant",
        show_rerun=False,
        show_undo=False,
        show_clear=True
    )

    # Add a welcome message
    chat_interface.send(
        "Welcome to the AI Travel Assistant! How can I help with your travel needs?", 
        user="Travel Assistant", 
        respond=False
    )

    # Create the app layout
    app = pn.Column(
        pn.pane.Markdown("# 🌍 AI Travel Assistant", align="center"),
        chat_interface,
        width=800,
        sizing_mode="stretch_width"
    )

    # Serve the app
    app.servable("Travel Assistant")
    pn.serve(app, port=5006, show=True)


if __name__ == "__main__":
    run()