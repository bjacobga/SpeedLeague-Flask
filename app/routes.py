from flask import Blueprint, render_template, request
from app.supabase_client import supabase

main = Blueprint("main", __name__)

POINTS_BY_PLACE = [10, 8, 6, 5, 4, 3, 2, 1]  # Example scoring

def compute_points(runs):
    from collections import defaultdict
    points_per_player = defaultdict(int)
    
    # Group runs by game
    runs_by_game = defaultdict(list)
    for run in runs:
        try:
            time_sec = float(run["Time"])
        except ValueError:
            time_sec = float("inf")
        run["TimeSeconds"] = time_sec
        runs_by_game[run["GameID"]].append(run)
    
    # Assign points per game
    for game_runs in runs_by_game.values():
        game_runs.sort(key=lambda x: x["TimeSeconds"])  # fastest first
        for i, run in enumerate(game_runs):
            if i < len(POINTS_BY_PLACE):
                points_per_player[run["PlayerName"]] += POINTS_BY_PLACE[i]
    
    return points_per_player

@main.route("/")
def index():
    try:
        response = supabase.table("Run")\
            .select('"Submission #", PlayerID, PlayerName, GameID, Time, SubmissionDate, Game(GameName, Category)')\
            .execute()
        response.raise_when_api_error("Failed to fetch runs")

        runs = response.data
        leaderboard_points = compute_points(runs)
        # Sort leaderboard descending
        leaderboard_sorted = sorted(leaderboard_points.items(), key=lambda x: x[1], reverse=True)

        return render_template("index.html", leaderboard=leaderboard_sorted)

    except Exception as e:
        return {"status": "exception", "message": str(e)}, 500


@main.route("/runs")
def runs():
    try:
        from flask import request  # make sure request is imported at the top

        # Get selected player ID from query string
        selected_player_id = request.args.get("player_id", type=int)

        # Fetch all players for the dropdown
        players_response = supabase.table("Player").select("*").execute()
        players_response.raise_when_api_error("Failed to fetch players")
        players_list = players_response.data

        # Default to first player if none selected
        if selected_player_id is None and players_list:
            selected_player_id = players_list[0]["PlayerID"]

        # Fetch all games for rank calculation
        games_response = supabase.table("Game").select("*").execute()
        games_response.raise_when_api_error("Failed to fetch games")
        games_list = games_response.data
        game_ids = [g["GameID"] for g in games_list]

        # Fetch runs for the selected player
        runs_response = (
            supabase
            .table("Run")
            .select("PlayerID, PlayerName, GameID, Game(GameName), Time, SubmissionDate")
            .eq("PlayerID", selected_player_id)
            .execute()
        )
        runs_response.raise_when_api_error(f"Failed to fetch runs for player {selected_player_id}")
        all_runs = runs_response.data

        # Keep only the best run per game
        best_runs = {}
        for run in all_runs:
            game_id = run["GameID"]
            run_time = float(run["Time"])
            if game_id not in best_runs or run_time < float(best_runs[game_id]["Time"]):
                best_runs[game_id] = run

        # For each best run, calculate the rank on that game's leaderboard
        runs_with_rank = []
        for run in best_runs.values():
            game_id = run["GameID"]
            # Fetch all runs for this game to calculate rank
            game_runs_response = (
                supabase
                .table("Run")
                .select("PlayerID, Time")
                .eq("GameID", game_id)
                .execute()
            )
            game_runs_response.raise_when_api_error(f"Failed to fetch runs for game {game_id}")
            game_runs = game_runs_response.data
            # Sort runs by time ascending
            sorted_game_runs = sorted(game_runs, key=lambda r: float(r["Time"]))
            # Determine rank
            for i, r in enumerate(sorted_game_runs, start=1):
                if r["PlayerID"] == selected_player_id:
                    run["Rank"] = i
                    break
            runs_with_rank.append(run)

        # Sort by game name for display
        runs_sorted = sorted(runs_with_rank, key=lambda r: r["Game"]["GameName"])

        return render_template(
            "runs.html",
            players=players_list,
            selected_player_id=selected_player_id,
            runs=runs_sorted
        )

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@main.route("/docs")
def docs():
    return render_template("documentation.html")


@main.route("/games")
def games():
    try:
        from flask import request
        from datetime import date

        selected_game_id = request.args.get("game_id", type=int)

        # Fetch all games for the dropdown
        games_response = supabase.table("Game").select("*").execute()
        games_response.raise_when_api_error("Failed to fetch games")
        games_list = games_response.data

        # Default to first game if none selected
        if selected_game_id is None and games_list:
            selected_game_id = games_list[0]["GameID"]

        # Fetch all runs for this game
        runs_response = (
            supabase
            .table("Run")
            .select("PlayerID, PlayerName, Time, SubmissionDate")
            .eq("GameID", selected_game_id)
            .order("SubmissionDate")  # earliest first
            .execute()
        )
        runs_response.raise_when_api_error(f"Failed to fetch runs for game {selected_game_id}")
        all_runs = runs_response.data

        # Track the historical best times for the graph
        historical_best = []
        best_time_so_far = None
        for run in all_runs:
            run_time = float(run["Time"])
            run_date = run["SubmissionDate"]
            if best_time_so_far is None or run_time < best_time_so_far:
                best_time_so_far = run_time
            historical_best.append({"date": run_date, "best_time": best_time_so_far})

        # Add a point for today
        today_str = date.today().isoformat()
        if not historical_best or historical_best[-1]["date"] != today_str:
            last_best_time = historical_best[-1]["best_time"] if historical_best else None
            historical_best.append({"date": today_str, "best_time": last_best_time})

        # For the leaderboard, only keep best run per player
        best_runs_per_player = {}
        for run in all_runs:
            pid = run["PlayerID"]
            run_time = float(run["Time"])
            if pid not in best_runs_per_player or run_time < float(best_runs_per_player[pid]["Time"]):
                best_runs_per_player[pid] = run
        leaderboard_runs = sorted(best_runs_per_player.values(), key=lambda r: float(r["Time"]))

        return render_template(
            "games.html",
            games=games_list,
            selected_game_id=selected_game_id,
            runs=leaderboard_runs,
            historical_best=historical_best  # for the chart
        )

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500