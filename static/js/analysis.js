

// ================= GET DATA =================

const topLabels = JSON.parse(document.getElementById("topLabels").innerText);
const topValues = JSON.parse(document.getElementById("topValues").innerText);

const bottomLabels = JSON.parse(document.getElementById("bottomLabels").innerText);
const bottomValues = JSON.parse(document.getElementById("bottomValues").innerText);

const years = JSON.parse(document.getElementById("years").innerText);
const yearValues = JSON.parse(document.getElementById("yearValues").innerText);


// ================= BAR =================

new Chart(document.getElementById("barChart"), {
    type: "bar",
    data: {
        labels: topLabels,
        datasets: [{
            label: "Crimes",
            data: topValues,
            backgroundColor: "steelblue"
        }]
    }
});


// ================= LINE =================

new Chart(document.getElementById("lineChart"), {
    type: "line",
    data: {
        labels: years,
        datasets: [{
            label: "Total Crimes",
            data: yearValues,
            borderColor: "green",
            fill: false,
            tension: 0.3
        }]
    }
});


// ================= PIE =================

new Chart(document.getElementById("pieChart"), {
    type: "pie",
    data: {
        labels: bottomLabels,
        datasets: [{
            data: bottomValues,
            backgroundColor: [
                "#ff6384",
                "#36a2eb",
                "#ffcd56",
                "#4bc0c0",
                "#9966ff"
            ]
        }]
    }
});
