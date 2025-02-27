from flask import Flask, request, jsonify
import requests
import rsk
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# API Client : Récupère le score et l'envoie au serveur

def format_timer(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}min {seconds}sec"

def send_score():
    client = rsk.Client()
    while True:
        try:
            blue_score = client.referee["teams"]["blue"]["score"]
            blue_name = client.referee["teams"]["blue"]["name"]
            green_score = client.referee["teams"]["green"]["score"]
            green_name = client.referee["teams"]["green"]["name"]
            timer = format_timer(client.referee["timer"])
            response = requests.post("https://app-rsk.onrender.com/update_score", json={
                "blue_score": blue_score, 
                "blue_name": blue_name,
                "green_score": green_score,
                "green_name": green_name,
                "timer": timer
            })
            response.raise_for_status()
            logging.info(f"Scores, names, and timer sent: Blue - {blue_score}, {blue_name}; Green - {green_score}, {green_name}; Timer - {timer}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending scores, names, and timer: {e}")
        except KeyError as e:
            logging.error(f"Error accessing scores, names, or timer: {e}")
        time.sleep(0.5)  # Met à jour toutes les 5 secondes

if __name__ == "__main__":
    send_score()