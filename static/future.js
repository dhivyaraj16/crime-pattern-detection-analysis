const box = document.getElementById("futureData");

if (box) {

    const years = JSON.parse(box.dataset.years);
    const values = JSON.parse(box.dataset.values);
    const crimes = JSON.parse(box.dataset.crimes);

    // 🌊 Trend Line Chart
    new Chart(document.getElementById('trendChart'), {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Crime Trend',
                data: values,
                borderColor: '#00ffe5',
                backgroundColor: 'rgba(0,255,229,0.15)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            animation: { duration: 2000 }
        }
    });

    // 🔥 Crime Risk Ranking
    new Chart(document.getElementById('crimeChart'), {
        type: 'bar',
        data: {
            labels: Object.keys(crimes),
            datasets: [{
                label: 'Future Crime Risk',
                data: Object.values(crimes),
                backgroundColor: [
                    '#ff5f7e', '#ffc75f', '#845ec2', '#00c9a7', '#f9f871'
                ]
            }]
        },
        options: {
            animation: { duration: 2000 }
        }
    });
}
