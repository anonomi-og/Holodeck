import sqlite3
import os
import re
from database import get_db_connection, DB_PATH
import json

# Absolute paths to source docs
PROJECT_DOCS_DIR = r"g:\My Drive\Projects\Holodeck\Project Docs"
SCHEMA_PATH = r"g:\My Drive\Projects\Holodeck\src\backend\schema.sql"
SRD_RULES_PATH = os.path.join(PROJECT_DOCS_DIR, "srd_rules_condensed.md")
ADVENTURE_SQL_PATH = os.path.join(PROJECT_DOCS_DIR, "wailing_glacier_inserts.sql")

def init_db():
    print(f"Initializing database at {DB_PATH}...")
    
    # 1. Create Tables
    with get_db_connection() as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
    print("Schema initialized.")

    # 2. Ingest Rules
    ingest_rules()

    # 3. Ingest Adventure
    ingest_adventure()

    # 4. Create Default Character
    create_test_character()

    print("Database initialization complete!")

def ingest_rules():
    print("Ingesting SRD Rules...")
    if not os.path.exists(SRD_RULES_PATH):
        print(f"Warning: Rules file not found at {SRD_RULES_PATH}")
        return

    with open(SRD_RULES_PATH, 'r') as f:
        content = f.read()

    # Regex to find sections starting with ###
    # This is a simple parser based on the known format
    sections = re.split(r'^###\s+', content, flags=re.MULTILINE)[1:] # Skip preamble
    
    rules_to_insert = []

    for section in sections:
        lines = section.strip().split('\n')
        topic_name = lines[0].strip()
        
        # Parse fields
        topic = ""
        category = ""
        summary = ""
        mechanics = {}
        tags = ""
        
        current_field = None
        mechanics_buffer = []

        for line in lines[1:]:
            line = line.strip()
            if not line: continue
            
            if line.startswith("- **Topic:**"):
                topic = line.split(":", 1)[1].strip()
            elif line.startswith("- **Category:**"):
                category = line.split(":", 1)[1].strip()
            elif line.startswith("- **Summary:**"):
                summary = line.split(":", 1)[1].strip()
            elif line.startswith("- **Tags:**"):
                tags = line.split(":", 1)[1].strip()
            elif line.startswith("- **Key Mechanics:**"):
                current_field = "mechanics"
            elif current_field == "mechanics":
                if line.startswith("-"):
                    mechanics_buffer.append(line.lstrip("- ").strip())
        
        # Build mechanics JSON
        if mechanics_buffer:
             mechanics_json = json.dumps({"points": mechanics_buffer})
        else:
            mechanics_json = "{}"

        if topic and category:
            rules_to_insert.append((topic, category, summary, mechanics_json, tags))

    if rules_to_insert:
        with get_db_connection() as conn:
            conn.executemany(
                "INSERT INTO rule (topic, category, summary, mechanics_json, tags) VALUES (?, ?, ?, ?, ?)",
                rules_to_insert
            )
            conn.commit()
        print(f"Inserted {len(rules_to_insert)} rules.")
    else:
        print("No rules found to insert.")

def ingest_adventure():
    print("Ingesting Adventure Data...")
    if not os.path.exists(ADVENTURE_SQL_PATH):
        print(f"Warning: Adventure SQL not found at {ADVENTURE_SQL_PATH}")
        return

    with open(ADVENTURE_SQL_PATH, 'r') as f:
        sql_content = f.read()

    with get_db_connection() as conn:
        try:
            conn.executescript(sql_content)
            conn.commit()
            print("Adventure data inserted.")
        except sqlite3.Error as e:
            print(f"Error inserting adventure data: {e}")

def create_test_character():
    print("Creating/Resetting Test Character 'Kraven'...")
    kraven_data = {
        "name": "Kraven",
        "class": "Fighter",
        "level": 3,
        "hp": 24,
        "max_hp": 24,
        "abilities": {"str": 16, "dex": 12, "con": 14, "int": 10, "wis": 10, "cha": 8},
        "skills": {"athletics": 5, "perception": 3},
        "inventory": [
            {"name": "Longsword", "qty": 1},
            {"name": "Shield", "qty": 1},
            {"name": "Torch", "qty": 3},
            {"name": "Potion of Healing", "qty": 1}
        ],
        "gold": 15
    }

    with get_db_connection() as conn:
        # Check if exists
        exists = conn.execute("SELECT id FROM character WHERE name = ?", ("Kraven",)).fetchone()
        
        if not exists:
            conn.execute("""
                INSERT INTO character (
                    adventure_id, name, class, level, hp, max_hp, 
                    abilities_json, skills_json, inventory_json, gold, location_room_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                1, # Adventure 1
                kraven_data["name"],
                kraven_data["class"],
                kraven_data["level"],
                kraven_data["hp"],
                kraven_data["max_hp"],
                json.dumps(kraven_data["abilities"]),
                json.dumps(kraven_data["skills"]),
                json.dumps(kraven_data["inventory"]),
                kraven_data["gold"],
                1 # Start in Room 1
            ))
            conn.commit()
            print("Created character 'Kraven'.")
        else:
            print("Character 'Kraven' already exists.")

if __name__ == "__main__":
    # Remove existing DB to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
