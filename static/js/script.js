URLBASE = "";

function submitForm(event, formId) {
    event.preventDefault();
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    fetch(form.action.startsWith(URLBASE) ? form.action : URLBASE + form.action, {
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
    fetch(URLBASE+"/delete_team", {
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
    fetch(URLBASE+'/reset_data', {
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
    fetch(URLBASE+'/start_match', {
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
    fetch(URLBASE+'/end_match', {
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
    fetch(URLBASE + '/update_match_time', {
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
          window.location.reload();
      }).catch(error => console.error('Error:', error));
}

function login(event) {
    event.preventDefault();
    const password = document.getElementById('password').value;
    fetch(URLBASE + '/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password: password })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              document.getElementById('login-form').style.display = 'none';
              document.getElementById('main-content').style.display = 'block';
          } else {
              alert('Incorrect password');
          }
      }).catch(error => console.error('Error:', error));
}