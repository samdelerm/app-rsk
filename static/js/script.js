function submitForm(event, formId) {
    event.preventDefault();
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    fetch(form.action, {
        method: form.method,
        body: formData
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        if (data.message) {
            alert(data.message);
        }
        window.location.reload();
    }).catch(error => console.error('Error:', error));
}

function deleteTeam(teamName) {
    fetch("/orga/delete_team", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ team_name: teamName })
    }).then(response => response.json())
      .then(data => {
          if (data.message) {
              alert(data.message);
          }
          window.location.reload();
      }).catch(error => console.error('Error:', error));
}

function resetData() {
    fetch('/orga/reset_data', {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.message) {
              alert(data.message);
          }
          window.location.reload();
      }).catch(error => console.error('Error:', error));
}

function startMatch(matchId) {
    fetch('/orga/start_match', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ match_id: matchId })
    }).then(response => response.json())
      .then(data => {
          if (data.message) {
              alert(data.message);
          }
          window.location.reload();
      }).catch(error => console.error('Error:', error));
}

function endMatch(matchId) {
    fetch('/orga/end_match', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ match_id: matchId })
    }).then(response => response.json())
      .then(data => {
          if (data.message) {
              alert(data.message);
          }
          window.location.reload();
      }).catch(error => console.error('Error:', error));
}

function updateMatchTime(matchId, matchTime) {
    fetch('/orga/update_match_time', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ match_id: matchId, match_time: matchTime })
    }).then(response => response.json())
      .then(data => {
          if (data.message) {
              alert(data.message);
          }
      }).catch(error => console.error('Error:', error));
}

function login(event) {
    event.preventDefault();
    const password = document.getElementById('password').value;
    fetch('/orga/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password: password })
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        if (data.success) {
            sessionStorage.setItem('loggedIn', 'true'); // Persist login state for the session
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('main-content').style.display = 'block';
        } else {
            alert('Mot de passe incorrect');
        }
    }).catch(error => console.error('Erreur :', error));
}

function openTablesWindow() {
    const poolsTable = document.getElementById('pools-table').outerHTML;
    const matchesTable = document.getElementById('matches-table').outerHTML;

    const newWindow = window.open('', '_blank', 'width=800,height=600');
    newWindow.document.write(`
        <html>
        <head>
            <title>Tableaux</title>
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
        </head>
        <body>
            <h1>Tableaux</h1>
            <h2>Poules</h2>
            ${poolsTable}
            <h2>Matchs Générés</h2>
            ${matchesTable}
        </body>
        </html>
    `);
    newWindow.document.close();
}

document.addEventListener('DOMContentLoaded', () => {
    // Check sessionStorage for login state
    if (sessionStorage.getItem('loggedIn') === 'true') {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('main-content').style.display = 'block';
    } else {
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('main-content').style.display = 'none';
    }
});