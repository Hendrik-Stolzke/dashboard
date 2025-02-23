from customtkinter import *
import pandas as pd
from datetime import datetime

# CSV-Datei für Speicherung
ALARM_FILE = "data/alarms.csv"

def build_page(app, frames, root):
    # Initialisiere die Daten (lade bestehende Wecker aus CSV)
    def load_all_alarms():
        try:
            data = pd.read_csv(ALARM_FILE)
            data = data.to_dict(orient="records")
            return data
        except BaseException:
            return []

    def save_alarms():
        pd.DataFrame(alarms).to_csv(ALARM_FILE, index=False)
    # Lade bestehende Alarme
    alarms = load_all_alarms()

    # Frame erstellen
    page_frame = CTkFrame(root)
    frames['alerts'] = page_frame

    # Überschrift
    CTkLabel(page_frame, text="Wecker", font=("Helvetica", 24, "bold")).pack(pady=20)

    # Liste der Wecker
    wecker_frame = CTkFrame(page_frame)
    wecker_frame.pack(pady=10, fill="both", expand=True)
    CTkLabel(wecker_frame, text="Eingestellte Wecker:", font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

    wecker_listbox = CTkScrollableFrame(wecker_frame, width=400, height=200)
    wecker_listbox.pack(pady=5, padx=10)

    # Eingabe für neuen Wecker
    new_alarm_frame = CTkFrame(page_frame)
    new_alarm_frame.pack(pady=20)

    CTkLabel(new_alarm_frame, text="Neue Weckzeit hinzufügen (HH:MM):", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=5)
    alarm_entry = CTkEntry(new_alarm_frame, width=150, placeholder_text="z.B. 07:30")
    alarm_entry.grid(row=0, column=1, padx=10)

    # Wochentage auswählen
    days_frame = CTkFrame(page_frame)
    days_frame.pack(pady=10)
    days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    selected_days = {day: CTkCheckBox(days_frame, text=day) for day in days}

    for i, day in enumerate(days):
        selected_days[day].grid(row=i // 4, column=i % 4, padx=10, pady=5, sticky="w")

    # Funktionen für Wecker
    def is_duplicate(alarm_time, chosen_days):
        return any(alarm['time'] == alarm_time and set(alarm['days'].split(",")) == set(chosen_days) for alarm in alarms)

    def add_alarm():
        alarm_time = alarm_entry.get().strip()
        chosen_days = [day for day, checkbox in selected_days.items() if checkbox.get() == 1]

        if not chosen_days:
            CTkLabel(page_frame, text="Bitte mindestens einen Wochentag auswählen!", text_color="red").pack(pady=5)
            return

        try:
            # Überprüfung des Zeitformats
            datetime.strptime(alarm_time, "%H:%M")

            if is_duplicate(alarm_time, chosen_days):
                CTkLabel(page_frame, text="Wecker bereits vorhanden!", text_color="red").pack(pady=5)
                return

            # Neuen Alarm hinzufügen
            alarms.append({"time": alarm_time, "days": ",".join(chosen_days)})
            save_alarms()
            update_alarm_list()
            alarm_entry.delete(0, END)
            for checkbox in selected_days.values():
                checkbox.deselect()
        except ValueError:
            CTkLabel(page_frame, text="Ungültige Zeit. Format: HH:MM", text_color="red").pack(pady=5)

    def update_alarm_list():
        # Liste aktualisieren
        for widget in wecker_listbox.winfo_children():
            widget.destroy()
        print(alarms)
        for alarm in alarms:
            alarm_frame = CTkFrame(wecker_listbox)
            alarm_frame.pack(fill="x", pady=2, padx=5)
            CTkLabel(alarm_frame, text=f"{alarm['time']} - {alarm['days']}", font=("Helvetica", 12)).pack(side="left", padx=5)
            CTkButton(alarm_frame, text="Löschen", width=60, command=lambda a=alarm: delete_alarm(a)).pack(side="right", padx=5)

    def delete_alarm(alarm):
        if alarm in alarms:
            alarms.remove(alarm)
            save_alarms()
            update_alarm_list()

    # Button für Wecker hinzufügen
    add_alarm_btn = CTkButton(new_alarm_frame, text="Hinzufügen", command=add_alarm)
    add_alarm_btn.grid(row=0, column=2, padx=10)

    # Liste beim Start anzeigen
    update_alarm_list()

    # Zurück-Button
    CTkButton(page_frame, text="Zurück zum Dashboard", command=lambda: app.show_page('dashboard')).pack(pady=10)

    page_frame.grid(row=0, column=0, sticky="nsew")
