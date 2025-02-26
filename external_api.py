from flask import Flask, request, jsonify
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# API Externe : Demande les infos de l'équipe au serveur

def fetch_team_info():
    try:
        response = requests.get("http://127.0.0.1:5000/get_team_info")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching team info: {e}")
        return {"name": "", "score": 0}

if __name__ == "__main__":
    while True:
        team_info = fetch_team_info()
        logging.info(f"Fetched team info: {team_info}")
        # Output: {'name': '', 'score': 0}
        # Output: {'name': 'Les bleus', 'score': 0}