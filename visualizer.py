import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

# =============================================================================
# Fonction : plot_price_rsi_signals
# Objectif fonctionnel :
#   Afficher un graphique en chandelier du prix, superposer l'indicateur RSI, 
#   sa SMA, ainsi que les signaux d'achat et de vente détectés, puis sauvegarder
#   le graphique sous forme d'image.
# Objectif technique :
#   - Utiliser mplfinance pour visualiser :
#       * Chandeliers OHLC du prix
#       * Courbes RSI et SMA_RSI sur un panneau secondaire
#       * Marqueurs BUY/SELL directement sur le graphique
#   - Sauvegarder le graphique au chemin spécifié avec résolution adaptée
# Entrée :
#   - df (pd.DataFrame) : Doit contenir les colonnes :
#       'open', 'high', 'low', 'close', 'RSI', 'SMA_RSI', 'signal_rsi'
#   - save_path (str, optionnel) : chemin de sauvegarde de l'image (défaut 'rsi.png')
# Sortie :
#   - None (le graphique est sauvegardé sur disque)
# =============================================================================
def plot_price_rsi_signals(df, save_path='rsi.png'):
    # -------------------------------------------------------------------------
    # Étape 1 : Vérification des colonnes requises
    # -------------------------------------------------------------------------
    required_cols = {'open', 'high', 'low', 'close', 'RSI', 'SMA_RSI', 'signal_rsi'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Colonnes manquantes : {missing}")

    df = df.copy()

    # -------------------------------------------------------------------------
    # Étape 2 : Préparation de l'index datetime
    # -------------------------------------------------------------------------
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        if 'datetime' in df.columns:
            df.set_index('datetime', inplace=True)
        else:
            df.index = pd.to_datetime(df.index)

    # -------------------------------------------------------------------------
    # Étape 3 : Création des signaux d'achat et de vente
    # -------------------------------------------------------------------------
    # BUY signal légèrement en dessous du low pour visibilité
    buy_signal = df['low'].where(df['signal_rsi'].isin(['BUY', 'BUY_ALERT'])) * 0.99
    # SELL signal légèrement au-dessus du high pour visibilité
    sell_signal = df['high'].where(df['signal_rsi'].isin(['SELL', 'SELL_ALERT'])) * 1.01

    # -------------------------------------------------------------------------
    # Étape 4 : Création des addplots mplfinance
    # -------------------------------------------------------------------------
    ap_buy = mpf.make_addplot(buy_signal, type='scatter', markersize=50, marker='^', color='green')
    ap_sell = mpf.make_addplot(sell_signal, type='scatter', markersize=50, marker='v', color='red')
    ap_rsi = mpf.make_addplot(df['RSI'], panel=1, color='blue', width=1)
    ap_sma_rsi = mpf.make_addplot(df['SMA_RSI'], panel=1, color='orange', width=1)

    # -------------------------------------------------------------------------
    # Étape 5 : Création du graphique
    # -------------------------------------------------------------------------
    fig, axes = mpf.plot(
        df,
        type='candle',
        addplot=[ap_buy, ap_sell, ap_rsi, ap_sma_rsi],
        figsize=(14, 10),
        panel_ratios=(3, 1),        # Ratio prix / RSI
        title="",
        style='yahoo',
        volume=False,
        returnfig=True,
        datetime_format='%d-%m-%Y',
        xrotation=0,
        warn_too_much_data=10000
    )

    # -------------------------------------------------------------------------
    # Étape 6 : Sauvegarde du graphique
    # -------------------------------------------------------------------------
    fig.savefig(save_path, dpi=150, bbox_inches='tight', pad_inches=0.1)

