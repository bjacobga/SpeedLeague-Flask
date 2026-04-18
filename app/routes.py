import json
from collections import defaultdict
from datetime import datetime, date, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from .supabase_client import supabase
from .utils import format_time, parse_time, compute_overall_standings, POINTS_MAP

main = Blueprint('main', __name__)


def _get_games():
    return supabase.table('games').select('*').order('display_order').execute().data or []


def _get_players():
    return supabase.table('players').select('id, username').execute().data or []


def _get_all_runs():
    return (
        supabase.table('runs')
        .select('id, player_id, game_id, time_seconds, submitted_at')
        .order('submitted_at')
        .execute()
        .data or []
    )


@main.route('/')
def index():
    games = _get_games()
    players = _get_players()
    runs = _get_all_runs()

    player_map = {p['id']: p['username'] for p in players}
    game_map = {g['id']: g['name'] for g in games}
    game_ids = [g['id'] for g in games]

    best_times = {}
    for run in runs:
        key = (run['player_id'], run['game_id'])
        if key not in best_times or run['time_seconds'] < best_times[key]:
            best_times[key] = run['time_seconds']

    standings = compute_overall_standings(best_times, list(player_map.keys()), game_ids)

    leaderboard = []
    for s in standings:
        pid = s['player_id']
        per_game = [
            {
                'game_name': game_map.get(gid, '?'),
                'points': pts,
                'time': format_time(best_times.get((pid, gid))),
            }
            for gid, pts in sorted(s['game_points'].items(), key=lambda x: game_map.get(x[0], ''))
        ]
        leaderboard.append({
            'username': player_map.get(pid, 'Unknown'),
            'points': s['points'],
            'per_game': per_game,
        })

    return render_template('index.html', leaderboard=leaderboard, games=games)


@main.route('/games')
def games():
    games_list = _get_games()
    players = _get_players()
    runs = _get_all_runs()

    player_map = {p['id']: p['username'] for p in players}

    game_data = {}
    for game in games_list:
        gid = game['id']
        game_runs = [r for r in runs if r['game_id'] == gid]

        best_per_player = {}
        for run in game_runs:
            pid = run['player_id']
            if pid not in best_per_player or run['time_seconds'] < best_per_player[pid]:
                best_per_player[pid] = run['time_seconds']

        leaderboard = sorted(
            [
                {
                    'username': player_map.get(pid, '?'),
                    'time_seconds': t,
                    'time_display': format_time(t),
                }
                for pid, t in best_per_player.items()
            ],
            key=lambda x: x['time_seconds'],
        )
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1
            entry['points'] = POINTS_MAP[i] if i < len(POINTS_MAP) else 0

        history = []
        best_so_far = None
        for run in game_runs:
            t = run['time_seconds']
            if best_so_far is None or t < best_so_far:
                best_so_far = t
                history.append({
                    'date': run['submitted_at'][:10],
                    'time_seconds': best_so_far,
                    'time_display': format_time(best_so_far),
                })

        today = date.today().isoformat()
        if history and history[-1]['date'] != today:
            history.append({
                'date': today,
                'time_seconds': history[-1]['time_seconds'],
                'time_display': history[-1]['time_display'],
            })

        game_data[str(gid)] = {
            'leaderboard': leaderboard,
            'history': history,
        }

    return render_template(
        'games.html',
        games=games_list,
        game_data_json=json.dumps(game_data),
    )


@main.route('/players')
def players():
    games_list = _get_games()
    players_list = _get_players()
    runs = _get_all_runs()

    game_map = {g['id']: g['name'] for g in games_list}

    game_rankings = {}
    for game in games_list:
        gid = game['id']
        best = {}
        for run in runs:
            if run['game_id'] != gid:
                continue
            pid = run['player_id']
            if pid not in best or run['time_seconds'] < best[pid]:
                best[pid] = run['time_seconds']
        sorted_pids = sorted(best, key=lambda p: best[p])
        game_rankings[gid] = {pid: rank + 1 for rank, pid in enumerate(sorted_pids)}

    player_data = {}
    for player in players_list:
        pid = player['id']
        player_runs = [r for r in runs if r['player_id'] == pid]

        best_per_game = {}
        for run in player_runs:
            gid = run['game_id']
            if gid not in best_per_game or run['time_seconds'] < best_per_game[gid]:
                best_per_game[gid] = run['time_seconds']

        best_times = []
        for game in games_list:
            gid = game['id']
            t = best_per_game.get(gid)
            rank = game_rankings.get(gid, {}).get(pid)
            pts = POINTS_MAP[rank - 1] if rank and rank <= len(POINTS_MAP) else 0
            best_times.append({
                'game_id': gid,
                'game_name': game['name'],
                'time_seconds': t,
                'time_display': format_time(t) if t is not None else '-',
                'rank': rank,
                'points': pts,
            })

        history = {}
        for game in games_list:
            gid = game['id']
            game_player_runs = sorted(
                [r for r in player_runs if r['game_id'] == gid],
                key=lambda r: r['submitted_at'],
            )
            pb = None
            game_history = []
            for run in game_player_runs:
                t = run['time_seconds']
                if pb is None or t < pb:
                    pb = t
                    game_history.append({
                        'date': run['submitted_at'][:10],
                        'time_seconds': pb,
                        'time_display': format_time(pb),
                    })
            if game_history:
                today = date.today().isoformat()
                if game_history[-1]['date'] != today:
                    game_history.append({
                        'date': today,
                        'time_seconds': game_history[-1]['time_seconds'],
                        'time_display': game_history[-1]['time_display'],
                    })
            history[str(gid)] = game_history

        player_data[str(pid)] = {
            'best_times': best_times,
            'history': history,
        }

    return render_template(
        'players.html',
        players=players_list,
        games=games_list,
        player_data_json=json.dumps(player_data),
    )


@main.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    games_list = _get_games()
    message = None
    error = None

    if request.method == 'POST':
        game_id = request.form.get('game_id', type=int)
        time_str = request.form.get('time', '').strip()

        try:
            time_seconds = parse_time(time_str)
            if time_seconds <= 0:
                raise ValueError('Time must be positive.')

            supabase.table('runs').insert({
                'player_id': current_user.id,
                'game_id': game_id,
                'time_seconds': time_seconds,
                'submitted_at': datetime.now(timezone.utc).isoformat(),
            }).execute()

            message = f"Run submitted: {format_time(time_seconds)}"
        except ValueError as e:
            error = f"Invalid time: {e}"
        except Exception as e:
            error = f"Submission failed: {e}"

    return render_template('submit.html', games=games_list, message=message, error=error)
