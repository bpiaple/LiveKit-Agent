import os
from dotenv import load_dotenv
from mem0 import MemoryClient
import logging
import json


load_dotenv()
user_name = 'Brice'
mem0 = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

def add_memory():
    
    messages_formatted = [
        {        
            "role": "user",
            "content": "I really like Linkin Park."
        },
        {
            "role": "assistant",
            "content": "That is a good choice."
        },
        {
            "role": "user",
            "content": "I think so too."
        },
        {
            "role": "assistant",
            "content": "What is your favorite song by them?"
        },
    ]

    mem0.add(messages_formatted, user_id="Brice")

def get_memory_by_query():
    mem0 = MemoryClient()
    query = "What are {user_name}'s preferences?"
    results = mem0.search(query, user_id=user_name)

    memories = [
            {
                "memory": result["memory"],
                "updated_at": result["updated_at"]
            }
            for result in results
        ]
    memories_str = json.dumps(memories)
    print(f"Memories: {memories_str}")
    return memories_str


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    add_memory()
    get_memory_by_query()