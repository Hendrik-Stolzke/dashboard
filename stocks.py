from customtkinter import *
from PIL import Image, ImageTk
import requests
import pandas as pd
import os
import glob
from main import delete_png_files
from predictions import calculate_aktien    

def build_page(app, frames, root):
    if 'stocks' in frames and frames['stocks'] is not None:
        frames['stocks'].destroy()
    page_frame = CTkFrame(root)
    frames['stocks'] = page_frame
    

    # Dateipfad zur CSV-Datei
    file_path = "data/stocks.csv"

    # Prüfen, ob die CSV-Datei existiert, wenn nicht, erstelle sie mit den notwendigen Spalten
    if not os.path.exists(file_path):
        columns = ['Name', 'ISIN', 'Wert', 'Anteile']
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)

    def load_data():
        """Lädt die Daten aus der CSV."""
        return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame(columns=['Name', 'ISIN', 'Wert', 'Anteile'])

    def save_data(df):
        """Speichert die Daten in die CSV."""
        df.to_csv(file_path, index=False)

    def add_stock():
        """Fügt eine neue Aktie hinzu."""
        name = entry_name.get().strip()
        isin = entry_isin.get().strip()
        wert = entry_wert.get().strip()
        anteile = entry_anteile.get().strip()

        if not name or not isin or not wert or not anteile:
            lbl_status.config(text="Bitte alle Felder ausfüllen!", text_color="red")
            return

        df = load_data()

        if isin in df['ISIN'].values:
            lbl_status.config(text="Aktie mit dieser ISIN existiert bereits!", text_color="red")
            return

        new_stock = {'Name': name, 'ISIN': isin, 'Wert': float(wert), 'Anteile': int(anteile)}
        df = pd.concat([df, pd.DataFrame([new_stock])], ignore_index=True)

        save_data(df)
        update_display()
        lbl_status.config(text="Aktie erfolgreich hinzugefügt!", text_color="green")

    def delete_stock():
        """Löscht eine Aktie basierend auf der ISIN."""
        name = entry_delete_isin.get().strip()

        if not name:
            lbl_status.config(text="Bitte ISIN angeben!", text_color="red")
            return

        df = load_data()

        if name not in df['Name'].values:
            lbl_status.config(text="Keine Aktie mit dieser ISIN gefunden!", text_color="red")
            return

        df = df[df['Name'] != name]
        save_data(df)
        update_display()
        lbl_status.config(text="Aktie erfolgreich gelöscht!", text_color="green")

    def update_display():
        """Aktualisiert die Anzeige der Aktien."""
        df = load_data()

        for widget in stocks_frame.winfo_children():
            widget.destroy()

        for idx, row in df.iterrows():
            stock_info = f"Name: {row['Name']}, ISIN: {row['ISIN']}, Wert: {row['Wert']}, Anteile: {row['Anteile']}"    
            CTkLabel(stocks_frame, text=stock_info, anchor="w").grid(row=idx, column=0, sticky="w", padx=5, pady=2)
        
    def get_aktien_buy():
        png_dateien = glob.glob(os.path.join("data/buy", "*.png"))  
        lst = []
        for png in png_dateien:
            if png and os.path.exists(png):  
                lst.append(png)
        return lst
    
    def get_aktien_sell():
        png_dateien2 = glob.glob(os.path.join("data/wait", "*.png"))  
        lst = []
        for png in png_dateien2:
            if png and os.path.exists(png):  
                lst.append(png)
        return lst
            
    def get_diagramm(is_buy):
        df = load_data()
        df = df.drop_duplicates(subset='Name')
        count = is_buy
        image = None
        png_dateien = glob.glob(os.path.join("data/buy", "*.png"))  
        for png in png_dateien:
            if png and os.path.exists(png):  
                if count == 0:
                    image = CTkImage(light_image=Image.open(png), 
                        size=(370, 370))
                    return image
                count -=1
                
        for idx, row in df.iterrows():
            file_path = f"data/wait/{row['Name']}_Verkaufen.png"
            file_path2 = f"data/wait/{row['Name']}_Warten sinkt.png"      
            # Überprüfen, ob überhaupt .png-Dateien gefunden wurden
            if os.path.exists(file_path):
                if count == 0:
                    image = CTkImage(light_image=Image.open(file_path), 
                                size=(400, 400))  
                    return image     
                count -=1              
            elif os.path.exists(file_path2):
                if count == 0:
                    image = CTkImage(light_image=Image.open(file_path2), 
                                size=(400, 400)) 
                    return image
                count -=1
        png_dateien = glob.glob(os.path.join("data/wait", "*.png"))  
        for png in png_dateien:
            if png and os.path.exists(png):  
                if count == 0:
                    image = CTkImage(light_image=Image.open(png), 
                        size=(400, 400))
                    return image
                count -=1
        
        return None
    
    def del_and_recalc():
        ordner_pfade = ["data/buy", "data/wait"]
        delete_png_files(ordner_pfade)
        calculate_aktien()
        update_display()

    # Konfiguration des Grids
    page_frame.grid_rowconfigure(0, weight=1)
    page_frame.grid_rowconfigure(1, weight=1)
    page_frame.grid_rowconfigure(2, weight=1)
    page_frame.grid_rowconfigure(3, weight=1)
    page_frame.grid_rowconfigure(4, weight=1)
    page_frame.grid_rowconfigure(5, weight=1)
    page_frame.grid_rowconfigure(6, weight=1)
    page_frame.grid_rowconfigure(7, weight=1)
    page_frame.grid_columnconfigure(0, weight=1)
    page_frame.grid_columnconfigure(1, weight=1)
    page_frame.grid_columnconfigure(2, weight=1)
    # Eingabefelder und Buttons für Hinzufügen
    CTkLabel(page_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_name = CTkEntry(page_frame)
    entry_name.grid(row=0, column=1, padx=3, pady=5)

    CTkLabel(page_frame, text="ISIN:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_isin = CTkEntry(page_frame)
    entry_isin.grid(row=1, column=1, padx=3, pady=5)

    CTkLabel(page_frame, text="Wert:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_wert = CTkEntry(page_frame)
    entry_wert.grid(row=2, column=1, padx=3, pady=5)

    CTkLabel(page_frame, text="Anteile:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_anteile = CTkEntry(page_frame)
    entry_anteile.grid(row=3, column=1, padx=3, pady=5)

    btn_add_stock = CTkButton(page_frame, text="Hinzufügen", command=add_stock)
    btn_add_stock.grid(row=4, column=0, padx=3, pady=5)

    # Eingabefeld und Button für Löschen
    CTkLabel(page_frame, text="Löschen (Name):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
    entry_delete_isin = CTkEntry(page_frame)
    entry_delete_isin.grid(row=3, column=2, padx=3, pady=5)

    btn_delete_stock = CTkButton(page_frame, text="Löschen", command=delete_stock)
    btn_delete_stock.grid(row=4, column=2, padx=3, pady=5)

    # Statusanzeige
    lbl_status = CTkLabel(page_frame, text="Meine Aktien", text_color="white", font=("Helvetica", 18, "bold"))
    lbl_status.grid(row=0, column=2, columnspan=9, pady=10, sticky="we")

    # Bereich für die Anzeige der Aktien
    stocks_frame = CTkFrame(page_frame)
    stocks_frame.grid(row=1, column=2, columnspan=9, sticky="w")
    
    # # Handelsempfehlungen
    # lbl_Empfehlungen = CTkLabel(page_frame, text="Handelsempfehlungen", text_color="white", font=("Helvetica", 18, "bold"))
    # lbl_Empfehlungen.grid(row=7, column=0, columnspan=3, pady=10, sticky="we")
    
    image = get_diagramm(0)
    if image != None:
        # Bild in ein Label einfügen
        image_label = CTkLabel(page_frame, image=image, text="")  # `text=""` entfernt Text neben dem Bild
        image_label.grid(row=6, column=0, padx=0, pady=0, sticky="we")  # Bild in Row 1, Column 2 platzieren

    # # Handelsempfehlungen
    # lbl_Empfehlungen = CTkLabel(page_frame, text="Handelsempfehlungen2", text_color="white", font=("Helvetica", 18, "bold"))
    # lbl_Empfehlungen.grid(row=7, column=1, columnspan=3, pady=10, sticky="we")
    
    
     # Dropdown-Menü erstellen
    optionen = get_aktien_buy()
    # Funktion, um das Bild basierend auf der Auswahl zu aktualisieren
    def auswahl_anzeigen(file_path):
        if os.path.exists(file_path):
            # Bild laden und skalieren
            img = Image.open(file_path)#.resize((400, 400))
            updated_image = CTkImage(light_image=img, size=(400, 400))
            
            # Bild im Label aktualisieren
            image_label_pic_buy.configure(image=updated_image)
            image_label_pic_buy.image = updated_image  # Referenz halten
        else:
            print("Datei nicht gefunden!")
    if len(optionen) != 0:
    # Initiales Bild setzen
        initial_image_path = optionen[0] if os.path.exists(optionen[0]) else None
        initial_ctk_image_buy = None
        if initial_image_path:
            initial_ctk_image_buy = Image.open(initial_image_path) #.resize((400, 400))
            initial_ctk_image_buy = CTkImage(light_image=initial_ctk_image_buy, size=(400, 400))

        # Initiales Bild in ein Label einfügen
        image_label_pic_buy = CTkLabel(page_frame, image=initial_ctk_image_buy, text="")
        image_label_pic_buy.grid(row=6, column=0, padx=10, pady=10, sticky="we")
    
        dropdown = CTkOptionMenu(page_frame, values=optionen, command=auswahl_anzeigen)
        dropdown.set(optionen[0])  # Standardwert setzen
        dropdown.grid(row=5, column=0, pady=10, sticky="nswe")
    
    
    
    
    image = get_diagramm(1)
    if image != None:
        # Bild in ein Label einfügen
        image_label = CTkLabel(page_frame, image=image, text="")  # `text=""` entfernt Text neben dem Bild
        image_label.grid(row=6, column=1, padx=0, pady=0, sticky="we")  # Bild in Row 1, Column 2 platzieren

    # Diagramme
    lbl_Vorhersagen = CTkLabel(page_frame, text="Vorhersage Diagramme", text_color="white", font=("Helvetica", 18, "bold"))
    lbl_Vorhersagen.grid(row=5, column=1, pady=10, sticky="nswe")
    
    
    
    # Dropdown-Menü erstellen
    optionen = get_aktien_sell()
    # Funktion, um das Bild basierend auf der Auswahl zu aktualisieren
    def auswahl_anzeigen(file_path):
        if os.path.exists(file_path):
            # Bild laden und skalieren
            img = Image.open(file_path)#.resize((400, 400))
            updated_image = CTkImage(light_image=img, size=(400, 400))
            
            # Bild im Label aktualisieren
            image_label_pic.configure(image=updated_image)
            image_label_pic.image = updated_image  # Referenz halten
        else:
            print("Datei nicht gefunden!")
    if len(optionen) != 0:
    # Initiales Bild setzen
        initial_image_path = optionen[0] if os.path.exists(optionen[0]) else None
        initial_ctk_image = None
        if initial_image_path:
            initial_img = Image.open(initial_image_path) #.resize((400, 400))
            initial_ctk_image = CTkImage(light_image=initial_img, size=(400, 400))

        # Initiales Bild in ein Label einfügen
        image_label_pic = CTkLabel(page_frame, image=initial_ctk_image, text="")
        image_label_pic.grid(row=6, column=2, padx=10, pady=10, sticky="we")
    
        dropdown = CTkOptionMenu(page_frame, values=optionen, command=auswahl_anzeigen)
        dropdown.set(optionen[0])  # Standardwert setzen
        dropdown.grid(row=5, column=2, pady=10, sticky="nswe")

    update_display()
    

    # Zurück-Button zum Dashboard
    btn_back = CTkButton(page_frame, text="Neugenerierung", command=lambda: [del_and_recalc(), build_page(app, frames, root)])
    btn_back.grid(row=7, column=0, columnspan=1, pady=10)

    # Zurück-Button zum Dashboard
    btn_back = CTkButton(page_frame, text="Zurück zum Dashboard", command=lambda: app.show_page('dashboard'))
    btn_back.grid(row=7, column=1, columnspan=2, pady=10)

    page_frame.grid(row=0, column=0, sticky="nsew")
