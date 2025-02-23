import spotipy
from spotipy.oauth2 import SpotifyOAuth
import speech_recognition as sr
import pyttsx3
import random
import pyfiglet  # Importing pyfiglet to create ASCII art

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Set up Spotify API authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='YOUR_CLIENT_ID',
                                               client_secret='YOUR_CLIENT_SECRET',
                                               redirect_uri='http://localhost:8888/callback',
                                               scope='user-library-read user-modify-playback-state user-read-playback-state'))

# Initialize Speech recognizer
recognizer = sr.Recognizer()

# Function to display ASCII art title
def display_title():
    title = "Spotify Voice Control"
    ascii_art = pyfiglet.figlet_format(title)
    print(ascii_art)  # Display the ASCII art

# Helper function for speech-to-text
def listen_to_microphone():
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise
        
        print("Listening for command...")
        try:
            # Increase the timeout to allow longer listening periods
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Timeout is 5 seconds, phrase time limit 10 seconds
            
            # Attempt to recognize the speech
            command = recognizer.recognize_google(audio).lower()
            print(f"Command received: {command}")
            return command
        
        except sr.WaitTimeoutError:
            print("Listening timeout, no speech detected.")
            return ""
        
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return ""
        
        except sr.RequestError:
            print("Couldn't request results from Google Speech Recognition service.")
            return ""

# Function to play a random track from an artist
def play_random_track_from_artist(artist_name):
    results = sp.search(q=f"artist:{artist_name}", type="track", limit=50)
    tracks = results['tracks']['items']
    
    if not tracks:
        engine.say(f"Sorry, I couldn't find any tracks by {artist_name}.")
        engine.runAndWait()
        return
    
    # Pick a random track
    track = random.choice(tracks)
    track_uri = track['uri']
    
    sp.start_playback(uris=[track_uri])
    engine.say(f"Now playing {track['name']} by {artist_name}.")
    engine.runAndWait()

# Function to play a specific track by track name (no artist specified)
def play_specific_track(track_name):
    results = sp.search(q=f"track:{track_name}", type="track", limit=1)
    tracks = results['tracks']['items']
    
    if not tracks:
        engine.say(f"Sorry, I couldn't find the track {track_name}.")
        engine.runAndWait()
        return
    
    track = tracks[0]
    track_uri = track['uri']
    
    sp.start_playback(uris=[track_uri])
    engine.say(f"Now playing {track_name}.")
    engine.runAndWait()

# Function to play a specific track by artist and track name
def play_specific_track_by_artist(artist_name, track_name):
    results = sp.search(q=f"track:{track_name} artist:{artist_name}", type="track", limit=1)
    tracks = results['tracks']['items']
    
    if not tracks:
        engine.say(f"Sorry, I couldn't find the track {track_name} by {artist_name}.")
        engine.runAndWait()
        return
    
    track = tracks[0]
    track_uri = track['uri']
    
    sp.start_playback(uris=[track_uri])
    engine.say(f"Now playing {track_name} by {artist_name}.")
    engine.runAndWait()

# Function to process voice command and control Spotify
def process_command(command):
    if "play" in command:
        # Remove 'play' and process the remaining part of the command
        command = command.replace("play", "").strip()

        # If command contains 'by' (indicating artist + track)
        if " by " in command:
            parts = command.split(" by ", 1)  # Split into track and artist
            
            track_name = parts[0].strip()
            artist_name = parts[1].strip()
            
            print(f"Trying track: {track_name}, artist: {artist_name}")
            play_specific_track_by_artist(artist_name, track_name)
        
        # Handle case where only a track name is given (e.g., "play hot in here")
        elif " " in command:
            print(f"Playing track: {command}")
            play_specific_track(command)
        
        # Handle case where only an artist name is given
        elif "random" in command and "artist" in command:
            artist_name = command.split("play random artist ")[-1]
            play_random_track_from_artist(artist_name)
        elif "artist" in command:
            artist_name = command.split("play artist ")[-1]
            play_random_track_from_artist(artist_name)
        else:
            engine.say("Sorry, I didn't understand which song to play.")
            engine.runAndWait()
    elif "pause" in command:
        sp.pause_playback()
        engine.say("Music paused.")
        engine.runAndWait()
    elif "next" in command:
        sp.next_track()
        engine.say("Next track.")
        engine.runAndWait()
    elif "previous" in command:
        sp.previous_track()
        engine.say("Previous track.")
        engine.runAndWait()
    elif "volume up" in command:
        current_volume = sp.current_playback()['device']['volume_percent']
        sp.volume(min(100, current_volume + 10))
        engine.say("Volume up.")
        engine.runAndWait()
    elif "volume down" in command:
        current_volume = sp.current_playback()['device']['volume_percent']
        sp.volume(max(0, current_volume - 10))
        engine.say("Volume down.")
        engine.runAndWait()
    else:
        engine.say("Sorry, I didn't understand that command.")
        engine.runAndWait()

# Main loop
if __name__ == "__main__":
    display_title()  # Display the ASCII art title when the program starts
    while True:
        command = listen_to_microphone()
        if command:
            process_command(command)
