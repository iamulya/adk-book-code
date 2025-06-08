from google.adk.agents import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset # Key import
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from building_intelligent_agents.utils import load_environment_variables, create_session, DEFAULT_LLM
load_environment_variables()

# Assume the OpenAPI spec JSON from section 7.1 is saved in "petstore_openapi.json"
# Or, for this example, let's embed it as a string:
petstore_spec_str = """
{
  "openapi": "3.0.0",
  "info": { "title": "Simple Pet Store API", "version": "1.0.0" },
  "servers": [ { "url": "https://petstore.swagger.io/v2" } ],   
  "paths": {
    "/pet/findByStatus": {
      "get": {
        "summary": "Finds Pets by status",
        "operationId": "findPetsByStatus",
        "parameters": [
          {
            "name": "status", "in": "query", "required": true,
            "description": "Status values that need to be considered for filter",
            "schema": { "type": "string", "enum": ["available", "pending", "sold"] }
          }
        ],
        "responses": {
          "200": { "description": "successful operation", "content": { "application/json": { "schema": { "type": "array", "items": { "$ref": "#/components/schemas/Pet" } } } } }
        }
      }
    },
    "/pet": {
      "post": {
        "summary": "Add a new pet to the store",
        "operationId": "addPet",
        "requestBody": {
          "required": true,
          "content": { "application/json": { "schema": { "$ref": "#/components/schemas/Pet" } } }
        },
        "responses": { "200": { "description": "Successfully added pet" }}
      }
    }
  },
  "components": {
    "schemas": {
      "Pet": {
        "type": "object",
        "properties": {
          "id": { "type": "integer", "format": "int64" },
          "name": { "type": "string", "example": "doggie" },
          "status": { "type": "string", "description": "pet status in the store", "enum": ["available", "pending", "sold"] }
        },
        "required": ["name"]
      }
    }
  }
}
"""

# 1. Initialize the OpenAPIToolset
# We pass the spec string and specify its type.
petstore_toolset = OpenAPIToolset(
    spec_str=petstore_spec_str,
    spec_str_type="json" # or "yaml" if it were YAML
)

# If you had the spec as a Python dictionary:
# petstore_spec_dict = json.loads(petstore_spec_str)
# petstore_toolset = OpenAPIToolset(spec_dict=petstore_spec_dict)


# 2. Create an agent and provide the toolset
# The agent will automatically get all tools generated from the spec.
petstore_agent = Agent(
    name="petstore_manager",
    model=DEFAULT_LLM,
    instruction="You are an assistant for managing a pet store. Use the available tools to find or add pets.",
    tools=[petstore_toolset] # Pass the toolset instance
)

# --- Example of running this agent ---
if __name__ == "__main__":
    runner = InMemoryRunner(agent=petstore_agent, app_name="PetStoreApp")

    user_id="pet_user" 
    session_id="s_petstore"
    create_session(runner, session_id, user_id)

    prompts = [
        "Find all available pets.",
        "Can you add a new pet named 'Buddy' with status 'available' and id 12345?",
    ]

    async def main(): # Using async for runner.run
        for prompt_text in prompts:
            print(f"\nYOU: {prompt_text}")
            user_message = Content(parts=[Part(text=prompt_text)], role="user")
            print("PETSTORE_MANAGER: ", end="", flush=True)
            # In a real scenario, the Petstore API would be called.
            # Since petstore.swagger.io is a live mock, these calls will actually work!
            for event in runner.run(user_id=user_id, session_id=session_id, new_message=user_message):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            print()

    import asyncio
    asyncio.run(main())
