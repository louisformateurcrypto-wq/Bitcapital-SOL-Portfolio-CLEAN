from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from email.mime.application import MIMEApplication

from benchmark import *
from analysis import *

import smtplib
import pandas as pd
import logging
import os

logger = logging.getLogger('TradingBot')

# =============================================================================
# Fonction : send_email
# Objectif fonctionnel :
#   Envoyer un email HTML formaté contenant :
#     - Les alertes de trading du jour (signaux RSI)
#     - Un résumé des performances de la stratégie
#     - Un historique des derniers signaux d'achat/vente sous forme de tableau HTML
#     - Des graphiques intégrés en images inline (logo, RSI)
#     - Un fichier Excel en pièce jointe si configuré
# Objectif technique :
#   - Extraire les paramètres SMTP, crypto, fréquence et fichiers depuis la configuration
#   - Filtrer les alertes du jour dans le DataFrame de trading
#   - Générer un contenu HTML structuré avec styles inline et images cid
#   - Construire un email multipart MIME (texte + HTML + images inline + éventuelle pièce jointe)
#   - Envoyer l'email via SMTP sécurisé en SSL ou STARTTLS selon le port
#   - Gérer et logger les erreurs ou warnings liées aux fichiers manquants ou échec d'envoi
# Entrée :
#   - df (pd.DataFrame) : DataFrame avec colonnes au minimum 'datetime' et 'signal_rsi'
#   - config (dict) : dictionnaire contenant les clés SMTP, crypto, fréquence, fichiers, etc.
# Sortie :
#   - None (action : envoi d'email, logging des erreurs)
# =============================================================================
def send_email(df: pd.DataFrame, config: dict):
    # -------------------------------------------------------------------------
    # Étape 1 : Extraction des paramètres essentiels depuis config
    # -------------------------------------------------------------------------

    frequency = config['ANALYSIS_FREQUENCY'].upper()

    crypto = config['CRYPTO']

    export = os.getenv('EXPORT')
    sender = os.getenv('SENDER')
    receiver = os.getenv('INTERNES')
    bcc = os.getenv('CLIENTS')
    smtp_server = os.getenv('EMAIL_SERVER')
    smtp_port = int(os.getenv('PORT', 465))
    smtp_password = os.getenv('EMAIL_PASSWORD')
    
    # -------------------------------------------------------------------------
    # Étape 2 : Extraction des signaux et génération des tableaux HTML
    # -------------------------------------------------------------------------
    last_alert, signal_emoji, signal_text, signal_color, html_signals = extract_signals_html_and_status(df, config)
    
    # -- Option d'affichage du tableau de performance
    show_performance = bool(config.get("DISPLAY_PERFORMANCE", True))

    if show_performance:
        result = performance_summary(df, config)
        performance_table_html = generate_performance_html_table(result, config)
    else:
        performance_table_html = ""  # on n'affiche rien et on ne calcule rien


    # -------------------------------------------------------------------------
    # Étape 3 : Construction du corps HTML de l'email
    # -------------------------------------------------------------------------

    # 3.1 Section performances (optionnelle)
    if show_performance:
        performance_section = f"""
                <!-- Résumé performances -->
                <tr>
                  <td style="padding:5px;">
                    <h3 style="background-color:#b71c1c; color:#ffffff; font-size:18px; padding:10px; border-radius:4px; margin:0 0 10px 0;">
                      Résumé des performances
                    </h3>
                    {performance_table_html}
                  </td>
                </tr>
        """
    else:
        performance_section = ""  # rien à insérer

    # 3.2 Corps HTML principal (un seul f-string)
    html_body = f"""  
    <html>
      <head><meta name="viewport" content="width=device-width, initial-scale=1.0"/></head>
      <body style="margin:0; padding:0; font-family: Helvetica, Arial, sans-serif; background:#120101; color:#333;">
        <center>
          <!-- Conteneur principal -->
          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:800px; width:100%; margin:auto; background:#fcfafa; border-radius:6px; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
            <!-- Logo / Image crypto -->
            <tr>
              <td style="padding:5px; text-align:center;">
                <img src="cid:crypto_image" alt="Crypto" width="440" style="display:block; max-width:100%; height:auto; border:none; margin:15px auto 0 auto;"/>
              </td>
            </tr>

            {performance_section}

            <!-- Historique du modèle -->
            <tr>
              <td style="padding:5px;">
                <h3 style="background-color:#b71c1c; color:#ffffff; font-size:18px; padding:10px; border-radius:4px; margin:0 0 10px 0;">
                  Historique du modèle 
                </h3>
                <table width="100%" cellpadding="6" cellspacing="0" border="0" style="border:1px solid #ddd; border-radius:4px; font-size:14px;">
                  <thead>
                    <tr style="background:#b71c1c; color:#fff; text-align:left;">
                      <th style="padding:8px;">Date</th>
                      <th style="padding:8px;">Signal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {html_signals}
                  </tbody>
                </table>
              </td>
            </tr>



            <!-- Footer -->
            <tr>
              <td style="padding:5px; text-align:center; font-size:12px; color:#999;">
                ⚠️ Avertissement important.
Les informations de ce mail sont fournies à titre informatif et éducatif uniquement.
Elles ne constituent ni un conseil en investissement personnalisé, ni une recommandation adaptée à ta situation personnelle.
Tu restes seul responsable des opérations que tu réalises sur tes comptes.<br/>
                &copy; Message généré automatiquement - merci de ne pas répondre.<br/>
                &copy; 2025 Crypto Analysis. Tous droits réservés.
              </td>
            </tr>
          </table>
        </center>
      </body>
    </html>
    """


    # -------------------------------------------------------------------------
    # Étape 4 : Construction du message MIME multipart
    # -------------------------------------------------------------------------
    msg = MIMEMultipart("related")
    msg["Subject"] = f"BITCAPITAL Strat BCM {crypto} ({frequency}) - {signal_text}"
    msg["From"] = formataddr(("BOT BITCAPITAL", sender))
    msg["To"] = receiver

    # Le CCI n'apparaît pas dans l'interface du destinataire
    if bcc:
        msg["Bcc"] = bcc

    # Alternative texte brut + HTML pour clients non HTML
    alternative = MIMEMultipart("alternative")
    text_body = f"Alerte Trading {frequency} ({frequency})\n\n{signal_emoji} Dernier signal détecté : {signal_text}\n\nConsultez les graphiques sur TradingView.\n\nMessage généré automatiquement."
    alternative.attach(MIMEText(text_body, "plain"))
    alternative.attach(MIMEText(html_body, "html"))
    msg.attach(alternative)

    # -------------------------------------------------------------------------
    # Étape 5 : Ajout des images inline (logo et graphique RSI)
    # -------------------------------------------------------------------------
    image_robot_path = os.path.join(os.getcwd(), "crypto.jpeg")
    image_rsi_path = os.path.join(os.getcwd(), "rsi.png")
    try:
        for path, cid in [(image_robot_path, "crypto_image")]:
            with open(path, "rb") as img_file:
                mime_image = MIMEImage(img_file.read())
                mime_image.add_header("Content-ID", f"<{cid}>")
                mime_image.add_header("Content-Disposition", "inline", filename=os.path.basename(path))
                msg.attach(mime_image)
    except FileNotFoundError:
        logger.warning(f"Fichier image introuvable, email envoyé sans image.")

    # -------------------------------------------------------------------------
    # Étape 6 : Ajout du fichier Excel en pièce jointe si configuré
    # -------------------------------------------------------------------------
    # Étape 6 : (Modifié) — Fichier Excel conservé uniquement en interne, non envoyé
    file_path = config["FILE"]["DAILY_EXCEL"] if frequency.lower() == "daily" else config["FILE"]["WEEKLY_EXCEL"]
    if os.path.isfile(file_path):
        logger.info(f"📊 Fichier Excel généré et conservé en interne : {file_path}")
    else:
        logger.warning(f"⚠️ Fichier Excel introuvable localement : {file_path}")


    # -------------------------------------------------------------------------
    # Étape 7 : Envoi de l'email via SMTP sécurisé (SSL ou STARTTLS)
    # -------------------------------------------------------------------------
    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, smtp_password)
                server.send_message(msg)
        logger.info(f"Email envoyé avec succès à {receiver}")
        print(f"📨 Email HTML envoyé avec succès à {receiver}")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {e}")
        print("❌ Échec de l'envoi de l'email :", e)
