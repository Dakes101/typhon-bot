# database.py — Character storage for In Search of Typhon
import aiosqlite
import json
import os

DB_PATH = "data/typhon.db"

async def init_db():
    """
    Create the database and tables if they don't exist.
    Called once when the bot starts up.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_user_id TEXT NOT NULL UNIQUE,
                discord_guild_id TEXT NOT NULL,
                name TEXT NOT NULL,
                career TEXT NOT NULL,
                age INTEGER DEFAULT 30,

                -- Attributes (1-5)
                strength INTEGER DEFAULT 2,
                agility INTEGER DEFAULT 2,
                wits INTEGER DEFAULT 2,
                empathy INTEGER DEFAULT 2,

                -- Skills (0-5, added to attribute for dice pool)
                heavy_machinery INTEGER DEFAULT 0,
                stamina INTEGER DEFAULT 0,
                ranged_combat INTEGER DEFAULT 0,
                mobility INTEGER DEFAULT 0,
                piloting INTEGER DEFAULT 0,
                close_combat INTEGER DEFAULT 0,
                observation INTEGER DEFAULT 0,
                survival INTEGER DEFAULT 0,
                comtech INTEGER DEFAULT 0,
                manipulation INTEGER DEFAULT 0,
                medical_aid INTEGER DEFAULT 0,
                command INTEGER DEFAULT 0,

                -- Condition
                health INTEGER DEFAULT 3,
                max_health INTEGER DEFAULT 3,
                stress INTEGER DEFAULT 0,

                -- Sheet message (so we can update it in Discord)
                sheet_message_id TEXT DEFAULT NULL,
                sheet_channel_id TEXT DEFAULT NULL,

                -- Last roll stored for push mechanic
                last_roll TEXT DEFAULT NULL,
                last_roll_skill TEXT DEFAULT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    print(f"Database initialised at {DB_PATH}")


async def create_character(discord_user_id: str, guild_id: str, name: str, 
                           career: str, age: int, attributes: dict, skills: dict):
    """
    Create a new character. Raises an error if the user already has one.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO characters (
                discord_user_id, discord_guild_id, name, career, age,
                strength, agility, wits, empathy,
                heavy_machinery, stamina, ranged_combat, mobility, piloting,
                close_combat, observation, survival, comtech, 
                manipulation, medical_aid, command,
                max_health, health
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?
            )
        """, (
            discord_user_id, guild_id, name, career, age,
            attributes.get("strength", 2),
            attributes.get("agility", 2),
            attributes.get("wits", 2),
            attributes.get("empathy", 2),
            skills.get("heavy_machinery", 0),
            skills.get("stamina", 0),
            skills.get("ranged_combat", 0),
            skills.get("mobility", 0),
            skills.get("piloting", 0),
            skills.get("close_combat", 0),
            skills.get("observation", 0),
            skills.get("survival", 0),
            skills.get("comtech", 0),
            skills.get("manipulation", 0),
            skills.get("medical_aid", 0),
            skills.get("command", 0),
            attributes.get("strength", 2),  # max_health = Strength
            attributes.get("strength", 2),  # health starts at max
        ))
        await db.commit()


async def get_character(discord_user_id: str):
    """
    Fetch a character by Discord user ID.
    Returns a dict or None if not found.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM characters WHERE discord_user_id = ?",
            (discord_user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return dict(row)


async def update_character_field(discord_user_id: str, field: str, value):
    """
    Update a single field on a character.
    Used for health/stress changes mid-session.
    """
    # Whitelist of fields that can be updated this way (security measure)
    allowed_fields = {
        "health", "stress", "strength", "agility", "wits", "empathy",
        "heavy_machinery", "stamina", "ranged_combat", "mobility", "piloting",
        "close_combat", "observation", "survival", "comtech",
        "manipulation", "medical_aid", "command",
        "sheet_message_id", "sheet_channel_id",
        "last_roll", "last_roll_skill",
    }

    if field not in allowed_fields:
        raise ValueError(f"Field '{field}' cannot be updated directly")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE characters SET {field} = ?, updated_at = CURRENT_TIMESTAMP "
            f"WHERE discord_user_id = ?",
            (value, discord_user_id)
        )
        await db.commit()


async def save_last_roll(discord_user_id: str, roll_result: dict, skill_name: str):
    """
    Save the last roll so the player can push it.
    Stored as JSON string in the database.
    """
    await update_character_field(
        discord_user_id, "last_roll", json.dumps(roll_result)
    )
    await update_character_field(
        discord_user_id, "last_roll_skill", skill_name
    )


async def get_last_roll(discord_user_id: str):
    """
    Retrieve the last roll for push mechanic.
    Returns (roll_dict, skill_name) or (None, None).
    """
    char = await get_character(discord_user_id)
    if not char or not char["last_roll"]:
        return None, None
    return json.loads(char["last_roll"]), char["last_roll_skill"]


async def delete_character(discord_user_id: str):
    """
    Delete a character entirely. Irreversible.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM characters WHERE discord_user_id = ?",
            (discord_user_id,)
        )
        await db.commit()
