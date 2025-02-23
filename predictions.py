import yfinance as yf
import matplotlib
matplotlib.use("Agg")  # Verwende ein nicht-interaktives Backend
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import threading
import time
from imblearn.under_sampling import RandomUnderSampler
from datetime import timedelta
from math import sqrt
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import os

os.makedirs('data/buy', exist_ok=True)
os.makedirs('data/wait', exist_ok=True)
buy_action = {}

def get_max_min_start_date(stock_symbol):
    # Daten für das Symbol abrufen
    stock = yf.download(stock_symbol)
    # Das erste verfügbare Datum erhalten
    max_start_date = stock.index[0].strftime('%Y-%m-%d')
    min_start_date = stock.index[-1].strftime('%Y-%m-%d')
    return (max_start_date, min_start_date)

def calculate(name, stock_symbol, est, buy_action)->str:
    print(f"running calc of {name}")
    try:
        (start_date, end_date) = get_max_min_start_date(stock_symbol)
        if start_date is None:
            print("Date is None")
            return "Fehler"
    except:
        print("Date is None!!!")
        return "Fehler"
    # Erwartete Daten zwischen Start- und Enddatum erstellen
    # start_date = "2005-04-08"
    # Aktienkursdaten abrufen

    # Aktienkursdaten abrufen
    try:
        stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    except:
        print("Fehler laden yf!!!!")
        return "Fehler"
    stock_data = stock_data.copy()
    stock_data_with_workdays = stock_data.copy()
    # Resample der Daten, um sicherzustellen, dass alle Datenpunkte vorhanden sind

    stock_data = stock_data.resample('D').asfreq()

    # Fehlende Werte mit vorherigem bzw. folgendem Wert auffüllen
    stock_data.fillna(method='ffill', inplace=True)
    stock_data.fillna(method='bfill', inplace=True)

    while stock_data.isnull().any().any():
            stock_data = stock_data.apply(lambda col: col.fillna(method='ffill', limit=1))
            stock_data = stock_data.apply(lambda col: col.fillna(method='bfill', limit=1))

    stock_data.fillna(0, inplace=True)
    stock_data =stock_data.droplevel('Ticker', axis=1)
    
        
    # Parameter
    anzahlTageZuTrainieren = 30  # Anzahl der Tage für das Training

    # Feature Engineering: Historische Aktienkurse als Features und Labels erstellen
    features = stock_data["Close"]  # Nur Close-Werte werden verwendet
    scaler = StandardScaler()

    X_0, y_0 = [], []
    X_1, y_1 = [], []

    # Feature-Vektoren und Zielvariablen erstellen
    halbzeit = int(anzahlTageZuTrainieren / 2)
    for i in range(len(features) - anzahlTageZuTrainieren):
        # Feature-Vektor für die erste Hälfte der Zeitspanne erstellen
        feature_vector = features.iloc[i : i + halbzeit].values.reshape(-1, 1)
        scaled_vector = scaler.fit_transform(feature_vector).flatten()
        
        # Zielvariable: Vergleich der Durchschnittswerte
        future_mean = features.iloc[i + halbzeit : i + anzahlTageZuTrainieren].mean()
        current_mean = features.iloc[i + halbzeit]
        
        if future_mean > current_mean:
            X_1.append(scaled_vector)
            y_1.append(1)
        else:
            X_0.append(scaled_vector)
            y_0.append(0)

    # Klassen ausbalancieren
    minimum_len = min(len(y_0), len(y_1))
    X_0, y_0 = X_0[-minimum_len:], y_0[-minimum_len:]
    X_1, y_1 = X_1[-minimum_len:], y_1[-minimum_len:]

    # Daten kombinieren
    X = X_0 + X_1
    y = y_0 + y_1

    # In DataFrame und Series konvertieren
    X = pd.DataFrame(X)
    y = pd.Series(y)

    # Trainings- und Testdaten aufteilen
    X_train = X.iloc[:-halbzeit]
    y_train = y.iloc[:-halbzeit]

    X_test = X.iloc[-halbzeit:]
    y_test = y.iloc[-halbzeit:]

    # Ergebnisse ausgeben (zur Verifizierung)
    print(f"Trainingsdaten: {X_train.shape}, Testdaten: {X_test.shape}")
    print(f"Klassenverteilung: {y.value_counts().to_dict()}")

    smote = SMOTE(random_state=0)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

    rf_model = RandomForestClassifier(n_estimators=est, oob_score=True, criterion="gini", random_state=0)
    rf_model.fit(X_train_balanced, y_train_balanced)

    y_test_pred = rf_model.predict(X_test)

    mse_steigung = accuracy_score(y_test, y_test_pred)
    # average_error_steigung = sqrt(1 - mse_steigung)

    print("Accuracy:", mse_steigung)

    # train_lost = len(y_train) - len(y_train_balanced)
    # Beispiellisten# Beispiellisten
    # list1 = [0] * (anzahlTageZuTrainieren//2)# + train_lost)
    list2 = y_train.iloc[-halbzeit:]
    list3 = y_test

    # Erstellen eines leeren DataFrame
    merged_list = pd.DataFrame(list2)

    # Listen an den DataFrame anhängen
    # merged_list = pd.concat([merged_list, pd.DataFrame(list2)], ignore_index=True)
    merged_list = pd.concat([merged_list, pd.DataFrame(list3)], ignore_index=True)

    lst_color = []
    wintotal = 0
    winorlose = 0
    prev = -1
    index = 0
    features = features.iloc[-anzahlTageZuTrainieren:]
    print(len(features))
    print(f"len merged_list: {len(merged_list)}")
    # print(f"len nulls: {len(list1)}")
    print(f"len y_train: {len(y_train)}")
    print(f"len y_test: {len(y_test)}")
    print(merged_list)
    for i in merged_list.iloc[:,0]:
        if i == prev:
            lst_color.append("black")
            index+=1
            continue
        elif i == 0:
            wintotal += features.iloc[index] - winorlose
            winorlose = 0
            lst_color.append('red')
        elif i == 1:
            winorlose = features.iloc[index]
            lst_color.append("green")
        prev = i
        index+=1
    if prev == 0:
        buy_or_not = "Warten sinkt"
    elif prev == 1:
        buy_or_not = "Warten steigt"
    if "green" == lst_color[-1]:
        buy_or_not = "Kaufen"
    elif "red" == lst_color[-1]:
        buy_or_not = "Verkaufen"
    # merged_list
    print("I made: ", wintotal, buy_or_not)
    lcolor = pd.Series(lst_color)

    # Erstelle nur eine Figur mit einem einzigen Plot
    fig, axes = plt.subplots(1, 1, figsize=(25, 20))  # 1 Reihe, 1 Spalte
    fig.suptitle(f"Aktie: {name}, Acc: {mse_steigung}, Made: {wintotal}\n Empfehlung: {buy_or_not}", fontsize=20, fontweight='bold')
    
    # Zeitraum von vor X bis Y Monaten
    # anzahlTageZuTrainieren = 30  # Beispielwert
    stock_data_period = features ###.tail(anzahlTageZuTrainieren * 2)  # Beispielsweise 6 Monate an Tagen
    lcolor_period = lcolor#.tail(anzahlTageZuTrainieren * 2)
    print("Stockdata:")
    print(stock_data.tail())
    print("lcolordata:")
    print(lcolor_period.tail())

    # Scatterplot und Linienplot im gleichen Plot
    # axes.scatter(stock_data_period.index, stock_data_period['Close'], color=lcolor_period)
    # axes.plot(stock_data_period.index, stock_data_period['Close'], label='Historische Daten', color='black')
    for i, color in enumerate(lcolor_period):
        if color == 'green':
            axes.scatter(
                stock_data_period.index[i], stock_data_period.iloc[i],
                color='green', s=200, marker='^', label='Anstieg' if i == 0 else ""
            )  # Pfeil nach oben
        elif color == 'red':
            axes.scatter(
                stock_data_period.index[i], stock_data_period.iloc[i],
                color='red', s=200, marker='v', label='Abfall' if i == 0 else ""
            )  # Pfeil nach unten

    axes.plot(
        stock_data_period.index, stock_data_period, 
        label='Historische Daten', color='black', linewidth=2
    )


    # Titel und Achsenbeschriftungen hinzufügen
    axes.set_title(f'Aktienkurs von vor {anzahlTageZuTrainieren * 2 // 30} Monate bis Heute')
    axes.set_xlabel('Datum')
    axes.set_ylabel('Schlusskurs')

    # Legende und Gitternetz hinzufügen
    axes.legend()
    axes.grid(True)

    # Bild speichern
    print(f"Buy or Not Decision: {buy_or_not}")
    print("Aktuelles Arbeitsverzeichnis:", os.getcwd())
    if buy_or_not == "Kaufen" or buy_or_not == "Warten steigt":
        plt.savefig(f'data/buy/{name}_{buy_or_not}.png')
    else:
        plt.savefig(f'data/wait/{name}_{buy_or_not}.png')
    buy_action[name] = buy_or_not
    # plt.show()
    # return buy_or_not

def calculate_aktien()->dict:
    global buy_action 
    est = 500
    threads = []
    # Liste der Namen der Aktien
    names = [
        "Linde", "Nvidia", "Meta Platforms", "Apple", "Microsoft", 
        "Tesla", "Alphabet (Google)", "SAP", "Broadcom", "Amazon", 
        "Boston Scientific", "TSMC", "Salesforce", "Adobe", "Ferrari",
        "Iron Mountain", "Kongsberg Gruppen", "Carl Zeiss Meditec", "MicroStrategy", 
        "Lam Research", "Synopsys", "Spotify", "Monday.com", "Cyberark", "Gubra", 
        "Arista Networks", "Intuitive Surgical", "Charter Communications", "Palo Alto Networks", 
        "Cadence Design Systems", "Berkshire Hathaway", "KLA-Tencor", "GameStop", "RTX Corporation", 
        "Agnico Eagle Mines", "Emerson Electric", "ARM", "Micron Technology", "Amazon.com", 
        "MongoDB A", "Rheinmetall", "E.L.F. Beauty", "Crowdstrike Holdings", "Thales", 
        "AMD", "LVMH Louis Vuitton Moet Hennessy", "Super Micro Computer", "Dell Technologies", 
        "ASM Internation", "Snowflake", "Tokyo Electron", "Applied Materials"
    ]

    # Liste der zugehörigen ISINs
    symbels = [
        "IE000S9YS762", "US67066G1040", "US30303M1027", "US0378331005", "US5949181045", 
        "US88160R1014", "US02079K3059", "DE0007164600", "US11135F1012", "US0231351067", 
        "US1011371077", "US8740391003", "US79466L3024", "US00724F1012", "NL0011585146",
        "US46284V1017", "NO0003043309", "DE0005313704", "US5949724083", 
        "US5128073062", "US8716071076", "LU1778762911", "IL0011762130", "IL0011334468", "DK0062266474", 
        "US0404131064", "US46120E6023", "US16119P1084", "US6974351057", 
        "US1273871087", "US0846707026", "US4824801009", "US36467W1099", "US75513E1010", 
        "CA0084741085", "US2910111044", "US0420682058", "US5951121038", "US0231351067", 
        "US60937P1066", "DE0007030009", "US26856L1035", "US22788C1053", "FR0000121329", 
        "US0079031078", "LVMH", "US86800U3023", "US24703L2025", 
        "NL0000334118", "US8334451098", "JP3571400005", "US0382221051"
    ]

    for i, j in zip(names,symbels):
        print(i)
        thread = threading.Thread(target=calculate, args=(i, j, est, buy_action))
        threads.append(thread)
        thread.start()
        time.sleep(5)
    # Warten, bis alle Threads fertig sind
    for thread in threads:
        thread.join()
    return buy_action 