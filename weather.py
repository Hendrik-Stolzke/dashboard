from customtkinter import *
import requests
from bs4 import BeautifulSoup
from PIL import Image

# Funktion zum Abrufen des Wetters für Reutlingen
def get_weather_Reutlingen():
    try:
        url = f"https://www.wetter.de/wetter/r/2772661"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        description = soup.find("p", class_="text-basic-white font-medium text-base m-0 mb-0 leading-5 pb-[16px]").get_text()
        temp = soup.find("span", class_="text-5xl font-medium").get_text()
        days_14 = soup.find("div", class_="hidden text-base leading-[26px] pb-[26px] font-normal text-grey-1").get_text()
        
        return {"temperatur": temp, "beschreibung": description, "days_14": days_14}
    except Exception as e:
        print(f"Fehler: {e}")
        return None

# Funktion zum Abrufen des Wetters für Offenburg
def get_weather_Offenburg():
    try:
        url = f"https://www.wetter.de/wetter/r/452988"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        description = soup.find("p", class_="text-basic-white font-medium text-base m-0 mb-0 leading-5 pb-[16px]").get_text()
        temp = soup.find("span", class_="text-5xl font-medium").get_text()
        days_14 = soup.find("div", class_="hidden text-base leading-[26px] pb-[26px] font-normal text-grey-1").get_text()
        
        return {"temperatur": temp, "beschreibung": description, "days_14": days_14}
    except Exception as e:
        print(f"Fehler: {e}")
        return None

def get_weather_image(description):
    """Gibt den Dateipfad eines passenden Bildes basierend auf der Wetterbeschreibung zurück."""
    if "sonnig" in description.lower():
        return "images/sun.png"
    elif "regen" in description.lower():
        return "images/rain.png"
    elif "bewölkt" in description.lower() or "wolken" in description.lower():
        return "images/cloud.png"
    elif "schnee" in description.lower():
        return "images/snow.png"
    else:
        return "images/default.png"  # Fallback-Bild

# Wetterseite aufbauen
def build_page(app, frames, root):
    page_frame = CTkFrame(root)
    frames['weather'] = page_frame

    # Wetterdaten abrufen
    weather1 = get_weather_Reutlingen()
    weather2 = get_weather_Offenburg()
    
    page_frame.grid_rowconfigure(0, weight=1)
    page_frame.grid_rowconfigure(1, weight=1)
    page_frame.grid_rowconfigure(3, weight=1)
    page_frame.grid_rowconfigure(4, weight=1)
    page_frame.grid_rowconfigure(5, weight=1)
    page_frame.grid_columnconfigure(0, weight=1)
    page_frame.grid_columnconfigure(1, weight=1)

    # Titel
    CTkLabel(page_frame, text="Willkommen auf der Wetter-Seite!", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

    # Wetterdaten darstellen
    if weather1:
        # Reutlingen
        CTkLabel(page_frame, text="Reutlingen", font=("Helvetica", 16, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        CTkLabel(page_frame, text=f"{weather1['temperatur']}°", font=("Helvetica", 40)).grid(row=2, column=0, padx=10, sticky="w")
        CTkLabel(page_frame, text=f"{weather1['beschreibung']}", font=("Helvetica", 14)).grid(row=3, column=0, padx=10, sticky="w")
        weather_image1_path = get_weather_image(weather1['beschreibung'].replace("\n", "").split("            ")[1].split(" ")[0])
        
        weather_image1 = CTkImage(Image.open(weather_image1_path), size=(100, 100))
        CTkLabel(page_frame, image=weather_image1, text="").grid(row=2, column=0, padx=10, pady=10)
        
        CTkLabel(page_frame, text=f"{weather1['days_14']}", font=("Helvetica", 14)).grid(row=4, column=0, padx=10, sticky="w")
    
    if weather2:
        # Offenburg
        CTkLabel(page_frame, text="Offenburg", font=("Helvetica", 16, "bold")).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        CTkLabel(page_frame, text=f"{weather2['temperatur']}°", font=("Helvetica", 40)).grid(row=2, column=1, padx=10, sticky="w")
        CTkLabel(page_frame, text=f"{weather2['beschreibung']}", font=("Helvetica", 14)).grid(row=3, column=1, padx=10, sticky="w")
        
        weather_image2_path = get_weather_image(weather1['beschreibung'].replace("\n", "").split("            ")[1].split(" ")[0])
        
        weather_image2 = CTkImage(Image.open(weather_image2_path), size=(100, 100))
        CTkLabel(page_frame, image=weather_image2, text="").grid(row=2, column=1, padx=10, pady=10)

        
        CTkLabel(page_frame, text=f"{weather2['days_14']}", font=("Helvetica", 14)).grid(row=4, column=1, padx=10, sticky="w")
    else:
        CTkLabel(page_frame, text="Fehler beim Abrufen der Wetterdaten.", font=("Helvetica", 14, "italic"), text_color="red").grid(row=1, column=0, columnspan=2, pady=10)

    # Zurück-Button
    btn_back = CTkButton(page_frame, text="Zurück zum Dashboard", command=lambda: app.show_page('dashboard'))
    btn_back.grid(row=5, column=0, columnspan=2, pady=20)

    page_frame.grid(row=0, column=0, sticky="nsew")
