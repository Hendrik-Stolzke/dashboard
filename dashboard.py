from customtkinter import *

def build_page(app, frames, root):
    page_frame = CTkFrame(root)
    frames['dashboard'] = page_frame

    # Konfiguriere das Grid des Hauptfensters (root), damit es den gesamten Raum einnimmt
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    page_frame.grid(row=0, column=0, sticky="nsew")  # Damit das Frame den gesamten verfügbaren Raum einnimmt

    # Layout für das Hauptfenster
    page_frame.grid_rowconfigure(0, weight=1)  # Zeile 0, gewichtet
    page_frame.grid_columnconfigure(0, weight=1)  # Spalte 0, gewichtet
    page_frame.grid_rowconfigure(1, weight=1)  # Zeile 1, gewichtet
    page_frame.grid_columnconfigure(1, weight=1)  # Spalte 1, gewichtet (zentrieren)
    page_frame.grid_rowconfigure(2, weight=1)  # Zeile 1, gewichtet
    page_frame.grid_columnconfigure(2, weight=1)  # Spalte 1, gewichtet (zentrieren)
    page_frame.grid_rowconfigure(3, weight=1)  # Zeile 1, gewichtet
    page_frame.grid_rowconfigure(4, weight=1)  # Spalte 1, gewichtet (zentrieren)
    page_frame.grid_rowconfigure(5, weight=1)  # Zeile 1, gewichtet

    # Dashboard-Inhalte
    CTkLabel(page_frame, text="Willkommen im Dashboard!", font=("Helvetica", 30, "bold")).grid(row=0, column=1, pady=20)

    # Button zu weiteren Seiten
    btn_go_to_news = CTkButton(page_frame, text="News", command=app.show_news, font=("Helvetica", 14, "bold"),
                                fg_color="#2196F3", text_color="white", corner_radius=8)
    btn_go_to_news.grid(row=3, column=1, pady=5)

    btn_go_to_settings = CTkButton(page_frame, text="Settings", command=app.show_settings, font=("Helvetica", 14, "bold"),
                                    fg_color="#FF9800", text_color="white", corner_radius=8)
    btn_go_to_settings.grid(row=5, column=1, pady=5)

    btn_go_to_stocks = CTkButton(page_frame, text="Stocks", command=app.show_stocks, font=("Helvetica", 14, "bold"),
                                  fg_color="lightblue", text_color="white", corner_radius=8)
    btn_go_to_stocks.grid(row=2, column=1, pady=5)

    btn_go_to_weather = CTkButton(page_frame, text="Weather", command=app.show_weather, font=("Helvetica", 14, "bold"),
                                   fg_color="#FFC107", text_color="white", corner_radius=8)
    btn_go_to_weather.grid(row=4, column=1, pady=5)

    btn_go_to_alerts = CTkButton(page_frame, text="Wecker", command=app.show_alerts, font=("Helvetica", 14, "bold"),
                                   fg_color="green", text_color="white", corner_radius=8)
    btn_go_to_alerts.grid(row=1, column=1, pady=5)


    page_frame.grid(row=0, column=0, sticky="nsew")  # Zeigt das Frame an
    # page_frame.pack()
