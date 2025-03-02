from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class MatchApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical')
        self.match_spinner = Spinner(text='Select Match', size_hint=(1, 0.2))
        self.match_spinner.bind(text=self.show_match_info)
        self.root.add_widget(self.match_spinner)
        self.info_label = Label(text='Match Info', size_hint=(1, 0.6))
        self.root.add_widget(self.info_label)
        self.back_button = Button(text='Back', size_hint=(1, 0.2), on_press=self.go_back)
        self.root.add_widget(self.back_button)
        self.fetch_matches()
        self.current_event = None
        return self.root

    def fetch_matches(self):
        try:
            response = requests.get("http://localhost:5000/get_matches")
            response.raise_for_status()
            matches = response.json()
            self.match_spinner.values = [f"{match['id']}: {match['blue_team']} vs {match['green_team']}" for match in matches]
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching matches: {e}")

    def show_match_info(self, spinner, text):
        match_id = text.split(':')[0]
        if self.current_event:
            Clock.unschedule(self.current_event)
        self.update_team_info(match_id)
        self.current_event = Clock.schedule_interval(lambda dt: self.update_team_info(match_id), 0.5)  # Update every 0.5 seconds

    def update_team_info(self, match_id):
        try:
            response = requests.get(f"http://localhost:5000/get_team_info?match_id={match_id}")
            response.raise_for_status()
            team_info = response.json()
            self.info_label.text = (f"Blue Team Name: {team_info['blue']['name']}\n"
                                    f"Blue Score: {team_info['blue']['score']}\n"
                                    f"Green Team Name: {team_info['green']['name']}\n"
                                    f"Green Score: {team_info['green']['score']}\n"
                                    f"Timer: {team_info['timer']}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching team info: {e}")

    def go_back(self, instance):
        self.info_label.text = 'Match Info'
        self.match_spinner.text = 'Select Match'
        if self.current_event:
            Clock.unschedule(self.current_event)

if __name__ == "__main__":
    MatchApp().run()
