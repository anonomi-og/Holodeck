PRAGMA foreign_keys = ON;

-- Assumes the following tables already exist:
-- adventure, room, room_exit, monster, monster_instance

-- ============================
-- ADVENTURE: THE WAILING GLACIER
-- ============================

INSERT INTO adventure (id, name, description)
VALUES (
    1,
    'The Wailing Glacier',
    'A survival-horror dungeon within a haunted glacier where ancient frost giant magic has bound tormented spirits into the ice.'
);

-- ============================
-- ROOMS
-- ============================

INSERT INTO room (
    id, adventure_id, room_key, title, short_description, full_description
) VALUES
-- Room 1: Ice Chasm
(
    1,
    1,
    'room_1',
    'Ice Chasm',
    'A narrow, wind-blasted ledge clings to the side of a vast frozen chasm while a sorrowful song drifts down from above.',
    'A cramped tunnel of rough rock and ice opens onto a narrow, wind-blasted ledge halfway up a vast blue-white chasm. The shelf of packed snow and glassy ice is barely a metre or so wide in places, and the abyss below disappears into a dim blue haze. Far beneath, the echo of dripping water and creaking ice rises from the depths. Jagged icicles hang like teeth from the ceiling overhead. A faint, sorrowful melody rides the freezing wind, at first indistinguishable from the howl of the gale until it shapes itself into words promising warmth, rest, and safety if you step just a little closer to the edge.'
),
-- Room 2: Frozen Murals
(
    2,
    1,
    'room_2',
    'Frozen Murals',
    'A cavern of blue ice carved with frost giant murals and a rippling sheet of magical frost sealing the way forward.',
    'The ledge widens into a cavern hollowed from pure blue ice, lit by a ghostly inner glow. The walls are carved with towering frost giants drawing wisps of soul-light from kneeling humanoids and binding them into great blocks of ice. Across the far side of the chamber, an archway leads deeper into the glacier, but a thick sheet of rippling, opalescent frost seals it shut. Faces swim within the ice—distorted, open-mouthed, silently screaming. Giant runes of binding encircle the portal, hinting that the spirits within will react violently to crude force or fire yet may be soothed or carefully released.'
),
-- Room 3: Whispering Hall
(
    3,
    1,
    'room_3',
    'Whispering Hall',
    'A narrow corridor where whispers claw at the mind and hateful spirits try to possess intruders.',
    'Beyond the ward lies a long, narrow hall of cloudy ice shot through with dark, humanoid shapes—bodies frozen mid-struggle inside the walls. The air feels thick and resistant, each breath laboured. At first the sound is a faint susurrus like words heard underwater, but as you advance the voices sharpen into urgent, overlapping whispers: pleading, accusing, mocking. Some speak your names or dredge up half-remembered fears. As you push deeper, the pressure of countless minds claws at your thoughts, threatening to overwhelm your focus before pale lights crack the ice ahead and drift free as will-o’-wisps.'
),
-- Room 4: Iceheart Guardian
(
    4,
    1,
    'room_4',
    'Iceheart Guardian',
    'A vast icy vault where a glowing crystal heart hangs above a frozen ogre-zombie bound in chains of rune-etched ice.',
    'The corridor opens into a vaulted chamber like a frozen cathedral. High above, the ceiling vanishes into shadow while faint blue light pulses from the centre of the room. Suspended within a pillar of translucent ice hangs a massive crystal heart—the Iceheart—throbbing with slow, cold light that sends ripples across the walls. Embedded beneath it is a hulking ogre-sized corpse encased from neck to toe in ice, skin rimed with hoarfrost and eyes closed. Chains of rune-etched ice bind the corpse to the crystal. As you step forward, the Iceheart flares, cracks spiderweb across the ice, and with a thunderous shatter the frozen shell explodes outward. The ogre lumbers free trailing shards of ice and ghostly mist, its eyes glowing with the same eerie blue as the heart above.'
),
-- Room 5: The Iceheart''s Secret
(
    5,
    1,
    'room_5',
    'The Iceheart''s Secret',
    'The shattered or intact Iceheart reveals the trapped souls within and forces a choice between mercy and greed.',
    'With the guardian destroyed, the chamber falls quiet save for the slow, frantic pulsing of the Iceheart. Up close, countless tiny faces are visible within the crystal—villagers, travellers, and long-dead souls packed together, some asleep, others silently screaming. A ring of ancient frost giant runes encircles the Iceheart''s base, interwoven with more recent mortal scratches where others have tried and failed to tamper with the prison. The weeping heard on the wind clearly comes from here. Careful study suggests the bindings can be unpicked to release the spirits in a controlled way, or the crystal can be shattered and claimed, risking a violent but brief eruption of anguished souls and leaving only glittering shards and a single, power-laden fragment behind.'
);

-- Set starting room id
UPDATE adventure
SET starting_room_id = 1
WHERE id = 1;

-- ============================
-- ROOM EXITS (simple linear path)
-- ============================

INSERT INTO room_exit (
    adventure_id, from_room_id, direction, to_room_id, description
) VALUES
-- Room 1 -> Room 2
(1, 1, 'inward', 2, 'A narrow tunnel slopes up from the ledge into the glacier, the wind fading as blue ice closes in.'),
-- Room 2 -> Room 1
(1, 2, 'back', 1, 'The tunnel back towards the chasm ledge, where the wind howls through the crack in the glacier.'),
-- Room 2 -> Room 3
(1, 2, 'deeper', 3, 'Beyond the now-weakened frost ward, a cramped icy passage leads deeper into the heart of the glacier.'),
-- Room 3 -> Room 2
(1, 3, 'back', 2, 'The whispering recedes slightly as you retreat towards the mural chamber.'),
-- Room 3 -> Room 4
(1, 3, 'forward', 4, 'The whispers rise to a crescendo as the hall opens into a vast chamber ahead.'),
-- Room 4 -> Room 3
(1, 4, 'back', 3, 'A shadowed passage leads back into the whispering hall.'),
-- Room 4 -> Room 5
(1, 4, 'up', 5, 'Rough ice steps and a low ramp curve up around the Iceheart to a raised platform overlooking it.'),
-- Room 5 -> Room 4
(1, 5, 'down', 4, 'A short descent leads back down beside the Iceheart and the site of the guardian''s fall.');

-- ============================
-- MONSTERS (TEMPLATES)
-- ============================

INSERT INTO monster (id, name, srd_name, base_hp, base_ac, meta_json) VALUES
-- Frost Harpy (reskinned harpy)
(
    1,
    'Frost Harpy',
    'Harpy',
    38,
    11,
    '{
        "size": "Medium",
        "type": "monstrosity",
        "alignment": "chaotic evil",
        "speed": "20 ft., fly 40 ft.",
        "abilities": { "str": 12, "dex": 13, "con": 12, "int": 7, "wis": 10, "cha": 13 },
        "ac": 11,
        "hp": 38,
        "traits": [
            {
                "name": "Luring Song",
                "desc": "Frost-tinged song that forces nearby creatures to make a Wisdom save (typical DC 11) or be charmed and drawn towards the harpy and the chasm edge."
            }
        ],
        "actions": [
            {
                "name": "Claws",
                "to_hit": 3,
                "damage": "2d4+1 slashing",
                "type": "melee"
            },
            {
                "name": "Club",
                "to_hit": 3,
                "damage": "1d4+1 bludgeoning",
                "type": "melee"
            }
        ],
        "flavour": "A harpy whose feathers are rimed with frost and whose sorrowful song echoes through the chasm."
    }'
),
-- Will-o''-Wisp
(
    2,
    'Will-o''-Wisp',
    'Will-o''-Wisp',
    22,
    19,
    '{
        "size": "Small",
        "type": "undead",
        "alignment": "chaotic evil",
        "speed": "0 ft., fly 50 ft. (hover)",
        "abilities": { "str": 1, "dex": 28, "con": 10, "int": 13, "wis": 14, "cha": 11 },
        "ac": 19,
        "hp": 22,
        "traits": [
            { "name": "Incorporeal", "desc": "Can pass through creatures and objects as difficult terrain." },
            { "name": "Invisibility", "desc": "Can turn invisible until it attacks or uses a feature." },
            { "name": "Flyby", "desc": "Does not provoke opportunity attacks when flying out of an enemy''s reach." }
        ],
        "actions": [
            {
                "name": "Shock",
                "to_hit": 4,
                "damage": "2d8 lightning",
                "type": "melee"
            }
        ],
        "flavour": "Malicious spirits of the glacier bound into spheres of pale, crackling light."
    }'
),
-- Iceheart Guardian (Frozen Ogre Zombie)
(
    3,
    'Iceheart Guardian',
    'Ogre Zombie',
    85,
    8,
    '{
        "size": "Large",
        "type": "undead",
        "alignment": "neutral evil",
        "speed": "30 ft.",
        "abilities": { "str": 19, "dex": 6, "con": 18, "int": 3, "wis": 6, "cha": 5 },
        "ac": 8,
        "hp": 85,
        "traits": [
            {
                "name": "Undead Fortitude",
                "desc": "When reduced to 0 hit points, makes a Constitution save to drop to 1 hp instead, representing the Iceheart''s power clinging to its corpse."
            }
        ],
        "actions": [
            {
                "name": "Icy Slam",
                "to_hit": 6,
                "damage": "2d8+4 cold",
                "type": "melee",
                "extra_effect": "On a hit, the target''s speed is reduced by 10 ft. until the start of the guardian''s next turn as ice creeps up their limbs."
            }
        ],
        "flavour": "A hulking ogre corpse bound directly to the Iceheart, trailing shards of ice and freezing mist."
    }'
);

-- ============================
-- MONSTER INSTANCES
-- ============================

INSERT INTO monster_instance (
    adventure_id, room_id, monster_id, instance_name, current_hp, status, notes
) VALUES
-- Frost Harpy in Room 1
(1, 1, 1, 'Frost Harpy of the Chasm', 38, 'alive', 'Lurks above the ledge, using Luring Song to draw characters to the edge.'),
-- Two Will-o''-Wisps in Room 3
(1, 3, 2, 'Whispering Wisp A', 22, 'alive', 'Emerges from the ice walls in the whispering hall.'),
(1, 3, 2, 'Whispering Wisp B', 22, 'alive', 'Second wisp bound to the hall, enraged if the ward was shattered in the mural chamber.'),
-- Iceheart Guardian in Room 4
(1, 4, 3, 'Iceheart Guardian', 85, 'alive', 'Breaks free of its icy prison when intruders approach the Iceheart.');
