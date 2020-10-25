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


from premium_functions import connect_add_note_single, just_connect, connect_note_list_profile, connect_list_profile, get_list_of_profiles, retrieve_name, Linkedin_connexion, update_json_file, check_length_msg, how_many_profiles, pending_invit
from premium_filters import location_filter, langue_filter, secteur_filter, degre_filter, ecole_filter
from premium_filters import	niveau_hierarchique_filter, anciennete_poste_actuel_filter, anciennete_entreprise_actuelle_filter
from premium_filters import	fonction_filter, titre_filter, experience, entreprise_filter, effectif_entreprise_filter
from premium_filters import	type_entreprise_filter, validate_research


""" 
Il s'agit de la version que l'on deploiera en production -- D'ou la presence d'une fonction main() afin de l'importer dans le Flask

Il s'agit du script principal du robot qui permet d'envoyer 20 messages par run, en utilisant les filtres
premium. Il est necessaire pour ce script de creer une df a une colonne : 'Personnes', et de le save en format csv,
car le script s'appuiera dessus pour ne pas recontacter les memes personnes

"""

def main(id_, id_linkedin, password_linkedin):

	CONTACTS_JSON = 'Contacts/stats_' + str(id_) + '.json'
	CONTACTS_CSV = 'Contacts/liste_personnes_' + str(id_) + '.csv'
	MESSAGE_FILE_PATH = 'Config/message_personalise_' + str(id_) + '.txt'
	CONFIG_FILTRES = 'Config/filtres_' + str(id_) + '.xlsx'

	"""       		******************		1ere partie		 	******************       		"""


	# Initialisation des fichiers stats
	print(os.path.join(os.path.dirname(__file__),CONTACTS_CSV))
	if path.exists(os.path.join(os.path.dirname(__file__),CONTACTS_CSV)) is False:
		df = pd.DataFrame(columns=['Personnes', 'Links', 'Dates'])
		df.to_csv(os.path.join(os.path.dirname(__file__), CONTACTS_CSV), sep=';') # A verifier si ce ; est le meme pour tous les clients
	else:
		print('Le CSV existe deja')

	if path.exists(os.path.join(os.path.dirname(__file__), CONTACTS_JSON)) is False:
		updated_json = {"Total messages envoyes": 0, "Total envoyes aujourd'hui": 0, 
			"Personnes a contacter pour ce filtre": 0, "Pending invit": 0}
					
		with open(os.path.join(os.path.dirname(__file__), CONTACTS_JSON), 'w') as json_file:
			json.dump(updated_json, json_file)
	else:
		print('Le JSON existe deja')



	# Premiere condition a respecter : message ne depasse pas les 300 caracteres
	msg_length = check_length_msg(MESSAGE_FILE_PATH)
	if msg_length > 300:
		print('Votre message depasse les 300 catacteres')
		sys.exit()


	
	# CONNEXION	
	print('Connexion')
	chrome_options = Options()  
	#chrome_options.add_argument("--headless")  
	#browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,   chrome_options=chrome_options) # Local
	browser = webdriver.Chrome(chrome_options=chrome_options) # AWS
	print('on va se connecter a linkedin')
	browser.get('https://www.linkedin.com/login/us?')
	time.sleep(randrange(1, 3))

	#Cette fonction prend en parametre les identifiants et mdp Linkedin afin de les chercher ds la DB SQLITE
	Linkedin_connexion(browser, id_linkedin, password_linkedin)
	time.sleep(randrange(2, 5))


	# PENDING INVIT
	# On verifie avant tout combien de Pending Invit on a, afin de voir si nous pouvons continuer a agrandir notre reseau
	pendings = pending_invit(browser)
	if pendings > 4900:
		print('ATTENTION, VOTRE NOMBRE DE PENDING INVIT DEPASSE 4900')
		sys.exit()
	else:
		print(pendings, ' pending invit')
	time.sleep(randrange(2, 5))




	"""       		******************		2eme partie		 	******************       		"""


	print('on va acceder aux filtres')

	# Recherche des profils
	# All filters Linkedin Premium
	browser.get('https://www.linkedin.com/sales/search/people?viewAllFilters=true')

	df_filtres = pd.read_excel(os.path.join(os.path.dirname(__file__), CONFIG_FILTRES))
	# FILTRES
	MOTS_CLEFS = df_filtres['MOTS CLÉS'].tolist()[0]
	LOCATION = df_filtres['LOCATION'].tolist()[0]
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

	time.sleep(randrange(5, 8))
	location_filter(browser, LOCATION)
	time.sleep(randrange(2, 4))
	langue_filter(browser, LANGUE)
	time.sleep(randrange(2, 4))
	secteur_filter(browser, SECTEUR)
	time.sleep(randrange(2, 4))
	degre_filter(browser, DEGRE)
	time.sleep(randrange(2, 4))
	ecole_filter(browser, ECOLE)
	time.sleep(randrange(2, 4))
	niveau_hierarchique_filter(browser, HIERARCHIE)
	time.sleep(randrange(2, 4))
	anciennete_poste_actuel_filter(browser, ANCIENNETE_POSTE)
	time.sleep(randrange(2, 4))
	anciennete_entreprise_actuelle_filter(browser, ANCIENNETE_ENTREPRISE)
	time.sleep(randrange(2, 4))
	fonction_filter(browser, FONCTION)
	time.sleep(randrange(2, 4))
	titre_filter(browser, TITRE)
	time.sleep(randrange(2, 4))
	experience(browser, EXPERIENCE)
	time.sleep(randrange(2, 4))
	entreprise_filter(browser, ENTREPRISE)
	time.sleep(randrange(2, 4))
	effectif_entreprise_filter(browser, EFFECTIF)
	time.sleep(randrange(2, 4))
	type_entreprise_filter(browser, TYPE)
	time.sleep(randrange(2, 4))

	print('on a applique les filtres')


	validate_research(browser)
	time.sleep(randrange(3, 6))
	# How many profiles to contact (to scrap) ?
	nb2scrap = how_many_profiles(browser)
	time.sleep(randrange(4, 7))

	""" ---------------------------------- Envoi de messages ---------------------------------- """

	df = pd.read_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';', index_col=None)
	# On visite les profils
	list_of_links = get_list_of_profiles(browser, df)
	today_total = connect_note_list_profile(df, browser, list_of_links, MESSAGE_FILE_PATH, nb2scrap, pendings, CONTACTS_CSV, CONTACTS_JSON)




	
	#TODO

	#faire un script qui permet de verifier les pending invit et reflechir a quand le lancer et ou save les infos
	# verifier si les time sleep sont bien places


