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

// Automatically update match info every 0.5 seconds
setInterval(() => {
    if (currentMatchId) {
        updateMatchInfo();
    }
}, 500);
