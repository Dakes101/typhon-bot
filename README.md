# Typhon Bot

**An Alien RPG Discord bot for character management and Year Zero Engine dice rolling**

Built for the *In Search of Typhon* campaign, designed to replace and extend traditional dice bots with persistent character sheets, integrated rolling, and full Year Zero Engine mechanics.

## Features

- **Character Management** — Persistent character sheets with attributes, skills, health, and stress tracking
- **Year Zero Engine Dice** — Full implementation of base dice, stress dice, successes, banes, and panic mechanics
- **Push Mechanic** — Reroll non-1s and non-6s at the cost of increased stress
- **Interactive Sheets** — Discord embeds with clickable roll buttons for skills and attributes
- **Condition Tracking** — Visual health and stress bars with automatic panic rolls
- **Panic Table** — Full 15-entry panic table from Alien RPG Evolved Edition

## Commands

- `/create_character` — Create your Alien RPG character
- `/sheet` — Display your character sheet with roll buttons
- `/train` — Add skill points
- `/damage` / `/heal` — Adjust health
- `/stress` — Adjust stress level
- `/help` — Show all commands and dice mechanics

## Installation

### Requirements
- Python 3.11+
- Discord.py
- A Discord bot token

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Dakes101/typhon-bot.git
cd typhon-bot
```

2. Install dependencies:
```bash
pip install discord.py python-dotenv aiosqlite
```

3. Create a `.env` file with your bot token:
```
DISCORD_TOKEN=your_token_here
```

4. Run the bot:
```bash
python3 main.py
```

### Docker Deployment

A `Dockerfile` and `docker-compose.yml` are included for containerized deployment.
```bash
docker compose up -d
```

## Game System

Built for **Alien RPG** using the **Year Zero Engine**:
- Roll pools of D6 (attribute + skill + stress)
- Sixes are successes
- Ones on base dice are banes
- Ones on stress dice trigger panic rolls
- Push mechanic allows rerolls at the cost of stress

## Development Status

**Current Version:** v0.1 (Beta)

Active development with beta testing underway. Feedback and contributions welcome.

## Roadmap

- [ ] Dedicated dice channel routing
- [ ] Persistent pinned character sheets
- [ ] GM tools (NPC quick rolls, initiative tracking)
- [ ] Talent system
- [ ] Multi-server support

## License

MIT License — feel free to use, modify, and distribute.

## Author

Built by Marcus for the *In Search of Typhon* campaign.

Part of the Rosebud Technology Group suite of tabletop gaming tools.

---

*"Welcome to the crew. Try not to die."*
