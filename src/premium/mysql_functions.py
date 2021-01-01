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


def MYSQL_create_connexion():
	""" Initialisation d'une connexion MYSQL """
    connexion = pymysql.connect(host='linkedin.c0oaoq9odgfz.eu-west-3.rds.amazonaws.com',
                                 user='root',
                                 password='Leomessi9',
                                 db='linkedin',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connexion




def MYSQL_update_table(df, id_, CONTACTS_CSV): FONCTION A MODIFIER CAR JE NE VEUX PLUS DU TOUT DE FICHIERS
    """ Cette fonction permet de mettre a jour la table SQL du client,
    afin de savoir les personnes contactees, ajoutees ... """
    logger.info("On update ta table SQL du client")
    connexion = MYSQL_create_connexion()
    try:
        connexion.cursor().execute("CREATE TABLE IF NOT EXISTS linkedin.user_%s (Personnes varchar(255), Links varchar(255)\
                                        Standard_Link varchar(255), Dates varchar(255), Nombre messages varchar(255));", (id_))

        for personne, link, standard_link, date, nombre_message in zip(df.Personnes, df.Links,
                                                                df.Standard_Link, df.Dates, df['Nombre messages']):
            connexion.cursor().execute("INSERT INTO linkedin.user_%s (Personnes, Links, Standard_Link, Dates, Nombre messages\
                                VALUES (%s, %s, %s, %s, %s)", (id_, personne, link, standard_link, date, nombre_message))
            connexion.commit()
            #Suppression du CSV
            os.remove(os.path.join(os.path.dirname(__file__),CONTACTS_CSV))
        connexion.close()
        logger.debug("Mise a jour de la table SQL reussie")
    except:
        logger.debug("Echec de mise a jour de la table SQL")
        connexion.close()



def MYSQL_id_table_to_df(id_):
	""" Cette fonction a pour but de chercher les datas dans la table d'un user 
	specifique et la mettre en format pandas dataframe """
	connexion = MYSQL_create_connexion()
	with connexion.cursor() as cursor:
		try:
		    query = cursor.execute("SELECT * FROM linkedin.user_%s", (id_))
		    output = cursor.fetchall()
		    df = pd.DataFrame(output)
			connexion.close()
		except:
			connexion.close()
	return df


def MYSQL_code_security_verification():
	""" Cette fonction a pour but d'aller chercher le code de verif d'un nouvel utilisateur
	etant donne que la premiere utilisation de cet algo sur le cloud necessite une verif """
	connexion = MYSQL_create_connexion()
    with connexion.cursor() as cursor:
    	try:
	        cursor.execute('use linkedin')
	        cursor.execute('SELECT security_code FROM linkedin.user WHERE email=%s', id_linkedin)
	        security_code = cursor.fetchall()[0]['security_code']
	    	connexion.close()
	    	return security_code
	    except:
	    	connexion.close()
	    	sys.exit()










