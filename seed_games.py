#!/usr/bin/env python3
"""Seed the games table. Run once after creating the schema."""
from dotenv import load_dotenv
load_dotenv()

from app.supabase_client import supabase

GAMES = [
    ("Mike Tyson's Punch-Out!!",                  'punch-out',        0),
    ("Pokémon Fire Red any%",                      'pokemon-fire-red', 1),
    ("Super Mario 64 16 Stars",                    'sm64-16-stars',    2),
    ("Getting Over It with Bennett Foddy any%",    'getting-over-it',  3),
    ("Celeste any%",                               'celeste',          4),
    ("Minecraft any%",                             'minecraft',        5),
    ("Doom 2016 any%",                             'doom-2016',        6),
    ("Titanfall 2 Practice Course",                'titanfall-2',      7),
    ("Elden Ring Godrick%",                        'elden-ring',       8),
]

for name, slug, order in GAMES:
    res = supabase.table('games').upsert(
        {'name': name, 'slug': slug, 'display_order': order},
        on_conflict='slug'
    ).execute()
    print(f"  {'✓' if res.data else '?'} {name}")

print("Done.")
