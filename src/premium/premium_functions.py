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

import mysql_functions

# Logger
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
LOGGER.setLevel(logging.WARNING)

def Linkedin_connexion(browser, username, password):
    """Connexion to Linkedin platform"""
    elementID = browser.find_element_by_id('username')
    elementID.send_keys(username)
    elementID = browser.find_element_by_id('password')
    elementID.send_keys(password)
    elementID.submit()


""" 1er robot ------------------------------------------------------------------------------------------------------------------ """

def connect_add_note_single(browser, profile_link, message_file_path):
    """ Permet de se connecter a une personne et d'ajouter une note en utilisant uniquement SN """
    with open(os.path.join(os.path.dirname(__file__),message_file_path)) as f:
        customMessage = f.read()
    browser.get(profile_link)
    try:
        time.sleep(randrange(2, 5))
        name = retrieve_name(browser)
        if 'XXXXXXX' in customMessage:
            customMessage = customMessage.replace('XXXXXXX', name.split(' ')[0]) #On insere le prenom ds le message uniquement
        # Menu Ajout
        time.sleep(randrange(5, 8))
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/button').click()
        # Connexion
        time.sleep(randrange(5, 8))
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div/div[1]/div/ul/li[1]/div/div[1]').click()
        # Note
        time.sleep(randrange(3, 6))
        msg_box = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/label[1]') # Comme pr les filtres, attention aux endroits ou on ecrit, il faut cliquer deux fois
        time.sleep(randrange(4, 7))
        msg_box.click()
        time.sleep(randrange(2, 5))
        msg_content_place = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/textarea') # on clique une 2e fois ds la box pr pouvoir ecrire
        time.sleep(randrange(2, 5))
        msg_content_place.click()
        # Msg
        time.sleep(randrange(2, 5))
        msg_content_place.send_keys(customMessage)
        # Envoyer . Il se peut que linkedin demande de rentrer ladresse mail du contact pour pouvoir se connecter ...
        time.sleep(randrange(5, 8))
        ####@ ON DESACTIVE LE BOUTON ENVOYE POUR LINSTANT
        browser.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/div/button[2]').click()
        return name, profile_link    
    except:
        traceback.print_exc()
        logger.info("Impossible d'ajouter ce contact en ami")
        return 'echec', 'echec'



def connect_note_list_profile(df, browser, list_profiles, message_file_path, nb2scrap, pendings):
    """ Permet d'envoyer des ajouts et notes a une liste de profiles et enregistre egalement
    le nombre de succes ainsi que le nombre d'echecs. Apres 20 messages envoyes pour un meme filtre et pour une
    meme DATE. Je ne recupere pas ici le lien Linkedin, mais seulement le SN. Ce robot ajoute une connexion + une note,
    donc on comptabilisera la personne comme contactee --> 1"""
    today = date.today()
    counter = 0
    for profile in list_profiles:
        # On check si on a pas deja envoye 20 msg AUJOURD'HUI (en utilisant les dates pr eviter tout pb)
        today_list = df['Dates'].tolist()
        today_list = [date for date in today_list if date==str(today)]
        if len(today_list) >= 20:
            logger.info("Plus de 20 messages envoyes today")
            break
        else:
            # On envoie
            logger.debug("Tentative de connexion et ajout de note")
            name, profile_link = connect_add_note_single(browser, profile, message_file_path)
            logger.info("*** %s ***", name)
            time.sleep(randrange(5, 8))
            if name != 'echec':
                # Ici on a reussi a envoyer
                new_row = {'Personnes':name, 'Links':profile_link, 'Dates':str(today), 'Nombre_messages':1}
                counter += 1
                logger.debug("%s ajouts + envoyés", counter)
                logger.info("******************")
            else:
                logger.info("Echec de connexion pour : %s", name)







""" 2eme robot ------------------------------------------------------------------------------------------------------------------ """


def just_connect(browser, profile_link):
    """ Meme si en entree elle prend le lien premium, on enregistre le lien standard pour l'utiliser plus
    tard dans la fonction envoyant des msgs. Renvoie le nom ainsi que le lien standard. Flow : acces au lien SN - acces au lien Linkedin
    -- copie du lien -- retour sur SN -- ajout"""
    try:
        logger.info("----------------------------------------------------------------------------------------------------")
        logger.info("----------------------------------------------------------------------------------------------------")
        browser.get(profile_link) # premium
        time.sleep(randrange(4, 7))
        name = retrieve_name(browser)
        logger.info("---> %s", name)
        logger.info("Acces au profile Linkedin")
        time.sleep(randrange(4, 7))
        # Menu pour acceder a l'URL linkedin standard
        menu = browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]')
        time.sleep(randrange(1, 2))
        menu.click()
        time.sleep(randrange(3, 6))
        # Linkedin normal - ICI UNE ERREUR REVIENT SOUVENT CAR LE XPATH CHANGE
        try:
            linkedinDOTcom = browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div/div[1]/div/ul/li[3]/div')
        except:
            linkedinDOTcom = browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div[1]/div/ul/li[3]/div')
        time.sleep(randrange(1, 2))
        linkedinDOTcom.click()
        time.sleep(randrange(3, 6))
        # Switch window
        logger.info("Succes. On Switch de browser windows (on passe de SN a Linkedin)")
        window_before = browser.window_handles[0]
        window_after = browser.window_handles[1]
        browser.switch_to.window(window_after)
        time.sleep(randrange(3, 6))
        profile_link = browser.current_url
        browser.close()
        logger.info("On recupere le standard link, et on revient a la page SN pour se connecter")
        browser.switch_to.window(window_before)
        time.sleep(randrange(2, 4))
        ## Connexion
        logger.info("Connexion au profil en cours")
        # plus
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]').click()
        time.sleep(randrange(3, 5))
        # Connect (changement recurrent de xpath)
        try:
            browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div/div[1]/div/ul/li[1]/div/div[1]').click()
        except:
            browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div[1]/div/ul/li[1]/div/div[1]').click()
        time.sleep(randrange(3, 6))
        # Envoyer
        browser.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/div/button[2]').click()
        time.sleep(randrange(1, 3))
        logger.info("Connexion success")
        logger.debug("On close la fenetre standard et on revient a la SN")
        #browser.close()
        return name, profile_link
    except:
        traceback.print_exc()
        logger.info("Impossible de se connecter")
        logger.info("******************************************************************************************************")
        return 'echec', 'echec'


def connect_list_profile(df, browser, list_profiles, nb2scrap, pendings, connexion, id_):
    """ Permet d'envoyer des demande d'ajouts a une liste de profiles et rescence egalement les echecs et les succes.
    Cette fonction n'envoi pas de notes """
    today = date.today()
    counter = 0
    for profile in list_profiles:
        # On check si on a pas deja envoye 20 msg AUJOURD'HUI (en utilisant les dates pr eviter tout pb)
        today_list = df['Dates'].tolist()
        today_list = [date for date in today_list if date==str(today)]
        if len(today_list) >= 20:
            logger.info("Plus de 20 connexions envoyes")
            break
        else:
            # On envoie
            name, standard_profile_link = just_connect(browser, profile)
            time.sleep(randrange(5, 8))
            if name != 'echec':
                # Ici on a reussi a envoyer
                # On ajoute le prospect dans MYSQL
                counter += 1
                mysql_functions.MYSQL_insert_table(id_, connexion, name, profile, standard_profile_link, str(today), 0)
                # On insere également une row dans df pour stopper l'algo après les 20 messages (ça nous evite de passer par MYSQL)
                new_row = {'Personnes':name, 'Links':standard_profile_link, 'Dates':str(today), 'Nombre_messages':0}
                df = df.append(new_row, ignore_index=True)
                logger.debug("%s ajouts ", counter)
            else:
                logger.info("Echec de connexion pour : %s", name)



def send_message(browser, message_file_path, profile_link, id_):
    """ Prend en input le lien linkedin standard - Envoie le message et retourne le nom.
    3 cas sont geres pour bien envoye le message, en fonction du bouton disponible"""
    with open(os.path.join(os.path.dirname(__file__), message_file_path)) as f:
        customMessage = f.read()
    try:
        browser.get(profile_link)
        time.sleep(randrange(3, 6))
        # Name de la page standard (different de la page premium !)
        html = browser.page_source
        #print(html)
        name = browser.find_element_by_class_name("break-words").text
        if 'XXXXXXX' in customMessage:
            customMessage = customMessage.replace('XXXXXXX', name.split(' ')[0]) #On insere le prenom ds le message uniquement
        logger.debug("Tentons d'envoyer un message a %s", name)
        time.sleep(randrange(2, 4))
        BOUTON = browser.find_element_by_class_name("pv-s-profile-actions").text
        if BOUTON == 'Se connecter':
            # CONNEXION
            logger.debug("%s n'est pas encore dans notre reseau (non demandee)", name)
            return 'echec'
        elif BOUTON == 'En attente':
            logger.debug("%s n'est pas encore dans notre reseau (attente)", name)
            return 'echec'
        else: #BOUTON=message. Mais attention, en premium il se peut que ce bouton apparaisse meme si on est pas connecte a la
                # personne. Et donc SN va s'ouvrir. On met donc un try except pour gerer ce cas la
            try:
                logger.debug("Bouton Message disponible pour %s", name)
                browser.find_element_by_class_name("message-anywhere-button").click()
                time.sleep(randrange(2, 4))
                content_place = browser.find_element_by_class_name("msg-form__contenteditable")
                time.sleep(randrange(2, 4))
                content_place.click()
                time.sleep(randrange(4, 7))
                content_place.send_keys(customMessage)
                time.sleep(randrange(3, 6))
                #On ajoute une eventuelle piece jointe
                for file in os.listdir(os.path.join(os.path.dirname(__file__), 'Config')):
                    if 'piece_jointe_' + str(id_) in file:
                        PJ = 'Config/' + file
                        #En REMOTE, upload un fichier est plus compliqué. Il FAUT utiliser le ABSOLUTE PATH. Et en le printant,
                        #J'ai remarque que le absolute path commençait par src/src... (du coup en local ce n'est pas ce path)
                        attach_file_to_message(browser, "/src/src/premium/" + PJ)
                try:
                    logger.debug("ESSAYONS DE CLIQUER SUR ENVOYER")
                    browser.find_element_by_class_name("msg-form__send-button").click()
                    time.sleep(randrange(1, 3))
                    time.sleep(randrange(2, 4))
                    #browser.find_element_by_xpath('/html/body/div[8]/aside/div[2]/header/section[2]/button[2]').click()#reduire window
                    logger.info("Message correctement envoye a %s (CLICK)", name)
                    logger.info("------------------------------------------------")
                    return name
                except: #cliquer sur envoyer
                    logger.debug("ESSAYONS ENCORE DE CLIQUER SUR ENVOYER")
                    content_place.send_keys(Keys.ENTER).click()
                    time.sleep(randrange(1, 3))
                    time.sleep(randrange(2, 4))
                    browser.find_element_by_xpath('/html/body/div[8]/aside/div[2]/header/section[2]/button[2]').click()#reduire window
                    logger.info("Message correctement envoye a %s (ENTER)", name)
                    return name
            except:
                logger.info("Apres verification, %s ne fait pas partie de notre reseau !", name)
                traceback.print_exc()
                try:
                    # si on est ici, c'est qu'une fenetre SN s'est ouvert, alors on la ferme et onb revient au browser initial
                    browser.switch_to.window(browser.window_handles[1])
                    time.sleep(1)
                    browser.close()
                    time.sleep(1)
                    browser.switch_to.window(browser.window_handles[0])
                    return 'echec'
                except:
                    return 'echec'

    except:
        traceback.print_exc()
        logger.info("Impossible d'appliquer la fonction send_message")
        return 'echec'
        



def first_flow_msg(browser, df, message_file_path, id_, connexion):
    """Fonction permettant d'envoyer des messages aux personnes SUSCEPTIBLES de nous avoir accepteé
    en passant par les liens standards ! Problème: on visite a chaque fois les profils de tout le monde"""

    logger.info("+%s contacts dans notre reseau", len(df))
    #Cherchons les personnes a contacter reelement
    person2contact, index_list, mysql_ids = get_list_of_profiles_for_sending_msg(browser, df)
    logger.info("+%s messages doivent être envoyés", len(person2contact))
    logger.debug("Démarrons l'envoi de messages")
    for ids, index_, person in zip(mysql_ids, index_list, person2contact):
        logger.info("Tentative de message ...")
        name = send_message(browser, message_file_path, person, id_)
        if name != 'echec':
            # On update la colonne "Nombre de messages" dans MYSQL
            query = "UPDATE linkedin.user_" + str(id_) + " SET Nombre_messages=1 WHERE id=" + str(ids)
            mysql_functions.MYSQL_update_table(connexion, query)
            time.sleep(randrange(2, 4))
        else: #echec
            logger.info("Impossible à contacter via Linkedin Standard")
            query = "UPDATE linkedin.user_" + str(id_) + " SET Nombre_messages=2 WHERE id=" + str(ids)
            mysql_functions.MYSQL_update_table(connexion, query)



def get_list_of_profiles_for_sending_msg(browser, df):
    """Amélioration de la fonction précédente - On essaye d'envoyer un message uniquement aux gens qui nous 
    ont accepté"""
    browser.get('https://www.linkedin.com/mynetwork/invitation-manager/sent/')
    final_list_of_profiles = []
    # On utilise une boucle while pour scrapper les liens de toutes les pages
    page = 1

    while page <= 25: #chiffre choisi aleatoirement
        CURRENT_URL = browser.current_url
        list_of_profiles_per_page = []
        time.sleep(randrange(2, 5))
        # On va scroller progressivement en utilisant la taille de la page
        total_height = int(browser.execute_script("return document.body.scrollHeight"))
        for i in range(1, total_height, 2):
            browser.execute_script("window.scrollTo(0, {});".format(i))

        # On recupere des liens, donc des href
        time.sleep(randrange(3, 6))
        elems = browser.find_elements_by_xpath("//a[@href]")
        links = [elem.get_attribute('href') for elem in elems]
        # On ne garde que les liens de personnes
        for link in links:
            if '/in/' in link and link:#ca signifie qu'il s'agit d'une personne
                list_of_profiles_per_page.append(link)
        final_list_of_profiles.extend(list_of_profiles_per_page)
        final_list_of_profiles = list(set(final_list_of_profiles))
        #TODO
        #Pour l'instant je n'ai pas eu affaire a des profiles ou il fallait changer de page pour scrapper les
        #pendings invit. Donc cette page renverra une erreur lorsque ca sera le cas
        page += 1
        # Puis on passe a la page suivante et on verifie si l'url n'est pas le meme que le precedent, ce qui justifierait la fin
        try:
            browser.find_element_by_xpath("/html/body/div[7]/div[3]/div/div/div/div/div/div/main/section/div[2]/div[2]/div/button[2]/span").click()
            logger.info("Accès page suivante pending invit")
            time.sleep(randrange(2, 5))
            NEXT_URL = browser.current_url
            if NEXT_URL == CURRENT_URL:
                break
        except:
            logger.debug("Bouton SUIVANT indisponible")
            logger.debug("%s relevés dans pending invit", len(final_list_of_profiles))
            break

    #On contacte donc ceux qui sont dans SQL (depuis au moins 3 jours), car on les ajoutes, et qui ne sont pas dans 
    #final_list_of_profiles (pendings)
    today_list = df['Dates'].tolist()
    today = date.today()
    today_list = [date for date in today_list if date==str(today)]
    #On tentera de contacter les personnes ajoutees jusqu'a J-3
    logger.info("Recuperation des precedentes connexions")
    upThisDay = today - timedelta(days=3)
    filter_ = (pd.to_datetime(df['Dates']) < pd.Timestamp(upThisDay)) & (df['Nombre_messages'] < 1)
    df_temporary = df.loc[filter_]
    logger.info("%s personnes de notre table SQL sont eventuellement contactables (avant soustraction des pendings)")
    df_temporary = df_temporary[~df_temporary.Standard_Link.isin(final_list_of_profiles)]

    person2contact = df_temporary.Standard_Link.tolist()[:20]
    index_list = df_temporary.index.values.tolist()[:20] #df_temporary (filtrée) devrait avoir les meme index que df initiale. Je sais plus pk jai ecrit ca
    mysql_ids = df_temporary['id'].tolist()[:20]

    return person2contact, index_list, mysql_ids


""" Fonctions communes ---------------------------------------------------------------------------------------------------------- """


def get_list_of_profiles(browser, df):
    """ Retourne une liste de tous les profiles correspondants a notre recherche """
    final_list_of_profiles = []
    # On utilise une boucle while pour scrapper les liens de toutes les pages
    page = 1

    while page <= 100: # car il y a au maximum 100 pages (les profils sont mis aleatoirement sur 100 pages a chaque actualisation)
        CURRENT_URL = browser.current_url
        list_of_profiles_per_page = []
        time.sleep(randrange(2, 5))
        # On va scroller progressivement en utilisant la taille de la page
        total_height = int(browser.execute_script("return document.body.scrollHeight"))
        for i in range(1, total_height, 5):
            browser.execute_script("window.scrollTo(0, {});".format(i))

        # On recupere des liens, donc des href
        time.sleep(randrange(3, 6))
        elems = browser.find_elements_by_class_name("search-results__result-list [href]")
        links = [elem.get_attribute('href') for elem in elems]

        # TODO : je ne garde qu'une partie du lien car la deuxieme change tout le temps. Est ce suffisant
        # On ne gardera que les liens 'people' et on verifie ensuite si les personnes n'ont pas deja ete contactees
        for link in links:
            base_link = link.split('_ntb')[0]
            if 'people' in link and base_link not in df['Links'].tolist():
                list_of_profiles_per_page.append(base_link)

        final_list_of_profiles.extend(list_of_profiles_per_page)
        final_list_of_profiles = list(set(final_list_of_profiles))
        logger.info("page %s : %s liens scrapes", page, len(final_list_of_profiles))

        # On envoie 20 msg par jour, donc des que notre liste contient 40 contacts (pour compenser les cas
        # ou il y a echec lors de l'envoie du message), on stop la fonctionn
        if len(final_list_of_profiles) >= 35: #35 normalement
            break

        time.sleep(randrange(2, 5))
        page += 1
        # Puis on passe a la page suivante et on verifie si l'url n'est pas le meme que le precedent, ce qui justifierait la fin
        try:
            browser.find_element_by_xpath('/html/body/main/div[1]/div/section/div[2]/nav/button[2]/span').click()
            time.sleep(randrange(2, 5))
            NEXT_URL = browser.current_url
            if NEXT_URL == CURRENT_URL:
                break
        except:
            logger.info('Impossible de cliquer sur SUIVANT')
            break
    logger.info('Nombre de profiles trouves : %s', len(final_list_of_profiles))
    return final_list_of_profiles, browser.current_url


        
def attach_file_to_message(browser, PJ):
    """Permet d'ajouter une piece jointe au message Linkedin"""
    try:
        pj = browser.find_element_by_class_name("msg-form__attachment-upload-input")
        pj.send_keys(PJ)
        # On recupere la taille du fichier et on attend qu'il se load avant d'envoyer (10 sec pour 1MB)
        size = os.path.getsize(PJ) #la size recupérée est en bytes
        time.sleep(size/10**6*10)
        logger.debug("On a ajouté une pièce jointe")
    except:
        traceback.print_exc()
        logger.debug("Probleme avec la fonction piece jointe (attach_file_to_message)")



def retrieve_name(browser):
    """ Permet de recuperer le nom de la personne """
    name = browser.find_element_by_class_name('profile-topcard-person-entity__name').text
    return name


def pending_invit(browser):
    """ Permet de retourner le nbe de pending invit. Si ce nombre excede 5000 Linkedin ne nous autorise plus
    a agrandir notre reseau"""
    browser.get('https://www.linkedin.com/mynetwork/invitation-manager/sent/')
    pendings = browser.find_element_by_class_name('artdeco-pill__text').text
    pendings = int(re.search(r'\d+', pendings).group())
    return pendings



def check_length_msg(message_file_path):
    """ Pour l'option robot 1, on est limite a 300 caracteres, donc cette fonction verifiera
    si le message respecte cette condition """
    with open(os.path.join(os.path.dirname(__file__), message_file_path)) as f:
        customMessage = f.read()
        print('Nombre de caracteres de votre message : ', len(customMessage))
        lenght_msg = len(customMessage) # On
        return lenght_msg


def how_many_profiles(browser):
    """ Permet de savoir le nomnbre de profils correspondant a une recherche """
    try:
        total_profiles = browser.find_element_by_xpath('/html/body/main/div[1]/div/div/div/div/div/button[1]/span[1]').text
        logger.info("------------------------------")
        logger.info("%s profiles doivent être contactés", total_profiles)
        return total_profiles # car parfois ce n'est pas un int !!
    except:
        logger.debug("fonction 'how_many_profiles' non fonctionelles")
        return 0



def linkedin_security_verification(browser, id_, connexion):
    """ Permet d'entrer le code de securite recu par mail lors de la
    premiere utilisation de cet algo """
    try:
        logger.info("Verifions si une verification par mail est necessaire")
        code_content = browser.find_element_by_class_name('form__input--text')
        code_content.click()
        logger.info("On a 20 mn pour rentrer le code dans MySQL")
        #time.sleep(randrange(1200, 1800))
        time.sleep(120)
        # On doit checker le code recu ds les mails (qu'on aura rentre sur sql)
        logger.info("Cherchons le code dans MySQL")
        security_code = mysql_functions.MYSQL_code_security_verification(id_, connexion)
        print('Security code :', security_code)
        code_content.send_keys(security_code)
        time.sleep(randrange(2, 4))
        browser.find_element_by_class_name('form__submit').click()
        time.sleep(randrange(2, 4))
        logger.info("Code de securite envoye")
    except:
        #traceback.print_exc()
        logger.info('***** Verification par mail non necessaire *****')






