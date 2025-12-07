# HOLODECK – AI D&D Dungeon Master (Project Outline)

## 1. Goal & Overview

Build an AI Agent that acts as a **personal AI Dungeon Master** for **voice-based D&D 5e** gameplay.

- **Mode:** Primarily voice: players speak, AI narrates back.
- **Platform:** Laptop for development; Raspberry Pi as optional production host.
- **Scope (MVP):** Single 5-room dungeon adventure with one player character.

The assistant (AI DM) will interpret natural language player actions, consult local tools (dice, rules, database), and respond with structured JSON that describes narration and game-state changes.

---

## 2. Core Technologies

- **LLM / DM Brain:** OpenAI Chat Completions API
- **Speech-to-Text:** OpenAI Whisper API
- **Text-to-Speech:** Any TTS service (OpenAI TTS or similar)
- **Data Storage:** Local SQLite database (`holodeck.db`)
- **External APIs:** Preferred over self-hosted models where they simplify implementation

---

## 3. Interaction Model

### 3.1 Voice Flow

1. System continuously listens for a **wake keyword** (usually the character name).
2. When keyword is detected, capture the **full utterance**.
3. Send audio to Whisper → obtain transcribed text.
4. Build a `GameRequest` object:

```jsonc
{
  "session_id": "session_123",
  "active_speaker": "Kraven",
  "player_utterance": "I want to open that door.",
  "timestamp": "2025-12-06T21:34:00Z",
  "game_state_snapshot": {
    "location_id": "room_1",
    "characters": ["Kraven"],
    "hp": { "Kraven": 14 },
    "conditions": [],
    "inventory_summary": ["shortsword", "torch", "10 gold"]
  }
}
```

5. Send this to the AI DM with tools enabled.
6. AI DM returns a `GameResponse` JSON (see §6).
7. Apply state changes using the SQLite DB and, optionally, Google Sheets mirrors.
8. Convert narration to speech via TTS and play it.
9. Append both request and response to session history for context.

### 3.2 Text-Only Mode

For development, a text-only REPL mode must exist:

- User types actions instead of speaking.
- Same `GameRequest` / `GameResponse` flow is used, bypassing Whisper and TTS.
- Makes it easy to iterate on prompts, tools, and DB structure.

---

## 4. AI Agent Design

### 4.1 Single Agent (MVP)

Use a **single AI DM agent** configured with:

- A strong **system prompt** that defines:
  - DM role and tone.
  - Adherence to D&D 5e SRD (condensed rules).
  - Requirement to output **strict JSON** only.
- Access to a set of **tools** implemented in Python and exposed with OpenAI function-calling schema.
- Context including:
  - Last N messages of the conversation (e.g. 10 turns).
  - A compact `game_state_snapshot` built from SQLite.
  - A short `campaign_summary` string maintained over time.

Future versions may introduce multiple agents (Narrator, Rules, Combat, etc.), but MVP is a single DM agent.

### 4.2 Responsibilities

The AI DM must:

- Interpret the player’s natural language actions.
- Decide which rules/mechanics apply (checks, saves, attack rolls, environmental hazards).
- Call tools for:
  - Dice rolling.
  - Rules lookup.
  - Character and monster data.
  - Room details.
- Produce a JSON-only response containing:
  - Descriptive narration.
  - Structured actions to update game state (HP, gold, location, conditions, flags, etc.).
  - Optional hints or a suggested next prompt.

---

## 5. Tools & Functions

All tools are exposed via OpenAI function-calling with explicit JSON schemas. Below is the conceptual spec (implementation will add exact parameter types).

### 5.1 `roll_dice`

**Purpose:** Perform dice rolls using standard notation and return all details.

- **Arguments:**
  - `notation` (string): e.g. `"1d20+3"`, `"2d6"`.
  - `reason` (string): short description, e.g. `"perception check"`.
- **Returns:**
  - `total` (int)
  - `individual_rolls` (array of ints)
  - `notation` (string)
  - `reason` (string)

### 5.2 `get_room_details`

**Purpose:** Retrieve details for a specific dungeon room from SQLite.

- **Arguments:**
  - `room_key` (string): e.g. `"room_1"`.
  - `detail_level` (string): `"overview"` or `"full"`.
- **Returns (example):**
```jsonc
{
  "room_key": "room_1",
  "title": "Ice Chasm",
  "short_description": "...",
  "full_description": "...",
  "exits": [
    { "direction": "inward", "room_key": "room_2", "description": "..." }
  ],
  "features": [
    { "type": "monster_instance", "name": "Frost Harpy of the Chasm" }
  ]
}
```

### 5.3 `get_character_data`

**Purpose:** Read the current character state from Google Sheets.

- **Arguments:**
  - `character_name` (string)

- **Returns (example):**
```jsonc
{
  "name": "Kraven",
  "class": "Fighter",
  "level": 3,
  "hp": 24,
  "max_hp": 24,
  "abilities": { "str": 16, "dex": 12, "con": 14, "int": 10, "wis": 10, "cha": 8 },
  "skills": { "athletics": 5, "perception": 3 },
  "gold": 15,
  "inventory": [
    { "name": "Longsword", "qty": 1 },
    { "name": "Shield", "qty": 1 },
    { "name": "Torch", "qty": 3 }
  ],
  "conditions": [],
  "location_room_key": "room_1"
}
```

### 5.4 `update_character_data`

**Purpose:** Modify character stats or inventory in Google Sheets.

- **Arguments:**
  - `character_name` (string)
  - `changes` (array of objects):
    - `field` (string): `"hp"`, `"gold"`, `"inventory"`, `"conditions"`, etc.
    - `operation` (string): `"set"`, `"increment"`, `"decrement"`, `"add_item"`, `"remove_item"`.
    - `value` (number or string or object, depending on field).

- **Returns:**
  - `success` (bool)
  - `new_state` (optional full character snapshot).

### 5.5 `rules_lookup`

**Purpose:** Lookup a condensed 5e SRD rule by topic.

- **Arguments:**
  - `topic` (string): e.g. `"ability checks"`, `"grappling"`, `"lightly obscured"`.

- **Returns (example):**
```jsonc
{
  "topic": "ability checks",
  "summary": "When a character attempts an action with uncertain outcome, roll d20 + relevant ability modifier...",
  "mechanics": {
    "roll_type": "d20",
    "uses_proficiency": true,
    "dc_guidelines": [10, 15, 20]
  }
}
```

### 5.6 `get_monster_stats`

**Purpose:** Retrieve a monster template from SQLite by name.

- **Arguments:**
  - `monster_name` (string): e.g. `"Frost Harpy"`, `"Will-o'-Wisp"`.

- **Returns:**
  - Basic stat block as JSON, including AC, HP, abilities, and actions.

### 5.7 Additional / Optional Tools

- `get_game_flags` / `update_game_flag` to manage world state (e.g. doors unlocked, NPC attitudes).
- `log_story_event` to append structured events to a story log.

---

## 6. Response Format (AI → Engine)

The AI DM **must** respond with **strict JSON only**, no prose outside JSON. Example schema:

```jsonc
{
  "narration": "You fail to persuade the guard. He folds his arms and demands five gold pieces.",
  "out_of_character_notes": "Persuasion check failed vs DC 12.",
  "actions": [
    {
      "type": "update_character",
      "character_name": "Kraven",
      "changes": [
        { "field": "gold", "operation": "decrement", "value": 5 }
      ]
    },
    {
      "type": "update_location",
      "target": "party",
      "location_room_key": "room_2"
    }
  ],
  "dice_rolls": [
    {
      "purpose": "persuasion_check",
      "notation": "1d20+3",
      "result": 6,
      "dc": 12,
      "success": false
    }
  ],
  "tool_calls": [
    {
      "tool": "roll_dice",
      "arguments": {
        "notation": "1d20+3",
        "reason": "Persuasion check vs guard"
      }
    }
  ],
  "next_prompt_suggestion": "The guard is waiting for payment or a better offer. What do you do?"
}
```

The backend engine will:

1. Validate JSON.
2. Execute `tool_calls` as actual function calls if present.
3. Apply `actions` to Google Sheets (for character data) and SQLite (for other game data).
4. Log `dice_rolls` and narration in the story log.
5. Send `narration` to TTS for playback.

---

## 7. Memory & Context

### 7.1 Layers

1. **Chat History (ephemeral):**
   - Last ~10 user/DM turns included in each LLM call.

2. **Game State (persistent, SQLite):**
   - Adventure ID, current room, character records, monster instances, flags.

3. **Campaign Summary:**
   - Short text summary updated occasionally and injected as a separate message, e.g.:
   - "Previously: Kraven explored the Ice Chasm, survived the Frost Harpy, and calmed some of the bound spirits."

### 7.2 Prompt Inputs

Each LLM request typically includes:

- System prompt with DM role + rules.
- A `campaign_summary` message.
- Recent chat history.
- Current `game_state_snapshot` (JSON).
- The latest `GameRequest` from the player.

---

## 8. Development Plan (MVP)

1. **Text-only engine**
   - Implement SQLite schema and game-state loader/updater functions.
   - Implement tools as regular Python functions.
   - Build a REPL loop to call the AI and apply responses.

2. **Prompts & Tools**
   - Write DM system prompt.
   - Define tool schemas and test them with manual calls.

3. **Adventure Data**
   - Populate SQLite with:
     - The Wailing Glacier adventure.
     - Its rooms, exits, monsters, and monster instances.

4. **Voice I/O**
   - Integrate Whisper for STT and chosen TTS engine for DM voice.

5. **Refinement**
   - Add story logging, flags, and campaign summary generation.
   - Optimise prompts and tool usage for reliability.

6. **Raspberry Pi Deployment (optional)**
   - Deploy backend + minimal UI to a Pi, offloading LLM calls to OpenAI.
