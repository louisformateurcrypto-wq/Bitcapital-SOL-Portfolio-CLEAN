import pandas as pd
import numpy as np
import logging
from typing import Optional, Tuple

# Initialisation du logger
logger = logging.getLogger('TradingBot')

# =============================================================================
# Fonction : calculate_rsi
# Objectif fonctionnel :
#   Calculer le RSI (Relative Strength Index) sur la base des cours de clôture.
# Objectif technique :
#   Utiliser les variations journalières des prix pour déterminer les gains et pertes moyens
#   selon une moyenne exponentielle, puis en déduire la valeur du RSI selon la formule standard.
# Entrée :
#   - df (pd.DataFrame) : contient au minimum une colonne 'close' (cours de clôture)
#   - config (dict) : contient la clé 'RSI_PERIOD' (int) représentant la période de calcul
# Sortie :
#   - pd.Series : Série contenant les valeurs du RSI calculé pour chaque ligne du DataFrame
# =============================================================================

def calculate_rsi(df: pd.DataFrame, config: dict) -> pd.Series:
    # Extraction de la période RSI depuis la configuration
    period = config['RSI_PERIOD']

    # -------------------------------------------------------------------------
    # Étape 1 : Calcul de la variation du prix jour par jour
    # La méthode diff() calcule la différence entre le cours de clôture actuel
    # et celui du jour précédent.
    # -------------------------------------------------------------------------
    delta = df['close'].diff()

    # -------------------------------------------------------------------------
    # Étape 2 : Séparation des gains et pertes
    #   - gain : valeurs positives (hausse du prix)
    #   - loss : valeurs négatives (baisse du prix, transformées en positives)
    # -------------------------------------------------------------------------
    gain = delta.clip(lower=0)        # Remplace les valeurs négatives par 0
    loss = -delta.clip(upper=0)       # Inverse les valeurs négatives pour obtenir des pertes positives

    # -------------------------------------------------------------------------
    # Étape 3 : Calcul des moyennes exponentielles des gains et pertes
    # Utilisation d’une moyenne mobile exponentielle (EMA) sur la période définie.
    # ewm() permet de lisser les variations pour obtenir un indicateur plus stable.
    #   - alpha = 1/period : facteur de pondération exponentielle
    #   - min_periods = period : nombre minimal de points avant de produire une valeur
    #   - adjust=False : simplifie le calcul pour des résultats plus rapides et cohérents
    # -------------------------------------------------------------------------
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    # -------------------------------------------------------------------------
    # Étape 4 : Calcul du RSI selon la formule standard
    # RSI = 100 - (100 / (1 + RS)), où RS = avg_gain / avg_loss
    # Plus le RSI est élevé, plus le marché est considéré comme suracheté, et inversement.
    # -------------------------------------------------------------------------
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # -------------------------------------------------------------------------
    # Étape 5 : Journalisation (log)
    # Permet de tracer dans les logs que le calcul du RSI a bien été effectué.
    # -------------------------------------------------------------------------
    logger.info(f"RSI ({period}) calculé")

    # -------------------------------------------------------------------------
    # Étape 6 : Retour du résultat
    # Retourne la série Pandas contenant le RSI calculé pour chaque ligne du DataFrame.
    # -------------------------------------------------------------------------
    return rsi

# =============================================================================
# Fonction : calculate_sma
# Objectif fonctionnel :
#   Calculer la Moyenne Mobile Simple (SMA) d’une série numérique (par exemple, un RSI).
# Objectif technique :
#   Appliquer une fenêtre glissante (rolling window) sur la série afin de calculer
#   la moyenne arithmétique sur un nombre défini de périodes.
# Entrée :
#   - series (pd.Series) : série de valeurs numériques (ex. RSI, prix, volume)
#   - config (dict) : contient la clé 'SMA_ON_RSI_PERIOD' (int) représentant
#                     la taille de la fenêtre de calcul
# Sortie :
#   - pd.Series : Série contenant la SMA calculée pour chaque position valide
# =============================================================================

def calculate_sma(series: pd.Series, config: dict) -> pd.Series:
    # -------------------------------------------------------------------------
    # Étape 1 : Extraction de la période de calcul depuis la configuration
    # Cette valeur définit la taille de la fenêtre glissante utilisée
    # pour calculer la moyenne mobile.
    # -------------------------------------------------------------------------
    period = config['SMA_ON_RSI_PERIOD']

    # -------------------------------------------------------------------------
    # Étape 2 : Journalisation (log)
    # Permet de tracer dans les logs que le calcul de la SMA a été effectué.
    # -------------------------------------------------------------------------
    logger.info(f"SMA ({period}) calculé")

    # -------------------------------------------------------------------------
    # Étape 3 : Calcul de la SMA (Simple Moving Average)
    # rolling(window=period) crée une fenêtre glissante de taille 'period'
    # mean() calcule la moyenne arithmétique des valeurs dans chaque fenêtre.
    # Le résultat est une série alignée sur l’index d’origine.
    # -------------------------------------------------------------------------
    return series.rolling(window=period).mean()



# =================================== Début CODE GPT SMA Prix ==========================================

# =============================================================================
# Fonction : calculate_sma_close
# Objectif fonctionnel :
#   Calculer la SMA sur les prix de clôture (période via config).
# Objectif technique :
#   Appliquer une moyenne glissante sur 'close' avec SMA_CLOSE_PERIOD.
# Entrée :
#   - df (pd.DataFrame) : doit contenir 'close'
#   - config (dict) : contient 'SMA_CLOSE_PERIOD' (int)
# Sortie :
#   - pd.Series : SMA des clôtures
# =============================================================================
def calculate_sma_close(df: pd.DataFrame, config: dict) -> pd.Series:
    period = config.get("SMA_CLOSE_PERIOD", 9)
    sma_close = df["close"].rolling(window=period).mean()
    logger.info(f"SMA_close ({period}) calculée")
    return sma_close

# =================================== Fin CODE GPT SMA Prix ==========================================




# =================================== Début CODE MAXIME STRAT ==========================================

# =============================================================================
# Fonction : detect_rsi_signals
# Objectif fonctionnel :
#   Détecter les signaux d'achat ou de vente basés sur les croisements entre le RSI
#   et sa moyenne mobile simple (SMA_RSI).
# Objectif technique :
#   Parcourir les valeurs successives de RSI et SMA_RSI pour identifier :
#     - un signal haussier ("BUY_ALERT") lorsque le RSI croise la SMA_RSI à la hausse,
#     - un signal baissier ("SELL_ALERT") lorsque le RSI croise la SMA_RSI à la baisse.
# Entrée :
#   - df (pd.DataFrame) : contient au minimum les colonnes 'RSI' et 'SMA_RSI'
# Sortie :
#   - pd.DataFrame : copie du DataFrame d’entrée avec une colonne supplémentaire
#                    'signal_rsi' indiquant les alertes détectées
# =============================================================================

#def detect_rsi_signals(df: pd.DataFrame) -> pd.DataFrame:
    # -------------------------------------------------------------------------
    # Étape 1 : Création d'une copie du DataFrame
    # On évite ainsi toute modification accidentelle du DataFrame original.
    # -------------------------------------------------------------------------
    #data = df.copy()

    # -------------------------------------------------------------------------
    # Étape 2 : Conversion explicite des colonnes RSI et SMA_RSI en format numérique
    # L’option errors='coerce' convertit les valeurs non numériques en NaN
    # pour éviter les erreurs de comparaison lors des calculs.
    # -------------------------------------------------------------------------
    #data['RSI'] = pd.to_numeric(data['RSI'], errors='coerce')
    #data['SMA_RSI'] = pd.to_numeric(data['SMA_RSI'], errors='coerce')

    # -------------------------------------------------------------------------
    # Étape 3 : Initialisation de la colonne signal_rsi
    # Cette colonne contiendra les signaux :
    #   - 'BUY_ALERT'  : croisement haussier du RSI au-dessus de la SMA_RSI
    #   - 'SELL_ALERT' : croisement baissier du RSI en dessous de la SMA_RSI
    #   - None         : aucun signal détecté
    # -------------------------------------------------------------------------
    #data['signal_rsi'] = None

    # -------------------------------------------------------------------------
    # Étape 4 : Parcours des lignes du DataFrame pour détecter les croisements
    # La boucle démarre à l’index 1 car on compare chaque ligne avec la précédente.
    # Pour chaque ligne :
    #   - on récupère RSI et SMA_RSI de la ligne actuelle et de la ligne précédente
    #   - on teste les conditions de croisement
    # -------------------------------------------------------------------------
    #for i in range(1, len(data)):
        # Récupération des valeurs précédentes et actuelles
       # prev_rsi = data.loc[data.index[i - 1], 'RSI']
       # prev_sma = data.loc[data.index[i - 1], 'SMA_RSI']
       # curr_rsi = data.loc[data.index[i], 'RSI']
       # curr_sma = data.loc[data.index[i], 'SMA_RSI']

        # ---------------------------------------------------------------------
        # Détection du croisement haussier :
        # Le RSI passe de sous la SMA_RSI à au-dessus → signal d'achat
        # ---------------------------------------------------------------------
        # if prev_rsi <= prev_sma and curr_rsi > curr_sma:
            # data.at[data.index[i], 'signal_rsi'] = 'BUY_ALERT'

        # ---------------------------------------------------------------------
        # Détection du croisement baissier :
        # Le RSI passe de au-dessus de la SMA_RSI à en dessous → signal de vente
        # ---------------------------------------------------------------------
       # elif prev_rsi >= prev_sma and curr_rsi < curr_sma:
           # data.at[data.index[i], 'signal_rsi'] = 'SELL_ALERT'

    # -------------------------------------------------------------------------
    # Étape 5 : Journalisation (log)
    # Indique que le processus de détection des signaux est terminé.
    # -------------------------------------------------------------------------
    #logger.info("Détection des signaux RSI terminée")

    # -------------------------------------------------------------------------
    # Étape 6 : Retour du DataFrame enrichi
    # On renvoie le DataFrame avec la nouvelle colonne signal_rsi.
    # -------------------------------------------------------------------------
    #return data


# =================================== Fin CODE MAXIME STRAT ==========================================





# =================== Début CODE GPT STRATEGY ================================================
# =================== Début STRAT V1 WEEKLY ================================
# BUY si croisement RSI↑SMA_RSI ET close > SMA_9
# SELL seulement si une position est ouverte

def detect_rsi_signals_strategy_weekly(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    STRAT V1 :
    - BUY quand RSI croise sa SMA_RSI à la hausse ET close > SMA_9
    - SELL uniquement si on est en position quand RSI croise à la baisse
    Fonctionne pour weekly ou daily (SMA_9 doit exister dans df).
    """
    data = df.copy()

    # Casts
    for col in ['RSI', 'SMA_RSI', 'close']:
        data[col] = pd.to_numeric(data.get(col), errors='coerce')

    # Sécurité : calcule SMA_9 si absente
    if 'SMA_9' not in data.columns:
        data['SMA_9'] = calculate_sma_close(data, config)
    data['SMA_9'] = pd.to_numeric(data['SMA_9'], errors='coerce')

    data['signal_rsi'] = None
    in_position = False

    for i in range(1, len(data)):
        idx_prev = data.index[i - 1]
        idx_cur  = data.index[i]

        prev_rsi = data.at[idx_prev, 'RSI']
        prev_sma = data.at[idx_prev, 'SMA_RSI']
        curr_rsi = data.at[idx_cur,  'RSI']
        curr_sma = data.at[idx_cur,  'SMA_RSI']

        if pd.isna(prev_rsi) or pd.isna(prev_sma) or pd.isna(curr_rsi) or pd.isna(curr_sma):
            continue

        # BUY : croisement haussier + filtre prix > SMA_9 et pas déjà en position
        if prev_rsi < prev_sma and curr_rsi > curr_sma:
            if not in_position:
                price_now = data.at[idx_cur, 'close']
                sma9_now  = data.at[idx_cur, 'SMA_9']
                if pd.notna(price_now) and pd.notna(sma9_now) and price_now > sma9_now:
                    data.at[idx_cur, 'signal_rsi'] = 'BUY_ALERT'
                    in_position = True

        # SELL : croisement baissier uniquement si en position
        elif prev_rsi > prev_sma and curr_rsi < curr_sma:
            if in_position:
                data.at[idx_cur, 'signal_rsi'] = 'SELL_ALERT'
                in_position = False

    logger.info("RSI STRAT V1 (BUY filtré par SMA_9, SELL seulement en position).")
    return data


# =================== Fin STRAT V1 WEEKLY ================================



# =================== Fin CODE GPT STRATEGY ================================================






# =============================================================================
# Fonction : extract_signals_html_and_status
# Objectif fonctionnel :
#   Extraire et formater les derniers signaux RSI en vue d’un affichage HTML, 
#   tout en déterminant le statut du signal le plus récent.
# Objectif technique :
#   - Identifier les signaux détectés la veille (J-1)
#   - Déterminer le dernier signal valide (achat/vente)
#   - Construire un tableau HTML affichant les 5 derniers signaux confirmés
# Entrée :
#   - df (pd.DataFrame) : contient au minimum les colonnes suivantes :
#       * 'datetime' (pd.Timestamp) : date et heure du signal
#       * 'signal_rsi' (str) : type de signal ('BUY_ALERT' ou 'SELL_ALERT')
# Sortie :
#   - tuple :
#       * last_alert (str | None) : dernier signal détecté la veille
#       * signal_emoji (str) : icône correspondant au signal (📈, 📉, ⚠)
#       * signal_text (str) : texte descriptif du signal
#       * signal_color (str) : couleur hexadécimale associée au signal
#       * html_signals (str) : tableau HTML contenant les 5 derniers signaux
# =============================================================================

def extract_signals_html_and_status(df: pd.DataFrame, config: dict):
    # -------------------------------------------------------------------------
    # Étape 1 : Définition de la date de référence (veille, J-1)
    # On normalise la date actuelle pour supprimer l'heure, puis on soustrait un jour.
    # -------------------------------------------------------------------------
    yesterday = pd.Timestamp.now().normalize() - pd.Timedelta(days=1)

    # -------------------------------------------------------------------------
    # Étape 2 : Filtrage des signaux datés de la veille uniquement
    # On compare la date (sans l’heure) de chaque entrée à celle de J-1.
    # -------------------------------------------------------------------------
    alerts_yesterday = df[df["datetime"].dt.normalize() == yesterday]

    # -------------------------------------------------------------------------
    # Étape 3 : Identification du dernier signal confirmé parmi ceux de la veille
    # Les signaux considérés sont 'BUY_ALERT' (achat) et 'SELL_ALERT' (vente).
    # -------------------------------------------------------------------------
    alert_row = alerts_yesterday[alerts_yesterday["signal_rsi"].isin(["BUY_ALERT", "SELL_ALERT"])]

    # -------------------------------------------------------------------------
    # Étape 4 : Détermination du dernier signal de la veille
    # Si un signal est trouvé, on en déduit le texte, l’emoji et la couleur associée.
    # Sinon, on indique qu’aucun signal n’a été émis.
    # -------------------------------------------------------------------------
    if not alert_row.empty:
        last_alert = alert_row.iloc[-1]["signal_rsi"]

        if last_alert == "BUY_ALERT":
            signal_emoji = "📈"
            signal_text = "Signal d'achat"
            signal_color = "#00a676"  # Vert
        else:  # SELL_ALERT
            signal_emoji = "📉"
            signal_text = "Signal de vente"
            signal_color = "#d32f2f"  # Rouge
    else:
        # Aucun signal détecté hier
        last_alert = None
        signal_emoji = "⚠"
        signal_text = "Aucun signal"
        signal_color = "#007a8a"  # Bleu neutre

    # -------------------------------------------------------------------------
    # Étape 5 : Extraction des 5 derniers signaux confirmés
    # Tri décroissant sur la date et sélection des 5 plus récents.
    # -------------------------------------------------------------------------
    recent_signals = (
        df[df["signal_rsi"].isin(["BUY_ALERT", "SELL_ALERT"])]
        .sort_values("datetime", ascending=False)
        .head(5)
    )


    # -------------------------------------------------------------------------
    # Étape 6 : Construction du tableau HTML des signaux récents
    # Pour chaque signal weekly :
    #   - on ajoute 7 jours à la date (J+7)
    #   - on affiche l’icône et le texte correspondant
    #   - chaque ligne du tableau est colorée selon le type de signal
    # Pour chaque signal daily :
    #   - on ajoute 1 jours à la date (J+1)
    #   - on affiche l’icône et le texte correspondant
    #   - chaque ligne du tableau est colorée selon le type de signal
    # -------------------------------------------------------------------------
    
def extract_signals_html_and_status(df: pd.DataFrame, config: dict):
    """
    Extraire et formater les signaux RSI pour l'email :
      - Le mail du jour (ex : 31/10) affiche le signal détecté la veille (ex : 30/10)
      - Si aucun signal la veille → "Aucun signal"
      - Inclut aussi un tableau HTML avec les 5 derniers signaux confirmés
    """
    data = df.copy()

    # -------------------------------------------------------------------------
    # Étape 1 : Sécurisation des données
    # -------------------------------------------------------------------------
    if 'datetime' not in data.columns:
        data['datetime'] = pd.NaT
    data['datetime'] = pd.to_datetime(data['datetime'], errors='coerce')

    # -------------------------------------------------------------------------
    # Étape 2 : Identification du signal de la veille (J-1)
    # -------------------------------------------------------------------------
    today = pd.Timestamp.now().normalize()
    yesterday = today - pd.Timedelta(days=1)

    # on prend toutes les lignes du 30/10 entre 00:00 et 23:59
    alerts_yesterday = data[
        (data["datetime"].dt.normalize() == yesterday)
    ]
    alert_row = alerts_yesterday[alerts_yesterday["signal_rsi"].isin(["BUY_ALERT", "SELL_ALERT"])]

    print(f"📅 Vérification des signaux du {yesterday.strftime('%d/%m/%Y')} : {len(alert_row)} trouvé(s)")
    if not alert_row.empty:
        print(alert_row[["datetime", "signal_rsi"]])

    # -------------------------------------------------------------------------
    # Étape 3 : Détermination du dernier signal détecté la veille
    # -------------------------------------------------------------------------
    if not alert_row.empty:
        last_alert = alert_row.iloc[-1]["signal_rsi"]

        if last_alert == "BUY_ALERT":
            signal_emoji = "📈"
            signal_text = "Signal d'achat"
            signal_color = "#00a676"  # Vert
        else:
            signal_emoji = "📉"
            signal_text = "Signal de vente"
            signal_color = "#d32f2f"  # Rouge
    else:
        last_alert = None
        signal_emoji = "⚠"
        signal_text = "Aucun signal"
        signal_color = "#007a8a"  # Bleu neutre

    # -------------------------------------------------------------------------
    # Étape 4 : Extraction des 5 derniers signaux confirmés
    # -------------------------------------------------------------------------
    recent_signals = (
        data[data["signal_rsi"].isin(["BUY_ALERT", "SELL_ALERT"])]
        .sort_values("datetime", ascending=False)
        .head(5)
    )

    # -------------------------------------------------------------------------
    # Étape 5 : Construction du tableau HTML
    # -------------------------------------------------------------------------
    freq = str(config.get("ANALYSIS_FREQUENCY", "daily")).lower()
    delta_days = 7 if freq == "weekly" else 1

    html_signals = ""
    for _, row in recent_signals.iterrows():
        dt = pd.to_datetime(row["datetime"])
        if pd.isna(dt):
            continue

        date_str = (dt + pd.Timedelta(days=delta_days)).strftime("%d/%m/%Y %H:%M")
        sig = row["signal_rsi"]

        if sig == "BUY_ALERT":
            signal_emoji_row = "📈✅"
            signal_text_row = "Le modèle passe en position acheteuse"
            color = "green"
        else:
            signal_emoji_row = "📉✅"
            signal_text_row = "Le modèle passe en position vendeuse"
            color = "red"

        html_signals += (
            f"<tr>"
            f"<td style='padding:8px; border-bottom:1px solid #ddd; text-align:center;'>{date_str}</td>"
            f"<td style='padding:8px; border-bottom:1px solid #ddd; text-align:left; color:{color};'>"
            f"{signal_emoji_row} {signal_text_row}</td>"
            f"</tr>"
        )

    # -------------------------------------------------------------------------
    # Étape 6 : Journalisation
    # -------------------------------------------------------------------------
    logger.info("Export des signaux HTML terminée")

    # -------------------------------------------------------------------------
    # Étape 7 : Retour final
    # -------------------------------------------------------------------------
    return last_alert, signal_emoji, signal_text, signal_color, html_signals
