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
import apply_filter

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
premium. Il est necessaire pour ce script de creer une df a une colonne : 'Personnes', et de le save en format csv,
car le script s'appuiera dessus pour ne pas recontacter les memes personnes

"""

def main(id_, id_linkedin, password_linkedin):

    # Dans le cas ou on a rencontre une erreur lors du run precedent, il faut fermer le browser qui ete ouvert
    logger.info("ID = %s --> %s vient de lancer l'algorithme", id_, id_linkedin)
    try:
        browser.quit()
    except:
        logger.info("Le browser precedent a bien ete ferme")

    CONTACTS_JSON = 'Contacts/stats_' + str(id_) + '.json'  ########### temporaire
    CONTACTS_CSV = 'Contacts/liste_personnes_' + str(id_) + '.csv'########### temporaire
    MESSAGE_FILE_PATH = 'Config/message_personalise_' + str(id_) + '.txt'
    CONFIG_FILTRES = 'Config/filtres_' + str(id_) + '.xlsx'


    # Initialisation des fichiers stats
    if path.exists(os.path.join(os.path.dirname(__file__),CONTACTS_CSV)) is False:
        df = pd.DataFrame(columns=['Personnes', 'Links', 'Standard_Link', 'Dates', 'Nombre messages'])
        df.to_csv(os.path.join(os.path.dirname(__file__), CONTACTS_CSV), sep=';') # A verifier si ce ; est le meme pour tous les clients
    else:
        logger.info("Le CSV existe deja")
    if path.exists(os.path.join(os.path.dirname(__file__), CONTACTS_JSON)) is False:
        updated_json = {"Total connexions envoyees": 0, "Total messages envoyes": 0, "Total connexions envoyees aujourd'hui": 0, 
            "Personnes a contacter pour ce filtre": 0, "Pending invit": 0}
                    
        with open(os.path.join(os.path.dirname(__file__), CONTACTS_JSON), 'w') as json_file:
            json.dump(updated_json, json_file)
    else:
        logger.info("Le JSON existe deja")


    # On evite de relancer le script pour rien si les 20 messages ont deja ete envoyes. Le script se stoppera tout de suite
    df = mysql_functions.MYSQL_id_table_to_df(id_)    
    ###df = pd.read_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';', index_col=None)
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
        logger.debug("Update du json")
        premium_functions.update_json_connect_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON)


    """             ******************      1ere partie         ******************              """
    
    # CONNEXION 
    logger.info("Initialisation ChromeDriver")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
      
    #browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,   chrome_options=chrome_options) # Local
    browser = webdriver.Chrome(chrome_options=chrome_options) # AWS
    logger.info("Connexion a Linkedin")
    browser.get('https://www.linkedin.com/login/us?')
    time.sleep(randrange(1, 3))

    #Cette fonction prend en parametre les identifiants et mdp Linkedin afin de les chercher ds la DB SQLITE
    premium_functions.Linkedin_connexion(browser, id_linkedin, password_linkedin)
    time.sleep(randrange(2, 5))

    # SECURITY VERIFICATION
    try:
        logger.info("Verifions si une verification par mail est necessaire")
        code_content = browser.find_element_by_class_name('form__input--text')
        code_content.click()
        logger.info("On a 2 mn pour rentrer le code dans MySQL")
        time.sleep(randrange(1200, 1800))
        # On doit checker le code recu ds les mails (qu'on aura rentre sur sql)
        logger.info("Cherchons le code dans MySQL")
        security_code = mysql_functions.MYSQL_code_security_verification(id_)
        code_content.send_keys(security_code)
        time.sleep(randrange(2, 4))
        browser.find_element_by_class_name('form__submit').click()
        time.sleep(randrange(2, 4))
        logger.info("Code de securite envoye")
    except:
        logger.info('***** Verification par mail non necessaire *****')



    # PENDING INVIT
    # On verifie avant tout combien de Pending Invit on a, afin de voir si nous pouvons continuer a agrandir notre reseau
    logger.info("Verifions les pending invitations")
    pendings = premium_functions.pending_invit(browser)
    if pendings > 4900:
        logger.info("ATTENTION, VOTRE NOMBRE DE PENDING INVIT DEPASSE 4900")
        sys.exit()
    else:
        logger.info(" %s pending invit", pendings)
    time.sleep(randrange(2, 5))



    """             ******************      2eme partie         ******************              """


    logger.info("Accedons aux filtres")
    # 2 options : soit on entre filtre apres filtre dans le cas d'une nouvelle recherche. Soit on recupere le dernier lien dans MYSQL
    df_filtres = pd.read_excel(os.path.join(os.path.dirname(__file__), CONFIG_FILTRES))
    boolean_new_filters = mysql_functions.MYSQL_is_new_filters(id_)
    if boolean_new_filters == 'YES':
        logger.debug("Il s'agit d'une nouvelle recherche, on entre chaque filtre")
        apply_filter.lets_apply_filter(browser, df_filtres)
        logger.info("Filtres appliques")
        premium_filters.validate_research(browser)
        time.sleep(randrange(3, 6))
    elif boolean_new_filters == 'NO':
        logger.debug("Nous sommes toujours sur la meme recherche, allons plus vite on recuperant le dernier lien")
        last_link_researched = mysql_functions.MYSQL_retrieve_last_link(id_)
        browser.get(last_link_researched)

    # How many profiles to contact (to scrap) ?
    logger.info("Recuperation du nombre de profiles a scrapper")
    nb2scrap = premium_functions.how_many_profiles(browser)
    time.sleep(randrange(4, 7))

    """ ---------------------------------- Demande de connexions ---------------------------------- """

    # On visite les profils
    logger.debug("Recuperation de la liste des profiles")
    list_of_links = premium_functions.get_list_of_profiles(browser, df)

    logger.info("-----------------------------------------------------------------------------------------------")
    logger.info("-----------------------------------------------------------------------------------------------")
    logger.debug("Envoi connexions")
    today_total = premium_functions.connect_list_profile(df, browser, list_of_links, nb2scrap, pendings, CONTACTS_CSV, CONTACTS_JSON)
    logger.info("--- Fin d'envoi des connexions ---")
    logger.info("-----------------------------------------------------------------------------------------------")
    logger.info("-----------------------------------------------------------------------------------------------")

    """ ---------------------------------- Envoie de messages aux NOUVEAUX amis ---------------------------------- """
    #Je dois reouvrir df avant l'envoi des messages pour actualiser ce qui vient d'etre fait (ce qui s'est fait dans les fonctions
    #de premium_functions n'a pas actualise ce qui se passe dans ce fichier-ci)
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';', index_col=None)
    time.sleep(randrange(10, 20))
    logger.debug("Debut des envois de messages")
    premium_functions.first_flow_msg(browser, df, MESSAGE_FILE_PATH, nb2scrap, pendings, CONTACTS_JSON, CONTACTS_CSV)
    logger.info("Fin du flow d'envoi de messages")
    time.sleep(randrange(3, 6))



    """ ------------------------------------ SQL ------------------------------------ """

    mysql_functions.MYSQL_update_table(df, id_)


    logger.info("************************* Cest fini pour aujourd'hui *************************")
    browser.quit()

    return render_template('fin_algo.html')




