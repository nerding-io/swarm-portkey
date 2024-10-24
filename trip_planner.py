import os
import json
from dotenv import load_dotenv
from swarm import Swarm, Agent
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Portkey-enabled OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        provider="openai", api_key=os.getenv("PORTKEY_API_KEY")
    ),
)

# Initialize Swarm client
swarm_client = Swarm(client=client)


def get_weather(location):
    """Get the weather for a specific location."""
    return f"Sunny, 25°C in {location}"


def book_flight(origin, destination, date):
    """Book a flight for the user."""
    return f"Flight booked from {origin} to {destination} on {date}"


def book_hotel(location, check_in, check_out):
    """Book a hotel for the user."""
    return f"Hotel booked in {location} from {check_in} to {check_out}"


def instructions(context_variables):
    name = context_variables.get("name", "Traveler")
    return f"You are a helpful travel agent. Greet the user by name ({name}) and assist them with their trip planning needs."


triage_agent = Agent(
    name="Triage Agent",
    instructions=instructions,
    functions=[get_weather],
)

flight_agent = Agent(
    name="Flight Booking Agent",
    instructions="You are a flight booking specialist. Help users book their flights.",
    functions=[book_flight],
)

hotel_agent = Agent(
    name="Hotel Booking Agent",
    instructions="You are a hotel booking specialist. Help users book their accommodations.",
    functions=[book_hotel],
)


def transfer_to_flight_agent():
    """Transfer to the flight booking agent."""
    return flight_agent


def transfer_to_hotel_agent():
    """Transfer to the hotel booking agent."""
    return hotel_agent


def transfer_back_to_triage():
    """Transfer back to the triage agent."""
    return triage_agent


triage_agent.functions.extend([transfer_to_flight_agent, transfer_to_hotel_agent])
flight_agent.functions.append(transfer_back_to_triage)
hotel_agent.functions.append(transfer_back_to_triage)


def process_and_print_streaming_response(response):
    content = ""
    last_sender = ""
    for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]
        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]
        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")
        if "delim" in chunk and chunk["delim"] == "end" and content:
            print()  # End of response message
            content = ""
    if "response" in chunk:
        return chunk["response"]


def run_trip_planner():
    context_variables = {"name": "Alice", "user_id": "12345"}
    messages = []
    agent = triage_agent

    print("Starting Trip Planner 🌴✈️🏨")

    while True:
        user_input = input("\033[90mUser\033[0m: ")
        messages.append({"role": "user", "content": user_input})

        response = swarm_client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables,
            stream=True,
        )

        response = process_and_print_streaming_response(response)
        messages.extend(response.messages)
        agent = response.agent


if __name__ == "__main__":
    run_trip_planner()
