from flask import Blueprint, render_template
from app.supabase_client import supabase

main = Blueprint("main", __name__)

@main.route("/")
def leaderboard():
    response = (
        supabase
        .table("speedruns")
        .select("*")
        .eq("status", "approved")
        .order("time_seconds")
        .execute()
    )

    return render_template("index.html", runs=response.data)
