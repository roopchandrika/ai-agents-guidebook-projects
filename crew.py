import os
from datetime import date

from crewai import LLM, Agent, Crew, Process, Task

from tools import BrowserbaseTool, KayakFlightTool


def get_llm() -> LLM:
    model = os.getenv("MODEL", "ollama/qwen3:8b")
    kwargs = {"model": model, "temperature": 0.1}
    if model.startswith("ollama/"):
        kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(**kwargs)


def build_crew() -> Crew:
    llm = get_llm()

    flights_agent = Agent(
        role="Flight Search Specialist",
        goal="Find the best flight options for the traveller's request",
        backstory=(
            "You search for flights like a human would: you build the right Kayak "
            "search URL, open it in a browser and read the results carefully."
        ),
        tools=[KayakFlightTool(), BrowserbaseTool()],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    summarize_agent = Agent(
        role="Travel Summary Writer",
        goal="Turn raw flight results into a clear, easy-to-compare summary",
        backstory="You are a travel agent known for concise, accurate recommendations.",
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    search_task = Task(
        description=(
            "Today's date is {today}. Traveller request: '{request}'.\n"
            "1. Work out the departure and arrival airport IATA codes and the travel date(s) "
            "(YYYY-MM-DD; if no year is given, use the next upcoming occurrence).\n"
            "2. Use kayak_flight_url_generator to create the search URL.\n"
            "3. Use browserbase_web_loader to open the URL.\n"
            "4. Extract the top 5 flights: airline(s), departure/arrival times, duration, "
            "number of stops and price."
        ),
        expected_output="A list of up to 5 flights with airline, times, duration, stops, price, plus the Kayak URL.",
        agent=flights_agent,
    )

    summarize_task = Task(
        description=(
            "Summarize the flights found for '{request}'. Present a markdown table, then "
            "recommend the cheapest, the fastest and the best-value option. Include the Kayak URL."
        ),
        expected_output="A markdown table of flights followed by 3 short recommendations.",
        agent=summarize_agent,
        context=[search_task],
    )

    return Crew(
        agents=[flights_agent, summarize_agent],
        tasks=[search_task, summarize_task],
        process=Process.sequential,
        planning=True,  # Planning pattern: an AgentPlanner drafts a step plan before execution
        planning_llm=llm,
        verbose=True,
    )


def find_flights(request: str) -> str:
    result = build_crew().kickoff(inputs={"request": request, "today": date.today().isoformat()})
    return result.raw
