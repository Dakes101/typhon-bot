# character.py — Character sheet display and button interactions
import discord
from discord.ui import View, Button
import json
from database import (
    get_character, update_character_field,
    save_last_roll, get_last_roll
)
from dice import roll_dice, push_roll, panic_roll, format_dice_roll

# ── Helpers ──────────────────────────────────────────────────────────────────

def health_bar(current: int, maximum: int, length: int = 10) -> str:
    """Visual health/stress bar using emoji squares."""
    filled = int((current / maximum) * length) if maximum > 0 else 0
    return "🟩" * filled + "⬛" * (length - filled)

def attribute_dots(value: int, maximum: int = 5) -> str:
    """Visual attribute display using dots."""
    return "●" * value + "○" * (maximum - value)

def stress_label(stress: int) -> str:
    """Return a stress level description."""
    if stress == 0:
        return "Calm"
    elif stress <= 2:
        return "Uneasy"
    elif stress <= 4:
        return "Stressed"
    elif stress <= 6:
        return "Rattled"
    elif stress <= 8:
        return "Panicking"
    else:
        return "Breaking Point"

def health_label(health: int, max_health: int) -> str:
    """Return a health status description."""
    if health == max_health:
        return "Healthy"
    elif health >= max_health * 0.75:
        return "Scratched"
    elif health >= max_health * 0.5:
        return "Hurt"
    elif health >= max_health * 0.25:
        return "Wounded"
    elif health > 0:
        return "Critical"
    else:
        return "💀 Broken"

# ── Skill definitions ─────────────────────────────────────────────────────────

# Maps skill name → (attribute it uses, display label)
SKILLS = {
    "heavy_machinery": ("strength", "Heavy Machinery"),
    "stamina":         ("strength", "Stamina"),
    "close_combat":    ("strength", "Close Combat"),
    "ranged_combat":   ("agility", "Ranged Combat"),
    "mobility":        ("agility", "Mobility"),
    "piloting":        ("agility", "Piloting"),
    "observation":     ("wits",    "Observation"),
    "survival":        ("wits",    "Survival"),
    "comtech":         ("wits",    "Comtech"),
    "manipulation":    ("empathy", "Manipulation"),
    "medical_aid":     ("empathy", "Medical Aid"),
    "command":         ("empathy", "Command"),
}

# ── Embed builder ─────────────────────────────────────────────────────────────

def build_character_embed(char: dict) -> discord.Embed:
    """Build the full character sheet as a Discord embed."""

    # Colour based on stress level
    if char["stress"] >= 8:
        colour = discord.Colour.red()
    elif char["stress"] >= 4:
        colour = discord.Colour.orange()
    elif char["stress"] >= 2:
        colour = discord.Colour.yellow()
    else:
        colour = discord.Colour.green()

    embed = discord.Embed(
        title=f"☠ {char['name']}",
        description=f"*{char['career']}  |  Age {char['age']}*",
        colour=colour
    )

    # ── Attributes ──
    attrs = (
        f"`STR` {attribute_dots(char['strength'])}  `{char['strength']}`\n"
        f"`AGI` {attribute_dots(char['agility'])}  `{char['agility']}`\n"
        f"`WIT` {attribute_dots(char['wits'])}  `{char['wits']}`\n"
        f"`EMP` {attribute_dots(char['empathy'])}  `{char['empathy']}`"
    )
    embed.add_field(name="ATTRIBUTES", value=attrs, inline=True)

    # ── Skills ──
    skill_lines = []
    for skill_key, (attr, label) in SKILLS.items():
        val = char[skill_key]
        if val > 0:
            skill_lines.append(f"`{label:<16}` {val}")

    if not skill_lines:
        skill_lines = ["*No trained skills*"]

    embed.add_field(
        name="TRAINED SKILLS",
        value="\n".join(skill_lines),
        inline=True
    )

    # ── Spacer ──
    embed.add_field(name="\u200b", value="\u200b", inline=False)

    # ── Condition ──
    h_bar = health_bar(char["health"], char["max_health"])
    s_bar = health_bar(char["stress"], 10)

    condition = (
        f"**Health**  {h_bar}  `{char['health']}/{char['max_health']}`\n"
        f"*{health_label(char['health'], char['max_health'])}*\n\n"
        f"**Stress**  {s_bar}  `{char['stress']}/10`\n"
        f"*{stress_label(char['stress'])}*"
    )
    embed.add_field(name="CONDITION", value=condition, inline=False)

    embed.set_footer(text="In Search of Typhon  •  Use the buttons below to roll")
    return embed

# ── Button Views ──────────────────────────────────────────────────────────────

class AttributeRollButton(Button):
    """A button that rolls a raw attribute (no skill bonus)."""

    def __init__(self, attribute: str, label: str, user_id: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            custom_id=f"roll_attr_{attribute}_{user_id}"
        )
        self.attribute = attribute
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "That's not your character sheet!", ephemeral=True
            )
            return

        char = await get_character(self.user_id)
        if not char:
            await interaction.response.send_message(
                "Character not found.", ephemeral=True
            )
            return

        dice_pool = char[self.attribute]
        result = roll_dice(base_dice=dice_pool, stress_dice=char["stress"])
        formatted = format_dice_roll(result, self.label)

        await save_last_roll(self.user_id, result, self.label)

        # If panic triggered, increase stress and do panic roll
        if result["panic_triggered"]:
            new_stress = min(char["stress"] + 1, 10)
            await update_character_field(self.user_id, "stress", new_stress)
            pr = panic_roll(new_stress)
            formatted += (
                f"\n\n**PANIC ROLL:** 1D6({pr['d6_roll']}) + "
                f"Stress({pr['stress']}) = **{pr['total']}**\n"
                f"*{pr['effect']}*"
            )

        await interaction.response.send_message(formatted)


class SkillRollButton(Button):
    """A button that rolls attribute + skill dice."""

    def __init__(self, skill_key: str, user_id: str):
        attribute, label = SKILLS[skill_key]
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=f"roll_skill_{skill_key}_{user_id}"
        )
        self.skill_key = skill_key
        self.attribute = attribute
        self.label_text = label
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "That's not your character sheet!", ephemeral=True
            )
            return

        char = await get_character(self.user_id)
        if not char:
            await interaction.response.send_message(
                "Character not found.", ephemeral=True
            )
            return

        dice_pool = char[self.attribute] + char[self.skill_key]
        result = roll_dice(base_dice=dice_pool, stress_dice=char["stress"])
        formatted = format_dice_roll(result, self.label_text)

        await save_last_roll(self.user_id, result, self.label_text)

        if result["panic_triggered"]:
            new_stress = min(char["stress"] + 1, 10)
            await update_character_field(self.user_id, "stress", new_stress)
            pr = panic_roll(new_stress)
            formatted += (
                f"\n\n**PANIC ROLL:** 1D6({pr['d6_roll']}) + "
                f"Stress({pr['stress']}) = **{pr['total']}**\n"
                f"*{pr['effect']}*"
            )

        await interaction.response.send_message(formatted)


class PushButton(Button):
    """Push the last roll — reroll non-1s and non-6s, gain 1 Stress."""

    def __init__(self, user_id: str):
        super().__init__(
            label="⚡ Push Roll",
            style=discord.ButtonStyle.danger,
            custom_id=f"push_roll_{user_id}"
        )
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message(
                "That's not your character sheet!", ephemeral=True
            )
            return

        last_roll, skill_name = await get_last_roll(self.user_id)
        if not last_roll:
            await interaction.response.send_message(
                "No roll to push!", ephemeral=True
            )
            return

        if not last_roll.get("pushable"):
            await interaction.response.send_message(
                "That roll can't be pushed — nothing to reroll.", ephemeral=True
            )
            return

        char = await get_character(self.user_id)

        # Increase stress by 1
        new_stress = min(char["stress"] + 1, 10)
        await update_character_field(self.user_id, "stress", new_stress)

        pushed = push_roll(last_roll)
        formatted = format_dice_roll(pushed, skill_name)
        formatted += f"\n*Stress increased to {new_stress}*"

        await save_last_roll(self.user_id, pushed, skill_name)

        if pushed["panic_triggered"]:
            pr = panic_roll(new_stress)
            formatted += (
                f"\n\n**PANIC ROLL:** 1D6({pr['d6_roll']}) + "
                f"Stress({pr['stress']}) = **{pr['total']}**\n"
                f"*{pr['effect']}*"
            )

        await interaction.response.send_message(formatted)


class CharacterSheetView(View):
    """
    The full set of buttons for a character sheet.
    Builds skill buttons only for skills the character has trained.
    """

    def __init__(self, char: dict):
        super().__init__(timeout=None)  # Persistent — survives bot restarts
        user_id = char["discord_user_id"]

        # Attribute buttons (row 0)
        for attr, label in [
            ("strength", "STR"), ("agility", "AGI"),
            ("wits", "WIT"), ("empathy", "EMP")
        ]:
            btn = AttributeRollButton(attr, label, user_id)
            btn.row = 0
            self.add_item(btn)

        # Skill buttons — only trained skills (rows 1-3)
        row = 1
        col = 0
        for skill_key, (attr, label) in SKILLS.items():
            if char[skill_key] > 0:
                btn = SkillRollButton(skill_key, user_id)
                btn.row = row
                self.add_item(btn)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
                    if row > 3:
                        break  # Discord max 5 rows, keep row 4 for push

        # Push button always on row 4
        push_btn = PushButton(user_id)
        push_btn.row = 4
        self.add_item(push_btn)
