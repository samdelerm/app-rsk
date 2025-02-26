import tkinter as tk
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_team_info(match_id):
    try:
        response = requests.get(f"https://app-rsk.onrender.com/get_team_info?match_id={match_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching team info: {e}")
        return {"blue": {"name": "", "score": 0}, "green": {"name": "", "score": 0}}

def fetch_matches():
    try:
        response = requests.get("https://app-rsk.onrender.com/get_matches")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching matches: {e}")
        return []

def update_team_info():
    team_info = fetch_team_info(selected_match_id.get())
    blue_name_label.config(text=f"Blue Team Name: {team_info['blue']['name']}")
    blue_score_label.config(text=f"Blue Score: {team_info['blue']['score']}")
    green_name_label.config(text=f"Green Team Name: {team_info['green']['name']}")
    green_score_label.config(text=f"Green Score: {team_info['green']['score']}")
    timer_label.config(text=f"Timer: {team_info['timer']}")
    root.after(50, update_team_info)  # Update every 5 seconds

def show_match_info():
    if selected_match_id.get():
        welcome_frame.pack_forget()
        match_frame.pack(fill="both", expand=True)
        update_team_info()
    else:
        logging.warning("No match selected")

def go_back():
    match_frame.pack_forget()
    welcome_frame.pack(fill="both", expand=True)

root = tk.Tk()
root.title("Match Info")
root.geometry("600x400")
root.configure(bg="#f0f0f0")

selected_match_id = tk.StringVar()

welcome_frame = tk.Frame(root, bg="#f0f0f0")
welcome_frame.pack(fill="both", expand=True)

title_label = tk.Label(welcome_frame, text="Welcome", font=("Helvetica", 24, "bold"), bg="#f0f0f0")
title_label.pack(pady=20)

matches = fetch_matches()
for match in matches:
    match_radio = tk.Radiobutton(welcome_frame, text=f"{match['blue_team']} vs {match['green_team']} - {match['status']}", variable=selected_match_id, value=match['id'], font=("Helvetica", 16), bg="#f0f0f0")
    match_radio.pack(pady=5)

start_button = tk.Button(welcome_frame, text="Watch Match", command=show_match_info, font=("Helvetica", 18), bg="#28a745", fg="#fff", bd=0, padx=20, pady=10)
start_button.pack(pady=20)

match_frame = tk.Frame(root, bg="#f0f0f0")

blue_frame = tk.Frame(match_frame, bg="#d0e1f9", bd=2, relief="groove")
blue_frame.pack(pady=10, padx=10, fill="x")

blue_name_label = tk.Label(blue_frame, text="Blue Team Name: ", font=("Helvetica", 18), bg="#d0e1f9")
blue_name_label.pack(pady=5)

blue_score_label = tk.Label(blue_frame, text="Blue Score: ", font=("Helvetica", 18), bg="#d0e1f9")
blue_score_label.pack(pady=5)

green_frame = tk.Frame(match_frame, bg="#d0f9d0", bd=2, relief="groove")
green_frame.pack(pady=10, padx=10, fill="x")

green_name_label = tk.Label(green_frame, text="Green Team Name: ", font=("Helvetica", 18), bg="#d0f9d0")
green_name_label.pack(pady=5)

green_score_label = tk.Label(green_frame, text="Green Score: ", font=("Helvetica", 18), bg="#d0f9d0")
green_score_label.pack(pady=5)

timer_label = tk.Label(match_frame, text="Timer: ", font=("Helvetica", 18), bg="#f0f0f0")
timer_label.pack(pady=10)

back_button = tk.Button(match_frame, text="Back", command=go_back, font=("Helvetica", 18), bg="#dc3545", fg="#fff", bd=0, padx=20, pady=10)
back_button.pack(pady=10)

root.mainloop()
