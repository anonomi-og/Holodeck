# HOLODECK Database Structure (SQLite)

This document describes the **SQLite schema** used by the HOLODECK project. It is designed to support:

- Adventure data (rooms, exits, monsters, instances)
- Player character data
- World flags and story logs
- Condensed SRD rules for AI lookup

The actual database file is typically called **`holodeck.db`**.

---

## Overview of Tables

Core tables:

1. `adventure` – Top-level adventures (e.g. “The Wailing Glacier”).
2. `room` – Rooms/areas within an adventure.
3. `room_exit` – Directional links between rooms.
4. `monster` – Monster templates (similar to SRD stat blocks).
5. `monster_instance` – Specific monster instances in specific rooms.
6. `character` – Player characters.
7. `game_flag` – Key/value flags for story and world state.
8. `story_log` – History of events and dialogue for recap/debugging.
9. `rule` – Condensed 5e SRD rules entries for `rules_lookup`.

All foreign keys reference `INTEGER PRIMARY KEY` IDs and `PRAGMA foreign_keys = ON` should be enabled.

---

## Table: `adventure`

**Purpose:** Top-level container for a dungeon or campaign segment.

```sql
CREATE TABLE adventure (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,          -- e.g. 'The Wailing Glacier'
    description     TEXT,                   -- short summary
    starting_room_id INTEGER,               -- first room for this adventure
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (starting_room_id) REFERENCES room(id)
);
```

---

## Table: `room`

**Purpose:** Individual rooms/areas within an adventure.

```sql
CREATE TABLE room (
    id                  INTEGER PRIMARY KEY,
    adventure_id        INTEGER NOT NULL,
    room_key            TEXT NOT NULL,      -- stable identifier like 'room_1'
    title               TEXT NOT NULL,      -- short title
    short_description   TEXT NOT NULL,      -- brief flavour
    full_description    TEXT NOT NULL,      -- detailed narration
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now')),
    UNIQUE (adventure_id, room_key),
    FOREIGN KEY (adventure_id) REFERENCES adventure(id)
);
```

**Usage:**

- `room_key` is what the AI refers to in JSON (e.g. `location_room_key`).
- The `get_room_details` tool queries by `room_key` + `adventure_id`.

---

## Table: `room_exit`

**Purpose:** Represent directional links between rooms.

```sql
CREATE TABLE room_exit (
    id              INTEGER PRIMARY KEY,
    adventure_id    INTEGER NOT NULL,
    from_room_id    INTEGER NOT NULL,
    direction       TEXT NOT NULL,      -- e.g. 'north', 'south', 'deeper', 'back'
    to_room_id      INTEGER NOT NULL,
    description     TEXT,               -- flavour text for the exit
    FOREIGN KEY (adventure_id) REFERENCES adventure(id),
    FOREIGN KEY (from_room_id) REFERENCES room(id),
    FOREIGN KEY (to_room_id) REFERENCES room(id),
    UNIQUE (adventure_id, from_room_id, direction)
);
```

**Usage:**

- Enables the AI to describe and reason about available exits.
- The room loader can fetch exits and pass them into `game_state_snapshot`.

---

## Table: `monster`

**Purpose:** Store monster templates (similar to SRD stat blocks) in a flexible way.

```sql
CREATE TABLE monster (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,          -- display name, e.g. 'Frost Harpy'
    srd_name        TEXT,                   -- base SRD name, e.g. 'Harpy'
    base_hp         INTEGER,                -- default HP
    base_ac         INTEGER,                -- default AC
    meta_json       TEXT NOT NULL,          -- JSON blob containing full stat block
    created_at      TEXT DEFAULT (datetime('now'))
);
```

**`meta_json` example:**

```jsonc
{
  "size": "Medium",
  "type": "monstrosity",
  "alignment": "chaotic evil",
  "speed": "20 ft., fly 40 ft.",
  "abilities": { "str": 12, "dex": 13, "con": 12, "int": 7, "wis": 10, "cha": 13 },
  "traits": [ ... ],
  "actions": [ ... ],
  "flavour": "Short description for the AI."
}
```

The `get_monster_stats` tool returns this JSON for a named monster.

---

## Table: `monster_instance`

**Purpose:** Represent specific monsters that exist in rooms for this adventure.

```sql
CREATE TABLE monster_instance (
    id              INTEGER PRIMARY KEY,
    adventure_id    INTEGER NOT NULL,
    room_id         INTEGER NOT NULL,
    monster_id      INTEGER NOT NULL,
    instance_name   TEXT,                   -- e.g. 'Frost Harpy of the Chasm'
    current_hp      INTEGER,                -- current HP in play
    status          TEXT DEFAULT 'alive',   -- 'alive', 'unconscious', 'dead', etc.
    notes           TEXT,                   -- optional DM notes
    FOREIGN KEY (adventure_id) REFERENCES adventure(id),
    FOREIGN KEY (room_id) REFERENCES room(id),
    FOREIGN KEY (monster_id) REFERENCES monster(id)
);
```

**Usage:**

- Combat updates `current_hp` and `status`.
- Room loaders can query `monster_instance` for the active room to populate `nearby_monsters` in the `game_state_snapshot`.

---

## Table: `character`

**Purpose:** Store player character data in a flexible way.

```sql
CREATE TABLE character (
    id              INTEGER PRIMARY KEY,
    adventure_id    INTEGER NOT NULL,
    name            TEXT NOT NULL,          -- character name
    player_name     TEXT,                   -- real-world player name (optional)
    class           TEXT,
    level           INTEGER,
    hp              INTEGER,
    max_hp          INTEGER,
    abilities_json  TEXT NOT NULL,          -- e.g. { "str":16, "dex":12, ... }
    skills_json     TEXT NOT NULL,          -- e.g. { "perception":5, ... }
    inventory_json  TEXT NOT NULL,          -- e.g. [ { "name":"Sword", "qty":1 } ]
    gold            INTEGER DEFAULT 0,
    conditions_json TEXT,                   -- e.g. [ "blinded", "frightened" ]
    location_room_id INTEGER,               -- current room
    notes           TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (adventure_id) REFERENCES adventure(id),
    FOREIGN KEY (location_room_id) REFERENCES room(id)
);
```

**Usage:**

- `get_character_data` and `update_character_data` work primarily with this table.
- A separate sync layer can mirror this to Google Sheets if desired.

---

## Table: `game_flag`

**Purpose:** Flexible key/value store for world and story state.

```sql
CREATE TABLE game_flag (
    id              INTEGER PRIMARY KEY,
    adventure_id    INTEGER NOT NULL,
    name            TEXT NOT NULL,      -- e.g. 'door_1_unlocked'
    value           TEXT NOT NULL,      -- e.g. 'true', 'false', or JSON
    UNIQUE (adventure_id, name),
    FOREIGN KEY (adventure_id) REFERENCES adventure(id)
);
```

**Examples:**

- `door_1_unlocked = "true"`
- `goblin_chief_attitude = "wary"`
- `spirits_appeased = "true"`

These flags can be included in the `game_state_snapshot` and influence AI decisions.

---

## Table: `story_log`

**Purpose:** Keep a chronological record of what happened, useful for recaps and debugging.

```sql
CREATE TABLE story_log (
    id              INTEGER PRIMARY KEY,
    adventure_id    INTEGER NOT NULL,
    turn_index      INTEGER NOT NULL,    -- sequence number
    timestamp       TEXT DEFAULT (datetime('now')),
    speaker_type    TEXT NOT NULL,      -- 'player' or 'dm'
    speaker_name    TEXT,               -- 'Kraven' or 'DM'
    content         TEXT NOT NULL,      -- text of the utterance or narration
    FOREIGN KEY (adventure_id) REFERENCES adventure(id)
);
```

**Usage:**

- The engine appends entries every time the player acts or the DM narrates.
- A recap function can summarise the last N entries for the LLM.

---

## Table: `rule`

**Purpose:** Store condensed 5e SRD rule fragments, indexed by topic and category, for the `rules_lookup` tool.

```sql
CREATE TABLE rule (
    id              INTEGER PRIMARY KEY,
    topic           TEXT NOT NULL,      -- e.g. 'ability checks', 'grappling'
    category        TEXT NOT NULL,      -- e.g. 'core', 'combat', 'movement'
    summary         TEXT NOT NULL,      -- short paragraph summary
    mechanics_json  TEXT,               -- structured details, e.g. DC ranges
    tags            TEXT,               -- comma-separated tags for search
    created_at      TEXT DEFAULT (datetime('now'))
);
```

**Examples:**

- `topic = 'ability checks'`, `category = 'core'`, tags `'ability,check,d20'`
- `topic = 'attack rolls'`, `category = 'combat'`, tags `'attack,roll,d20'`

The `rules_lookup` tool can search this table by `topic`, `tags`, or both.

---

## Minimal Schema for MVP

For the initial single-adventure MVP you can:

- Implement and populate:
  - `adventure`, `room`, `room_exit`, `monster`, `monster_instance`
- Optionally add a single `character` row for the player.

Later you can layer in:

- `game_flag` (for puzzle state, NPC attitudes, etc.)
- `story_log` (for campaign summaries)
- `rule` (for AI-friendly SRD lookups)
