from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google, openai
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, send_email, web_search

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            # llm=google.beta.realtime.RealtimeModel(voice="Charon", temperature=0.7, ),
            llm=openai.LLM.with_ollama(
                model="qwen/qwen3-4b-thinking-2507",
                base_url="http://localhost:1234/v1",
            ),
            tts="cartesia/sonic-2:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
            # tts=None,
            
            tools=[
                send_email,
                web_search,
                get_weather,
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            # audio_enabled=False,
            # text_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(instructions=SESSION_INSTRUCTION)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
