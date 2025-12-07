import os
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from tools import (
    roll_dice, get_room_details, get_character_data, update_character_data, 
    rules_lookup, get_monster_stats, move_character
)

logger = logging.getLogger(__name__)
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("LLM_MODEL", "gpt-4o")

# Tool Schemas for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "roll_dice",
            "description": "Roll dice using standard notation (e.g. 1d20+3).",
            "parameters": {
                "type": "object",
                "properties": {
                    "notation": {"type": "string", "description": "Dice notation e.g. 1d20+5"},
                    "reason": {"type": "string", "description": "Reason for the roll"}
                },
                "required": ["notation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_room_details",
            "description": "Get details about a specific room.",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_key": {"type": "string", "description": "The unique key of the room e.g. room_1"}
                },
                "required": ["room_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rules_lookup",
            "description": "Lookup a D&D 5e rule.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The rule topic to search for"}
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_character_data",
            "description": "Update character stats (HP, Gold, Inventory).",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "changes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {"type": "string", "enum": ["hp", "gold"]},
                                "operation": {"type": "string", "enum": ["increment", "decrement", "set"]},
                                "value": {"type": "integer"}
                            },
                            "required": ["field", "operation", "value"]
                        }
                    }
                },
                "required": ["character_name", "changes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_character",
            "description": "Move the character to a different room via a known exit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "room_key": {"type": "string", "description": "Target room key (e.g. room_2)"}
                },
                "required": ["character_name", "room_key"]
            }
        }
    }
]

SYSTEM_PROMPT = """
You are the Dungeon Master (DM) for a solo D&D 5e adventure called 'The Wailing Glacier'.
Your goal is to narrate the adventure, manage the game state, and respond to the player's actions.

GUIDELINES:
1. **Be Immersive**: Describe the environment, sounds, smells, and atmosphere. Use the provided room descriptions.
2. **Use Tools**:
    - Use `get_room_details` when the player enters a new room or asks for details.
    - Use `rules_lookup` if you are unsure about a mechanic.
    - Use `roll_dice` for ANY outcome that is uncertain (attacks, checks, saves).
    - Use `update_character_data` to track HP changes, gold, etc.
3. **Response Format**:
    - Provide a JSON response with:
        - `narration`: The story text to show the user.
        - `out_of_character`: (Optional) Mechanics logic explaining what happened (e.g. "Rolled 15 vs DC 12, Success").
    - DO NOT output plain text outside the JSON.

4. **Game State**:
    - You know the current room and character status.
    - If the player hits 0 HP, they are unconscious (death saves).

Remember: You are the interface to the world.
"""

def process_player_action(player_input: str, character_name: str, session_history: List[Dict]) -> Dict[str, Any]:
    """
    Main loop to process a turn.
    """
    
    # 1. Fetch Context
    char_data = get_character_data(character_name)
    current_room_key = "room_1" # Default fallback
    if isinstance(char_data, dict) and "location_room_id" in char_data:
        # We need to map ID to Key. For MVP, let's just cheat and query room details by ID? 
        # Or better, just get current room details here. 
        # I'll rely on the agent to call get_room_details based on context or history, 
        # BUT providing it in the prompt is better.
        pass

    context_message = f"""
    Current Character State: {json.dumps(char_data)}
    Player Input: "{player_input}"
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    
    # Add history (last 5 turns)
    messages.extend(session_history[-5:])
    
    messages.append({"role": "user", "content": context_message})

    logger.info(f"Processing action for {character_name}: {player_input}")

    # 2. LLM Call
    try:
        logger.info("Sending request to LLM...")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        logger.info("Received response from LLM.")
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return {"narration": "Error connecting to AI brain.", "out_of_character": str(e)}

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # 3. Handle Tool Calls
    if tool_calls:
        logger.info(f"LLM requested {len(tool_calls)} tools.")
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            logger.info(f"Executing tool: {function_name} with args {function_args}")
            
            tool_result = "{}"
            
            try:
                if function_name == "roll_dice":
                    tool_result = json.dumps(roll_dice(**function_args))
                elif function_name == "get_room_details":
                    tool_result = json.dumps(get_room_details(**function_args))
                elif function_name == "rules_lookup":
                    tool_result = json.dumps(rules_lookup(**function_args))
                elif function_name == "update_character_data":
                    tool_result = json.dumps(update_character_data(**function_args))
                elif function_name == "move_character":
                    tool_result = json.dumps(move_character(**function_args))
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                tool_result = json.dumps({"error": str(e)})

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result
            })
        
        # 4. Final Response after tools
        logger.info("Sending follow-up request to LLM with tool outputs...")
        try:
            final_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                response_format={ "type": "json_object" } # Ensure JSON output
            )
            final_content = final_response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Follow-up Error: {e}")
            return {"narration": "The DM struggles to describe the outcome.", "out_of_character": f"Follow-up Error: {str(e)}"}
    else:
        logger.info("No tools called. Using direct response.")
        final_content = response_message.content

    logger.info(f"Final LLM content: {final_content}")

    # Parse JSON output
    try:
        if not final_content:
             return {"narration": "The DM is silent."}
        return json.loads(final_content)
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON from LLM. Returning raw content.")
        # Fallback if model fails to output JSON despite instructions
        return {"narration": final_content, "out_of_character": "Model output raw text."}
