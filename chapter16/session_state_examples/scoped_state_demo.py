
# session_state_examples/scoped_state_demo.py
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext
from google.adk.runners import InMemoryRunner
from google.adk.sessions.state import State 
from google.genai.types import Content, Part; import asyncio
def manage_preferences(tool_context: ToolContext, theme: str = None, language: str = None) -> dict:
    """Sets/gets user and app preferences."""
    changes={};
    if theme: tool_context.state[State.USER_PREFIX + "theme"]=theme; changes["user_theme_set"]=theme
    if language: tool_context.state[State.APP_PREFIX + "default_language"]=language; changes["app_language_set"]=language
    tool_context.state["last_pref_tool_call_id"]=tool_context.function_call_id
    tool_context.state[State.TEMP_PREFIX + "last_tool_name"]="manage_preferences"
    return {"status":"Prefs updated.","changes":changes, "user_theme":tool_context.state.get(State.USER_PREFIX+"theme"), "app_lang":tool_context.state.get(State.APP_PREFIX+"default_language")}
preference_tool=FunctionTool(manage_preferences)
state_demo_agent=Agent(name="pref_mgr",model="gemini-2.0-flash",instruction="Manage prefs with 'manage_preferences' tool.",tools=[preference_tool])
if __name__=="__main__":
    runner=InMemoryRunner(agent=state_demo_agent,app_name="PrefsDemo")
    u1="user_alpha"; u2="user_beta"; s1u1="s1_alpha"; s2u1="s2_alpha"; s1u2="s1_beta"
    async def run_and_print_state(uid,sid,prompt,app="PrefsDemo"):
        print(f"\n--- User:{uid},Session:{sid} ---\nYOU:{prompt}")
        msg=Content(parts=[Part(text=prompt)]);print("AGENT:",end="",flush=True)
        async for ev in runner.run_async(uid,sid,msg):
            if ev.author==state_demo_agent.name and ev.content and ev.content.parts[0].text and not (ev.get_function_calls() or ev.get_function_responses()):print(ev.content.parts[0].text.strip())
        s=await runner.session_service.get_session(app,uid,sid)
        print(f"  Session State:{ {k:v for k,v in s.state.items() if not (k.startswith(State.APP_PREFIX) or k.startswith(State.USER_PREFIX))} }")
        print(f"  User State ({uid}):{ {k:v for k,v in s.state.items() if k.startswith(State.USER_PREFIX)} }")
        print(f"  App State ({app}):{ {k:v for k,v in s.state.items() if k.startswith(State.APP_PREFIX)} }")
        print(f"  Temp State:{ {k:v for k,v in s.state.items() if k.startswith(State.TEMP_PREFIX)} }")
    async def main():
        await run_and_print_state(u1,s1u1,"Set theme 'dark', app lang 'English'.")
        await run_and_print_state(u1,s2u1,"My theme and app lang?")
        await run_and_print_state(u2,s1u2,"Set theme 'light'. App lang?")
        await run_and_print_state(u1,s1u1,"My theme again.")
    asyncio.run(main())

