from agent import process_player_action
from tools import get_character_data
from init_db import init_db
import json
import sqlite3

def test_game_loop():
    print("--- Starting Verification ---")
    
    # 1. Reset DB
    import os
    if os.path.exists("holodeck.db"):
        os.remove("holodeck.db")
    init_db()
    
    character_name = "Kraven"
    history = []

    # 2. Test 1: Initial Look
    print("\n[Test 1] Action: 'Look around'")
    response = process_player_action("Look around", character_name, history)
    print("Response:", json.dumps(response, indent=2))
    
    if not response.get("narration"):
        print("FAIL: No narration in response.")
        return
    else:
        print("PASS: Narration received.")
    
    history.append({"role": "user", "content": "Look around"})
    history.append({"role": "assistant", "content": response.get("narration")})

    # 3. Test 2: Move to Room 2
    # We need to make sure the AI knows about the exit.
    print("\n[Test 2] Action: 'I enter the tunnel to the glacier'")
    response = process_player_action("I enter the tunnel to the glacier", character_name, history)
    print("Response:", json.dumps(response, indent=2))

    # Verify DB update
    char_data = get_character_data(character_name)
    # Room 1 is ID 1. Room 2 is ID 2.
    # The exit from Room 1 to Room 2 is 'inward' -> Room 2.
    # We hope the AI called update_character_data or similar, OR just narrated it.
    # In MVP, we rely on the AI to call tools or for us to parse the response actions if we had them.
    # But my agent.py currently just returns the narration and executes tools internally.
    # Does 'agent.py' handle location updates?
    # The tool `update_character_data` only handles hp/gold/inventory/conditions?
    # Wait, `update_character_data` in `tools.py` does NOT handle location?
    # I should check `tools.py`. It probably doesn't based on my memory.
    # I need to fix `tools.py` to allow location updates if the AI decides to move the player.
    # Or add `update_location` tool.
    
    print(f"Current Location ID: {char_data.get('location_room_id')}")

if __name__ == "__main__":
    test_game_loop()
