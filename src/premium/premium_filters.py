import os, random, sys, time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from random import randrange


""" Ce script presente tous les filtres presents sur Sales Navigator """


def location_filter(browser, X):
	""" Filtre geolocalisation """			 		 
	location = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[4]/div/div/div[1]/div/button')
	location.click()
	time.sleep(randrange(2, 5))
	# Attention, voir titre_filter fonction      		
	location_content_place = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[4]/div/div/div[2]/input')
	location_content_place.click()
	try:
		location_content_place.send_keys(X)
		# FIRST SUGGESTION
		time.sleep(randrange(1, 4))
		browser.find_element_by_class_name('link-without-visited-state').click()
	except:
		pass

def langue_filter(browser, X):
	""" Permet de choisir entre Anglais et Francais dans la langue du profil """
	langue = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[8]/div/div/div/div')
	langue.click()
	time.sleep(randrange(2, 5))
	# Possibilites
	# 1 anglais
	try:
		if X == 'Anglais':
			anglais = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[8]/div/div/div[2]/ol/li[2]/button')
			anglais.click()
		# 2 francais
		if X == 'Français':
			francais = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[8]/div/div/div[2]/ol/li[6]/button')
			francais.click()
	except:
		print('Seuls les profils anlais et francais sont pertinents pour le moment')
		pass

### TODO :ATTENTION POUR CETTE FONCTION, IL EXISTE AUSSI UNE LONGUE LISTE DE POSSIBILITES
def secteur_filter(browser, X):
	""" On choisi le secteur """
	secteur = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[6]/div/div/div/div')
	secteur.click()
	time.sleep(randrange(2, 5))
	input_secteur = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[6]/div/div/div[2]/input')
	input_secteur.click()
	time.sleep(randrange(2, 5))
	try:
		input_secteur.send_keys(X)
		# FIRST SUGGESTION
		time.sleep(randrange(1, 4))
		browser.find_element_by_class_name('link-without-visited-state').click()
	except:
		pass

def degre_filter(browser, X):
	""" Permet de choisir le degre de relation entre 1, 2 ou 3 """
	degre = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[5]/div/div/div/div')
	degre.click()
	time.sleep(randrange(2, 5))
	# POSSIBILITES
	if X == 'Relations de 1er niveau':
		degre_1 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[5]/div/div/div[2]/ol/li[1]/button')
		degre_1.click()
	if X == 'Relations de 2e niveau':
		degre_2 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[5]/div/div/div[2]/ol/li[2]/button')
		degre_2.click()
	if X == 'Relations de 3e niveau et plus':
		#html = browser.page_source
		degre_3 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[5]/div/div/div[2]/ol/li[4]/button')
		degre_3.click()

def ecole_filter(browser, X):
	""" Permet de specifier une ecole """
	ecole = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[7]/div/div/div/div')
	ecole.click()
	try:
		ecole.send_keys(X)
		# FIRST SUGGESTION
		time.sleep(randrange(1, 4))
		browser.find_element_by_class_name('link-without-visited-state').click()
	except:
		pass

def niveau_hierarchique_filter(browser, X):
	""" Permet de specifier le niveau hierarchique"""
	# niveau hierarchique
	hierarchie = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div/div')
	hierarchie.click()
	time.sleep(randrange(2, 5))
	# POSSIBILITES
	if X == 'Propriétaire':
		proprietaire = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div[2]/ol/li[1]/button')
		proprietaire.click()
	if X == 'Partenaire':
		partenaire = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div[2]/ol/li[2]/button')
		partenaire.click()
	if X == 'PDG':
		pdg = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div[2]/ol/li[3]/button')
		pdg.click()
	if X == 'VP':
		vp = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div[2]/ol/li[4]/button')
		vp.click()
	if X == 'Directeur':
		directeur = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div[2]/ol/li[5]/button')
		directeur.click()
	if X == 'Manager':
		manager = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div[2]/ol/li[6]/button')
		manager.click()
	if X == 'Cadre supérieur':
		cadre = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div[2]/ol/li[7]/button')
		cadre.click()
	if X == 'Jeune diplômé':
		jeune_diplome = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div[2]/ol/li[8]/button')
		jeune_diplome.click()

def anciennete_poste_actuel_filter(browser, X):
	""" Permet de specifier l anciennete en nbe d annees ds le poste actuel """
	anciennete = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[2]/div/div/div/div')
	anciennete.click()
	time.sleep(randrange(2, 5))
	# POSSIBILITES - on parlera de level :
	# level 1 = moins d'un an
	# level 2 = entre 1 et 2
	# level 3 = entre 3 et 5
	# level 4 : entre 6 et 10
	# level 5 : plus de 10
	if X == 'Moins d’un an':
		level_1 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[2]/div/div/div[2]/ol/li[1]/button')
		level_1.click()
	if X == 'Entre 1 et 2 ans':
		level_2 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[2]/div/div/div[2]/ol/li[2]/button')
		level_2.click()
	if X == 'Entre 3 et 5 ans':
		level_3 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[2]/div/div/div[2]/ol/li[3]/button')
		level_3.click()
	if X == 'Entre 6 et 10 ans':
		level_4 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[2]/div/div/div[2]/ol/li[4]/button')
		level_4.click()
	if X == 'Plus de 10 ans':
		level_5 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[2]/div/div/div[2]/ol/li[5]/button')
		level_5.click()

def anciennete_entreprise_actuelle_filter(browser, X):
	""" Permet de specifier l'anciennete au sein de cette meme entreprise """
	# anciennete dans lnterprise actuelle
	anciennete_entreprise = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[3]/div/div/div/div')
	anciennete_entreprise.click()
	time.sleep(randrange(2, 5))
	# POSSIBILITES - on parlera de level :
	# level 1 = moins d'un an
	# level 2 = entre 1 et 2
	# level 3 = entre 3 et 5
	# level 4 : entre 6 et 10
	# level 5 : plus de 10
	if X == 'Moins d’un an':
		level_1 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[3]/div/div/div[2]/ol/li[1]/button')
	if X == 'Entre 1 et 2 ans':
		level_2 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[3]/div/div/div[2]/ol/li[2]/button')
	if X == 'Entre 3 et 5 ans':
		level_3 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[3]/div/div/div[2]/ol/li[3]/button')
	if X == 'Entre 6 et 10 ans':
		level_4 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[3]/div/div/div[2]/ol/li[4]/button')
	if X == 'Plus de 10 ans':
		level_5 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[3]/div/div/div[2]/ol/li[5]/button')


def fonction_filter(browser, X):
	""" Permet de specifier la fonction de nos cibles - choix multiple"""
	# fonction
	fonction = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[4]/div/div/div/div')
	fonction.click()
	time.sleep(randrange(2, 5))
	# POSSIBILITES
	input_fonction = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[4]/div/div/div[2]/input')
	input_fonction.click()
	time.sleep(randrange(2, 5))
	try:
		input_fonction.send_keys(X)
		# FIRST SUGGESTION
		time.sleep(randrange(1, 4))
		browser.find_element_by_class_name('link-without-visited-state').click()
	except:
		pass

def titre_filter(browser, X):
	""" Permet de specifier le titre apparaissant sur le profil """
	titre = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[5]/div/div/div[1]/div')
	titre.click()
	time.sleep(randrange(2, 5))
	# Attention, une fois qu'on clique sur titre, on ne peut pas ecrire via selenium, il faut encore cliquer sur la place reservee au contenu !!!!!
	titre_content_place = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[5]/div/div/div[2]/input')
	titre_content_place.click()
	try:
		titre_content_place.send_keys(X)
		# FIRST SUGGESTION
		time.sleep(randrange(2, 5))
		browser.find_element_by_class_name('link-without-visited-state').click()
	except:
		pass


def experience(browser, X):
	""" Permet de specifier le nbe d'annees d'experience """
	# annees dexperience
	annee_exp = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[6]/div/div/div/div/div/label')
	annee_exp.click()
	time.sleep(randrange(2, 5))
	# POSSIBILITES - on parlera de level :
	# level 1 = moins d'un an
	# level 2 = entre 1 et 2
	# level 3 = entre 3 et 5
	# level 4 : entre 6 et 10
	# level 5 : plus de 10
	if X == 'Moins d’un an':
		level_1 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[6]/div/div/div[2]/ol/li[1]/button')
		level_1.click()
	if X == 'De 1 à 2 ans':
		level_2 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[6]/div/div/div[2]/ol/li[2]/button')
		level_2.click()
	if X == 'De 3 à 5 ans':
		level_3 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[6]/div/div/div[2]/ol/li[3]/button')
		level_3.click()
	if X == 'De 6 à 10 ans':
		level_4 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[6]/div/div/div[2]/ol/li[4]/button')
		level_4.click()
	if X == 'Plus de 10 ans':
		level_5 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[6]/div/div/div[2]/ol/li[5]/button')
		level_5.click()

### Filtres entreprie

def entreprise_filter(browser, X):
	""" Permet de preciser le nom de l'entreprise """
	# entreprise
	entreprise = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[1]/div/div/div[1]/div')
	entreprise.click()
	time.sleep(randrange(2, 5))
	entreprise_content_place = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[1]/div/div/div[2]/input')
	entreprise_content_place.click()
	try:
		entreprise_content_place.send_keys(X)
		# FIRST SUGGESTION
		time.sleep(randrange(1, 4))
		browser.find_element_by_class_name('link-without-visited-state').click()
	except:
		pass

def effectif_entreprise_filter(browser, X):
	""" Permet de specifier l'effectif de l'entreprise en question """
	effectif = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div/div')
	effectif.click()
	time.sleep(randrange(2, 5))
	# POSSIBILITES - on parlera de palliers :
	# palliers 1 = independant
	# palliers 2 = 1-10
	# palliers 3 = 11-50
	# palliers 4 : 51-200
	# palliers 5 : 201-500
	# palliers 6 : 501-1000
	# palliers 7 : 1001-5000
	# palliers 8 : 5001-10000
	# palliers 9 : +10000
	if X == 'Indépendant':
		pallier_1 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[1]/button')
		pallier_1.click()
	if X == '1-10':
		pallier_2 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[2]/button')
		pallier_2.click()
	if X == '11-50':
		pallier_3 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[3]/button')
		pallier_3.click()
	if X == '51-200':
		pallier_4 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[4]/button')
		pallier_4.click()
	if X == '201-500':
		pallier_5 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[5]/button')
		pallier_5.click()
	if X == '501-1 000':
		pallier_6 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[6]/button')
		pallier_6.click()
	if X == '1 001-5 000':
		pallier_7 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[7]/button')
		pallier_7.click()
	if X == '5 001-10 000':
		pallier_8 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[8]/button')
		pallier_8.click()
	if X == '+ de 10 000':
		pallier_9 = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div[2]/ol/li[9]/button')
		pallier_9.click()

def type_entreprise_filter(browser, X):
	""" Permet de specifier le type de l'entreprise """
	type_entreprise = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div/div/button')
	type_entreprise.click()
	time.sleep(randrange(2, 5))
	# POSSIBILITES
	if X == 'Société cotée en bourse':
		bourse = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div[2]/ol/li[1]/button')
		bourse.click()
	if X == 'Société civile/Société commerciale/Autres types de sociétés':
		societe_civile = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div[2]/ol/li[2]/button')
		societe_civile.click()
	if X == 'À but non lucratif':
		non_lucratif = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div[2]/ol/li[3]/button')
		non_lucratif.click()
	if X == 'Établissement éducatif':
		educatif = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div[2]/ol/li[4]/button')
		educatif.click()
	if X == 'Société de personnes (associés)':
		societe_personne = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div[2]/ol/li[5]/button')
		societe_personne.click()
	if X == 'Indépendant':
		independant = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div[2]/ol/li[6]/button')
		independant.click()
	if X == 'Propriété propre':
		propriete_propre = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div[2]/ol/li[7]/button')
		propriete_propre.click()
	if X == 'Administration publique':
		adm_publique = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div[2]/ol/li[8]/button')
		adm_publique.click()


""" UNE FOIS LES FILTRES TERMINeS, ON VALIDE LA RECHERCHE EN CLIQUANT SUR LE BOUTON RECHERHCE """

def validate_research(browser):
	browser.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div[2]/button').click()


##################################################  TEST
def Linkedin_connexion(browser, username, password):
    """Connexion to Linkedin platform"""
    elementID = browser.find_element_by_id('username')
    elementID.send_keys(username)

    elementID = browser.find_element_by_id('password')
    elementID.send_keys(password)

    elementID.submit()


#file = open('../config.txt')
#lines = file.readlines()
#username = lines[0]
#password = lines[1]#

#CHROME_DRIVER_PATH = '/Users/remyadda/Desktop/chromedriver'#

#browser = webdriver.Chrome(CHROME_DRIVER_PATH) # chemin de l exe chromedriver
#browser.get('https://www.linkedin.com/login/us?') # connexion to linkedin#

#Linkedin_connexion(browser, username, password)
##browser.get('https://www.linkedin.com/sales/homepage') # SN homepage
#time.sleep(randrange(2, 5))
#browser.get('https://www.linkedin.com/sales/search/people?viewAllFilters=true') # All filters#

#time.sleep(5)#

#location_filter('Asie')
#time.sleep(randrange(2, 5))
#langue_filter('anglais')
#time.sleep(randrange(2, 5))
#degre_filter('3')
#time.sleep(randrange(2, 5))
#niveau_hierarchique_filter('manager')
#time.sleep(randrange(2, 5))
#fonction_filter('finance')
#time.sleep(randrange(2, 5))
#titre_filter('responsable financier')
#time.sleep(randrange(2, 5))
#validate_research()


