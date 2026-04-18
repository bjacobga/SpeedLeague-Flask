#!/usr/bin/env python3
"""Create a player account. Run this to add each competitor."""
import sys
import getpass
from dotenv import load_dotenv
load_dotenv()

from werkzeug.security import generate_password_hash
from app.supabase_client import supabase

username = input("Username: ").strip()
if not username:
    print("Username cannot be empty.")
    sys.exit(1)

password = getpass.getpass("Password: ")
if len(password) < 4:
    print("Password must be at least 4 characters.")
    sys.exit(1)

res = supabase.table('players').insert({
    'username': username,
    'password_hash': generate_password_hash(password),
}).execute()

if res.data:
    print(f"Player '{username}' created (id={res.data[0]['id']}).")
else:
    print("Failed to create player. Username may already exist.")
    sys.exit(1)
