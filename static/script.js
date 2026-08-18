let activityChart = null;
let breakdownChart = null;

async function fetchData() {
    const loadingMsg = document.getElementById('loading-message');
    const errorMsg = document.getElementById('error-message');
    const statsGrid = document.getElementById('stats-grid');
    const chartsGrid = document.getElementById('charts-grid');
    const tableCard = document.getElementById('table-card');

    loadingMsg.style.display = 'block';
    errorMsg.style.display = 'none';
    statsGrid.style.display = 'none';
    chartsGrid.style.display = 'none';
    tableCard.style.display = 'none';

    try {
        const [issuesResponse, prsResponse] = await Promise.all([
            fetch('/github/issues'),
            fetch('/github/pull-requests'),
        ]);

        if (!issuesResponse.ok) {
            throw new Error(`Issues request returned ${issuesResponse.status}: ${issuesResponse.statusText}`);
        }

        if (!prsResponse.ok) {
            throw new Error(`Pull requests request returned ${prsResponse.status}: ${prsResponse.statusText}`);
        }

        const [issuesData, prsData] = await Promise.all([
            issuesResponse.json(),
            prsResponse.json(),
        ]);

        loadingMsg.style.display = 'none';

        // Update Stats
        document.getElementById('total-issues').textContent = issuesData.total_issues;
        document.getElementById('open-issues').textContent = issuesData.open_issues;
        document.getElementById('total-prs').textContent = prsData.total_pull_requests;
        document.getElementById('activity-count').textContent = (issuesData.total_issues + prsData.total_pull_requests);

        statsGrid.style.display = 'grid';
        chartsGrid.style.display = 'grid';
        tableCard.style.display = 'block';

        // Update Charts
        const combinedItems = [...issuesData.issues, ...prsData.pull_requests]
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        updateActivityChart(combinedItems);
        updateBreakdownChart(issuesData.total_issues, prsData.total_pull_requests);

        // Update Table
        updateTable(combinedItems.slice(0, 10));

    } catch (error) {
        loadingMsg.style.display = 'none';
        errorMsg.style.display = 'block';
        errorMsg.innerHTML = `<div class="error-text">Error: ${error.message}</div>`;
        console.error(error);
    }
}

function buildMonthlyCounts(items, monthsBack = 11) {
    const now = new Date();
    const buckets = [];

    for (let i = monthsBack - 1; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        buckets.push({
            key: `${d.getFullYear()}-${d.getMonth()}`,
            label: d.toLocaleString('en-US', { month: 'short' }),
            count: 0
        });
    }

    const bucketByKey = Object.fromEntries(buckets.map(b => [b.key, b]));

    items.forEach(item => {
        const created = new Date(item.created_at);
        const key = `${created.getFullYear()}-${created.getMonth()}`;

        if (bucketByKey[key]) {
            bucketByKey[key].count += 1;
        }
    });

    return {
        labels: buckets.map(b => b.label),
        counts: buckets.map(b => b.count)
    };
}

function updateActivityChart(issues) {
    const ctx = document.getElementById('activityChart').getContext('2d');

    if (activityChart) activityChart.destroy();

    const { labels, counts } = buildMonthlyCounts(issues);

    activityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Activity',
                data: counts,
                backgroundColor: '#667eea',
                borderRadius: 4,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    border: { display: false },
                    grid: { color: '#ecf0f1' }
                },
                x: {
                    border: { display: false },
                    grid: { display: false }
                }
            }
        }
    });
}

function updateBreakdownChart(issues, prs) {
    const ctx = document.getElementById('breakdownChart').getContext('2d');

    if (breakdownChart) breakdownChart.destroy();

    breakdownChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Issues', 'Pull Requests'],
            datasets: [{
                data: [issues, prs],
                backgroundColor: ['#667eea', '#60a5c9'],
                borderColor: 'white',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { boxWidth: 12, font: { size: 12 } }
                }
            }
        }
    });
}

function updateTable(items) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = items.length ? items.map(item => `
        <tr>
            <td>#${item.number}</td>
            <td>${item.title.substring(0, 50)}...</td>
            <td>${item.author}</td>
            <td>${item.labels.join(', ') || 'none'}</td>
            <td><span class="status-badge status-${item.state}">${item.state}</span></td>
        </tr>
    `).join('') : `
        <tr>
            <td colspan="5">No issues or pull requests found.</td>
        </tr>
    `;
}

void fetchData();
