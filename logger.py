import logging

# =============================================================================
# Fonction : setup_logger
# Objectif fonctionnel :
#   Configurer et initialiser le logger pour l'application de trading afin de
#   centraliser le suivi et le débogage.
# Objectif technique :
#   - Purger le contenu existant du fichier de log au démarrage
#   - Configurer le niveau de log à INFO
#   - Définir un format standard pour tous les messages de log
#   - Ajouter deux handlers :
#       * FileHandler : écrit les logs dans 'script_trading.log'
#       * StreamHandler : affiche les logs dans la console
#   - Retourner un logger nommé 'TradingBot' pour une utilisation centralisée
# Entrée :
#   - Aucune
# Sortie :
#   - logging.Logger : instance configurée du logger
# =============================================================================
def setup_logger():
    # -------------------------------------------------------------------------
    # Étape 1 : Purge du fichier de log existant au démarrage
    # -------------------------------------------------------------------------
    with open('script_trading.log', 'w'):
        pass  # Efface le contenu du fichier en l'ouvrant en mode écriture

    # -------------------------------------------------------------------------
    # Étape 2 : Configuration globale du système de logging
    # -------------------------------------------------------------------------
    logging.basicConfig(
        level=logging.INFO,  # Niveau minimum pour afficher INFO et supérieur
        format='%(asctime)s - %(levelname)s - %(message)s',  # Format horodaté
        handlers=[
            logging.FileHandler('script_trading.log'),  # Log vers fichier
            logging.StreamHandler()                      # Log vers console
        ]
    )

    # -------------------------------------------------------------------------
    # Étape 3 : Retour du logger nommé 'TradingBot'
    # -------------------------------------------------------------------------
    return logging.getLogger('TradingBot')

