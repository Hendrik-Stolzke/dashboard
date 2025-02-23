from customtkinter import *

def build_page(app, frames, root):
    page_frame = CTkFrame(root)
    frames['settings'] = page_frame

    # News-Inhalte
    CTkLabel(page_frame, text="Willkommen auf der Settings-Seite!").pack(pady=20)
    btn_back = CTkButton(page_frame, text="Zurück zum Dashboard", command=lambda: app.show_page('dashboard'))
    btn_back.pack(pady=10)

    page_frame.grid(row=0, column=0, sticky="nsew")  # Wichtige Zeile: Frame soll die gesamte Fenstergröße einnehmen
