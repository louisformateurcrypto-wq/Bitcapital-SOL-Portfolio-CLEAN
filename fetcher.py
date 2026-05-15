import os
import requests
import json
import logging
import pandas as pd
from analysis import *

logger = logging.getLogger('TradingBot')


# =============================================================================
# Fonction : fetch_data
# Objectif fonctionnel :
#   Récupérer les données de marché historiques depuis une API externe selon
#   la configuration spécifiée.
# Objectif technique :
#   - Déterminer l’URL et les paramètres de la requête selon la crypto, devise,
#     fréquence et limite de données
#   - Faire la requête HTTP GET et vérifier le statut
#   - Extraire les données JSON et créer un DataFrame Pandas
#   - Convertir les timestamps en datetime, filtrer et renommer les colonnes
#   - Trier les données par date croissante
# Entrée :
#   - config (dict) : dictionnaire contenant au minimum les clés suivantes :
#       * 'CRYPTO', 'CURRENCY', 'FETCH_LIMIT', 'ANALYSIS_FREQUENCY',
#         'URL_MAP', 'INCLUDE_VOLUME'
# Sortie :
#   - pd.DataFrame : DataFrame contenant les colonnes essentielles :
#       * 'datetime', 'open', 'high', 'low', 'close' [, 'volume' si inclus]
# =============================================================================
def fetch_data(config: dict) -> pd.DataFrame:
    crypto = config['CRYPTO']
    currency = config['CURRENCY']
    limit = config['FETCH_LIMIT']
    frequency = config['ANALYSIS_FREQUENCY']

    # -------------------------------------------------------------------------
    # Étape 1 : Sélection de l'URL selon la fréquence demandée
    # -------------------------------------------------------------------------
    if frequency == "daily":
        url_map = config["URL_MAP"]["daily"]
    elif frequency == "weekly":
        url_map = config["URL_MAP"]["weekly"]
    else:
        url_map = config["URL_MAP"]["hourly"]

    url = url_map

    # -------------------------------------------------------------------------
    # Étape 2 : Paramètres de la requête API
    # -------------------------------------------------------------------------
    params = {"fsym": crypto, "tsym": currency, "limit": limit}
    response = requests.get(url, params=params)
    response.raise_for_status()  # Lève une erreur si statut HTTP != 200

    # -------------------------------------------------------------------------
    # Étape 3 : Extraction des données de la réponse JSON
    # -------------------------------------------------------------------------
    data = response.json()["Data"]["Data"]

    # -------------------------------------------------------------------------
    # Étape 4 : Création du DataFrame pandas
    # -------------------------------------------------------------------------
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["time"], unit="s")  # Conversion timestamp

    # -------------------------------------------------------------------------
    # Étape 5 : Sélection et renommage des colonnes
    # -------------------------------------------------------------------------
    columns = ["datetime", "open", "high", "low", "close"]
    if config["INCLUDE_VOLUME"]:
        columns.append("volumeto")
    df = df[columns]
    if config["INCLUDE_VOLUME"]:
        df.rename(columns={"volumeto": "volume"}, inplace=True)

    # -------------------------------------------------------------------------
    # Étape 6 : Tri chronologique croissant
    # -------------------------------------------------------------------------
    df.sort_values("datetime", inplace=True)

    # -------------------------------------------------------------------------
    # Étape 7 : Log de suivi
    # -------------------------------------------------------------------------
    logger.info(
        f"Récupération des données pour :\n"
        f"- Crypto ({crypto}) en ({currency})\n"
        f"- Limite de ({limit})\n"
        f"- Période de ({frequency})"
    )

    return df

# =============================================================================
# Fonction : generate_weekly_data
# Objectif fonctionnel :
#   Agréger les données journalières en données hebdomadaires et calculer
#   les indicateurs techniques RSI et SMA sur RSI.
# Objectif technique :
#   - Utiliser un regroupement temporel hebdomadaire (resample) sur la colonne 'datetime'
#   - Agréger les colonnes standard selon les règles financières :
#       * 'open'  : premier prix de la semaine
#       * 'high'  : prix le plus haut
#       * 'low'   : prix le plus bas
#       * 'close' : dernier prix de la semaine
#       * 'volume': somme hebdomadaire (si inclus et présent)
#   - Calculer RSI sur la série hebdomadaire
#   - Calculer SMA du RSI pour lisser la série
# Entrée :
#   - df_daily (pd.DataFrame) : DataFrame avec colonnes journalières standards
#   - config (dict) : dictionnaire contenant au minimum :
#       * 'INCLUDE_VOLUME', paramètres RSI/SMA
# Sortie :
#   - pd.DataFrame : DataFrame hebdomadaire enrichi avec colonnes 'RSI' et 'SMA_RSI'
# =============================================================================
def generate_weekly_data(df_daily: pd.DataFrame, config: dict) -> pd.DataFrame:
    # -------------------------------------------------------------------------
    # Étape 1 : Définir les règles d'agrégation pour le regroupement hebdomadaire
    # -------------------------------------------------------------------------
    agg_dict = {
        "open": "first",  # premier prix de la semaine
        "high": "max",    # plus haut de la semaine
        "low": "min",     # plus bas de la semaine
        "close": "last"   # dernier prix de la semaine
    }

    # Agrégation du volume si configuré et présent
    if config.get("INCLUDE_VOLUME", False) and "volume" in df_daily.columns:
        agg_dict["volume"] = "sum"

    # -------------------------------------------------------------------------
    # Étape 2 : Regroupement hebdomadaire (semaine commençant lundi)
    # -------------------------------------------------------------------------
    df_weekly = (
        df_daily
        .set_index("datetime")
        .resample("W-MON", label="left", closed="left")
        .agg(agg_dict)
        .dropna()
        .reset_index()
    )

    # -------------------------------------------------------------------------
    # Étape 3 : Calcul des indicateurs techniques
    # -------------------------------------------------------------------------
    df_weekly["RSI"] = calculate_rsi(df_weekly, config)              # RSI
    df_weekly["SMA_RSI"] = calculate_sma(df_weekly["RSI"], config)   # SMA sur RSI

    # -------------------------------------------------------------------------
    # Étape 4 : Retour du DataFrame hebdomadaire enrichi
    # -------------------------------------------------------------------------
    return df_weekly