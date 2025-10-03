import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun


@function_tool
async def get_weather(context: RunContext, city: str) -> str:
    """
    Fetches the current weather for a given city using the wttr.in service.
    """

    logging.info(f"Fetching weather data for {city}")
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather in {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(
                f"Failed to fetch weather data for {city}: {response.status_code}"
            )
            return "Sorry, I couldn't fetch the weather information right now."
    except Exception as e:
        logging.error(f"Error fetching weather data for {city}: {e}")
        return "Sorry, I couldn't fetch the weather information right now."


@function_tool
async def web_search(context: RunContext, query: str) -> str:
    """
    Performs a web search using DuckDuckGo and returns the top result.
    """

    logging.info(f"Performing web search for query: {query}")
    try:
        search_tool = DuckDuckGoSearchRun()
        results = search_tool.run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error performing web search for '{query}': {e}")
        return "Sorry, I couldn't perform the web search right now."
