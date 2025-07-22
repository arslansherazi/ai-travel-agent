from pydantic import BaseModel
from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, input_guardrail


class TravelCheckOutput(BaseModel):
    is_travel_query: bool
    is_greeting: bool
    reasoning: str


# Lightweight internal agent to classify travel-related queries and greetings
travel_guardrail_agent = Agent(
    name="Travel Guardrail Checker",
    instructions="""
    Determine if the user query is related to travel assistance (weather, booking, places, planning) OR if it's a greeting/polite conversation starter.
    
    Travel queries include: weather, accommodations, hotels, restaurants, attractions, trip planning, itineraries, flights, etc.
    
    Greetings include: hello, hi, good morning/afternoon/evening, how are you, thanks, thank you, goodbye, bye, etc.
    
    Output a JSON with `is_travel_query`, `is_greeting`, and `reasoning`.
    """,
    output_type=TravelCheckOutput,
)


@input_guardrail
async def travel_query_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    user_input: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(travel_guardrail_agent, user_input, context=ctx.context)
    output: TravelCheckOutput = result.final_output

    # Allow both travel queries and greetings
    trigger = not (output.is_travel_query or output.is_greeting)

    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=trigger
    )