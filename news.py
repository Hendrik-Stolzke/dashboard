from customtkinter import *
from PIL import Image
import requests
from io import BytesIO

# Anzahl der anzuzeigenden Artikel
anz = 12

def add_more(app, frames, root):
    """Erhöht die Anzahl der anzuzeigenden Artikel und lädt die Seite neu."""
    global anz
    anz += 16  # Zeige 8 weitere Artikel
    build_page(app, frames, root)  # Seite neu rendern

# Funktion, um die Nachrichten-Seite zu erstellen
def build_page(app, frames, root):
    global anz
    page_frame = CTkFrame(root)
    frames['news'] = page_frame

    # Titel der Seite
    CTkLabel(page_frame, text="Aktuelle Nachrichten", font=("Helvetica", 24, "bold")).pack(pady=10)

    # Scrollbarer Bereich für die Nachrichten
    scrollable_frame = CTkScrollableFrame(page_frame, width=600, height=400)  # Größe des Scrollbereichs
    scrollable_frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Grid-Konfiguration für das scrollbare Frame
    scrollable_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)  # Vier Spalten

    # API-Daten abrufen
    api_key = "3397ac9f591c482eb0cf4f34a81565df"  # Ersetze durch deinen API-Schlüssel
    news_data = fetch_news(api_key)

    # Nachrichten im scrollbaren Bereich in vier Spalten anzeigen
    if news_data:
        display_articles_grid(scrollable_frame, news_data[:anz])  # Zeige `anz` Artikel
    else:
        CTkLabel(scrollable_frame, text="Keine Nachrichten verfügbar.", font=("Helvetica", 16)).pack(pady=10)

    # „Mehr“ Button
    btn_more = CTkButton(page_frame, text="Mehr", command=lambda: add_more(app, frames, root))
    btn_more.pack(pady=10)

    # Zurück-Button
    btn_back = CTkButton(page_frame, text="Zurück zum Dashboard", command=lambda: app.show_page('dashboard'))
    btn_back.pack(pady=10)

    page_frame.grid(row=0, column=0, sticky="nsew")

# Funktion, um aktuelle Nachrichten abzurufen
def fetch_news(api_key):
    url = f"https://newsapi.org/v2/everything?q=Deutschland&sortBy=publishedAt&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print(f"Fehler beim Abrufen der Nachrichten: {e}")
        return None

# Funktion, um Artikel im Grid anzuzeigen (4 Spalten)
def display_articles_grid(parent, articles):
    """Zeigt Artikel in einem Grid-Layout mit vier Spalten an."""
    for index, article in enumerate(articles):
        row = index // 4  # Vier Artikel pro Reihe
        col = index % 4   # Spalten 0, 1, 2, 3

        frame = CTkFrame(parent)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")  # Platzierung im Grid

        # Titel
        CTkLabel(frame, text=article.get("title", "Kein Titel"), font=("Helvetica", 12, "bold"), wraplength=200).pack(pady=5)

        # Bild
        image_url = article.get("urlToImage")
        if image_url:
            try:
                response = requests.get(image_url)
                image_data = BytesIO(response.content)
                image = Image.open(image_data).resize((150, 100))  # Angepasste Bildgröße
                ctk_image = CTkImage(light_image=image, size=(150, 100))
                CTkLabel(frame, image=ctk_image, text="").pack()
            except Exception as e:
                print(f"Fehler beim Laden des Bildes: {e}")

        # Beschreibung
        description = article.get("description", "Keine Beschreibung verfügbar.")
        CTkLabel(frame, text=description, wraplength=200).pack(pady=5)

        # Link
        url = article.get("url")
        if url:
            CTkButton(frame, text="Mehr erfahren", command=lambda u=url: open_link(u)).pack(pady=5)

# Funktion, um Links im Browser zu öffnen
def open_link(url):
    import webbrowser
    webbrowser.open(url)
