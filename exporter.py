import pandas as pd
import logging

logger = logging.getLogger('TradingBot')

# =============================================================================
# Fonction : export_to_csv
# Objectif fonctionnel :
#   Exporter les données traitées vers un fichier CSV en fonction de la fréquence
#   d'analyse spécifiée ('daily' ou 'weekly').
# Objectif technique :
#   - Déterminer la fréquence d'analyse à partir de la configuration
#   - Sélectionner le chemin de fichier CSV approprié
#   - Convertir les données en DataFrame Pandas si nécessaire
#   - Exporter la DataFrame au format CSV sans inclure l'index
#   - Loguer l'opération pour suivi
# Entrée :
#   - data : données à exporter (pd.DataFrame ou objet convertible en DataFrame)
#   - config (dict) : configuration contenant au minimum :
#       * 'ANALYSIS_FREQUENCY' : 'daily' ou 'weekly'
#       * 'FILE' : dictionnaire avec chemins CSV ('DAILY_CSV', 'WEEKLY_CSV')
# Sortie :
#   - Aucun retour (action : écriture du fichier CSV)
# =============================================================================

def export_to_csv(data, config: dict):
    # -------------------------------------------------------------------------
    # Étape 1 : Récupération de la fréquence d'analyse
    # -------------------------------------------------------------------------
    frequency = config['ANALYSIS_FREQUENCY']

    # -------------------------------------------------------------------------
    # Étape 2 : Détermination du fichier CSV cible selon la fréquence
    # -------------------------------------------------------------------------
    if frequency == "daily":
        base_file = config['FILE']['DAILY_CSV']  # Exemple : "crypto_data_daily.csv"
    else:
        base_file = config['FILE']['WEEKLY_CSV']  # Exemple : "crypto_data_weekly.csv"

    # -------------------------------------------------------------------------
    # Étape 3 : Conversion en DataFrame Pandas si nécessaire
    # -------------------------------------------------------------------------
    df = pd.DataFrame(data)

    # -------------------------------------------------------------------------
    # Étape 4 : Export vers CSV sans inclure l'index
    # -------------------------------------------------------------------------
    df.to_csv(base_file, index=False)

    # -------------------------------------------------------------------------
    # Étape 5 : Journalisation (log)
    # -------------------------------------------------------------------------
    logger.info(f"Données exportées vers {base_file}")

# =============================================================================
# Fonction : export_to_excel
# Objectif fonctionnel :
#   Exporter les données traitées vers un fichier Excel en fonction de la fréquence
#   d'analyse spécifiée ('daily' ou 'weekly').
# Objectif technique :
#   - Déterminer la fréquence d'analyse à partir de la configuration
#   - Sélectionner le fichier Excel et le nom de la feuille appropriés
#   - Convertir les données en DataFrame Pandas si nécessaire
#   - Exporter la DataFrame vers Excel sans inclure l'index
#   - Loguer l'opération pour suivi
# Entrée :
#   - data : données à exporter (pd.DataFrame ou objet convertible en DataFrame)
#   - config (dict) : configuration contenant au minimum :
#       * 'ANALYSIS_FREQUENCY' : 'daily' ou 'weekly'
#       * 'FILE' : dictionnaire avec chemins Excel ('DAILY_EXCEL', 'WEEKLY_EXCEL')
# Sortie :
#   - Aucun retour (action : écriture du fichier Excel)
# =============================================================================

def export_to_excel(data, config: dict):
    # -------------------------------------------------------------------------
    # Étape 1 : Récupération de la fréquence d'analyse
    # -------------------------------------------------------------------------
    frequency = config['ANALYSIS_FREQUENCY']

    # -------------------------------------------------------------------------
    # Étape 2 : Détermination du fichier Excel cible et du nom de la feuille
    # -------------------------------------------------------------------------
    if frequency == "daily":
        base_file = config['FILE']['DAILY_EXCEL']  # Exemple : "crypto_data_daily.xlsx"
        sheet_name = "Données Daily"
    else:
        base_file = config['FILE']['WEEKLY_EXCEL']  # Exemple : "crypto_data_weekly.xlsx"
        sheet_name = "Données Weekly"

    # -------------------------------------------------------------------------
    # Étape 3 : Conversion en DataFrame Pandas si nécessaire
    # -------------------------------------------------------------------------
    df = pd.DataFrame(data)

    # -------------------------------------------------------------------------
    # Étape 4 : Export vers Excel sans inclure l'index et avec nom de feuille
    # -------------------------------------------------------------------------
    df.to_excel(base_file, index=False, sheet_name=sheet_name)

    # -------------------------------------------------------------------------
    # Étape 5 : Journalisation (log)
    # -------------------------------------------------------------------------
    logger.info(f"Données exportées vers {base_file}")
