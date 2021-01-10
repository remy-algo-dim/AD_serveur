import os, random, sys, time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
import re
import json
from random import randrange
from datetime import date, datetime, timedelta
import logging
import pymysql.cursors
from selenium.webdriver.remote.remote_connection import LOGGER
import traceback
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


# Logger
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
LOGGER.setLevel(logging.WARNING)



def MYSQL_create_connexion():
    """ Initialisation d'une connexion MYSQL """
    connexion = pymysql.connect(host='linkedin.c0oaoq9odgfz.eu-west-3.rds.amazonaws.com',
                                user='root',
                                password='Leomessi9',
                                db='linkedin',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connexion


def MYSQL_globale_table_to_df(connexion):
    """ Cette fonction permet de chercher les datas dans la table principale
    'user', et de les rendre au format df """
    with connexion.cursor as cursor:
        try:
            cursor.execute("""SELECT * FROM linkedin.user""")
            output = cursor.fetchall()
            df = pd.DataFrame(output)
            return df
        except:
            print("Echec lors de la recupération des datas MYSQL")
            ### Je ne mets pas de sys.exit car cette fonction n'est pas utilisee dans l'algo mais seulement dans l'UI (dashboard)


def MYSQL_id_table_to_df(id_, connexion):
    """ Cette fonction a pour but de chercher les datas dans la table d'un user 
    specifique et la mettre en format pandas dataframe """
    with connexion.cursor() as cursor:
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS user_%s (Personnes varchar(255), Links varchar(255),\
                                        Standard_Link varchar(255), Dates varchar(255), Nombre_messages varchar(255))""", (id_))
            connexion.commit()
            query = cursor.execute("SELECT * FROM linkedin.user_%s", (id_))
            output = cursor.fetchall()
            df = pd.DataFrame(output)
            return df
        except:
            print("Echec lors de la recuperation des datas MYSQL")
            sys.exit()  




def MYSQL_insert_table(id_, connexion, personne, link, standard_link, date, nombre_message):
    """ Cette fonction permet d'inserer dans la table SQL du client, un prospect supplementaire
    afin de savoir les personnes contactees, ajoutees ... """
    logger.info("On insere les données client dans MYSQL")
    with connexion.cursor() as cursor:
        query = "INSERT INTO linkedin.user_" + str(id_) + " (Personnes, Links, Standard_Link, Dates, Nombre_messages) VALUES (" + "'" + str(personne) + "','" + str(link) + "','" + str(standard_link) + "','" + str(date) + "','" + str(nombre_message) + "')"
        try:
            cursor.execute(query)
            connexion.commit()
            logger.debug("Mise a jour de la table SQL reussie")
        except:
            logger.debug("Echec de mise a jour de la table SQL")


def MYSQL_update_table(id_, connexion, column_name, new_column_value):
    """ Cette fonction permet de mettre a jour la table SQL du client,
    en updatant notamment le nombre de messages envoyes a un client """
    logger.info("On update ta table SQL du client")
    with connexion.cursor() as cursor:
        query = "UPDATE linkedin.user SET " + str(column_name) + "=" + "'" + new_column_value + "'" " WHERE id=" + str(id_)
        try:
            cursor.execute(query)
            connexion.commit()
            logger.debug("Mise a jour de la table SQL reussie")
        except:
            logger.debug("Echec de mise a jour de la table SQL")



def MYSQL_code_security_verification(id_, connexion):
    """ Cette fonction a pour but d'aller chercher le code de verif d'un nouvel utilisateur
    etant donne que la premiere utilisation de cet algo sur le cloud necessite une verif """
    with connexion.cursor() as cursor:
        cursor.execute('use linkedin')
        cursor.execute('SELECT security_code FROM linkedin.user WHERE id=%s', id_)
        security_code = cursor.fetchall()[0]['security_code']
        return security_code



def MYSQL_retrieve_last_link(id_, connexion):
    """ Permet de recuperer le dernier lien de recherche avant d'eviter de relancer tous les filtres """
    with connexion.cursor() as cursor:
        try:
            cursor.execute('use linkedin')
            cursor.execute('SELECT last_link_researched FROM linkedin.user WHERE id=%s', id_)
            last_link_researched = cursor.fetchall()[0]['last_link_researched']
            return last_link_researched
        except:
            print("On a pas pu recuperer le last link researched ... ERROR")
            sys.exit()  



