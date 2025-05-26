
# orchestration_examples/parallel_analysis.py
from google.adk.agents import Agent, ParallelAgent, BaseAgent, InvocationContext 
from google.adk.events.event import Event
from google.adk.runners import InMemoryRunner; from google.genai.types import Content,Part; import asyncio
sentiment_analyzer_agent=Agent(name="sentiment_analyzer",model="gemini-2.0-flash",instruction="Analyze sentiment. Output: positive, negative, or neutral.")
keyword_extractor_agent=Agent(name="keyword_extractor",model="gemini-2.0-flash",instruction="Extract up to 3 keywords. Output: comma-separated list.")
text_analysis_parallel_tasks=ParallelAgent(name="parallel_text_analyzer",sub_agents=[sentiment_analyzer_agent,keyword_extractor_agent])
class AnalysisOrchestrator(BaseAgent): # Changed to BaseAgent for custom _run_async_impl
    async def _run_async_impl(self, ctx: InvocationContext):
        print("  Orchestrator: Starting parallel analysis...")
        all_parallel_events = []; sentiment_res="N/A"; keywords_res="N/A"
        async for event in text_analysis_parallel_tasks.run_async(ctx): # text_analysis_parallel_tasks defined above
            all_parallel_events.append(event) 
        for event in all_parallel_events:
            if event.author==sentiment_analyzer_agent.name and event.content and event.content.parts[0].text and not (event.get_function_calls() or event.get_function_responses()):
                sentiment_res=f"Sentiment ({event.branch}): {event.content.parts[0].text.strip()}"
            elif event.author==keyword_extractor_agent.name and event.content and event.content.parts[0].text and not (event.get_function_calls() or event.get_function_responses()):
                keywords_res=f"Keywords ({event.branch}): {event.content.parts[0].text.strip()}"
        yield Event(invocation_id=ctx.invocation_id,author=self.name,content=Content(parts=[Part(text=f"Combined results:\n{sentiment_res}\n{keywords_res}")]))
analysis_orchestrator=AnalysisOrchestrator(name="analysis_orchestrator",description="Orchestrates parallel text analysis.",sub_agents=[text_analysis_parallel_tasks]) # BaseAgent takes name/desc
if __name__=="__main__":
    runner=InMemoryRunner(agent=analysis_orchestrator,app_name="ParallelAnalysisApp")
    review_text="ADK is powerful and flexible!"
    print(f"YOU: Analyze: \"{review_text}\"");user_message=Content(parts=[Part(text=review_text)])
    async def main():
        async for event in runner.run_async(user_id="parallel_user",session_id="s_parallel_an",new_message=user_message):
            if event.author==analysis_orchestrator.name and event.content and event.content.parts:
                print(f"ORCHESTRATOR: {event.content.parts[0].text.strip()}")
        s=await runner.session_service.get_session("ParallelAnalysisApp","parallel_user","s_parallel_an");print(f"\nFinal state: {s.state}")
    asyncio.run(main())

