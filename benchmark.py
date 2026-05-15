import logging
logger = logging.getLogger('TradingBot')

# =============================================================================
# Fonction : generate_performance_html_table
# Objectif fonctionnel :
#   Générer un tableau HTML affichant la performance des différentes stratégies de trading.
# Objectif technique :
#   - Parcourir le dictionnaire de résultats fourni
#   - Vérifier la configuration de benchmark (bench_config) pour filtrer les stratégies affichées
#   - Construire un tableau HTML complet avec en-têtes et lignes formatées
# Entrée :
#   - results (dict) : dictionnaire contenant pour chaque stratégie des statistiques :
#       * 'count'        : nombre de trades
#       * 'total_return' : rendement total (float, décimal)
#       * 'avg_return'   : rendement moyen (float, décimal)
#       * 'winners'      : nombre de trades gagnants
#       * 'losers'       : nombre de trades perdants
#   - config (dict, optionnel) : configuration pouvant contenir la clé 'BENCH' dict pour filtrer l'affichage
# Sortie :
#   - str : tableau HTML formaté avec les statistiques des stratégies
# =============================================================================

def generate_performance_html_table(results, config=None):
    # -------------------------------------------------------------------------
    # Étape 1 : Extraction de la configuration de benchmark (filtrage des stratégies)
    # -------------------------------------------------------------------------
    bench_config = {}
    if config and "BENCH" in config:
        bench_config = config["BENCH"]

    # -------------------------------------------------------------------------
    # Étape 2 : Début du tableau HTML avec en-tête
    # Styles CSS intégrés pour uniformité visuelle
    # -------------------------------------------------------------------------
    html = """
    <table style="width:100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size:14px;">
      <thead>
        <tr style="background-color:#b71c1c; color:#fff; text-align:left;">
          <th style="padding:8px; border:1px solid #ddd;">Stratégie</th>
          <th style="padding:8px; border:1px solid #ddd;">Nombre Trades</th>
          <th style="padding:8px; border:1px solid #ddd;">Rendement Total (%)</th>
          <th style="padding:8px; border:1px solid #ddd;">Rendement Moyen (%)</th>
          <th style="padding:8px; border:1px solid #ddd;">Gagnants</th>
          <th style="padding:8px; border:1px solid #ddd;">Perdants</th>
        </tr>
      </thead>
      <tbody>
    """

    # -------------------------------------------------------------------------
    # Étape 3 : Parcours des résultats pour générer les lignes HTML
    # -------------------------------------------------------------------------
    for strategy, stats in results.items():
        # Normalisation de la clé pour correspondre à la configuration de benchmark
        key = strategy.upper().replace("COMBINÉE (RSI+MACD)", "COMBINED").replace(" ", "")

        # Vérification que la stratégie doit être affichée selon bench_config
        if not bench_config or bench_config.get(key, False):
            html += f"""
            <tr style="border-bottom:1px solid #ddd;">
              <td style="padding:8px; border:1px solid #ddd;">{strategy}</td>
              <td style="padding:8px; border:1px solid #ddd; text-align:center;">{stats['count']}</td>
              <td style="padding:8px; border:1px solid #ddd; text-align:right;">{stats['total_return']*100:.2f}</td>
              <td style="padding:8px; border:1px solid #ddd; text-align:right;">{stats['avg_return']*100:.2f}</td>
              <td style="padding:8px; border:1px solid #ddd; text-align:center;">{stats['winners']}</td>
              <td style="padding:8px; border:1px solid #ddd; text-align:center;">{stats['losers']}</td>
            </tr>
            """

    # -------------------------------------------------------------------------
    # Étape 4 : Fermeture du tableau HTML
    # -------------------------------------------------------------------------
    html += """
      </tbody>
    </table>
    """

    # -------------------------------------------------------------------------
    # Étape 5 : Retour du HTML complet
    # -------------------------------------------------------------------------
    return html


# =============================================================================
# Fonction : performance_summary
# Objectif fonctionnel :
#   Générer un résumé de performance pour différentes stratégies de trading
#   à partir d'un DataFrame de données financières.
# Objectif technique :
#   - Filtrer les stratégies à analyser selon la configuration 'BENCH'
#   - Calculer les statistiques de performance pour chaque stratégie :
#       * nombre de trades
#       * rendement total
#       * rendement moyen
#       * nombre de trades gagnants et perdants
# Entrée :
#   - df (pd.DataFrame) : données de marché ou signaux pour backtesting
#   - config (dict, optionnel) : peut contenir la clé 'BENCH' pour filtrer les stratégies
# Sortie :
#   - dict : dictionnaire avec pour chaque stratégie ses statistiques de performance
# =============================================================================

def performance_summary(df, config=None):
    # -------------------------------------------------------------------------
    # Étape 1 : Récupération de la configuration BENCH ou activation par défaut
    # -------------------------------------------------------------------------
    bench_config = {}
    if config and "BENCH" in config:
        bench_config = config["BENCH"]

    # -------------------------------------------------------------------------
    # Étape 2 : Fonction interne pour calculer les statistiques d'une liste de trades
    # -------------------------------------------------------------------------
    def trade_stats(trades):
        count = len(trades)  # nombre total de trades
        import numpy as np
        total_return = np.prod([1 + t for t in trades]) - 1
        
        avg_return = total_return / count if count else 0  # rendement moyen
        winners = len([t for t in trades if t > 0])  # trades gagnants
        losers = len([t for t in trades if t <= 0])  # trades perdants
        return {
            'count': count,
            'total_return': total_return,
            'avg_return': avg_return,
            'winners': winners,
            'losers': losers
        }

    # -------------------------------------------------------------------------
    # Étape 3 : Initialisation du dictionnaire des résultats
    # -------------------------------------------------------------------------
    results = {}

    # -------------------------------------------------------------------------
    # Étape 4 : Calcul conditionnel des backtests selon la configuration
    # -------------------------------------------------------------------------
    if not bench_config.get("RSI", True):
        # Si la stratégie RSI est désactivée, initialiser les statistiques à zéro
        results["RSI"] = {'count': 0, 'total_return': 0, 'avg_return': 0, 'winners': 0, 'losers': 0}
    else:
        # Sinon, exécuter le backtest RSI et calculer les statistiques
        trades_rsi = backtest_rsi(df)
        results["RSI"] = trade_stats(trades_rsi)

    # -------------------------------------------------------------------------
    # Étape 5 : Retour des résultats
    # -------------------------------------------------------------------------
    return results

# =============================================================================
# Fonction : backtest_rsi
# Objectif fonctionnel :
#   Effectuer un backtest basé sur les signaux RSI présents dans la colonne 
#   'signal_rsi' du DataFrame, en prenant en compte les séquences :
#     - Entrée : signal 'BUY_ALERT'
#     - Sortie : signal 'SELL_ALERT'
#   Le rendement de chaque trade est calculé en pourcentage relatif.
# Objectif technique :
#   - Parcourir le DataFrame ligne par ligne
#   - Ouvrir une position lors d'un BUY_ALERT si aucune position n'est ouverte
#   - Fermer la position lors d'un SELL_ALERT et calculer le rendement
#   - Gérer les positions ouvertes à la fin du dataset
# Entrée :
#   - df (pd.DataFrame) : DataFrame contenant au minimum les colonnes :
#       * 'signal_rsi' : signal de trading ('BUY_ALERT' ou 'SELL_ALERT')
#       * 'open'       : prix d'ouverture du trade
#       * 'close'      : prix de clôture (pour fermeture forcée)
# Sortie :
#   - trades (list) : liste des rendements relatifs des trades réalisés
# =============================================================================

def backtest_rsi(df):
    # -------------------------------------------------------------------------
    # Étape 1 : Initialisation
    # - trades : liste pour stocker le rendement de chaque trade
    # - buy_price : prix d'achat en cours (None si pas de position ouverte)
    # -------------------------------------------------------------------------
    trades = []
    buy_price = None

    # -------------------------------------------------------------------------
    # Étape 2 : Parcours du DataFrame (jusqu'à l'avant-dernière ligne)
    # Pour chaque ligne, on regarde le signal et le prix d'ouverture de la semaine suivante
    # -------------------------------------------------------------------------
    for i in range(len(df) - 1):
        signal = df.iloc[i]['signal_rsi']
        next_open = df.iloc[i + 1]['open']  # ouverture du trade suivant

        # ---------------------------------------------------------------------
        # Entrée en position (BUY)
        # Si signal BUY_ALERT et aucune position ouverte, on achète au prix d'ouverture suivant
        # ---------------------------------------------------------------------
        if signal == 'BUY_ALERT' and buy_price is None:
            buy_price = next_open
            logger.info("RSI - Ouverture BUY à %.2f (index %d -> semaine suivante %d)", 
                        buy_price, i, i + 1)

        # ---------------------------------------------------------------------
        # Sortie de position (SELL)
        # Si signal SELL_ALERT et position ouverte, on calcule le rendement et ferme la position
        # ---------------------------------------------------------------------
        elif signal == 'SELL_ALERT' and buy_price is not None:
            sell_price = next_open
            return_pct = (sell_price - buy_price) / buy_price  # rendement relatif
            trades.append(return_pct)
            logger.info("RSI - Fermeture SELL à %.2f (index %d -> semaine suivante %d) - Rendement %.2f%%",
                        sell_price, i, i + 1, return_pct * 100)
            buy_price = None  # réinitialisation de la position

    # -------------------------------------------------------------------------
    # Étape 3 : Gestion des positions ouvertes à la fin du dataset
    # On ferme la position au prix de clôture de la dernière ligne
    # -------------------------------------------------------------------------
    if buy_price is not None:
        last_price = df.iloc[-1]['close']
        return_pct = (last_price - buy_price) / buy_price
        trades.append(return_pct)
        logger.info("RSI - Fermeture forcée à la fin du dataset (prix %.2f) - Rendement %.2f%%",
                    last_price, return_pct * 100)

    # -------------------------------------------------------------------------
    # Étape 4 : Journalisation finale
    # Indique le nombre total de trades détectés et la fin du backtest
    # -------------------------------------------------------------------------
    logger.info("Backtest RSI terminé : %d trades détectés", len(trades))

    # -------------------------------------------------------------------------
    # Étape 5 : Retour de la liste des rendements
    # -------------------------------------------------------------------------
    return trades
