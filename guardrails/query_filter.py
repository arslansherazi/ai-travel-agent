from pydantic import BaseModel
from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, Runner, input_guardrail


class TravelCheckOutput(BaseModel):
    is_travel_query: bool
    reasoning: str


# Lightweight internal agent to classify travel-related queries
travel_guardrail_agent = Agent(
    name="Travel Guardrail Checker",
    instructions="Determine if the user query is related to travel assistance (weather, booking, places, planning). Output a JSON with `is_travel_query` and `reasoning`.",
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

    trigger = not output.is_travel_query

    return GuardrailFunctionOutput(
        output_info=output.reasoning,
        tripwire_triggered=trigger
    )