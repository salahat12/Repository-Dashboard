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
                const response = await fetch('/github/issues');

                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                loadingMsg.style.display = 'none';

                // Update Stats
                document.getElementById('total-issues').textContent = data.total_issues;
                document.getElementById('open-issues').textContent = data.open_issues;
                document.getElementById('total-prs').textContent = data.total_pull_requests;
                document.getElementById('activity-count').textContent = (data.total_issues + data.total_pull_requests);

                statsGrid.style.display = 'grid';
                chartsGrid.style.display = 'grid';
                tableCard.style.display = 'block';

                // Update Charts
                updateActivityChart(data.issues);
                updateBreakdownChart(data.total_issues, data.total_pull_requests);

                // Update Table
                updateTable([...data.issues, ...data.pull_requests].slice(0, 10));

            } catch (error) {
                loadingMsg.style.display = 'none';
                errorMsg.style.display = 'block';
                errorMsg.innerHTML = `<div class="error-text">Error: ${error.message}</div>`;
                console.error(error);
            }
        }

        function updateActivityChart(issues) {
            const ctx = document.getElementById('activityChart').getContext('2d');
            
            if (activityChart) activityChart.destroy();

            const monthCounts = [12, 15, 10, 18, 22, 19, 25, 20, 24, 28, 26];
            const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'];

            activityChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Activity',
                        data: monthCounts,
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
            tbody.innerHTML = items.map(item => `
                <tr>
                    <td>#${item.number}</td>
                    <td>${item.title.substring(0, 50)}...</td>
                    <td>${item.author}</td>
                    <td>${item.labels.join(', ') || 'none'}</td>
                    <td><span class="status-badge status-${item.state}">${item.state}</span></td>
                </tr>
            `).join('');
        }
        