document.addEventListener('DOMContentLoaded', async function () {
    var canvas = document.getElementById('priceChart');
    if (!canvas) return;

    try {
        var response = await fetch('/api/prices');
        var data = await response.json();

        if (data.length === 0) {
            var msg = document.createElement('p');
            msg.className = 'no-data';
            msg.textContent = 'No price data available yet.';
            canvas.parentElement.replaceChild(msg, canvas);
            return;
        }

        var labels = data.map(function (row) { return row.date; });
        var mogasData = data.map(function (row) { return row.mogas; });
        var gasoilData = data.map(function (row) { return row.gasoil; });

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Mogas (Gasoline) Rs/L',
                        data: mogasData,
                        borderColor: '#EC8F8D',
                        backgroundColor: 'rgba(236, 143, 141, 0.12)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 2,
                        pointHoverRadius: 6,
                        borderWidth: 2
                    },
                    {
                        label: 'Gas Oil (Diesel) Rs/L',
                        data: gasoilData,
                        borderColor: '#44A194',
                        backgroundColor: 'rgba(68, 161, 148, 0.12)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 2,
                        pointHoverRadius: 6,
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: { size: 13 }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(30, 30, 30, 0.95)',
                        titleFont: { size: 14 },
                        bodyFont: { size: 13 },
                        padding: 12,
                        callbacks: {
                            title: function (items) {
                                var d = new Date(items[0].parsed.x);
                                return d.toLocaleDateString('en-GB', {
                                    day: 'numeric', month: 'long', year: 'numeric'
                                });
                            },
                            label: function (context) {
                                return context.dataset.label + ': Rs ' + context.parsed.y.toFixed(2);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'year',
                            displayFormats: { year: 'yyyy' }
                        },
                        title: {
                            display: true,
                            text: 'Year',
                            font: { size: 13, weight: 'bold' }
                        },
                        grid: { display: false }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price (Rs / Litre)',
                            font: { size: 13, weight: 'bold' }
                        },
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.06)' }
                    }
                }
            }
        });
    } catch (err) {
        var errorMsg = document.createElement('p');
        errorMsg.className = 'no-data';
        errorMsg.textContent = 'Failed to load price data.';
        canvas.parentElement.replaceChild(errorMsg, canvas);
    }
});
