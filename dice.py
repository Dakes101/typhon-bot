# dice.py — Year Zero Engine dice mechanics for In Search of Typhon
import random

# Stress Response table from Alien RPG Evolved Edition.
# Triggered immediately when any 1 appears on stress dice.
# Roll 1D6 and apply the result — this is NOT a Panic Roll.
# ⚠ Nova: please verify these entries verbatim against the Evolved Edition book.
STRESS_RESPONSE_TABLE = {
    1: "Adrenaline Rush. You may immediately take an extra fast action.",
    2: "Nervous Tremors. -1 to all skill rolls until end of next round.",
    3: "Drop It. Drop whatever you are holding.",
    4: "Freeze. Lose your next fast action.",
    5: "Flee. You must immediately move toward the nearest exit or away from the threat.",
    6: "Panic Attack. You must immediately make a Panic Roll.",
}

def roll_dice(base_dice: int, stress_dice: int = 0, modifier: int = 0):
    """
    Roll Year Zero Engine dice pool.

    base_dice: number of base D6s (from attribute + skill)
    stress_dice: number of stress D6s (from current Stress score)

    Returns a dict with full breakdown of the roll.
    """

    # Make sure we're not rolling negative dice
    base_dice = max(0, base_dice)
    stress_dice = max(0, stress_dice)
    effective_base = max(1, base_dice + modifier) if (base_dice + modifier) > 0 else base_dice

    # Roll the dice
    base_results = [random.randint(1, 6) for _ in range(effective_base)]
    stress_results = [random.randint(1, 6) for _ in range(stress_dice)]

    # Count successes (6s on any dice)
    base_successes = base_results.count(6)
    stress_successes = stress_results.count(6)
    total_successes = base_successes + stress_successes

    # Count banes (1s)
    base_banes = base_results.count(1)
    stress_banes = stress_results.count(1)  # These trigger Stress Response

    # Can we push? (there are dice showing something other than 1 or 6)
    pushable = any(d not in (1, 6) for d in base_results + stress_results)

    # Does stress trigger a Stress Response?
    stress_response_triggered = stress_banes > 0

    return {
        "base_dice": base_dice,
        "stress_dice": stress_dice,
        "modifier": modifier,
        "base_results": base_results,
        "stress_results": stress_results,
        "base_successes": base_successes,
        "stress_successes": stress_successes,
        "total_successes": total_successes,
        "base_banes": base_banes,
        "stress_banes": stress_banes,
        "stress_response_triggered": stress_response_triggered,
        "pushable": pushable,
        "was_pushed": False,
    }

def push_roll(previous_roll: dict):
    """
    Push a previous roll — reroll all dice that aren't 1s or 6s.
    Stress increases by 1 (handled by the character sheet, not here).
    """

    # Keep 1s and 6s, reroll everything else
    new_base = [
        d if d in (1, 6) else random.randint(1, 6)
        for d in previous_roll["base_results"]
    ]
    new_stress = [
        d if d in (1, 6) else random.randint(1, 6)
        for d in previous_roll["stress_results"]
    ]

    base_successes = new_base.count(6)
    stress_successes = new_stress.count(6)
    stress_banes = new_stress.count(1)

    return {
        "base_dice": previous_roll["base_dice"],
        "stress_dice": previous_roll["stress_dice"],
        "modifier": 0,
        "base_results": new_base,
        "stress_results": new_stress,
        "base_successes": base_successes,
        "stress_successes": stress_successes,
        "total_successes": base_successes + stress_successes,
        "base_banes": new_base.count(1),
        "stress_banes": stress_banes,
        "stress_response_triggered": stress_banes > 0,
        "pushable": False,  # Can only push once
        "was_pushed": True,
    }

def stress_response_roll():
    """
    Roll on the Stress Response table (Alien RPG Evolved Edition).
    Triggered when any 1 appears on stress dice.
    Roll 1D6 — no modifier — and apply the result immediately.
    This is NOT a Panic Roll.
    """
    roll = random.randint(1, 6)
    return {
        "d6_roll": roll,
        "effect": STRESS_RESPONSE_TABLE[roll],
    }

# Panic Roll table from Alien RPG Evolved Edition.
# Triggered when Stress Response result 6 (Panic Attack) occurs, or manually via /panicroll.
# Roll 1D6 and add the character's current Stress score.
# ⚠ Nova: verify all 8 entries verbatim against the Evolved Edition book before shipping.
PANIC_ROLL_TABLE = {
    6:  "Keep Your Cool. Nothing happens. This round is no different from any other.",
    7:  "Nervous. −1 to all dice rolls until end of the scene.",
    8:  "Trembling. Drop whatever you are holding.",
    9:  "Paralyzed. Lose all your actions next round.",
    10: "Seek Cover. Move behind the nearest cover; cannot perform any other actions this round.",
    11: "Scream. All friendly PCs and NPCs within Short range must immediately make a Panic Roll.",
    12: "Flee. You must flee by any available means until end of the scene.",
    13: "Berserk. Attack the nearest creature, friend or foe, until end of scene or you are Broken.",
}

def panic_roll(stress: int, resolve: int = 0):
    """
    Roll on the Panic Roll table (Alien RPG Evolved Edition).
    Roll 1D6 + Stress - Resolve, capped at 13, floored at 6 (Keep Your Cool).
    """
    d6_roll = random.randint(1, 6)
    raw_total = d6_roll + stress - resolve
    capped_total = max(min(raw_total, 13), 6)

    return {
        "d6_roll": d6_roll,
        "stress_added": stress,
        "resolve": resolve,
        "raw_total": raw_total,
        "capped_total": capped_total,
        "effect": PANIC_ROLL_TABLE[capped_total],
    }

def format_dice_roll(result: dict, skill_name: str = "Roll") -> str:
    """
    Format a roll result as a readable string for Discord.
    """

    # Build visual dice display
    # Base dice shown as [N], stress dice as (N) — brackets vs parens for instant distinction
    def base_die(value):
        return "✅" if value == 6 else f"[{value}]"

    def stress_die(value):
        if value == 6:
            return "✅"
        elif value == 1:
            return "💀"
        return f"({value})"

    base_display   = " ".join(base_die(d)   for d in result["base_results"])
    stress_display = " ".join(stress_die(d) for d in result["stress_results"])

    modifier = result.get("modifier", 0)
    modifier_tag = ""
    if modifier and not result["was_pushed"]:
        sign = "+" if modifier > 0 else ""
        modifier_tag = f" `{sign}{modifier} modifier`"

    # Result summary — shown first so it's visible without scrolling
    s = result["total_successes"]
    if s == 0:
        result_line = "**FAILURE** — no successes"
    else:
        result_line = f"**{s} SUCCESS{'ES' if s > 1 else ''}** 🎯"

    lines = []
    lines.append(f"**{skill_name}**{modifier_tag}" + (" *(Pushed)*" if result["was_pushed"] else ""))
    lines.append(result_line)
    lines.append("")

    if result["base_results"]:
        lines.append(f"🟨 Base    {base_display}")
    if result["stress_results"]:
        lines.append(f"⬛ Stress  {stress_display}")

    if result["stress_response_triggered"]:
        lines.append("")
        lines.append("💀 **STRESS RESPONSE** — rolling on the Stress Response table!")
    elif result["pushable"] and not result["was_pushed"]:
        lines.append("")
        lines.append("*You may Push this roll (costs 1 Stress)*")

    return "\n".join(lines)
