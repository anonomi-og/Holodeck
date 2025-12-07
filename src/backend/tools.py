import random
import re
import json
from typing import Dict, Any, List, Optional
from database import execute_query

def roll_dice(notation: str, reason: str = "") -> Dict[str, Any]:
    """
    Rolls dice based on standard notation (e.g., '1d20+5', '2d6').
    """
    try:
        # Simple parser for XdY+Z or XdY-Z
        match = re.match(r"(\d+)d(\d+)([\+\-]\d+)?", notation.strip().lower())
        if not match:
             # Fallback for simple "d20"
            if notation.strip().lower() == "d20":
                match = re.search(r"()d(\d+)", "1d20")
            elif notation.strip().lower().startswith("d"):
                 match = re.search(r"()d(\d+)", "1" + notation.strip().lower())
            
            if not match:
                return {"error": f"Invalid dice notation: {notation}"}

        num_dice = int(match.group(1) or 1)
        die_faces = int(match.group(2))
        modifier_str = match.group(3) or "+0"
        modifier = int(modifier_str)

        rolls = [random.randint(1, die_faces) for _ in range(num_dice)]
        total = sum(rolls) + modifier

        return {
            "purpose": reason,
            "notation": notation,
            "total": total,
            "individual_rolls": rolls,
            "modifier": modifier,
            "result_str": f"{rolls} {modifier_str} = {total}"
        }
    except Exception as e:
        return {"error": f"Dice roll failed: {str(e)}"}

def get_room_details(room_key: str, adventure_id: int = 1) -> Dict[str, Any]:
    """Retrieve details for a specific dungeon room."""
    # Get Room
    room_query = "SELECT * FROM room WHERE room_key = ? AND adventure_id = ?"
    room = execute_query(room_query, (room_key, adventure_id), fetch_one=True)
    
    if not room:
        return {"error": f"Room {room_key} not found."}

    # Get Exits
    exits_query = "SELECT * FROM room_exit WHERE from_room_id = ?"
    exits = execute_query(exits_query, (room['id'],), fetch_all=True)

    # Get Monsters
    monsters_query = """
        SELECT mi.instance_name, mi.current_hp, mi.status, m.name as template_name
        FROM monster_instance mi
        JOIN monster m ON mi.monster_id = m.id
        WHERE mi.room_id = ? AND mi.status = 'alive'
    """
    monsters = execute_query(monsters_query, (room['id'],), fetch_all=True)

    return {
        "room_key": room['room_key'],
        "title": room['title'],
        "short_description": room['short_description'],
        "full_description": room['full_description'],
        "exits": [dict(e) for e in exits],
        "monsters": [dict(m) for m in monsters]
    }

def get_character_data(name: str) -> Dict[str, Any]:
    """Read the current character state."""
    query = "SELECT * FROM character WHERE name = ?"
    char = execute_query(query, (name,), fetch_one=True)
    
    if not char:
        return {"error": f"Character {name} not found."}

    # Parse JSON fields
    data = dict(char)
    for field in ['abilities_json', 'skills_json', 'inventory_json', 'conditions_json']:
        if data.get(field):
            try:
                data[field.replace('_json', '')] = json.loads(data[field])
                del data[field]
            except:
                pass
    return data

def update_character_data(character_name: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Modify character stats or inventory."""
    char = get_character_data(character_name)
    if "error" in char:
        return char

    char_id = char['id']
    
    success = True
    messages = []

    for change in changes:
        field = change.get("field")
        op = change.get("operation")
        val = change.get("value")

        if field == "hp":
            current = char['hp']
            if op == "decrement":
                new_val = max(0, current - val)
            elif op == "increment":
                new_val = min(char['max_hp'], current + val)
            elif op == "set":
                new_val = val
            else:
                continue
            
            execute_query("UPDATE character SET hp = ? WHERE id = ?", (new_val, char_id), commit=True)
            messages.append(f"HP updated to {new_val}")

        elif field == "gold":
            current = char['gold']
            if op == "decrement":
                new_val = max(0, current - val)
            elif op == "increment":
                new_val = current + val
            elif op == "set":
                new_val = val
            else:
                continue
            
            execute_query("UPDATE character SET gold = ? WHERE id = ?", (new_val, char_id), commit=True)
            messages.append(f"Gold updated to {new_val}")
        
        # Simple inventory (just add/remove items by name for MVP)
        elif field == "inventory":
            inv = char.get("inventory", [])
            # Implementation could be complex, for MVP just simple modifications
            # Assume val is {name: "Item", qty: 1}
            # This requires better JSON handling, keeping it simple for now
            pass 

    return {"success": success, "messages": messages}

def rules_lookup(topic: str) -> Dict[str, Any]:
    """Lookup a condensed 5e SRD rule by topic."""
    # Simple semantic search using LIKE
    query = """
        SELECT topic, summary, mechanics_json 
        FROM rule 
        WHERE topic LIKE ? OR tags LIKE ? 
        LIMIT 1
    """
    search_term = f"%{topic}%"
    rule = execute_query(query, (search_term, search_term), fetch_one=True)
    
    if rule:
        res = dict(rule)
        if res.get('mechanics_json'):
             try:
                 res['mechanics'] = json.loads(res['mechanics_json'])
                 del res['mechanics_json']
             except:
                 pass
        return res
    return {"message": f"No specific rule found for '{topic}'."}

def get_monster_stats(monster_name: str) -> Dict[str, Any]:
    """Retrieve a monster template from SQLite by name."""
    query = "SELECT * FROM monster WHERE name = ? OR srd_name = ?"
    monster = execute_query(query, (monster_name, monster_name), fetch_one=True)
    
    if monster:
        res = dict(monster)
        if res.get('meta_json'):
            try:
                res.update(json.loads(res['meta_json']))
                del res['meta_json']
            except:
                pass
        return res
    return {"error": "Monster not found"}

def move_character(character_name: str, room_key: str) -> Dict[str, Any]:
    """Move a character to a new room."""
    char = get_character_data(character_name)
    if "error" in char:
        return char

    # Verify room exists
    room = execute_query("SELECT id FROM room WHERE room_key = ?", (room_key,), fetch_one=True)
    if not room:
        return {"error": f"Room {room_key} not found"}

    execute_query(
        "UPDATE character SET location_room_id = ? WHERE id = ?", 
        (room['id'], char['id']), 
        commit=True
    )
    return {"success": True, "message": f"Moved {character_name} to {room_key}"}
