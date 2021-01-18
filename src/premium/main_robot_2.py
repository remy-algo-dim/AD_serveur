import os, random, sys, time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
import pandas as pd
import random
import json
from random import randrange
from selenium.webdriver.chrome.options import Options  
from os import path
import pymysql.cursors
import logging
from flask import Flask, render_template
from datetime import date
from selenium.webdriver.remote.remote_connection import LOGGER

import premium_functions
import premium_filters
import mysql_functions
import apply_filters

CHROME_DRIVER_PATH = '/Users/remyadda/Desktop/chromedriver'

# Logger
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
LOGGER.setLevel(logging.WARNING)

""" 
Il s'agit de la version que l'on deploiera en production -- D'ou la presence d'une fonction main() afin de l'importer dans le Flask

Il s'agit du script principal du robot qui permet d'envoyer 20 messages par run, en utilisant les filtres
premium. Il est necessaire pour ce script de creer une df a une colonne : 'Personnes', et de le save sur MYSQL,
car le script s'appuiera dessus pour ne pas recontacter les memes personnes

"""

def main(id_, id_linkedin, password_linkedin):

    # Dans le cas ou il y a eu une erreur lors du run precdt, on ferme le browser qui ete ouvert ainsi que la connexion MYSQL
    logger.info("ID = %s --> %s vient de lancer l'algorithme", id_, id_linkedin)
    try:
        browser.quit()
        logger.info("Fermons avant tout le browser precedent")
    except:
        logger.info("Le browser precedent a bien ete ferme")
    try:
        connexion.close()
        logger.info("Fermons avant tout la connexion precedente")
    except:
        logger.info("La connexion precedente a bien ete fermee")

    # On commencer par ouvrir une connexion MYSQL pour updater en live la DB
    connexion = mysql_functions.MYSQL_create_connexion()

    MESSAGE_FILE_PATH = 'Config/message_personalise_' + str(id_) + '.txt'
    CONFIG_FILTRES = 'Config/filtres_' + str(id_) + '.xlsx'


    # On evite de relancer le script pour rien si les 20 messages ont deja ete envoyes. Le script se stoppera tout de suite
    df = mysql_functions.MYSQL_id_table_to_df(id_, connexion)
    # Dans le cas ou c'est la premiere fois, df est vide, et en la loadant depuis mysql, on ne recoit rien, donc creeons la
    if len(df) == 0:
        df = pd.DataFrame(columns=['Personnes', 'Links', 'Standard_Link', 'Dates', 'Nombre_messages'])
        logger.info("Mazal Tov, Demarrage de la premiere journee")
    # Je check le nbe de messages envoyes aujourd'hui
    today = date.today()
    today_list = df['Dates'].tolist()
    today_list = [date for date in today_list if date==str(today)]
    logger.info("TODAY LISTE : %s", len(today_list))
    if len(today_list) >= 20:
        logger.info("C'est fini pour aujourd'hui ... Plus de 20 messages envoyes")
        return render_template('fin_algo_prematuree.html')
    else:
        logger.info("Demarrage d'une nouvelle journee")
        nb2scrap, pendings = '...', '...'



    """             ******************      1ere partie : ChromeDriver, security, info       ******************              """
    
    # CONNEXION A LINKEDIN
    logger.info("Initialisation ChromeDriver")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
      
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,   chrome_options=chrome_options) # Local
    browser = webdriver.Chrome(chrome_options=chrome_options) # AWS
    logger.info("Connexion a Linkedin")
    browser.get('https://www.linkedin.com/login/us?')
    time.sleep(randrange(1, 3))

    #Cette fonction prend en parametre les identifiants et mdp Linkedin afin de les chercher ds MYSQL
    premium_functions.Linkedin_connexion(browser, id_linkedin, password_linkedin)
    time.sleep(randrange(2, 5))

    # SECURITY VERIFICATION : car linkedin nous demande une verif lors de la premiere connexion sur la VM
    premium_functions.linkedin_security_verification(browser, id_, connexion)

    # PENDING INVIT
    # On verifie avant tout combien de Pending Invit on a, afin de voir si nous pouvons continuer a agrandir notre reseau
    logger.info("Verifions les pending invitations")
    pendings = premium_functions.pending_invit(browser)
    query = "UPDATE linkedin.user SET pending_invit=" + "'" + str(pendings) + "'" " WHERE id=" + str(id_)
    mysql_functions.MYSQL_update_table(connexion, query)
    if pendings > 4900:
        logger.info("ATTENTION, VOTRE NOMBRE DE PENDING INVIT DEPASSE 4900")
        sys.exit()
    else:
        logger.info(" %s pending invit", pendings)
    time.sleep(randrange(2, 5))



    """             ******************      2eme partie : Filtres & Recherche        ******************              """


    logger.info("Accedons aux filtres")
    df_filtres = pd.read_excel(os.path.join(os.path.dirname(__file__), CONFIG_FILTRES))
    # 2 OPTIONS : 
    # - soit on entre filtre apres filtre dans le cas d'une nouvelle recherche.
    # - soit on recupere le dernier lien dans MYSQL
    last_link_researched = mysql_functions.MYSQL_retrieve_last_link(id_, connexion)
    # Nouvelle recherche
    if not last_link_researched:
        # Colonne 'last_link_researched' vide
        logger.debug("Il s'agit d'une nouvelle recherche, on entre chaque filtre manuellement")
        apply_filters.lets_apply_filters(browser, df_filtres)
        logger.info("Filtres appliques")
        premium_filters.validate_research(browser)
        time.sleep(randrange(3, 6))
        # How many profiles to contact (to scrap) ?
        logger.info("Recuperation du nombre de profiles a scrapper")
        nb2scrap = premium_functions.how_many_profiles(browser)
        time.sleep(randrange(4, 7))
    # Recuperation des anciens filtres
    else:
        # Colonne 'last_link_researched' remplie
        logger.debug("Nous sommes toujours sur la meme recherche, allons plus vite on recuperant le dernier lien")
        browser.get(last_link_researched)


    """ ---------------------------------- Demande de connexions ---------------------------------- """

    # On visite les profils
    logger.debug("Recuperation de la liste des profiles")
    list_of_links, last_link = premium_functions.get_list_of_profiles(browser, df)
    # On save le dernier lien visité
    query = "UPDATE linkedin.user SET last_link_researched=" + "'" + last_link + "'" " WHERE id=" + str(id_)
    mysql_functions.MYSQL_update_table(connexion, query)

    logger.info("-----------------------------------------------------------------------------------------------")
    logger.info("-----------------------------------------------------------------------------------------------")
    logger.debug("Envoi connexions")
    today_total = premium_functions.connect_list_profile(df, browser, list_of_links, nb2scrap, pendings, connexion, id_)
    logger.info("--- Fin d'envoi des connexions ---")
    logger.info("-----------------------------------------------------------------------------------------------")
    logger.info("-----------------------------------------------------------------------------------------------")

    """ ---------------------------------- Envoie de messages aux NOUVEAUX amis ---------------------------------- """
    #Je dois reouvrir df avant l'envoi des messages pour actualiser ce qui vient d'etre fait (ce qui s'est fait dans les fonctions
    #de premium_functions n'a pas actualise ce qui se passe dans ce fichier-ci)
    df = mysql_functions.MYSQL_id_table_to_df(id_, connexion)    
    time.sleep(randrange(10, 20))
    logger.debug("Debut des envois de messages")
    premium_functions.first_flow_msg(browser, df, MESSAGE_FILE_PATH, nb2scrap, pendings, id_, connexion)
    logger.info("Fin du flow d'envoi de messages")
    time.sleep(randrange(3, 6))


    logger.info("************************* Cest fini pour aujourd'hui *************************")
    connexion.close()
    browser.quit()

    return render_template('fin_algo.html')




