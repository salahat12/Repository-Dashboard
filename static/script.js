let activityChart = null;
let breakdownChart = null;

function formatDate(value) {
    if (!value) {
        return '-';
    }

    return new Date(value).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
    });
}

function formatDateTime(value) {
    if (!value) {
        return '-';
    }

    return new Date(value).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
    });
}

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

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
        const [repoResponse, prsResponse] = await Promise.all([
            fetch('/github'),
            fetch('/github/pull-requests'),
        ]);

        if (!repoResponse.ok) {
            throw new Error(`Repository request returned ${repoResponse.status}: ${repoResponse.statusText}`);
        }

        if (!prsResponse.ok) {
            throw new Error(`Pull requests request returned ${prsResponse.status}: ${prsResponse.statusText}`);
        }

        const [repoData, pullRequests] = await Promise.all([
            repoResponse.json(),
            prsResponse.json(),
        ]);

        loadingMsg.style.display = 'none';

        document.title = `${repoData.owner}/${repoData.name} - Repository Dashboard`;
        document.getElementById('repo-title').textContent = `${repoData.owner}/${repoData.name}`;
        document.getElementById('repo-description').textContent = repoData.description || 'No description provided.';
        document.getElementById('repo-meta').textContent =
            `Created ${formatDate(repoData.created_at)} • Updated ${formatDate(repoData.updated_at)}`;
        const repoLink = document.getElementById('repo-link');
        repoLink.textContent = 'Open repository.py';
        repoLink.href = repoData.url;

        const openPullRequests = pullRequests.filter(item => item.state === 'open').length;
        const closedPullRequests = pullRequests.filter(item => item.state === 'closed').length;
        const latestUpdate = pullRequests.length
            ? pullRequests.reduce((latest, item) =>
                new Date(item.updated_at) > new Date(latest.updated_at) ? item : latest
            ).updated_at
            : repoData.updated_at;

        document.getElementById('total-prs').textContent = pullRequests.length;
        document.getElementById('open-prs').textContent = openPullRequests;
        document.getElementById('closed-prs').textContent = closedPullRequests;
        document.getElementById('latest-update').textContent = formatDateTime(latestUpdate);

        statsGrid.style.display = 'grid';
        chartsGrid.style.display = 'grid';
        tableCard.style.display = 'block';

        const sortedPullRequests = [...pullRequests]
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        updateActivityChart(sortedPullRequests);
        updateBreakdownChart(openPullRequests, closedPullRequests);

        updateTable(sortedPullRequests.slice(0, 10));

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
                label: 'Pull Requests',
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
            labels: ['Open Pull Requests', 'Closed Pull Requests'],
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
            <td>${escapeHtml(item.title)}</td>
            <td>${escapeHtml(item.author)}</td>
            <td><span class="status-badge status-${item.state}">${item.state}</span></td>
            <td>${formatDate(item.updated_at)}</td>
        </tr>
    `).join('') : `
        <tr>
            <td colspan="5">No pull requests found.</td>
        </tr>
    `;
}

void fetchData();
