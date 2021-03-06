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

    logger.info("ID = %s --> %s vient de lancer l'algorithme", id_, id_linkedin)
    # Dans le cas ou on a rencontre une erreur lors du run precedent, il faut fermer le browser qui ete ouvert
    try:
        browser.quit()
    except:
        logger.info("Le browser precedent a bien ete ferme")

    CONTACTS_JSON = 'Contacts/stats_' + str(id_) + '.json'
    CONTACTS_CSV = 'Contacts/liste_personnes_' + str(id_) + '.csv'
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
    df = pd.read_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';', index_col=None)
    print(df.head(2))
    # Je check le nbe de messages envoyes aujourd'hui
    today = date.today()
    today_list = df['Dates'].tolist()
    today_list = [date for date in today_list if date==str(today)]
    if len(today_list) >= 20:
        logger.info("C'est fini pour aujourd'hui ... Plus de 20 messages envoyes")
        return render_template('fin_algo_prematuree.html')
    else:
        logger.info("Demarrage d'une nouvelle journee")
        nb2scrap, pendings = '...', '...'
        logger.debug("Update du json")
        premium_functions.update_json_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON)


    """             ******************      1ere partie         ******************              """


    # Premiere condition a respecter : message ne depasse pas les 300 caracteres
    msg_length = premium_functions.check_length_msg(MESSAGE_FILE_PATH)
    if msg_length > 300:
        logging.info('Votre message depasse les 300 catacteres')
        sys.exit()


    # CONNEXION 
    logger.info("Initialisation ChromeDriver")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
      
    #browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,   chrome_options=chrome_options) # Local
    browser = webdriver.Chrome(chrome_options=chrome_options) # AWS
    logger.info('Connexion a Linkedin')
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
        logger.info('On a 2 mn pour rentrer le code dans MySQL')
        time.sleep(randrange(1200, 1800))
        # On doit checker le code recu ds les mails (qu'on aura rentre sur sql)
        logger.info("Cherchons le code dans MySQL")
        connection = pymysql.connect(host='linkedin.c0oaoq9odgfz.eu-west-3.rds.amazonaws.com',
                                 user='root',
                                 password='Leomessi9',
                                 db='linkedin',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            cursor.execute('use linkedin')
            cursor.execute('SELECT security_code FROM linkedin.user WHERE email=%s', id_linkedin)
            security_code = cursor.fetchall()[0]['security_code']
        connection.close()

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

    # Recherche des profils
    # All filters Linkedin Premium
    browser.get('https://www.linkedin.com/sales/search/people?viewAllFilters=true')

    df_filtres = pd.read_excel(os.path.join(os.path.dirname(__file__), CONFIG_FILTRES))
    # FILTRES - on obtient pr chaque filtre une liste avec les input du user
    LOCATION = df_filtres['ZONE GÉOGRAPHIQUE'].tolist()[0]
    LANGUE = df_filtres['LANGUE'].tolist()[0]
    SECTEUR = df_filtres['SECTEUR'].tolist()[0]
    DEGRE = df_filtres['NIVEAU DE RELATION'].tolist()[0]
    ECOLE = df_filtres['ÉCOLE'].tolist()[0]
    HIERARCHIE = df_filtres['HIÉRARCHIE'].tolist()[0]
    ANCIENNETE_POSTE = df_filtres['ANCIENNETÉ DU POSTE'].tolist()[0]
    ANCIENNETE_ENTREPRISE = df_filtres["ANCIENNETÉ D'ENTREPRISE"].tolist()[0]
    FONCTION = df_filtres['FONCTION'].tolist()[0]
    TITRE = df_filtres['TITRE'].tolist()[0]
    EXPERIENCE = df_filtres['EXPERIENCE'].tolist()[0]
    ENTREPRISE = df_filtres['ENTREPRISE'].tolist()[0]
    EFFECTIF = df_filtres['EFFECTIF'].tolist()[0]
    TYPE = df_filtres["TYPE D'ENTREPRISE"].tolist()[0]

    try:
        LANGUE = LANGUE.split(';')
        LANGUE = LANGUE[::-1]
    except:
        LANGUE = [LANGUE]
    try:
        SECTEUR = SECTEUR.split(';')
    except:
        SECTEUR = [SECTEUR]
    try:
        DEGRE = DEGRE.split(';')
        DEGRE = DEGRE[::-1]
    except:
        DEGRE = [DEGRE]
    try:
        ANCIENNETE_ENTREPRISE = ANCIENNETE_ENTREPRISE.split(';')
        ANCIENNETE_ENTREPRISE = ANCIENNETE_ENTREPRISE[::-1]
    except:
        ANCIENNETE_ENTREPRISE = [ANCIENNETE_ENTREPRISE]
    try:
        HIERARCHIE = HIERARCHIE.split(';')
        HIERARCHIE = HIERARCHIE[::-1]
    except:
        HIERARCHIE = [HIERARCHIE]
    try:
        ANCIENNETE_POSTE = ANCIENNETE_POSTE.split(';')
        ANCIENNETE_POSTE = ANCIENNETE_POSTE[::-1]
    except:
        ANCIENNETE_POSTE = [ANCIENNETE_POSTE]
    try:
        FONCTION = FONCTION.split(';')
    except:
        FONCTION = [FONCTION]
    try:
        EXPERIENCE = EXPERIENCE.split(';')
        EXPERIENCE = EXPERIENCE[::-1]
    except:
        EXPERIENCE = [EXPERIENCE]
    try:
        EFFECTIF = EFFECTIF.split(';')
        EFFECTIF = EFFECTIF[::-1]
    except:
        EFFECTIF = [EFFECTIF]
    try:
        TYPE = TYPE.split(';')
        TYPE = TYPE[::-1]
    except:
        TYPE = [TYPE]
    try:
        LOCATION = LOCATION.split(';')
    except:
        LOCATION = [LOCATION]
    try:
        ECOLE = ECOLE.split(';')
    except:
        ECOLE = [ECOLE]
    try:
        TITRE = TITRE.split(';')
    except:
        TITRE = [TITRE]
    try:
        ENTREPRISE = ENTREPRISE.split(';')
    except:
        ENTREPRISE = [ENTREPRISE]

    logger.info("Entrons les filtres")

    time.sleep(randrange(5, 8))
    for location in LOCATION:
        premium_filters.location_filter(browser, location)
        time.sleep(randrange(2, 4))
    for langue in LANGUE:
        premium_filters.langue_filter(browser, langue)
        time.sleep(randrange(2, 4))
    for secteur in SECTEUR:
        premium_filters.secteur_filter(browser, secteur)
        time.sleep(randrange(2, 4))
    for degre in DEGRE:
        premium_filters.degre_filter(browser, degre)
        time.sleep(randrange(2, 4))
    for ecole in ECOLE:
        premium_filters.ecole_filter(browser, ecole)
        time.sleep(randrange(2, 4))
    for hierarchie in HIERARCHIE:
        premium_filters.niveau_hierarchique_filter(browser, hierarchie)
        time.sleep(randrange(2, 4))
    for anciennete_poste in ANCIENNETE_POSTE:
        premium_filters.anciennete_poste_actuel_filter(browser, anciennete_poste)
        time.sleep(randrange(2, 4))
    for anciennete_entreprise in ANCIENNETE_ENTREPRISE:
        premium_filters.anciennete_entreprise_actuelle_filter(browser, anciennete_entreprise)
        time.sleep(randrange(2, 4))
    for fonction in FONCTION:
        premium_filters.fonction_filter(browser, fonction)
        time.sleep(randrange(2, 4))
    for titre in TITRE:
        premium_filters.titre_filter(browser, titre)
        time.sleep(randrange(2, 4))
    for exp in EXPERIENCE:
        premium_filters.experience(browser, exp)
        time.sleep(randrange(2, 4))
    for entreprise in ENTREPRISE:
        premium_filters.entreprise_filter(browser, entreprise)
        time.sleep(randrange(2, 4))
    for effectif in EFFECTIF:
        premium_filters.effectif_entreprise_filter(browser, effectif)
        time.sleep(randrange(2, 4))
    for type_ in TYPE:
        premium_filters.type_entreprise_filter(browser, type_)
        time.sleep(randrange(2, 4))

    logger.info("Filtres appliques")

    premium_filters.validate_research(browser)
    time.sleep(randrange(3, 6))
    # How many profiles to contact (to scrap) ?
    logger.info("Recuperation du nombre de profiles a scrapper")
    nb2scrap = premium_functions.how_many_profiles(browser)
    time.sleep(randrange(4, 7))

    """ ---------------------------------- Envoi de messages ---------------------------------- """

    # On visite les profils
    logger.debug("Recuperation de la liste des profiles")
    list_of_links = premium_functions.get_list_of_profiles(browser, df)

    logger.info("--------------------- Debut des envois de messages ---------------------")
    today_total = premium_functions.connect_note_list_profile(df, browser, list_of_links, MESSAGE_FILE_PATH, nb2scrap, pendings, CONTACTS_CSV, CONTACTS_JSON)
    time.sleep(randrange(3, 6))

    logger.info("----------------------- Cest fini pour aujourd'hui -----------------------")
    browser.quit()

    return render_template('fin_algo.html')




