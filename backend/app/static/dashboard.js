const API_BASE = '/api/v1';
let trendChart = null;

// Update API status
function updateStatus(connected) {
    const statusEl = document.getElementById('api-status');
    statusEl.textContent = connected ? '🟢 Connected' : '🔴 Disconnected';
    document.getElementById('last-update').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
}

// Fetch and display indicators
async function loadIndicators() {
    try {
        const response = await fetch(`${API_BASE}/indicators`);
        const indicators = await response.json();

        const grid = document.getElementById('indicators');
        grid.innerHTML = indicators.map(ind => `
            <div class="indicator-card">
                <div class="indicator-header">
                    <span class="indicator-name">${ind.name}</span>
                    <span class="trend-arrow">➡️</span>
                </div>
                <div class="indicator-value">--</div>
                <div class="confidence">Loading...</div>
            </div>
        `).join('');

        // Load details for each
        for (let ind of indicators) {
            loadIndicatorDetails(ind.indicator_id);
        }

        updateStatus(true);
    } catch (err) {
        console.error('Failed to load indicators:', err);
        updateStatus(false);
    }
}

// Load indicator details
async function loadIndicatorDetails(id) {
    try {
        const response = await fetch(`${API_BASE}/indicators/${id}`);
        if (!response.ok) return;

        const detail = await response.json();
        // Update UI (simplified for brevity)
    } catch (err) {
        console.error(`Failed to load ${id}:`, err);
    }
}

// Load trend chart
async function loadTrendChart() {
    try {
        const response = await fetch(`${API_BASE}/indicators/ECO_CURRENCY_STABILITY/history?days=30`);
        if (!response.ok) return;

        const data = await response.json();
        const ctx = document.getElementById('trendChart').getContext('2d');

        if (trendChart) trendChart.destroy();

        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.time_series.map(d => new Date(d.date).toLocaleDateString()),
                datasets: [{
                    label: 'Currency Stability',
                    data: data.time_series.map(d => d.value),
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    } catch (err) {
        console.error('Failed to load chart:', err);
    }
}

// Load narratives
async function loadNarratives() {
    const narrativesEl = document.getElementById('narratives');
    narrativesEl.innerHTML = '<p>Sample narratives will appear here when available.</p>';
}

// Initialize dashboard
async function init() {
    await loadIndicators();
    await loadTrendChart();
    await loadNarratives();

    // Refresh every 30 seconds
    setInterval(() => {
        loadIndicators();
        loadTrendChart();
    }, 30000);
}

init();
