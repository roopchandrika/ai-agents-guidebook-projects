"""Agentic RAG served with LitServe.

LitServe calls: decode_request -> predict -> encode_response for each request.
"""
import litserve as ls
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

from llm import get_llm
from tools import FirecrawlSearchTool, VectorDBSearchTool

load_dotenv()


class AgenticRAGAPI(ls.LitAPI):
    def setup(self, device):
        llm = get_llm()

        researcher = Agent(
            role="Research Specialist",
            goal="Find the most relevant, accurate context for: {query}",
            backstory=(
                "You are meticulous at finding information. You check the private "
                "knowledge base first and fall back to web search when it is not enough."
            ),
            tools=[VectorDBSearchTool(), FirecrawlSearchTool()],
            llm=llm,
            verbose=True,
        )
        research_task = Task(
            description=(
                "Answer-oriented research for the user query: {query}\n"
                "1. Search the knowledge base.\n"
                "2. If the results are missing or insufficient, search the web.\n"
                "Collect the key facts and note where each one came from."
            ),
            expected_output="Bullet-point research notes with sources.",
            agent=researcher,
        )

        writer = Agent(
            role="Response Writer",
            goal="Write a clear, correct answer to: {query}",
            backstory="You turn research notes into concise, well-structured answers.",
            llm=llm,
            verbose=True,
        )
        writer_task = Task(
            description=(
                "Using the research notes, write the final answer to: {query}. "
                "Be concise, cite sources inline, and say so if the answer is unknown."
            ),
            expected_output="A short, well-formatted answer with sources.",
            agent=writer,
            context=[research_task],
        )

        self.crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, writer_task],
            process=Process.sequential,
            verbose=True,
        )

    def decode_request(self, request):
        return request["query"]

    def predict(self, query):
        return self.crew.kickoff(inputs={"query": query})

    def encode_response(self, output):
        return {"output": output.raw}


if __name__ == "__main__":
    server = ls.LitServer(AgenticRAGAPI(), accelerator="cpu", timeout=600)
    server.run(port=8000)
