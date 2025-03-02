from flask import Flask, request, jsonify
import requests
import rsk
import time
import logging
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)

# API Client : Récupère le score et l'envoie au serveur

def format_timer(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}min {seconds}sec"

class MatchSelectorApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Select an ongoing match to send scores:")
        self.layout.add_widget(self.label)
        
        self.spinner = Spinner(text='Select Match', values=[])
        self.layout.add_widget(self.spinner)
        
        self.start_button = Button(text="Start Sending Scores")
        self.start_button.bind(on_press=self.start_sending_scores)
        self.layout.add_widget(self.start_button)
        
        self.stop_button = Button(text="Stop Sending Scores")
        self.stop_button.bind(on_press=self.stop_sending_scores)
        self.layout.add_widget(self.stop_button)
        
        self.update_matches()
        
        return self.layout
    
    def update_matches(self):
        try:
            response = requests.get("https://app-rsk.onrender.com/get_matches")
            response.raise_for_status()
            matches = response.json()
            ongoing_matches = [f"{match['id']}: {match['blue_team']} vs {match['green_team']}" for match in matches if match['status'] == 'ongoing']
            self.spinner.values = ongoing_matches
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching matches: {e}")
        time.sleep(0.1)
    
    def start_sending_scores(self, instance):
        selected_match = self.spinner.text
        if selected_match != 'Select Match':
            match_id = int(selected_match.split(":")[0])
            self.send_score_thread = threading.Thread(target=send_score, args=(match_id,))
            self.send_score_thread.start()
    
    def stop_sending_scores(self, instance):
        global stop_sending
        stop_sending = True

def send_score(match_id):
    global stop_sending
    stop_sending = False
    client = rsk.Client()
    while not stop_sending:
        try:
            blue_score = client.referee["teams"]["blue"]["score"]
            blue_name = client.referee["teams"]["blue"]["name"]
            green_score = client.referee["teams"]["green"]["score"]
            green_name = client.referee["teams"]["green"]["name"]
            timer = format_timer(client.referee["timer"])
            response = requests.post("https://app-rsk.onrender.com/update_score", json={
                "match_id": match_id,
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
        time.sleep(0.5)  # Update every 0.5 seconds

if __name__ == "__main__":
    MatchSelectorApp().run()