from PIL import Image, ImageTk
from tkinter import Toplevel, StringVar
from customtkinter import *
import threading
from playsound import playsound  # Zum Abspielen eines Alarmsounds
from tkinter import messagebox
from datetime import datetime, timedelta
from predictions import calculate_aktien
import time
import dashboard
import news
import settings
import stocks
import weather
import time
import alerts
import pandas as pd
import locale
import pygame
import os

# Variable, um den Tag zu speichern, an dem die Berechnung zuletzt durchgeführt wurde
last_calculated_day = None
executed_alarms = {}  # Speichert die Alarme, die am aktuellen Tag bereits ausgelöst wurden

# Musik-Controller
stop_music = threading.Event()
# Setze die Sprache für Datum und Uhrzeit auf Deutsch
# locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")  # Für Linux/macOS
locale.setlocale(locale.LC_TIME, "German_Germany.1252")  # Für Windows

def delete_png_files(folder_paths):
    for folder in folder_paths:
        if os.path.exists(folder):  # Prüfen, ob der Ordner existiert
            for file_name in os.listdir(folder):  # Dateien im Ordner auflisten
                if file_name.endswith(".png"):  # Nur `.png`-Dateien auswählen
                    file_path = os.path.join(folder, file_name)
                    try:
                        os.remove(file_path)  # Datei löschen
                        print(f"Gelöscht: {file_path}")
                    except Exception as e:
                        print(f"Fehler beim Löschen von {file_path}: {e}")
        else:
            print(f"Ordner nicht gefunden: {folder}")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Wolf")
        self.root.iconbitmap("Wolf.ico")

        # Berechne die Fenstergröße
        screen_width = self.root.winfo_screenwidth()  # Bildschirmbreite
        screen_height = self.root.winfo_screenheight()  # Bildschirmhöhe

        # Setze die Fenstergröße auf volle Höhe und halbe Breite
        window_width = screen_width//2  # Hälfte der Bildschirmbreite
        window_height = screen_height/100*80    # Volle Bildschirmhöhe
        self.root.geometry(f"{window_width}x{int(window_height)}+0+0")  # Setze Fenstergröße und Position

        # Container für die Frames (Seiten)
        self.frames = {}

        # Erstelle die Hauptseite
        self.main_frame = CTkFrame(self.root)
        self.frames['main'] = self.main_frame

        # Konfiguriere das Grid des Hauptfensters (root), damit es den gesamten Raum einnimmt
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.main_frame.grid(row=0, column=0, sticky="nsew")  # Damit das Frame den gesamten verfügbaren Raum einnimmt

        # Layout für das Hauptfenster
        self.main_frame.grid_rowconfigure(0, weight=3)  # Zeile 0, gewichtet
        self.main_frame.grid_columnconfigure(0, weight=1)  # Spalte 0, gewichtet
        self.main_frame.grid_rowconfigure(1, weight=1)  # Zeile 1, gewichtet
        self.main_frame.grid_columnconfigure(1, weight=1)  # Spalte 1, gewichtet (zentrieren)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Zeile 1, gewichtet
        self.main_frame.grid_columnconfigure(2, weight=3)  # Spalte 1, gewichtet (zentrieren)
        self.main_frame.grid_rowconfigure(3, weight=1)  # Zeile 1, gewichtet

        # Startseite aufbauen
        self.build_main_page()

    def build_main_page(self):
        # Hauptseite Inhalte
        label = CTkLabel(self.main_frame, text="Willkommen zu Wolf", font=("Helvetica", 34, "bold"))
        label.grid(row=0, column=1, pady=20)  # Zentrieren innerhalb des Grids

        image = CTkImage(light_image=Image.open("Wolf.png"), 
                     size=(500, 500)) 
        # Bild in ein Label einfügen
        image_label = CTkLabel(self.main_frame, image=image, text="")  # `text=""` entfernt Text neben dem Bild
        image_label.grid(row=1, column=1, padx=0, pady=0)  # Bild in Row 1, Column 2 platzieren
        
        label = CTkLabel(self.main_frame, text="""W: Wake-up Call (Weckruf)
            O: Organized Schedule (Organisierter Zeitplan)
            L: Live Data (Echtzeitdaten)
            F: Financial Recommendations (Finanzempfehlungen)"""
            , font=("Helvetica", 14, "bold"))
        label.grid(row=2, column=1, pady=0)  # Zentrieren innerhalb des Grids

        # Start Button, der zum Dashboard führt
        btn_start = CTkButton(self.main_frame, text="Starten", command=self.show_dashboard,
                              font=("Helvetica", 14, "bold"), 
                              fg_color="lightblue", text_color="white", corner_radius=8)
        btn_start.grid(row=3, column=1, pady=20)  # Zentrieren innerhalb des Grids

    def build_page(self, page_name):
        # Dynamische Seiteninhalte
        page_module = globals().get(page_name)  # Holt das Modul basierend auf dem Namen
        if page_module:
            page_module.build_page(self, self.frames, self.root)

    def show_page(self, page_name):
        # Wechselt zu einer beliebigen Seite
        for frame in self.frames.values():
            frame.grid_forget()  # Versteckt alle Seiten

        self.build_page(page_name)  # Baue die Seite
        self.frames[page_name].grid(row=0, column=0, sticky="nsew")  # Zeigt die Seite an

    def show_dashboard(self):
        self.show_page('dashboard')

    def show_news(self):
        self.show_page('news')

    def show_settings(self):
        self.show_page('settings')

    def show_stocks(self):
        self.show_page('stocks')

    def show_weather(self):
        self.show_page('weather')

    def show_alerts(self):
        self.show_page('alerts')

def check_alarms():
    global last_calculated_day, executed_alarms

    while True:
        try:
            print("Check Alarm")
            alarms = load_alarms()  # Beispiel-Funktion zum Laden der Alarme
            now = datetime.now()
            current_day = now.strftime("%A")  # Wochentag (z.B. Montag)

            # Filtere die Alarme für den aktuellen Tag
            todays_alarms = [
                alarm for alarm in alarms if current_day in alarm['days'].split(",")
            ]

            # Früheste Alarmzeit berechnen
            if todays_alarms:
                earliest_alarm = min(
                    datetime.strptime(alarm['time'], "%H:%M") for alarm in todays_alarms
                )
                earliest_alarm = earliest_alarm.replace(
                    year=now.year, month=now.month, day=now.day
                )

                # Berechnung 1 Stunde vor dem frühesten Alarm
                one_hour_before = earliest_alarm - timedelta(hours=1)

                # Einmalige Berechnung für den Tag
                if now >= one_hour_before and now < earliest_alarm:
                    if last_calculated_day != now.date():                 
                        ordner_pfade = ["data/buy", "data/wait"]
                        delete_png_files(ordner_pfade)
                        calculate_aktien()
                        last_calculated_day = now.date()  # Speichere das Datum der Berechnung

            # Alarme prüfen und einmalig auslösen
            for alarm in todays_alarms:
                alarm_time = datetime.strptime(alarm['time'], "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day
                )

                # Alarm nur auslösen, wenn er noch nicht ausgeführt wurde
                if now >= alarm_time and now < alarm_time + timedelta(minutes=1):
                    if alarm['time'] not in executed_alarms.get(now.date(), []):
                        show_alarm_popup(alarm)
                        # Hinzufügen zur Liste der ausgeführten Alarme
                        if now.date() not in executed_alarms:
                            executed_alarms[now.date()] = []
                        executed_alarms[now.date()].append(alarm['time'])
        except Exception as e:
            print(f"Error in check_alarms: {e}")
        finally:
            time.sleep(55)  # Warten, um Ressourcen zu schonen        

def show_alarm_popup(alarm_time):
    global stop_music
    stop_music.clear()

    # Popup-Fenster erstellen
    popup = Toplevel()
    popup.title("Alarm!")
    popup.iconbitmap("Wolf.ico")

    # Berechne die Fenstergröße
    screen_width = popup.winfo_screenwidth()  # Bildschirmbreite
    screen_height = popup.winfo_screenheight()  # Bildschirmhöhe

    # Setze die Fenstergröße auf volle Höhe und halbe Breite
    window_width = screen_width  # Hälfte der Bildschirmbreite
    window_height = screen_height    # Volle Bildschirmhöhe
    popup.geometry(f"{window_width}x{int(window_height)}+0+0")  # Setze Fenstergröße und Position

    popup.grab_set()  # Modal machen

    # Nachricht
    alarm_message = StringVar()
    alarm_message.set(f"Der Wecker für {alarm_time} klingelt!")
    label = CTkLabel(popup, textvariable=alarm_message, font=("Helvetica", 16, "bold"))
    label.pack(pady=20)

    # Musik starten
    music_thread = threading.Thread(target=play_music_in_loop, args=("Universfield.mp3",))
    music_thread.start()

    # Button zum Stoppen des Alarms
    def stop_alarm():
        stop_music.set()  # Musik stoppen
        popup.destroy()  # Popup schließen

    button = CTkButton(popup, text="Alarm ausstellen", command=stop_alarm)
    button.pack(pady=20)

    # popup.mainloop()


def play_music_in_loop(file_path):
    """Spielt die Musik in einer Schleife ab, bis `stop_music` gesetzt wird."""
    pygame.mixer.init()
    while not stop_music.is_set():
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() and not stop_music.is_set():
                time.sleep(0.1)
        except:
            pass
    pygame.mixer.music.stop()
    pygame.mixer.quit()


# CSV-Datei für Speicherung
ALARM_FILE = "data/alarms.csv"
        
def load_alarms():
    try:
        return pd.read_csv(ALARM_FILE).to_dict(orient="records")
    except BaseException:  # Fängt wirklich alles ab
        return []

def start_alarm_checker():
    alarm_thread = threading.Thread(target=check_alarms, daemon=True)
    alarm_thread.start()

if __name__ == "__main__":
    ordner_pfade = ["data/buy", "data/wait"]  # Ersetzen Sie dies durch Ihre tatsächlichen Pfade
    delete_png_files(ordner_pfade)  # PNG-Dateien löschen
    start_alarm_checker()
    root = CTk()
    app = App(root)
    root.mainloop()
