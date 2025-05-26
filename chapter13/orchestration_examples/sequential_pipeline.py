
# orchestration_examples/sequential_pipeline.py
from google.adk.agents import Agent, SequentialAgent 
from google.adk.tools import FunctionTool, ToolContext
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio; import re; from google.adk.sessions.state import State
def gather_user_data(name: str, email: str, tool_context: ToolContext) -> dict:
    """Gathers user name/email, stores in session state."""
    tool_context.state["user_name_collected"]=name; tool_context.state["user_email_collected"]=email
    return {"status":"success", "message":f"Data for {name} collected."}
gather_data_tool=FunctionTool(gather_user_data)
data_collection_agent=Agent(name="data_collector",model="gemini-2.0-flash",instruction="Collect user name/email using 'gather_user_data' tool.",tools=[gather_data_tool])
def validate_email_format(email: str, tool_context: ToolContext) -> dict:
    """Validates email format."""
    if re.match(r"[^@]+@[^@]+\.[^@]+", email): tool_context.state["email_validated"]=True; return {"is_valid":True,"email":email}
    else: tool_context.state["email_validated"]=False; return {"is_valid":False,"email":email,"error":"Invalid email."}
validate_email_tool=FunctionTool(validate_email_format)
email_validation_agent=Agent(name="email_validator",model="gemini-2.0-flash",instruction="Validate email from `state['user_email_collected']` using 'validate_email_format' tool.",tools=[validate_email_tool])
def send_welcome_email(tool_context: ToolContext) -> str:
    """Simulates sending welcome email if validated."""
    if tool_context.state.get("email_validated") and tool_context.state.get("user_name_collected"):
        return f"Welcome email sent to {tool_context.state['user_name_collected']} at {tool_context.state['user_email_collected']}."
    return "Could not send: email not validated or name missing."
send_email_tool=FunctionTool(send_welcome_email)
welcome_email_agent=Agent(name="welcome_emailer",model="gemini-2.0-flash",instruction="If `state['email_validated']` is true, use 'send_welcome_email' tool.",tools=[send_email_tool])
user_onboarding_pipeline=SequentialAgent(name="user_onboarding_orchestrator",sub_agents=[data_collection_agent,email_validation_agent,welcome_email_agent])
if __name__=="__main__":
    runner=InMemoryRunner(agent=user_onboarding_pipeline,app_name="OnboardingApp")
    initial_prompt="Onboard user Alice, email alice@example.com"
    print(f"YOU: {initial_prompt}");user_message=Content(parts=[Part(text=initial_prompt)])
    async def main():
        final_agent_responses=[]
        async for event in runner.run_async(user_id="new_user_seq",session_id="s_onboard_seq",new_message=user_message):
            print(f"  EVENT from [{event.author}]:")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text: print(f"    Text: {part.text.strip()}"); final_agent_responses.append(part.text.strip())
                    elif part.function_call: print(f"    Tool Call: {part.function_call.name}({part.function_call.args})")
                    elif part.function_response: print(f"    Tool Resp for {part.function_response.name}: {part.function_response.response}")
        print("\n--- Final Output from Pipeline ---"); print("SEQ_PIPELINE: "+" ".join(final_agent_responses[-1:])) # Get last text
        s = await runner.session_service.get_session("OnboardingApp","new_user_seq","s_onboard_seq"); print(f"\nFinal state: {s.state}")
    asyncio.run(main())

