CREATE TABLE adventure (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,          -- e.g. 'The Wailing Glacier'
    description     TEXT,                   -- short summary
    starting_room_id INTEGER,               -- first room for this adventure
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (starting_room_id) REFERENCES room(id)
);

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

CREATE TABLE monster (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,          -- display name, e.g. 'Frost Harpy'
    srd_name        TEXT,                   -- base SRD name, e.g. 'Harpy'
    base_hp         INTEGER,                -- default HP
    base_ac         INTEGER,                -- default AC
    meta_json       TEXT NOT NULL,          -- JSON blob containing full stat block
    created_at      TEXT DEFAULT (datetime('now'))
);

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

CREATE TABLE game_flag (
    id              INTEGER PRIMARY KEY,
    adventure_id    INTEGER NOT NULL,
    name            TEXT NOT NULL,      -- e.g. 'door_1_unlocked'
    value           TEXT NOT NULL,      -- e.g. 'true', 'false', or JSON
    UNIQUE (adventure_id, name),
    FOREIGN KEY (adventure_id) REFERENCES adventure(id)
);

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

CREATE TABLE rule (
    id              INTEGER PRIMARY KEY,
    topic           TEXT NOT NULL,      -- e.g. 'ability checks', 'grappling'
    category        TEXT NOT NULL,      -- e.g. 'core', 'combat', 'movement'
    summary         TEXT NOT NULL,      -- short paragraph summary
    mechanics_json  TEXT,               -- structured details, e.g. DC ranges
    tags            TEXT,               -- comma-separated tags for search
    created_at      TEXT DEFAULT (datetime('now'))
);
