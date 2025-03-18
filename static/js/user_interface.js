let currentMatchId = null;

function fetchMatchInfo() {
    const matchSelector = document.getElementById("match-selector");
    const matchId = matchSelector.value;

    if (!matchId) {
        clearMatchInfo();
        currentMatchId = null;
        return;
    }

    currentMatchId = matchId;
    updateMatchInfo();
}

function updateMatchInfo() {
    if (!currentMatchId) return;

    fetch(`/get_team_info?match_id=${currentMatchId}`)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                clearMatchInfo();
                alert(data.message);
            } else {
                document.getElementById("blue-team").textContent = data.blue.name;
                document.getElementById("blue-score").textContent = data.blue.score;
                document.getElementById("green-team").textContent = data.green.name;
                document.getElementById("green-score").textContent = data.green.score;
                document.getElementById("match-timer").textContent = data.timer;
                document.getElementById("match-time").textContent = data.match_time || "N/A";
                document.getElementById("match-status").textContent = data.status || "N/A";
            }
        })
        .catch(error => console.error("Error fetching match info:", error));
}

// Clear match information display
function clearMatchInfo() {
    document.getElementById("blue-team").textContent = "N/A";
    document.getElementById("blue-score").textContent = "N/A";
    document.getElementById("green-team").textContent = "N/A";
    document.getElementById("green-score").textContent = "N/A";
    document.getElementById("match-timer").textContent = "N/A";
    document.getElementById("match-time").textContent = "N/A";
}

function fetchStandings() {
    fetch("/get_standings")
        .then(response => response.json())
        .then(data => {
            const standingsContainer = document.getElementById("standings-info");
            standingsContainer.innerHTML = ""; // Clear previous standings

            if (data.message) {
                standingsContainer.innerHTML = `<p>${data.message}</p>`;
            } else {
                const table = document.createElement("table");
                table.className = "styled-table";
                const thead = document.createElement("thead");
                thead.innerHTML = `
                    <tr>
                        <th>Team</th>
                        <th>Wins</th>
                        <th>Losses</th>
                        <th>Draws</th>
                        <th>Goal Average</th>
                    </tr>
                `;
                table.appendChild(thead);

                const tbody = document.createElement("tbody");
                for (const [team, record] of Object.entries(data)) {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${team}</td>
                        <td>${record.wins}</td>
                        <td>${record.losses}</td>
                        <td>${record.draws}</td>
                        <td>${record.goal_average}</td>
                    `;
                    tbody.appendChild(row);
                }
                table.appendChild(tbody);
                standingsContainer.appendChild(table);
            }
        })
        .catch(error => console.error("Error fetching standings:", error));
}

function refreshStandings() {
    const standingsContainer = document.getElementById("standings-info");
    standingsContainer.innerHTML = "<p>Refreshing standings...</p>";
    fetchStandings();
}

// Automatically update match info every 0.5 seconds
setInterval(() => {
    if (currentMatchId) {
        updateMatchInfo();
    }
}, 500);
