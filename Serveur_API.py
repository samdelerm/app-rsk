from flask import Flask, request, jsonify, render_template_string

# API Serveur : Stocke les infos et gère les requêtes
server = Flask(__name__)
team_info = {
    "blue": {"name": "", "score": 0},
    "green": {"name": "", "score": 0},
    "timer": 0
}

matches = []
teams = []

# HTML template for index.html
index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Match Info</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }
        h1, h2 {
            color: #333;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background: #fff;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        label {
            display: block;
            margin-bottom: 10px;
        }
        input[type="text"], input[type="datetime-local"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background-color: #28a745;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ccc;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Match Info</h1>
    <h2>Matches</h2>
    <ul>
        {% for match in matches %}
            <li style="font-weight: {% if match.status == 'ongoing' %}bold{% endif %};">
                {{ match.blue_team }} vs {{ match.green_team }} - {{ match.blue_score }}:{{ match.green_score }} ({{ match.status }})
                {% if match.status == 'upcoming' %}
                    <form action="/start_match" method="post" style="display:inline;">
                        <input type="hidden" name="match_id" value="{{ match.id }}">
                        <button type="submit">Start Match</button>
                    </form>
                {% elif match.status == 'ongoing' %}
                    <form action="/end_match" method="post" style="display:inline;">
                        <input type="hidden" name="match_id" value="{{ match.id }}">
                        <button type="submit">End Match</button>
                    </form>
                {% endif %}
            </li>
        {% endfor %}
    </ul>
    <h2>Add Team</h2>
    <form action="/add_team" method="post">
        <label for="team_name">Team Name:</label>
        <input type="text" id="team_name" name="team_name">
        <button type="submit">Add Team</button>
    </form>
    <h2>Update Team Name</h2>
    <form action="/set_team_name" method="post">
        <label for="blue_name">Blue Team Name:</label>
        <input type="text" id="blue_name" name="blue_name">
        <label for="green_name">Green Team Name:</label>
        <input type="text" id="green_name" name="green_name">
        <button type="submit">Update</button>
    </form>
    <h2>Team Standings</h2>
    <table>
        <thead>
            <tr>
                <th>Team</th>
                <th>Wins</th>
                <th>Losses</th>
            </tr>
        </thead>
        <tbody>
            {% for team, record in standings.items() %}
                <tr>
                    <td>{{ team }}</td>
                    <td>{{ record.wins }}</td>
                    <td>{{ record.losses }}</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
    <h2>Teams</h2>
    <ul>
        {% for team in teams %}
            <li>{{ team }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

def calculate_standings():
    standings = {}
    for match in matches:
        if match["status"] == "completed":
            blue_team = match["blue_team"]
            green_team = match["green_team"]
            if blue_team not in standings:
                standings[blue_team] = {"wins": 0, "losses": 0}
            if green_team not in standings:
                standings[green_team] = {"wins": 0, "losses": 0}
            if match["blue_score"] > match["green_score"]:
                standings[blue_team]["wins"] += 1
                standings[green_team]["losses"] += 1
            else:
                standings[blue_team]["losses"] += 1
                standings[green_team]["wins"] += 1
    return standings

@server.route("/")
def index():
    standings = calculate_standings()
    return render_template_string(index_html, team_info=team_info, matches=matches, standings=standings, teams=teams)

def distribute_teams_and_create_matches(teams):
    import random
    random.shuffle(teams)
    num_pools = 4  # Example: 4 pools
    pools = [teams[i::num_pools] for i in range(num_pools)]
    match_id = 1
    for pool in pools:
        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                matches.append({
                    "id": match_id,
                    "blue_team": pool[i],
                    "green_team": pool[j],
                    "blue_score": 0,
                    "green_score": 0,
                    "status": "upcoming"
                })
                match_id += 1

@server.route("/distribute_teams", methods=["POST"])
def distribute_teams():
    try:
        distribute_teams_and_create_matches(teams)
        return jsonify({"message": "Teams distributed successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error distributing teams"}), 500

@server.route("/add_team", methods=["POST"])
def add_team():
    try:
        team_name = request.form.get("team_name")
        if team_name:
            teams.append(team_name)

            distribute_teams_and_create_matches(teams)
            return jsonify({"message": "Team added and matches created successfully"}), 200
        else:
            return jsonify({"message": "Invalid team name"}), 400
    except Exception as e:
        return jsonify({"message": "Error adding team"}), 500

@server.route("/update_score", methods=["POST"])
def update_score():
    global matches
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        match = next((m for m in matches if m["id"] == int(match_id)), None)
        if match:
            match["blue_score"] = data.get("blue_score", match["blue_score"])
            match["blue_team"] = data.get("blue_name", match["blue_team"])
            match["green_score"] = data.get("green_score", match["green_score"])
            match["green_team"] = data.get("green_name", match["green_team"])
            match["timer"] = data.get("timer", match.get("timer", 0))
            return jsonify({"message": "Scores, names, and timer updated"}), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error updating scores, names, and timer"}), 500

@server.route("/set_team_name", methods=["POST"])
def set_team_name():
    global team_info
    try:
        data = request.form
        team_info["blue"]["name"] = data.get("blue_name", team_info["blue"]["name"])
        team_info["green"]["name"] = data.get("green_name", team_info["green"]["name"])
        return jsonify({"message": "Team names updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error updating team names"}), 500

@server.route("/get_team_info", methods=["GET"])
def get_team_info():
    match_id = request.args.get("match_id")
    try:
        if match_id == "Select Match":
            return jsonify({"message": "Invalid match ID"}), 400
        match_id = int(match_id)
        match = next((m for m in matches if m["id"] == match_id), None)
        if match:
            return jsonify({
                "blue": {"name": match["blue_team"], "score": match["blue_score"]},
                "green": {"name": match["green_team"], "score": match["green_score"]},
                "timer": match.get("timer", 0)
            }), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error fetching team info"}), 500

@server.route("/get_matches", methods=["GET"])
def get_matches():
    try:
        return jsonify(matches), 200
    except Exception as e:
        return jsonify({"message": "Error fetching matches"}), 500

@server.route("/add_update_match", methods=["POST"])
def add_update_match():
    global matches
    try:
        data = request.form
        match_id = data.get("match_id")
        blue_team = data.get("blue_team")
        green_team = data.get("green_team")
        match_time = data.get("match_time")
        
        if match_id:
            match_id = int(match_id)
            for match in matches:
                if match["id"] == match_id:
                    match["blue_team"] = blue_team
                    match["green_team"] = green_team
                    match["match_time"] = match_time
                    match["status"] = "upcoming"
                    break
            else:
                matches.append({"id": match_id, "blue_team": blue_team, "green_team": green_team, "blue_score": 0, "green_score": 0, "status": "upcoming", "match_time": match_time})
        else:
            new_id = max(match["id"] for match in matches) + 1 if matches else 1
            matches.append({"id": new_id, "blue_team": blue_team, "green_team": green_team, "blue_score": 0, "green_score": 0, "status": "upcoming", "match_time": match_time})
        
        return jsonify({"message": "Match added/updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error adding/updating match"}), 500

@server.route("/start_match", methods=["POST"])
def start_match():
    global matches
    try:
        match_id = int(request.form.get("match_id"))
        for match in matches:
            if match["id"] == match_id:
                match["status"] = "ongoing"
                break
        return jsonify({"message": "Match started successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error starting match"}), 500

@server.route("/end_match", methods=["POST"])
def end_match():
    global matches
    try:
        match_id = int(request.form.get("match_id"))
        for match in matches:
            if match["id"] == match_id:
                match["status"] = "completed"
                match["blue_score"] = team_info["blue"]["score"]
                match["green_score"] = team_info["green"]["score"]
                match["timer"] = team_info["timer"]
                break
        return jsonify({"message": "Match ended successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error ending match"}), 500

if __name__ == "__main__":
    server.run(host="0.0.0.0", debug=True, port=5000)