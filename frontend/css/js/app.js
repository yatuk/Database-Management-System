/**
 * Shared JavaScript utilities for the WDI Database Management System.
 * Include after Chart.js in base.html.
 */

// ---- Detail Row Toggle ----
function toggleDetails(rowId) {
    const row = document.getElementById('detail-' + rowId);
    if (row) {
        row.classList.toggle('show');
    }
}

// ---- Client-side Table Sort ----
function applySort(tableSelector, colIndex, order) {
    const tbody = document.querySelector(tableSelector + ' tbody');
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = order === 'asc';

    rows.sort(function (a, b) {
        let cellA = a.children[colIndex].innerText.trim();
        let cellB = b.children[colIndex].innerText.trim();
        const numA = parseFloat(cellA.replace(/,/g, ''));
        const numB = parseFloat(cellB.replace(/,/g, ''));
        if (!isNaN(numA) && !isNaN(numB)) {
            return isAsc ? numA - numB : numB - numA;
        }
        return isAsc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
    });

    rows.forEach(function (row) { tbody.appendChild(row); });
}

// ---- Quadratic Regression ----
function fitQuadratic(points) {
    var n = points.length;
    if (n < 3) return null;

    var sumX = 0, sumY = 0, sumX2 = 0, sumX3 = 0, sumX4 = 0, sumXY = 0, sumX2Y = 0;
    for (var i = 0; i < n; i++) {
        var x = points[i].x;
        var y = points[i].y;
        sumX += x;
        sumY += y;
        sumX2 += x * x;
        sumX3 += x * x * x;
        sumX4 += x * x * x * x;
        sumXY += x * y;
        sumX2Y += x * x * y;
    }

    var det = n * (sumX2 * sumX4 - sumX3 * sumX3)
            - sumX * (sumX * sumX4 - sumX2 * sumX3)
            + sumX2 * (sumX * sumX3 - sumX2 * sumX2);

    if (Math.abs(det) < 1e-10) return null;

    var a = (n * (sumX2 * sumX2Y - sumX3 * sumXY) - sumX * (sumX * sumX2Y - sumX2 * sumXY) + sumX2 * (sumX * sumXY - sumX2 * sumY)) / det;
    var b = (n * (sumX4 * sumXY - sumX3 * sumX2Y) - sumX * (sumX * sumX2Y - sumX2 * sumXY) + sumX2 * (sumX * sumY - n * sumXY)) / det;
    var c = (sumY - b * sumX - a * sumX2) / n;

    return { a: a, b: b, c: c };
}

// ---- Autocomplete Fetch ----
function autocompleteFetch(url, query, callback) {
    if (!query || query.length < 1) {
        callback([]);
        return;
    }
    fetch(url + '?q=' + encodeURIComponent(query))
        .then(function (r) { return r.json(); })
        .then(callback)
        .catch(function () { callback([]); });
}
