from google.adk.agents import Agent, ParallelAgent # Import ParallelAgent
from google.adk.events import Event
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

# --- Define Sub-Agents for Parallel Execution ---
sentiment_analyzer_agent = Agent(
    name="sentiment_analyzer",
    model=DEFAULT_LLM,
    instruction="Analyze the sentiment of the provided text. Output only 'positive', 'negative', or 'neutral'.",
    description="Analyzes text sentiment."
    # output_key="sentiment_analysis_result" # LlmAgent can save its output to state
)
# For LlmAgent output_key to work as expected with ParallelAgent,
# each agent's output needs to be distinguishable.
# We'll set it in the orchestrator for this example.

keyword_extractor_agent = Agent(
    name="keyword_extractor",
    model=DEFAULT_LLM,
    instruction="Extract up to 3 main keywords from the provided text. Output as a comma-separated list.",
    description="Extracts keywords from text."
    # output_key="keyword_extraction_result"
)

# --- Define the ParallelAgent ---
text_analysis_parallel_tasks = ParallelAgent(
    name="parallel_text_analyzer",
    description="Performs sentiment analysis and keyword extraction in parallel.",
    sub_agents=[
        sentiment_analyzer_agent,
        keyword_extractor_agent
    ]
)

# --- Orchestrator to use the ParallelAgent and combine results ---
class AnalysisOrchestrator(Agent): # Custom agent to manage parallel results
    async def _run_async_impl(self, ctx):
        # First, run the parallel tasks. The ParallelAgent itself doesn't have an LLM.
        # It yields events from its children. We need to collect those.
        # For this demo, we'll assume the user's initial text is the input for parallel tasks.

        # Re-invoke the ParallelAgent. This is a bit manual for this example.
        # A more robust way would be to make ParallelAgent a tool for the orchestrator
        # or use a different flow.

        print("  Orchestrator: Starting parallel analysis...")
        all_parallel_events = []
        async for event in text_analysis_parallel_tasks.run_async(ctx):
            all_parallel_events.append(event)
            # Optionally yield these to show progress
            # yield event

        # Now, extract results from the state (assuming sub-agents saved them)
        # This requires sub-agents to be designed to save their distinct outputs to state.
        # For simplicity, we'll assume the LLM for the orchestrator will synthesize
        # from the combined history of the parallel agents.
        # The ParallelAgent sets a distinct `branch` for each sub-agent's events.

        # Create a summary prompt for the orchestrator's LLM
        history_summary = "Parallel analysis performed. Results from sub-agents:\n"
        sentiment_result_text = "Sentiment: Not found."
        keywords_result_text = "Keywords: Not found."

        for event in all_parallel_events:
            if event.author == sentiment_analyzer_agent.name and event.content and event.content.parts[0].text:
                if not event.get_function_calls() and not event.get_function_responses(): # Final text
                    sentiment_result_text = f"Sentiment Analysis by '{event.author}' (branch '{event.branch}'): {event.content.parts[0].text.strip()}"
            elif event.author == keyword_extractor_agent.name and event.content and event.content.parts[0].text:
                 if not event.get_function_calls() and not event.get_function_responses(): # Final text
                    keywords_result_text = f"Keyword Extraction by '{event.author}' (branch '{event.branch}'): {event.content.parts[0].text.strip()}"

        combined_results_text = f"{sentiment_result_text}\n{keywords_result_text}"
        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name, # Orchestrator's name
            content=Content(parts=[Part(text=f"Combined analysis results:\n{combined_results_text}")])
        )

analysis_orchestrator = AnalysisOrchestrator( # Using our custom LlmAgent-like class
    name="analysis_orchestrator",
    # instruction="You received analysis results. Summarize them for the user.",
    description="Orchestrates parallel text analysis and presents combined results.",
    sub_agents=[text_analysis_parallel_tasks] # Conceptually, it USES the parallel agent
)

# --- Running the ParallelAgent (via orchestrator) ---
if __name__ == "__main__":
    runner = InMemoryRunner(agent=analysis_orchestrator, app_name="ParallelAnalysisApp")
    session_id = "s_parallel_an"
    user_id = "parallel_user"
    create_session(runner, user_id=user_id, session_id=session_id)

    review_text = "This ADK framework is incredibly powerful and flexible, making agent development a breeze! Highly recommended."
    print(f"YOU: Analyze this text: {review_text}")
    user_message = Content(parts=[Part(text=review_text)], role="user")  # User message to the agent

    async def main():
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message):
            if event.author == analysis_orchestrator.name and event.content and event.content.parts:
                print(f"ORCHESTRATOR: {event.content.parts[0].text.strip()}")


    asyncio.run(main())