# Crypto Trading Bot

## Description
Bot d'analyse technique pour les cryptomonnaies basé sur les indicateurs RSI et SMA.  
Il détecte les signaux d'achat/vente, génère des graphiques et envoie automatiquement un email récapitulatif.

## Fonctionnalités
- Récupération des données depuis une API externe
- Calcul des indicateurs RSI et SMA
- Détection de signaux BUY_ALERT / SELL_ALERT
- Backtest et tableau de performance
- Graphiques en chandeliers avec RSI et SMA
- Export CSV et Excel
- Envoi automatique d'email HTML avec graphiques et pièce jointe

## Installation
```bash
git clone <repo_url>
cd crypto_trading_bot
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
