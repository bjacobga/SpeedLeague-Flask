# SpeedLeague

A speedrunning competition tracker for a 9-game, year-long league. Tracks personal bests, per-game leaderboards, and overall standings.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create a `.env` file in the project root
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key
SECRET_KEY=any-random-string
```

### 3. Set up the database
Paste the contents of `schema.sql` into the Supabase SQL Editor and run it. This creates the tables and seeds the 9 games.

### 4. Run the app
```bash
python run.py
```

Visit http://127.0.0.1:5000

---

## Adding Players

Run this script once per competitor and follow the prompts:
```bash
python create_player.py
```

Players cannot self-register — accounts must be created this way.

---

## Adding Games

Games are seeded automatically by `schema.sql`. If you need to add or change games later, either edit `schema.sql` and re-run the insert, or run:
```bash
python seed_games.py
```

---

## Pages

| Page | URL | Description |
|---|---|---|
| Standings | `/` | Overall leaderboard (top 8 of 9 games count) |
| Games | `/games` | Per-game leaderboards + world record progression chart |
| Players | `/players` | Per-player best times + personal best history charts |
| Submit | `/submit` | Submit a run (login required) |

## Scoring

- Players earn points based on their best time ranking in each game
- 1st = 10 pts, 2nd = 9 pts, … 9th = 2 pts
- Each player's **top 8 of 9 game scores** count toward overall standings
