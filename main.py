import os
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


def transfer_to_agent_b():
    return agent_b


agent_a = Agent(
    name="Agent A",
    instructions="You are a helpful agent.",
    functions=[transfer_to_agent_b],
)

agent_b = Agent(
    name="Agent B",
    instructions="Only speak in Haikus.",
)


def main():
    response = swarm_client.run(
        agent=agent_a,
        messages=[{"role": "user", "content": "I want to talk to agent B."}],
    )
    print(response.messages[-1]["content"])


if __name__ == "__main__":
    main()
