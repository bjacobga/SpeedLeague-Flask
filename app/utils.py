from collections import defaultdict

POINTS_MAP = [10, 9, 8, 7, 6, 5, 4, 3, 2]  # index 0 = 1st place, 9 places


def parse_time(time_str):
    """Parse H:MM:SS.mmm (or any variation) to total seconds as float."""
    time_str = time_str.strip()
    decimal_part = 0.0
    if '.' in time_str:
        main, dec = time_str.rsplit('.', 1)
        decimal_part = int(dec) / (10 ** len(dec))
    else:
        main = time_str

    parts = main.split(':')
    if len(parts) == 3:
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
    elif len(parts) == 2:
        h, m, s = 0, int(parts[0]), int(parts[1])
    else:
        h, m, s = 0, 0, int(parts[0])

    return h * 3600 + m * 60 + s + decimal_part


def format_time(seconds):
    """Format total seconds to H:MM:SS.mmm"""
    if seconds is None:
        return '-'
    total_ms = round(seconds * 1000)
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h}:{m:02d}:{s:02d}.{ms:03d}"


def compute_overall_standings(all_best_times, player_ids, game_ids):
    """
    all_best_times: dict {(player_id, game_id): time_seconds}
    Returns list of {player_id, points, game_points} sorted by points desc.
    Top 8 of 9 games count per player.
    """
    game_points = defaultdict(dict)

    for game_id in game_ids:
        times = [(pid, t) for (pid, gid), t in all_best_times.items() if gid == game_id]
        times.sort(key=lambda x: x[1])
        for rank, (pid, _) in enumerate(times):
            pts = POINTS_MAP[rank] if rank < len(POINTS_MAP) else 0
            game_points[pid][game_id] = pts

    result = []
    for pid in player_ids:
        player_game_pts = game_points.get(pid, {})
        all_pts = sorted(player_game_pts.values(), reverse=True)
        total = sum(all_pts[:8])
        result.append({
            'player_id': pid,
            'points': total,
            'game_points': player_game_pts,
        })

    result.sort(key=lambda x: x['points'], reverse=True)
    return result
