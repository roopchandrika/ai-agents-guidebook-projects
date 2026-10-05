import os
from datetime import date

from crewai import LLM, Agent, Crew, Process, Task

from tools import BrowserbaseTool, KayakHotelTool


def get_llm() -> LLM:
    model = os.getenv("MODEL", "ollama/qwen3:8b")
    kwargs = {"model": model, "temperature": 0.1}
    if model.startswith("ollama/"):
        kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(**kwargs)


def build_crew() -> Crew:
    llm = get_llm()

    hotels_agent = Agent(
        role="Hotel Search Specialist",
        goal="Find the best hotel options for the traveller's request",
        backstory=(
            "You search for hotels like a human would: you build the right Kayak "
            "search URL, open it in a browser and read the listings carefully."
        ),
        tools=[KayakHotelTool(), BrowserbaseTool()],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    summarize_agent = Agent(
        role="Travel Summary Writer",
        goal="Turn raw hotel listings into a clear, easy-to-compare summary",
        backstory="You are a travel agent known for concise, accurate recommendations.",
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    search_task = Task(
        description=(
            "Today's date is {today}. Traveller request: '{request}'.\n"
            "1. Work out the location, check-in and check-out dates (YYYY-MM-DD; if no year "
            "is given, use the next upcoming occurrence) and number of adults (default 2).\n"
            "2. Use kayak_hotel_url_generator to create the search URL.\n"
            "3. Use browserbase_web_loader to open the URL.\n"
            "4. Extract the top 5 hotels: name, price per night, total price if shown, "
            "rating/review score, neighbourhood and notable amenities."
        ),
        expected_output="A list of up to 5 hotels with name, price, rating, area and amenities, plus the Kayak URL.",
        agent=hotels_agent,
    )

    summarize_task = Task(
        description=(
            "Summarize the hotels found for '{request}'. Present a markdown table, then "
            "recommend the best budget, best rated and best value option. Include the Kayak URL."
        ),
        expected_output="A markdown table of hotels followed by 3 short recommendations.",
        agent=summarize_agent,
        context=[search_task],
    )

    return Crew(
        agents=[hotels_agent, summarize_agent],
        tasks=[search_task, summarize_task],
        process=Process.sequential,
        planning=True,
        planning_llm=llm,
        verbose=True,
    )


def find_hotels(request: str) -> str:
    result = build_crew().kickoff(inputs={"request": request, "today": date.today().isoformat()})
    return result.raw
