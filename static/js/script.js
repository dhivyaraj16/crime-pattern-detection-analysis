document.addEventListener("DOMContentLoaded", function () {

    // ============================
    // DROPDOWNS
    // ============================

    const stateSelect = document.getElementById("state");
    const districtSelect = document.getElementById("district");
    const crimeSelect = document.getElementById("crime");
    const yearSelect = document.getElementById("year");


    // Load States
    if (stateSelect) {
        fetch("/get_states")
            .then(res => res.json())
            .then(data => {

                stateSelect.innerHTML = "<option value=''>Select State</option>";

                data.forEach(state => {
                    let opt = document.createElement("option");
                    opt.value = state;
                    opt.text = state;
                    stateSelect.appendChild(opt);
                });

            })
            .catch(err => console.log("State Error:", err));
    }


    // Load Districts
    if (stateSelect && districtSelect) {

        stateSelect.addEventListener("change", function () {

            let state = this.value;

            districtSelect.innerHTML = "<option>Select District</option>";

            if (!state) return;

            fetch(`/get_districts/${state}`)
                .then(res => res.json())
                .then(data => {

                    data.forEach(d => {

                        let opt = document.createElement("option");
                        opt.value = d;
                        opt.text = d;
                        districtSelect.appendChild(opt);

                    });

                })
                .catch(err => console.log("District Error:", err));
        });

    }


    // Load Crimes
    if (crimeSelect) {

        fetch("/get_crimes")
            .then(res => res.json())
            .then(data => {

                crimeSelect.innerHTML = "<option>Select Crime Type</option>";

                data.forEach(c => {

                    let opt = document.createElement("option");
                    opt.value = c;
                    opt.text = c;
                    crimeSelect.appendChild(opt);

                });

            })
            .catch(err => console.log("Crime Error:", err));
    }


    // Load Years
    if (yearSelect) {

        yearSelect.innerHTML = "<option>Select Year</option>";

        for (let i = 2001; i <= 2013; i++) {

            let opt = document.createElement("option");
            opt.value = i;
            opt.text = i;

            yearSelect.appendChild(opt);
        }
    }



    // ============================
    // TREND CHART
    // ============================

    const chartDiv = document.getElementById("trend-chart");

    if (chartDiv) {

        const years = JSON.parse(chartDiv.dataset.years || "[]");
        const values = JSON.parse(chartDiv.dataset.values || "[]");
        const district = chartDiv.dataset.district;
        const state = chartDiv.dataset.state;
        const crime = chartDiv.dataset.crime;

        if (years.length === 0 || values.length === 0) {

            chartDiv.innerHTML =
                "<p style='color:white;text-align:center;'>No trend data available</p>";

        } else {

            const data = [{
                x: years,
                y: values,
                type: "scatter",
                mode: "lines+markers",
                line: {
                    shape: "spline",
                    color: "#ff5fa2",
                    width: 4
                },
                marker: {
                    size: 8,
                    color: "#4ddcff"
                }
            }];


            const layout = {

                title: {
                    text: `Crime Trend: ${crime} (${district}, ${state})`,
                    font: { size: 18 }
                },

                xaxis: {
                    title: "Year",
                    tickangle: -45,
                    showgrid: false
                },

                yaxis: {
                    title: "Crime Count",
                    showgrid: true
                },

                plot_bgcolor: "rgba(0,0,0,0)",
                paper_bgcolor: "rgba(0,0,0,0)",

                font: { color: "#fff" },

                margin: { t: 60, l: 50, r: 20, b: 60 }
            };


            Plotly.newPlot("trend-chart", data, layout, { responsive: true });

        }
    }



    // ============================
    // FUTURE SLIDERS
    // ============================

    const yearSlider = document.getElementById("yearSlider");
    const growthSlider = document.getElementById("growthSlider");

    if (yearSlider && growthSlider) {

        yearSlider.addEventListener("input", updatePrediction);
        growthSlider.addEventListener("input", updatePrediction);

    }

});


// ============================
// TOGGLE SECTION
// ============================

function toggleSection(id) {

    const el = document.getElementById(id);

    if (!el) return;

    el.style.display =
        (el.style.display === "none") ? "block" : "none";
}
// Read Flask Data
const jsonData = document.getElementById("crime-data").textContent;
const data = JSON.parse(jsonData);

const trendData = data.trend;
const districtData = data.district;
const crimeData = data.crime;


// Trend Chart
new Chart(document.getElementById('trendChart'), {
    type: 'line',
    data: {
        labels: trendData.years,
        datasets: [{
            label: 'Total Crimes',
            data: trendData.counts,
            fill: true,
            tension: 0.4
        }]
    }
});


// District Chart
new Chart(document.getElementById('districtChart'), {
    type: 'bar',
    data: {
        labels: districtData.names,
        datasets: [{
            label: 'Crimes',
            data: districtData.values
        }]
    }
});


// Crime Chart
new Chart(document.getElementById('crimeChart'), {
    type: 'pie',
    data: {
        labels: crimeData.labels,
        datasets: [{
            data: crimeData.values
        }]
    }
});
