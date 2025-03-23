import json
import os
from flask import Flask, request, jsonify, render_template

# API Serveur : Stocke les infos et gère les requêtes
server = Flask(__name__)
team_info = {
    "blue": {"name": "", "score": 0},
    "green": {"name": "", "score": 0},
    "timer": 0
}

matches = []
teams = []
pools = [[], [], [], []]

# Password is defined by an environment variable, defaults to "default_password"
PASSWORD = os.getenv("MATCH_INFOS", "default_password")
print("Password:", PASSWORD)

def load_data():
    global matches, teams, pools
    try:
        with open('matches.json', 'r') as f:
            matches = json.load(f)
            # Ensure matches are dictionaries
            if not all(isinstance(match, dict) for match in matches):
                raise ValueError("Invalid data format in matches.json")
    except (FileNotFoundError, ValueError):
        matches = []
    try:
        with open('teams.json', 'r') as f:
            teams = json.load(f)
    except FileNotFoundError:
        teams = []
    try:
        with open('pools.json', 'r') as f:
            pools = json.load(f)
    except FileNotFoundError:
        pools = [[], [], [], []]

def save_data():
    with open('matches.json', 'w') as f:
        json.dump(matches, f)
    with open('teams.json', 'w') as f:
        json.dump(teams, f)
    with open('pools.json', 'w') as f:
        json.dump(pools, f)

def reset_data():
    global matches, teams, pools
    matches = []
    teams = []
    pools = [[], [], [], []]
    save_data()

load_data()

def calculate_standings():
    standings = {}
    for match in matches:
        if not isinstance(match, dict):
            continue  # Skip invalid entries
        if match.get("status") == "completed":
            blue_team = match.get("blue_team")
            green_team = match.get("green_team")
            if blue_team not in standings:
                standings[blue_team] = {"wins": 0, "losses": 0, "draws": 0, "goal_average": 0}
            if green_team not in standings:
                standings[green_team] = {"wins": 0, "losses": 0, "draws": 0, "goal_average": 0}
            if match.get("blue_score", 0) > match.get("green_score", 0):
                standings[blue_team]["wins"] += 1
                standings[green_team]["losses"] += 1
            elif match.get("blue_score", 0) < match.get("green_score", 0):
                standings[blue_team]["losses"] += 1
                standings[green_team]["wins"] += 1
            else:
                standings[blue_team]["draws"] += 1
                standings[green_team]["draws"] += 1
            standings[blue_team]["goal_average"] += match.get("blue_score", 0) - match.get("green_score", 0)
            standings[green_team]["goal_average"] += match.get("green_score", 0) - match.get("blue_score", 0)
    return standings

@server.route("/orga/interface")
def organizer_interface():
    standings = calculate_standings()
    return render_template("index.html", team_info=team_info, matches=matches, standings=standings, teams=teams, pools=pools, len=len, max=max)

def distribute_teams_into_pools(teams):
    import random
    random.shuffle(teams)
    num_pools = min(4, max(2, len(teams) // 3))  # Create up to 4 pools of 3 teams each, at least 1 pool
    for i in range(num_pools):
        pools[i] = teams[i::num_pools]

@server.route("/orga/generate_pools", methods=["POST"])
def generate_pools():
    try:
        if len(teams) < 2:
            return jsonify({"message": "At least 2 teams are required to generate pools"}), 400
        for pool in pools:
            pool.clear()  # Clear existing pools before creating new ones
        distribute_teams_into_pools(teams)
        save_data()
        return jsonify({"message": "Pools generated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error generating pools"}), 500

def generate_matches_for_pools(match_time):
    match_id = 1
    for pool_index, pool in enumerate(pools):
        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                matches.append({
                    "id": match_id,
                    "poule": pool_index + 1,
                    "blue_team": pool[i],
                    "green_team": pool[j],
                    "blue_score": 0,
                    "green_score": 0,
                    "status": "upcoming",
                    "match_time": match_time
                })
                match_id += 1

@server.route("/orga/generate_matches", methods=["POST"])
def generate_matches():
    try:
        matches.clear()  # Clear existing matches before creating new ones
        match_time = request.form.get("match_time")
        generate_matches_for_pools(match_time)
        save_data()
        return jsonify({"message": "Matches generated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error generating matches"}), 500

@server.route("/orga/add_team", methods=["POST"])
def add_team():
    try:
        team_name = request.form.get("team_name")
        if team_name:
            teams.append(team_name)
            save_data()
            return jsonify({"message": "Team added successfully"}), 200
        else:
            return jsonify({"message": "Invalid team name"}), 400
    except Exception as e:
        return jsonify({"message": "Error adding team"}), 500

@server.route("/orga/delete_team", methods=["POST"])
def delete_team():
    try:
        data = request.get_json()
        team_name = data.get("team_name")
        if (team_name in teams) and (team_name not in [match["blue_team"] for match in matches]) and (team_name not in [match["green_team"] for match in matches]):
            teams.remove(team_name)
            save_data()
            return jsonify({"message": "Team deleted successfully"}), 200
        else:
            return jsonify({"message": "Team not found or is part of a match"}), 404
    except Exception as e:
        return jsonify({"message": "Error deleting team"}), 500

@server.route("/orga/reset_data", methods=["POST"])
def reset_data_route():
    try:
        reset_data()
        return jsonify({"message": "Data reset successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error resetting data"}), 500

@server.route("/orga/update_score", methods=["POST"])
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
            save_data()
            return jsonify({"message": "Scores, names, and timer updated"}), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error updating scores, names, and timer"}), 500

@server.route("/get_team_info", methods=["GET"])
def get_team_info():
    match_id = request.args.get("match_id")
    try:
        if not match_id or match_id == "Select Match":
            return jsonify({"message": "Invalid match ID"}), 400
        match_id = int(match_id)
        match = next((m for m in matches if m["id"] == match_id), None)
        if match:
            return jsonify({
                "blue": {"name": match["blue_team"], "score": match["blue_score"]},
                "green": {"name": match["green_team"], "score": match["green_score"]},
                "timer": match.get("timer", 0),
                "match_time": match.get("match_time", "N/A"),
                "status": match.get("status", "N/A")
            }), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error fetching match info"}), 500

@server.route("/orga/get_matches", methods=["GET"])
def get_matches():
    try:
        return jsonify(matches), 200
    except Exception as e:
        return jsonify({"message": "Error fetching matches"}), 500

@server.route("/orga/add_update_match", methods=["POST"])
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
        
        save_data()
        return jsonify({"message": "Match added/updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error adding/updating match"}), 500

@server.route("/orga/start_match", methods=["POST"])
def start_match():
    global matches
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        match = next((m for m in matches if m["id"] == int(match_id)), None)
        if match:
            match["status"] = "ongoing"
            save_data()
            return jsonify({"message": "Match started successfully"}), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error starting match"}), 500

@server.route("/orga/end_match", methods=["POST"])
def end_match():
    global matches
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        match = next((m for m in matches if m["id"] == int(match_id)), None)
        if match:
            match["status"] = "completed"
            match["blue_score"] = team_info["blue"]["score"]
            match["green_score"] = team_info["green"]["score"]
            match["timer"] = team_info["timer"]
            save_data()
            return jsonify({"message": "Match ended successfully"}), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error ending match"}), 500

@server.route("/orga/update_match_time", methods=["POST"])
def update_match_time():
    global matches
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        match_time = data.get("match_time")
        match = next((m for m in matches if m["id"] == int(match_id)), None)
        if match:
            match["match_time"] = match_time
            save_data()
            return jsonify({"message": "Match time updated successfully"}), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error updating match time"}), 500

@server.route("/get_standings", methods=["GET"])
def get_standings():
    try:
        standings = calculate_standings()
        return jsonify(standings), 200
    except Exception as e:
        return jsonify({"message": "Error fetching standings"}), 500

@server.route("/orga/login", methods=["POST"])
def login():
    data = request.get_json()
    if data.get("password") == PASSWORD:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 401

@server.route("/")
def user_interface():
    return render_template("user_interface.html", matches=matches)

if __name__ == "__main__":
    server.run(host="0.0.0.0", debug=True, port=5000)