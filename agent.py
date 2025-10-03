from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import openai
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, send_email, web_search

from mem0 import AsyncMemoryClient
import json
import logging

load_dotenv()


class Assistant(Agent):
    def __init__(self, chat_ctx=None) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            # llm=google.beta.realtime.RealtimeModel(voice="Charon", temperature=0.7, ),
            llm=openai.LLM.with_ollama(
                model="qwen/qwen3-1.7b",
                base_url="http://localhost:1234/v1",
            ),
            tts="cartesia/sonic-2:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
            # tts=None,

            tools=[
                send_email,
                web_search,
                get_weather,
            ],
            chat_ctx=chat_ctx,
        )


async def entrypoint(ctx: agents.JobContext):

    async def shutdown_hook(chat_ctx: ChatContext, mem0: AsyncMemoryClient, memory_str: str):
        logging.info("Shutting down, saving chat context to memory...")

        messages_formatted = []

        logging.info(f"Chat context messages: {chat_ctx.items}")

        for item in chat_ctx.items:
            # Handle different types of chat items
            try:
                # Check if item has content attribute and role
                if hasattr(item, 'content') and hasattr(item, 'role'):
                    content_str = ''.join(item.content) if isinstance(item.content, list) else str(item.content)

                    if memory_str and memory_str in content_str:
                        continue

                    if item.role in ['user', 'assistant']:
                        messages_formatted.append({
                            "role": item.role,
                            "content": content_str.strip()
                        })
                else:
                    # Skip items that don't have content (like FunctionCall objects)
                    logging.debug(f"Skipping item without content: {type(item).__name__}")
                    continue

            except AttributeError as e:
                logging.warning(f"Skipping chat item due to attribute error: {e}")
                continue

        logging.info(f"Formatted messages to add to memory: {messages_formatted}")
        if messages_formatted:  # Only add if there are messages to save
            await mem0.add(messages_formatted, user_id="Brice")
            logging.info("Chat context saved to memory.")
        else:
            logging.info("No messages to save to memory.")

    session = AgentSession()


    mem0 = AsyncMemoryClient()
    user_name = 'Brice'

    results = await mem0.get_all(user_id=user_name)
    initial_ctx = ChatContext()
    memory_str = ""

    if results:
        memories = [
            {
                "memory": result["memory"],
                "updated_at": result["updated_at"]
            }
            for result in results
        ]
        memory_str = json.dumps(memories)
        logging.info(f"Memories: {memory_str}")
        initial_ctx.add_message(
            role="assistant",
            content=f"The following is a list of memories from previous conversations with {user_name}: {memory_str}",
        )

    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=initial_ctx),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            # audio_enabled=False,
            # text_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(instructions=SESSION_INSTRUCTION)

    # Fix: Use add_shutdown_callback instead of _shutdown_callbacks
    ctx.add_shutdown_callback(lambda: shutdown_hook(session._agent.chat_ctx, mem0, memory_str))


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
