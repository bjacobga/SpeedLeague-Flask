/* ─── Theme Toggle ──────────────────────────────────────────────────────── */
(function () {
    const root = document.documentElement;
    const btn  = document.getElementById('theme-toggle');
    const saved = localStorage.getItem('theme');

    if (saved === 'light') {
        root.setAttribute('data-theme', 'light');
        if (btn) btn.textContent = '🌙';
    }

    if (btn) {
        btn.addEventListener('click', () => {
            const current = root.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            btn.textContent = next === 'dark' ? '☀' : '🌙';
            localStorage.setItem('theme', next);
            // Re-render charts with updated colors
            if (typeof reRenderCharts === 'function') reRenderCharts();
        });
    }
})();

/* ─── Chart Helpers ─────────────────────────────────────────────────────── */
function isDark() {
    return document.documentElement.getAttribute('data-theme') !== 'light';
}

function chartColors() {
    return {
        grid:  isDark() ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)',
        tick:  isDark() ? '#888' : '#666',
        text:  isDark() ? '#ccc' : '#333',
    };
}

function formatTime(seconds) {
    if (seconds === null || seconds === undefined) return '-';
    const totalMs = Math.round(seconds * 1000);
    const ms  = totalMs % 1000;
    const totalS = Math.floor(totalMs / 1000);
    const s  = totalS % 60;
    const totalM = Math.floor(totalS / 60);
    const m  = totalM % 60;
    const h  = Math.floor(totalM / 60);
    return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(ms).padStart(3,'0')}`;
}

function makeStepChart(ctx, history, label) {
    const c = chartColors();
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.map(h => h.date),
            datasets: [{
                label: label || 'Best Time',
                data: history.map(h => h.time_seconds),
                stepped: 'before',
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34,197,94,0.08)',
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: '#22c55e',
                fill: true,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 200 },
            scales: {
                x: {
                    ticks: { color: c.tick, maxTicksLimit: 6, maxRotation: 0 },
                    grid:  { color: c.grid },
                },
                y: {
                    ticks: {
                        color: c.tick,
                        callback: (v) => formatTime(v),
                        maxTicksLimit: 5,
                    },
                    grid: { color: c.grid },
                },
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => formatTime(ctx.parsed.y),
                    },
                },
            },
        },
    });
}

/* ─── Games Page ────────────────────────────────────────────────────────── */
if (typeof gameData !== 'undefined') {
    let currentChart = null;

    function rankClass(rank) {
        if (rank === 1) return 'rank-gold';
        if (rank === 2) return 'rank-silver';
        if (rank === 3) return 'rank-bronze';
        return '';
    }

    function renderGame(gameId) {
        const id  = String(gameId);
        const data = gameData[id];
        const game = games.find(g => String(g.id) === id);

        document.getElementById('game-title').textContent = game ? game.name : '';

        // Leaderboard
        const tbody = document.getElementById('game-leaderboard-body');
        if (!data || data.leaderboard.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="loading-cell">No runs yet for this game.</td></tr>';
        } else {
            tbody.innerHTML = data.leaderboard.map(row => `
                <tr class="${rankClass(row.rank)}">
                    <td class="rank-cell">${row.rank}</td>
                    <td class="player-cell">${row.username}</td>
                    <td style="font-family:monospace">${row.time_display}</td>
                    <td class="points-cell">${row.points}</td>
                </tr>
            `).join('');
        }

        // Chart
        if (currentChart) { currentChart.destroy(); currentChart = null; }
        const canvas = document.getElementById('game-chart');
        if (data && data.history.length > 0) {
            currentChart = makeStepChart(canvas.getContext('2d'), data.history, 'World Record');
        } else {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    // Tab click
    document.getElementById('game-tabs').addEventListener('click', (e) => {
        const btn = e.target.closest('.tab');
        if (!btn) return;
        document.querySelectorAll('#game-tabs .tab').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        renderGame(btn.dataset.gameId);
    });

    // Initial render
    if (games.length > 0) renderGame(games[0].id);

    window.reRenderCharts = function () {
        const active = document.querySelector('#game-tabs .tab.active');
        if (active) renderGame(active.dataset.gameId);
    };
}

/* ─── Players Page ──────────────────────────────────────────────────────── */
if (typeof playerData !== 'undefined') {
    let miniCharts = [];

    function rankClass(rank) {
        if (rank === 1) return 'rank-gold';
        if (rank === 2) return 'rank-silver';
        if (rank === 3) return 'rank-bronze';
        return '';
    }

    function renderPlayer(playerId) {
        const id   = String(playerId);
        const data = playerData[id];
        const player = players.find(p => String(p.id) === id);

        document.getElementById('player-title').textContent = player ? player.username : '';

        // Best times table
        const tbody = document.getElementById('player-best-times-body');
        if (!data || data.best_times.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="loading-cell">No runs yet.</td></tr>';
        } else {
            tbody.innerHTML = data.best_times.map(row => `
                <tr class="${rankClass(row.rank)}">
                    <td class="player-cell">${row.game_name}</td>
                    <td style="font-family:monospace">${row.time_display}</td>
                    <td class="rank-cell">${row.rank !== null ? '#' + row.rank : '—'}</td>
                    <td class="points-cell">${row.points}</td>
                </tr>
            `).join('');
        }

        // Destroy old mini charts
        miniCharts.forEach(c => c.destroy());
        miniCharts = [];

        // Build 3×3 charts grid
        const grid = document.getElementById('charts-grid');
        grid.innerHTML = '';

        games.forEach(game => {
            const history = (data && data.history[String(game.id)]) || [];
            const card = document.createElement('div');
            card.className = 'chart-card';

            if (history.length === 0) {
                card.innerHTML = `
                    <div class="chart-card-title">${game.name}</div>
                    <div class="chart-canvas-wrapper">
                        <p class="no-data">No runs yet</p>
                    </div>`;
            } else {
                card.innerHTML = `
                    <div class="chart-card-title">${game.name}</div>
                    <div class="chart-canvas-wrapper"><canvas></canvas></div>`;
            }

            grid.appendChild(card);

            if (history.length > 0) {
                const canvas = card.querySelector('canvas');
                const chart = makeStepChart(canvas.getContext('2d'), history, game.name);
                miniCharts.push(chart);
            }
        });
    }

    // Player tab click
    document.getElementById('player-tabs').addEventListener('click', (e) => {
        const btn = e.target.closest('.player-tab');
        if (!btn) return;
        document.querySelectorAll('#player-tabs .player-tab').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        renderPlayer(btn.dataset.playerId);
    });

    // Initial render
    if (players.length > 0) renderPlayer(players[0].id);

    window.reRenderCharts = function () {
        const active = document.querySelector('#player-tabs .player-tab.active');
        if (active) renderPlayer(active.dataset.playerId);
    };
}
