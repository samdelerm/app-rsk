from flask import Flask, request, jsonify, render_template_string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# API Serveur : Stocke les infos et gère les requêtes
server = Flask(__name__)
team_info = {
    "blue": {"name": "", "score": 0},
    "green": {"name": "", "score": 0},
    "timer": 0
}

matches = [
    {"id": 1, "blue_team": "Team A", "green_team": "Team B", "blue_score": 2, "green_score": 1, "status": "completed"},
    {"id": 2, "blue_team": "Team C", "green_team": "Team D", "blue_score": 0, "green_score": 0, "status": "ongoing"},
    {"id": 3, "blue_team": "Team E", "green_team": "Team F", "blue_score": 0, "green_score": 0, "status": "upcoming"}
]

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
    </style>
    <script>
        setInterval(function() {
            window.location.reload();
        }, 5000);  // Refresh every 5 seconds
    </script>
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
    <h2>Update Team Name</h2>
    <form action="/set_team_name" method="post">
        <label for="blue_name">Blue Team Name:</label>
        <input type="text" id="blue_name" name="blue_name">
        <label for="green_name">Green Team Name:</label>
        <input type="text" id="green_name" name="green_name">
        <button type="submit">Update</button>
    </form>
    <h2>Add/Update Match</h2>
    <form action="/add_update_match" method="post">
        <label for="match_id">Match ID (leave blank to add new match):</label>
        <input type="text" id="match_id" name="match_id">
        <label for="blue_team">Blue Team:</label>
        <input type="text" id="blue_team" name="blue_team">
        <label for="green_team">Green Team:</label>
        <input type="text" id="green_team" name="green_team">
        <label for="match_time">Match Time:</label>
        <input type="datetime-local" id="match_time" name="match_time">
        <button type="submit">Add/Update Match</button>
    </form>
</body>
</html>
"""

@server.route("/")
def index():
    return render_template_string(index_html, team_info=team_info, matches=matches)

@server.route("/update_score", methods=["POST"])
def update_score():
    global team_info, matches
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        match = next((m for m in matches if m["id"] == int(match_id)), None)
        if match:
            match["blue_score"] = data.get("blue_score", match["blue_score"])
            match["blue_team"] = data.get("blue_name", match["blue_team"])
            match["green_score"] = data.get("green_score", match["green_score"])
            match["green_team"] = data.get("green_name", match["green_team"])
            team_info["timer"] = data.get("timer", team_info["timer"])
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
        #logging.info(f"Team names updated: Blue - {team_info['blue']['name']}, Green - {team_info['green']['name']}")
        return jsonify({"message": "Team names updated"}), 200
    except Exception as e:
        logging.error(f"Error updating team names: {e}")
        return jsonify({"message": "Error updating team names"}), 500

@server.route("/get_team_info", methods=["GET"])
def get_team_info():
    match_id = request.args.get("match_id")
    try:
        match_id = int(match_id)
        match = next((m for m in matches if m["id"] == match_id), None)
        if match:
            return jsonify({
                "blue": {"name": match["blue_team"], "score": match["blue_score"]},
                "green": {"name": match["green_team"], "score": match["green_score"]},
                "timer": team_info["timer"]
            }), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching team info: {e}")
        return jsonify({"message": "Error fetching team info"}), 500

@server.route("/get_matches", methods=["GET"])
def get_matches():
    try:
        return jsonify(matches), 200
    except Exception as e:
        logging.error(f"Error fetching matches: {e}")
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
            new_id = max(match["id"] for match in matches) + 1
            matches.append({"id": new_id, "blue_team": blue_team, "green_team": green_team, "blue_score": 0, "green_score": 0, "status": "upcoming", "match_time": match_time})
        
       # logging.info(f"Match added/updated: {blue_team} vs {green_team} at {match_time}")
        return jsonify({"message": "Match added/updated"}), 200
    except Exception as e:
        logging.error(f"Error adding/updating match: {e}")
        return jsonify({"message": "Error adding/updating match"}), 500

@server.route("/start_match", methods=["POST"])
def start_match():
    global matches
    try:
        match_id = int(request.form.get("match_id"))
        for match in matches:
            if match["id"] == match_id:
                match["status"] = "ongoing"
                #logging.info(f"Match started: {match['blue_team']} vs {match['green_team']}")
                break
        return jsonify({"message": "Match started"}), 200
    except Exception as e:
        logging.error(f"Error starting match: {e}")
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
               #logging.info(f"Match ended: {match['blue_team']} vs {match['green_team']} with score {match['blue_score']}:{match['green_score']}")
                break
        return jsonify({"message": "Match ended"}), 200
    except Exception as e:
        logging.error(f"Error ending match: {e}")
        return jsonify({"message": "Error ending match"}), 500

if __name__ == "__main__":
    server.run(debug=True, port=5000)