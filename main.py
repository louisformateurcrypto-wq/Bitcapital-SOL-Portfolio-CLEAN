import json
import logging
import os

from dotenv import load_dotenv

#from analysis import *
from analysis import calculate_rsi, calculate_sma, calculate_sma_close, detect_rsi_signals_strategy_weekly
from benchmark import *
from fetcher import *
from visualizer import *
from exporter import *
from notifier import *
from logger import *

# =============================================================================
# Fonction : load_config
# Objectif fonctionnel :
#   Charger les paramètres de configuration depuis un fichier JSON externe
#   afin de les rendre accessibles dans l'application.
# Objectif technique :
#   - Ouvrir le fichier 'config.json' en lecture
#   - Charger son contenu avec json.load() pour obtenir un dictionnaire Python
#   - Charger les variables d'environnement depuis 'config.env'
#   - Remplacer les valeurs sensibles dans la configuration par les variables d'environnement
# Entrée :
#   - Aucune
# Sortie :
#   - dict : dictionnaire contenant les paramètres de configuration
# =============================================================================

def load_config():
    # -------------------------------------------------------------------------
    # Étape 1 : Ouverture du fichier 'config.json' en mode lecture
    # -------------------------------------------------------------------------
    with open('config.json', 'r') as f:
        # ---------------------------------------------------------------------
        # Étape 2 : Chargement du contenu JSON en dictionnaire Python
        # La fonction json.load() convertit le JSON en dict, list, etc.
        # ---------------------------------------------------------------------
        config = json.load(f)

    # -------------------------------------------------------------------------
    # Étape 2 : Chargement des variables d'environnement depuis 'config.env'
    # -------------------------------------------------------------------------
    load_dotenv('config.env')

    # -------------------------------------------------------------------------
    # Étape 3 : Remplacer les valeurs sensibles par les variables d'environnement
    # - EMAIL_PASSWORD, SENDER, EMAIL_SERVER, CLIENTS, INTERNES
    # - Si la variable d'environnement n'existe pas, conserver la valeur du JSON
    # -------------------------------------------------------------------------
    if 'EMAIL' in config:
        config['EMAIL']['PASSWORD'] = os.getenv('EMAIL_PASSWORD', config['EMAIL'].get('PASSWORD', ''))
        config['EMAIL']['SENDER'] = os.getenv('SENDER', config['EMAIL'].get('SENDER', ''))
        config['EMAIL']['SERVER'] = os.getenv('EMAIL_SERVER', config['EMAIL'].get('SERVER', ''))
        config['EMAIL']['CLIENTS'] = os.getenv('CLIENTS', config['EMAIL'].get('CLIENTS', ''))
        config['EMAIL']['INTERNES'] = os.getenv('INTERNES', config['EMAIL'].get('INTERNES', ''))
    
    return config

# =============================================================================
# Fonction : main
# Objectif fonctionnel :
#   Point d'entrée principal de l'application pour l'analyse de données financières.
#   Orchestration complète du processus :
#     - Chargement de la configuration
#     - Récupération des données de marché
#     - Agrégation journalière → hebdomadaire si fréquence hebdomadaire
#     - Calcul des indicateurs techniques (RSI, SMA)
#     - Détection des signaux de trading (RSI/SMA)
#     - Visualisation graphique des données et signaux
#     - Export des résultats vers Excel
#     - Envoi de synthèses par email
# Objectif technique :
#   Déterminer le flux de traitement selon la fréquence d'analyse définie ('weekly' ou quotidienne),
#   appliquer les transformations et analyses appropriées, et logger toutes les étapes.
# Entrée :
#   - Aucune (fonction exécutable directement)
# Sortie :
#   - Aucune (produit des fichiers Excel, graphiques et emails selon la configuration)
# =============================================================================

def main():
    # -------------------------------------------------------------------------
    # Étape 1 : Initialisation du logger
    # Utilisation d'une configuration personnalisée pour tracer l'exécution.
    # -------------------------------------------------------------------------
    logger = setup_logger()
    logger.info("==========================================================================================")
    logger.info("Démarrage du programme")

    # -------------------------------------------------------------------------
    # Étape 2 : Chargement des paramètres depuis config.json
    # -------------------------------------------------------------------------
    config = load_config()
    
    # -------------------------------------------------------------------------
    # Étape 3 : Récupération de la fréquence d'analyse définie dans la configuration
    # -------------------------------------------------------------------------
    frequency = config['ANALYSIS_FREQUENCY']



    #==================== Début code GPT ====================================
        
    # -------------------------------------------------------------------------
    # Étape 4 : Flux d'analyse selon la fréquence
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # Étape 4 : Flux d'analyse (WEEKLY uniquement)
    # -------------------------------------------------------------------------
    if frequency == "weekly":
        # 1) Données brutes
        data = fetch_data(config)
        df_data_daily = data.copy()

        # 2) Agrégation journalière → hebdomadaire
        df_data_weekly = generate_weekly_data(df_data_daily, config)

        # 3) RSI & SMA_RSI (si absents)
        if "RSI" not in df_data_weekly.columns:
            df_data_weekly["RSI"] = calculate_rsi(df_data_weekly, config)
        if "SMA_RSI" not in df_data_weekly.columns:
            df_data_weekly["SMA_RSI"] = calculate_sma(df_data_weekly["RSI"], config)

        # 4) SMA 9 (hebdo) du prix
        df_data_weekly["SMA_9"] = calculate_sma_close(df_data_weekly, config)

        # 5) STRAT V1 WEEKLY : BUY si close>SMA_9 & RSI↑SMA_RSI ; SELL si en position
        df_data_weekly = detect_rsi_signals_strategy_weekly(df_data_weekly, config)

        # 6) (optionnel) MACD si tu veux aussi l’avoir
        # df_data_weekly = calculate_macd(df_data_weekly, config)
        # df_data_weekly = detect_macd_signals(df_data_weekly)

        # 7) Graphs / export / email
        plot_price_rsi_signals(df_data_weekly, save_path='rsi.png')
        export_to_excel(df_data_weekly, config)
        send_email(df_data_weekly, config)
    
    else:
        # -------------------------------------------------------------------------
        # Cas d’analyse quotidienne (DAILY)
        # -------------------------------------------------------------------------
        logger.info("Mode DAILY activé")

        # 1) Récupération des données brutes journalières
        data = fetch_data(config)
        df_data_daily = data.copy()

        # 1b) Exclure la bougie du jour (pas encore clôturée à 00:00 UTC)
        today_utc = pd.Timestamp.today().normalize()
        df_data_daily = df_data_daily[df_data_daily['datetime'] < today_utc]

        # 2) Calcul des indicateurs RSI et SMA_RSI
        df_data_daily["RSI"] = calculate_rsi(df_data_daily, config)
        df_data_daily["SMA_RSI"] = calculate_sma(df_data_daily["RSI"], config)

        # 3) Calcul de la SMA_9 (sur le prix de clôture)
        df_data_daily["SMA_9"] = calculate_sma_close(df_data_daily, config)

        # 4) Application de la stratégie RSI/SMA_9 (version journalière)
        df_data_daily = detect_rsi_signals_strategy_weekly(df_data_daily, config)
        # ⚠️ Oui, on peut réutiliser la même fonction, elle marche aussi pour le daily.
        # Si tu veux, on peut la renommer detect_rsi_signals_strategy_daily pour plus de clarté.

        # 5) (Optionnel) Calcul du MACD
        # df_data_daily = calculate_macd(df_data_daily, config)
        # df_data_daily = detect_macd_signals(df_data_daily)

        # 6) Visualisation graphique (RSI + prix)
        plot_price_rsi_signals(df_data_daily, save_path='rsi.png')
        # plot_macd_signals(df_data_daily, save_path='macd.png')  # seulement si MACD calculé

        # 7) Export vers Excel
        export_to_excel(df_data_daily, config)

        # 8) Envoi du rapport par email
        send_email(df_data_daily, config)


    #==================== Fin code GPT ====================================



    
#==================== Début code Maxime ====================================
    # -------------------------------------------------------------------------
    # Étape 4 : Flux d'analyse selon la fréquence
    # -------------------------------------------------------------------------

    
    # --- Cas d’analyse hebdomadaire ---
#    if frequency == "weekly":
#        # Récupération des données brutes
#        data = fetch_data(config)
#        df_data_daily = data.copy()
#
#        # Agrégation journalière → hebdomadaire
#        df_data_weekly = generate_weekly_data(df_data_daily, config)
#        
#        # SMA 9 (hebdo) via analysis.py
#        df_data_weekly["SMA_9"] = calculate_sma_close(df_data_weekly, config)
#
#        # Détection des signaux RSI/SMA sur données hebdomadaires
#        df_data_weekly = detect_rsi_signals(df_data_weekly)
#
#        # Visualisation graphique (chandeliers + RSI/SMA)
#        plot_price_rsi_signals(df_data_weekly, save_path='rsi.png')
#
#        # Export des résultats vers Excel
#        export_to_excel(df_data_weekly, config)
#
#        # Envoi de la synthèse par email
#        send_email(df_data_weekly, config)
        

#    # --- Cas d’analyse quotidienne (par défaut) ---
#    else:
#        # Récupération des données brutes
#        data = fetch_data(config)
#        df_data_daily = data.copy()
#
#        # Calcul des indicateurs techniques
#        df_data_daily["RSI"] = calculate_rsi(df_data_daily, config)
#        df_data_daily["SMA_RSI"] = calculate_sma(df_data_daily["RSI"], config)
#
#        # Détection des signaux RSI/SMA
#        df_data_daily = detect_rsi_signals(df_data_daily)
#
#        # Visualisation graphique (chandeliers + RSI/SMA)
#        plot_price_rsi_signals(df_data_daily, save_path='rsi.png')
#
#        # Export des résultats vers Excel
#        export_to_excel(df_data_daily, config)
#
#        # Envoi de la synthèse par email
#        send_email(df_data_daily, config)
        
#==================== Fin code Maxime ====================================    
        
        

    # -------------------------------------------------------------------------
    # Étape 5 : Fin du programme
    # -------------------------------------------------------------------------
    logger.info("Programme terminé")
    logger.info("==========================================================================================")

# -------------------------------------------------------------------------
# Point d'entrée du script
# -------------------------------------------------------------------------
if __name__ == "__main__":
    main()
