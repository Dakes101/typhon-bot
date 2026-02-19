# dice.py — Year Zero Engine dice mechanics for In Search of Typhon
import random

# Panic table from Alien RPG Evolved Edition
PANIC_TABLE = {
    1:  "Keeping it together. No effect.",
    2:  "Trembling. -1 to all rolls until end of next turn.",
    3:  "Dropping things. Drop whatever you're holding.",
    4:  "Freezing. Lose your next slow action.",
    5:  "Seeking cover. Must move to nearest cover immediately.",
    6:  "Screaming. Lose both actions next turn.",
    7:  "Fleeing. Must move away from threat as fast as possible.",
    8:  "Berserk. Attack nearest person (friend or foe) next turn.",
    9:  "Catatonic. Can't act until someone snaps you out of it.",
    10: "Cardiac arrest. Take 1 damage, lose all actions next turn.",
    11: "Permanent PTSD. Gain a permanent mental trauma.",
    12: "Spreading panic. All allies must make a Panic Roll.",
    13: "Heart attack. Broken immediately.",
    14: "Comatose. Unconscious until end of scene.",
    15: "Death wish. Actively try to get yourself killed this scene.",
}

def roll_dice(base_dice: int, stress_dice: int = 0):
    """
    Roll Year Zero Engine dice pool.

    base_dice: number of base D6s (from attribute + skill)
    stress_dice: number of stress D6s (from current Stress score)

    Returns a dict with full breakdown of the roll.
    """

    # Make sure we're not rolling negative dice
    base_dice = max(0, base_dice)
    stress_dice = max(0, stress_dice)

    # Roll the dice
    base_results = [random.randint(1, 6) for _ in range(base_dice)]
    stress_results = [random.randint(1, 6) for _ in range(stress_dice)]

    # Count successes (6s on any dice)
    base_successes = base_results.count(6)
    stress_successes = stress_results.count(6)
    total_successes = base_successes + stress_successes

    # Count banes (1s)
    base_banes = base_results.count(1)
    stress_banes = stress_results.count(1)  # These trigger panic check

    # Can we push? (there are dice showing something other than 1 or 6)
    pushable = any(d not in (1, 6) for d in base_results + stress_results)

    # Does stress trigger a panic check?
    panic_triggered = stress_banes > 0

    return {
        "base_dice": base_dice,
        "stress_dice": stress_dice,
        "base_results": base_results,
        "stress_results": stress_results,
        "base_successes": base_successes,
        "stress_successes": stress_successes,
        "total_successes": total_successes,
        "base_banes": base_banes,
        "stress_banes": stress_banes,
        "panic_triggered": panic_triggered,
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
        "base_results": new_base,
        "stress_results": new_stress,
        "base_successes": base_successes,
        "stress_successes": stress_successes,
        "total_successes": base_successes + stress_successes,
        "base_banes": new_base.count(1),
        "stress_banes": stress_banes,
        "panic_triggered": stress_banes > 0,
        "pushable": False,  # Can only push once
        "was_pushed": True,
    }

def panic_roll(stress: int):
    """
    Roll on the panic table.
    Roll 1D6 and add current Stress, capped at 15.
    """
    roll = random.randint(1, 6)
    result = min(roll + stress, 15)
    return {
        "d6_roll": roll,
        "stress": stress,
        "total": result,
        "effect": PANIC_TABLE[result],
    }

def format_dice_roll(result: dict, skill_name: str = "Roll") -> str:
    """
    Format a roll result as a readable string for Discord.
    """

    # Build visual dice display
    def dice_emoji(value, is_stress=False):
        if value == 6:
            return "✅"  # Success
        elif value == 1:
            return "💀" if is_stress else "⚠️"  # Panic / Bane
        else:
            return f"[{value}]"

    base_display = " ".join(dice_emoji(d) for d in result["base_results"])
    stress_display = " ".join(dice_emoji(d, is_stress=True) for d in result["stress_results"])

    lines = []
    lines.append(f"**{skill_name}**" + (" *(Pushed)*" if result["was_pushed"] else ""))
    lines.append("")

    if result["base_results"]:
        lines.append(f"Base dice:   {base_display}")
    if result["stress_results"]:
        lines.append(f"Stress dice: {stress_display}")

    lines.append("")

    if result["total_successes"] == 0:
        lines.append("**Result: FAILURE** — no successes")
    else:
        lines.append(f"**Result: {result['total_successes']} SUCCESS{'ES' if result['total_successes'] > 1 else ''}**")

    if result["base_banes"] > 0:
        lines.append(f"⚠️ {result['base_banes']} bane(s) on base dice")

    if result["panic_triggered"]:
        lines.append(f"💀 **PANIC TRIGGERED** — roll on the panic table!")
    elif result["pushable"] and not result["was_pushed"]:
        lines.append("*You may Push this roll (costs 1 Stress)*")

    return "\n".join(lines)
