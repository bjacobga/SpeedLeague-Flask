-- SpeedLeague Database Schema
-- Paste this into the Supabase SQL editor and run it.
-- Use your service_role key in SUPABASE_KEY so RLS is bypassed,
-- or disable RLS on each table in the Supabase dashboard.

-- ── Tables ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS players (
    id            SERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS games (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    slug          TEXT UNIQUE NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS runs (
    id           SERIAL PRIMARY KEY,
    player_id    INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    game_id      INTEGER NOT NULL REFERENCES games(id)   ON DELETE CASCADE,
    time_seconds FLOAT   NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Seed Games ────────────────────────────────────────────────────────────
-- Run seed_games.py instead, or paste this manually:

INSERT INTO games (name, slug, display_order) VALUES
    ('Mike Tyson''s Punch-Out!!',                  'punch-out',       0),
    ('Pokémon Fire Red any%',                       'pokemon-fire-red',1),
    ('Super Mario 64 16 Stars',                     'sm64-16-stars',   2),
    ('Getting Over It with Bennett Foddy any%',     'getting-over-it', 3),
    ('Celeste any%',                                'celeste',         4),
    ('Minecraft any%',                              'minecraft',       5),
    ('Doom 2016 any%',                              'doom-2016',       6),
    ('Titanfall 2 Practice Course',                 'titanfall-2',     7),
    ('Elden Ring Godrick%',                         'elden-ring',      8)
ON CONFLICT (slug) DO NOTHING;
