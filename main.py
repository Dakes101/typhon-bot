# main.py — In Search of Typhon Discord Bot
import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

from database import init_db, create_character, get_character, update_character_field
from character import build_character_embed, CharacterSheetView
from dice import panic_roll

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ── Bot setup ─────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ── Events ────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    await init_db()
    await tree.sync()
    print(f"In Search of Typhon bot online as {bot.user}")
    print(f"Connected to {len(bot.guilds)} server(s)")

# ── Commands ──────────────────────────────────────────────────────────────────

@tree.command(name="create_character", description="Create your Alien RPG character")
@app_commands.describe(
    name="Your character's full name",
    career="Your career (e.g. Colonial Marine, Roughneck, Medic)",
    age="Your character's age",
    strength="Strength attribute (1-5)",
    agility="Agility attribute (1-5)",
    wits="Wits attribute (1-5)",
    empathy="Empathy attribute (1-5)",
    resolve="Resolve attribute (1-5) — used to resist Panic Rolls",
)
async def create_character_cmd(
    interaction: discord.Interaction,
    name: str,
    career: str,
    age: int,
    strength: int,
    agility: int,
    wits: int,
    empathy: int,
    resolve: int = 3,
):
    # Check they don't already have a character
    existing = await get_character(str(interaction.user.id))
    if existing:
        await interaction.response.send_message(
            f"You already have a character: **{existing['name']}**. "
            f"Use `/sheet` to view them.",
            ephemeral=True
        )
        return

    # Validate attributes
    for label, val in [
        ("Strength", strength), ("Agility", agility),
        ("Wits", wits), ("Empathy", empathy), ("Resolve", resolve)
    ]:
        if not 1 <= val <= 5:
            await interaction.response.send_message(
                f"{label} must be between 1 and 5.", ephemeral=True
            )
            return

    if not 10 <= age <= 100:
        await interaction.response.send_message(
            "Age must be between 10 and 100.", ephemeral=True
        )
        return

    await create_character(
        discord_user_id=str(interaction.user.id),
        guild_id=str(interaction.guild_id),
        name=name,
        career=career,
        age=age,
        attributes={
            "strength": strength,
            "agility": agility,
            "wits": wits,
            "empathy": empathy,
            "resolve": resolve,
        },
        skills={}  # Skills added separately via /train
    )

    char = await get_character(str(interaction.user.id))
    embed = build_character_embed(char)
    view = CharacterSheetView(char)

    await interaction.response.send_message(
        f"Welcome to the crew, **{name}**. Try not to die.",
        embed=embed,
        view=view
    )
    msg = await interaction.original_response()
    await update_character_field(str(interaction.user.id), "sheet_message_id", str(msg.id))
    await update_character_field(str(interaction.user.id), "sheet_channel_id", str(msg.channel.id))


@tree.command(name="sheet", description="Display your character sheet")
async def sheet_cmd(interaction: discord.Interaction):
    char = await get_character(str(interaction.user.id))
    if not char:
        await interaction.response.send_message(
            "You don't have a character yet. Use `/create_character` to make one.",
            ephemeral=True
        )
        return

    embed = build_character_embed(char)
    view = CharacterSheetView(char)
    await interaction.response.send_message(embed=embed, view=view)
    msg = await interaction.original_response()
    await update_character_field(str(interaction.user.id), "sheet_message_id", str(msg.id))
    await update_character_field(str(interaction.user.id), "sheet_channel_id", str(msg.channel.id))


@tree.command(name="train", description="Add points to a skill")
@app_commands.describe(
    skill="The skill to train",
    points="Number of points to add (1-3)"
)
@app_commands.choices(skill=[
    app_commands.Choice(name="Heavy Machinery", value="heavy_machinery"),
    app_commands.Choice(name="Stamina", value="stamina"),
    app_commands.Choice(name="Ranged Combat", value="ranged_combat"),
    app_commands.Choice(name="Mobility", value="mobility"),
    app_commands.Choice(name="Piloting", value="piloting"),
    app_commands.Choice(name="Close Combat", value="close_combat"),
    app_commands.Choice(name="Observation", value="observation"),
    app_commands.Choice(name="Survival", value="survival"),
    app_commands.Choice(name="Comtech", value="comtech"),
    app_commands.Choice(name="Manipulation", value="manipulation"),
    app_commands.Choice(name="Medical Aid", value="medical_aid"),
    app_commands.Choice(name="Command", value="command"),
])
async def train_cmd(interaction: discord.Interaction, skill: str, points: int):
    char = await get_character(str(interaction.user.id))
    if not char:
        await interaction.response.send_message(
            "You don't have a character yet.", ephemeral=True
        )
        return

    if not 1 <= points <= 3:
        await interaction.response.send_message(
            "Points must be between 1 and 3.", ephemeral=True
        )
        return

    new_val = min(char[skill] + points, 5)
    await update_character_field(str(interaction.user.id), skill, new_val)

    await interaction.response.send_message(
        f"**{char['name']}** trained **{skill.replace('_', ' ').title()}** "
        f"to level {new_val}.",
        ephemeral=True
    )


@tree.command(name="damage", description="Apply damage to your character")
@app_commands.describe(amount="Amount of damage to take")
async def damage_cmd(interaction: discord.Interaction, amount: int):
    char = await get_character(str(interaction.user.id))
    if not char:
        await interaction.response.send_message(
            "You don't have a character yet.", ephemeral=True
        )
        return

    new_health = max(char["health"] - amount, 0)
    await update_character_field(str(interaction.user.id), "health", new_health)

    status = "still standing" if new_health > 0 else "**BROKEN**"
    await interaction.response.send_message(
        f"**{char['name']}** takes {amount} damage. "
        f"Health: {new_health}/{char['max_health']} — {status}"
    )


@tree.command(name="heal", description="Recover health")
@app_commands.describe(amount="Amount of health to recover")
async def heal_cmd(interaction: discord.Interaction, amount: int):
    char = await get_character(str(interaction.user.id))
    if not char:
        await interaction.response.send_message(
            "You don't have a character yet.", ephemeral=True
        )
        return

    new_health = min(char["health"] + amount, char["max_health"])
    await update_character_field(str(interaction.user.id), "health", new_health)

    await interaction.response.send_message(
        f"**{char['name']}** recovers {amount} health. "
        f"Health: {new_health}/{char['max_health']}"
    )


@tree.command(name="stress", description="Adjust stress level")
@app_commands.describe(
    amount="Stress to add (positive) or remove (negative)",
)
async def stress_cmd(interaction: discord.Interaction, amount: int):
    char = await get_character(str(interaction.user.id))
    if not char:
        await interaction.response.send_message(
            "You don't have a character yet.", ephemeral=True
        )
        return

    new_stress = max(0, min(char["stress"] + amount, 10))
    await update_character_field(str(interaction.user.id), "stress", new_stress)

    direction = "gains" if amount > 0 else "loses"
    await interaction.response.send_message(
        f"**{char['name']}** {direction} {abs(amount)} stress. "
        f"Stress: {new_stress}/10"
    )


@tree.command(name="panicroll", description="Make a Panic Roll (1D6 + Stress - Resolve)")
@app_commands.describe(
    stress="Override your Stress value (optional if you have a character)",
    resolve="Override your Resolve value (optional if you have a character)",
)
async def panicroll_cmd(
    interaction: discord.Interaction,
    stress: int = None,
    resolve: int = None,
):
    # Determine stress and resolve values
    current_stress = stress
    current_resolve = resolve
    character_name = None

    if stress is None or resolve is None:
        # Try to look up character
        char = await get_character(str(interaction.user.id))
        if not char:
            await interaction.response.send_message(
                "You don't have a registered character. Provide your Stress and Resolve:\n"
                "`/panicroll stress:4 resolve:3`",
                ephemeral=True
            )
            return
        if stress is None:
            current_stress = char["stress"]
        if resolve is None:
            current_resolve = char.get("resolve", 3)
        character_name = char["name"]

    # Roll panic
    result = panic_roll(current_stress, current_resolve)

    # Determine embed color based on result severity
    capped_total = result["capped_total"]
    if capped_total >= 11:  # Scream, Flee, Berserk
        embed_color = discord.Color.red()
    elif capped_total >= 7:  # Nervous through Seek Cover
        embed_color = discord.Color.orange()
    else:  # Keep Your Cool
        embed_color = discord.Color.greyple()

    # Build embed
    embed = discord.Embed(
        title="🎲 Panic Roll",
        color=embed_color
    )

    if character_name:
        embed.add_field(name="Character", value=character_name, inline=False)

    embed.add_field(name="Die Roll", value=f"🎲 1D6 = **{result['d6_roll']}**", inline=True)
    embed.add_field(name="Stress", value=f"**+{result['stress_added']}**", inline=True)
    embed.add_field(name="Resolve", value=f"**−{result['resolve']}**", inline=True)

    if result["raw_total"] != result["capped_total"]:
        total_display = f"{result['raw_total']} → capped to {result['capped_total']}"
    else:
        total_display = str(result["capped_total"])
    embed.add_field(name="Total (1D6 + Stress − Resolve)", value=f"**{total_display}**", inline=False)

    embed.add_field(
        name="Result",
        value=f"**Entry {result['capped_total']}:** {result['effect']}",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ── Run ───────────────────────────────────────────────────────────────────────

bot.run(TOKEN)
