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
#from selenium.webdriver.remote.file_detector import UselessFileDetector

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



    """             ******************      1ere partie : ChromeDriver, security, info       ******************              """
    
    # CONNEXION A LINKEDIN
    logger.info("Initialisation ChromeDriver")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-dev-shm-usage')
      
    #browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,   chrome_options=chrome_options) # Local
    browser = webdriver.Chrome(chrome_options=chrome_options) # AWS
    #browser.file_detector = UselessFileDetector()
    logger.info("Connexion a Linkedin")
    browser.get('https://www.linkedin.com/login/us?')
    time.sleep(randrange(1, 3))

    #Cette fonction prend en parametre les identifiants et mdp Linkedin afin de les chercher ds MYSQL
    premium_functions.Linkedin_connexion(browser, id_linkedin, password_linkedin)
    time.sleep(randrange(2, 5))

   
    """ ---------------------------------- Envoie de messages aux NOUVEAUX amis ---------------------------------- """
    #Je dois reouvrir df avant l'envoi des messages pour actualiser ce qui vient d'etre fait (ce qui s'est fait dans les fonctions
    #de premium_functions n'a pas actualise ce qui se passe dans ce fichier-ci)
    df = mysql_functions.MYSQL_id_table_to_df(id_, connexion)    
    time.sleep(randrange(10, 20))
    logger.debug("Debut des envois de messages")
    premium_functions.first_flow_msg(browser, df, MESSAGE_FILE_PATH, id_, connexion)
    logger.info("Fin du flow d'envoi de messages")
    time.sleep(randrange(3, 6))


    logger.info("************************* Cest fini pour aujourd'hui *************************")
    connexion.close()
    browser.quit()

    return render_template('fin_algo.html')




