import os, random, sys, time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
import re
import json
from random import randrange
from datetime import date
import logging
import pymysql.cursors
from selenium.webdriver.remote.remote_connection import LOGGER
import traceback
from selenium.webdriver.common.keys import Keys



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
    """ Permet de se connecter a une personne et d'ajouter une note """
    with open(os.path.join(os.path.dirname(__file__),message_file_path)) as f:
        customMessage = f.read()
    browser.get(profile_link)
    try:
        time.sleep(randrange(2, 5))
        # Menu Ajout
        name = retrieve_name(browser)
        time.sleep(randrange(5, 8))
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/button').click()
        # Connexion
        time.sleep(randrange(5, 8))
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div/div/div[1]/div/ul/li[1]/div/div[1]').click()
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
        logger.info("Impossible d'ajouter ce contact en ami")
        return 'echec', 'echec'



def connect_note_list_profile(df, browser, list_profiles, message_file_path, nb2scrap, pendings, CONTACTS_CSV, CONTACTS_JSON):
    """ Permet d'envoyer des ajouts et notes a une liste de profiles et enregistre egalement
    le nombre de succes ainsi que le nombre d'echecs. Apres 20 messages envoyes pour un meme filtre et pour une
    meme DATE, ce qui equivaut a 400 par mois, l'algo stop """
    today = date.today()
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
            logger.info("*** %s ***", "name")
            time.sleep(randrange(5, 8))
            if name != 'echec':
                # Ici on a reussi a envoyer
                # On update de suite le csv
                new_row = {'Personnes':name, 'Links':profile_link, 'Dates':str(today)}
                df = df.append(new_row, ignore_index=True)
                df.to_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';')
                # On update egalement le JSON
                logger.info("Message envoye")
                logger.debug("Mise a jour du JSON")
                update_json_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON)
            else:
                logger.info("Echec de connexion pour : %s", name)







""" 2eme robot ------------------------------------------------------------------------------------------------------------------ """

def just_connect(browser, profile_link):
    """ Permet seulement de se connecter a la personne """
    # Menu Ajout
    try:
        browser.get(profile_link)
        time.sleep(randrange(4, 7))
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/button').click()
        # Connexion
        name = retrieve_name(browser)
        time.sleep(randrange(2, 5))
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div/div/div[1]/div/ul/li[1]/div/div[1]').click()
        time.sleep(randrange(2, 5))
        # ON DESACTIVE LE BOUTON ENVOYE PR LINSTANT
        browser.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/div/button[2]').click()
        logger.info("Connexion success")
        return name
    except:
        logger.info("Impossible de se connecter")
        return 'echec'

def just_connect_bis(browser, profile_link):
    """ Permet seulement de se connecter a la personne en utilisant le lien standard, meme si en entree elle
    prend le lien premium. Renvoie le nom ainsi que le lien standard"""
    try:
        logger.info("*******************************************************")
        logger.info("Acces au profile Linkedin standard")
        browser.get(profile_link) # premium
        name = retrieve_name(browser)
        time.sleep(randrange(4, 7))
        # Menu pour acceder a l'URL linkedin standard
        menu = browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]')
        time.sleep(randrange(1, 2))
        menu.click()
        time.sleep(randrange(3, 6))
        # Linkedin normal
        linkedinDOTcom = browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div/div/div[1]/div/ul/li[3]/div')
        time.sleep(randrange(1, 2))
        linkedinDOTcom.click()
        time.sleep(randrange(3, 6))
        # Switch window
        logger.info("Succes. On Switch de browser windows")
        window_before = browser.window_handles[0]
        window_after = browser.window_handles[1]
        browser.switch_to.window(window_after)
        time.sleep(randrange(3, 6))
        profile_link = browser.current_url
        # Connexion
        logger.info("Connexion au profil")
        CONNEXION = browser.find_element_by_xpath('/html/body/div[7]/div[3]/div/div/div/div/div[2]/main/div[1]/section/div[2]/div[1]/div[2]/div/div/div[1]/div/button/span')
        time.sleep(randrange(1, 2))
        CONNEXION.click()
        time.sleep(randrange(3, 6))
        # Envoyer
        ENVOYER = browser.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[2]/span')
        time.sleep(randrange(1, 2))
        ENVOYER.click()
        time.sleep(randrange(1, 3))
        logger.info("Connexion success")
        logger.debug("On close la fenetre standard et on revient a la premium")
        browser.close()
        time.sleep(1)
        browser.switch_to.window(window_before)
        return name, profile_link
    except:
        traceback.print_exc()
        try:
            time.sleep(1)
            browser.close()
            time.sleep(1)
            browser.switch_to.window(window_before)
        except:
            pass
        logger.info("Impossible de se connecter")
        return 'echec', 'echec'


def connect_list_profile(df, browser, list_profiles, nb2scrap, pendings, CONTACTS_CSV, CONTACTS_JSON):
    """ Permet d'envoyer des ajouts a une liste de profiles et rescence egalement les echecs et les succes """
    today = date.today()
    for profile in list_profiles:
        # On check si on a pas deja envoye 20 msg AUJOURD'HUI (en utilisant les dates pr eviter tout pb)
        today_list = df['Dates'].tolist()
        today_list = [date for date in today_list if date==str(today)]
        if len(today_list) >= 3:
            logger.info("Plus de 20 connexions envoyes")
            break
        else:
            # On envoie
            name, standard_profile_link = just_connect_bis(browser, profile)
            time.sleep(randrange(5, 8))
            if name != 'echec':
                # Ici on a reussi a envoyer
                # On update de suite le csv
                logger.info("------> %s", name)
                new_row = {'Personnes':name, 'Links':profile, 
                                    'Standard_Link': standard_profile_link,'Dates':str(today), 'Nombre messages':0}
                df = df.append(new_row, ignore_index=True)
                df.to_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';')
                # On update egalement le JSON
                logger.debug("Mise a jour du JSON")
                update_json_connect_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON)
            else:
                logger.info("Echec de connexion pour : %s", name)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def send_message(browser, message_file_path, profile_link):
    """Permet d'envoyer un message a une personne de notre reseau"""
    with open(os.path.join(os.path.dirname(__file__), message_file_path)) as f:
        customMessage = f.read()
    try:
        browser.get(profile_link)
        time.sleep(randrange(3, 6))
        name = retrieve_name(browser)
        logger.debug("Tentative envoie message %s", name)
        time.sleep(randrange(2, 4))
        #bouton message
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[2]/button/span').click()
        time.sleep(randrange(5, 8))
        #contenu + message
        #content = browser.find_element_by_xpath('/html/body/div[6]/div[1]/section/div[2]/section/div[2]/form[1]/section/textarea')
        logger.debug("Attendons que le content place se charge avant de cliquer dessus")
        #content = WebDriverWait(browser, 200).until(EC.element_to_be_clickable((By.XPATH,
                    #"/html/body/div[6]/div[1]/section/div[2]/section/div[2]/form[1]/section/textarea")))
        content = browser.find_element_by_xpath('/html/body/div[6]/div[1]/section/div[2]/section/div[2]/form[1]/section/textarea')
        time.sleep(5)
        browser.execute_script("arguments[0].click();", content)        
        #content.click()
        time.sleep(randrange(4, 8))
        #Envoi
        html = browser.page_source
        #print(html)
        content.send_keys(customMessage)
        time.sleep(randrange(5, 8))
        logger.debug("Bouton ENVOYER")

        element = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH,
                    "/html/body/div[6]/div[1]/section/div[2]/section/div[2]/form[1]/div/section/button[2]")))

        element.click()

        #browser.execute_script("arguments[0].click();", SEND)
        time.sleep(randrange(1, 3))
        #SEND.click()
        time.sleep(randrange(2, 4))
        logger.info("Succes")
        return name
    except:
        traceback.print_exc()
        logging.info("Impossible d'envoyer un message (send msg fonction)")
        return 'echec'



def send_message_bis(browser, message_file_path, profile_link):
    """ Prend en input le lien linkedin standard - Envoie le message et retourne le nom 
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
        print(name)
        logger.debug("Tentons d'envoyer un message a %s", name)
        time.sleep(randrange(2, 4))
        #on clique sur le bouton plus
        ##browser.find_element_by_class_name("pv-s-profile-actions__overflow-toggle").click()
        ##time.sleep(randrange(2, 4))
        #Si on on peut se connecter a la personne, c'est qu'on l'a pas en ami ... Si on ne peut pas, on peut
        # donc lui envoyer un msg
        BOUTON = browser.find_element_by_class_name("pv-s-profile-actions").text
        if BOUTON == 'Se connecter':
            # CONNEXION
            logger.debug("%s n'est pas encore dans notre reseau (non demandee)", name)
            return name
        elif BOUTON == 'En attente':
            logger.debug("%s n'est pas encore dans notre reseau (attente)", name)
            return name
        else: #BOUTON=message. Mais attention, en premium il se peut que ce bouton apparaisse meme si on est pas connecte a la
                # personne. Et donc SN va s'ouvrir. On met donc un try except pour gerer ce cas la
            try:
                logger.debug("%s est dans mon reseau, je devrais donc pouvoir lui envoyer un message", name)
                browser.find_element_by_class_name("message-anywhere-button").click()
                time.sleep(randrange(2, 4))
                content_place = browser.find_element_by_class_name("msg-form__contenteditable")
                time.sleep(randrange(2, 4))
                content_place.click()
                time.sleep(randrange(4, 7))
                content_place.send_keys(customMessage)
                time.sleep(randrange(3, 6))
                print(customMessage)
                #il y a 2 moyens d'envoyer : soit cliquer sur entrer
                try:
                    browser.find_element_by_class_name("msg-form__send-button").click()
                    time.sleep(randrange(1, 3))
                    logger.info("Message correctement envoye (CLICK)")
                    return name
                except: #cliquer sur envoyer
                    content_place.send_keys(Keys.ENTER).click()
                    time.sleep(randrange(1, 3))
                    logger.info("Message correctement envoye (ENTER)")
                    return name
            except:
                logger.info("Apres verification, la personne ne fait pas partie de notre reseau !")
                try:
                    # si on est ici, c'est qu'une fenetre SN s'est ouvert, alors on la ferme et onb revient au browser initial
                    browser.switch_to.window(browser.window_handles[1])
                    time.sleep(1)
                    browser.close()
                    time.sleep(1)
                    browser.switch_to.window(browser.window_handles[0])
                except:
                    pass

    except:
        traceback.print_exc()
        logger.info("Impossible d'appliquer la fonction send_message")
        return 'echec'
        
        




def first_flow_msg(browser, df, message_file_path, nb2scrap, pendings, CONTACTS_JSON):
    """Fonction permettant d'envoyer des messages aux personnes qui nous ont acceptees
    en passant par les liens standards !"""
    today = date.today()
    today_list = df['Dates'].tolist()
    previous_days_list = [date for date in today_list if date!=str(today)]
    print('len previous profils : ', len(previous_days_list))
    print(df['Dates'])
    #Ceux ajoutes aujourd'hui nous ont surement pas accepte encore, on cherchera les previous contacts alors
    logger.info("Recuperation des precedentes connexions")
    df_temporary = df[df['Dates'].isin(previous_days_list)]
    print(df_temporary['Dates'])
    print('LEN DF TOTAL : ', len(df))
    print('LEN DF TEMPORARY : ', len(df_temporary))
    print(df_temporary['Nombre messages'])

    person2contact = df_temporary['Links'].tolist()
    nbe_msg_envoyes = df_temporary['Nombre messages'].tolist()
    index_list = df_temporary.index.values.tolist() #df_temporary (filtree) devrait avoir les meme index que df initiale

    logger.debug("Envoi des messages aux connexions non contactees")
    for index_, person, nb_msg in zip(index_list, person2contact, nbe_msg_envoyes):
        print(index_, person, nb_msg, type(nb_msg))
        if nb_msg == 0:
            break
            logger.info("Essayons d'envoyer un message a ce contact car c'est un 0")
            name = send_message_bis(browser, message_file_path, person)
            if name != 'echec':
                #message correctement envoye - on ajoute le lien dans la liste
                df.loc[index_, 'Nombre de messages'] = 1
                df.to_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';')
                time.sleep(randrange(2, 4))
                # On update egalement le JSON
                update_json_connect_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON)
                logger.info("Succes ! Message envoye a %s", name)
            else: #echec
                logger.info("Echec pour ce 0, surement qu'il nous a pas accepte")
                pass
        else:
            logging.info("Message deja envoye au contact")

    #logger.info("Tentons l'INCONNU")
    #name = send_message(browser, message_file_path, "https://www.linkedin.com/sales/people/ACwAACBthBYBxaRBRkQRTLttXkV3SUoExJM3Krw,NAME_SEARCH,LcCq")
    logger.info("Tentons ma FEMME")
    name = send_message(browser, message_file_path, "https://www.linkedin.com/sales/people/ACwAACVDV2sBKA0MJwOJcGKmJW-1s7EgWCSFaYA,NAME_SEARCH,dt0z")



 




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

        # TODO : jene garde qu'une partie du lien car la deuxieme change tout le temps. Est ce suffisant
        # On ne gardera que les liens 'people' et on verifie ensuite si les personnes n'ont pas deja ete contactees
        for link in links:
            base_link = link.split('_ntb')[0]
            if 'people' in link and base_link not in df['Links'].tolist():
                list_of_profiles_per_page.append(base_link)

        final_list_of_profiles.extend(list_of_profiles_per_page)
        final_list_of_profiles = list(set(final_list_of_profiles))
        print('Page ', page, ' : ', len(final_list_of_profiles), ' liens scrapes')

        # On envoie 20 msg par jour, donc des que notre liste contient 40 contacts (pour compenser les cas
        # ou il y a echec lors de l'envoie du message), on stop la fonctionn
        if len(final_list_of_profiles) >= 5:
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


    print('Nombre de profiles trouves : ', len(final_list_of_profiles))
    return final_list_of_profiles


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


def update_json_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON):
    """ Cette fonction met a jour le json file afin de mettre a jour egalement les stats ainsi que le dashboard,
    On mettra autant de parametres ds la fonction qu'il y a de parametres dans le json """
    updated_json = {"Total messages envoyes":len(df),
                    "Total envoyes aujourd'hui":len(today_list),
                    "Personnes a contacter pour ce filtre": nb2scrap,
                    "Pending invit": pendings}
                    
    with open(os.path.join(os.path.dirname(__file__), CONTACTS_JSON), 'w') as json_file:
        json.dump(updated_json, json_file)

def update_json_connect_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON):
    """ Cette fonction met a jour le json file afin de mettre a jour egalement les stats ainsi que le dashboard,
    On mettra autant de parametres ds la fonction qu'il y a de parametres dans le json """
    print(df['Nombre messages'].dtypes)
    msg_envoyes = len(df[df['Nombre messages']==1])
    updated_json = {"Total connexions envoyees":len(df),
                    "Total messages envoyes": msg_envoyes,
                    "Total envoyes aujourd'hui":len(today_list),
                    "Personnes a contacter pour ce filtre": nb2scrap,
                    "Pending invit": pendings}
                    
    with open(os.path.join(os.path.dirname(__file__), CONTACTS_JSON), 'w') as json_file:
        json.dump(updated_json, json_file)        


def check_length_msg(message_file_path):
    """ Pour l'option robot 1, on est limite a 300 caracteres, donc cette fonction verifiera
    si le message respecte cette condition """
    with open(os.path.join(os.path.dirname(__file__), message_file_path)) as f:
        customMessage = f.read()
        print('Nombre de caracteres de votre message : ', len(customMessage))
        return len(customMessage)


def how_many_profiles(browser):
    """ Permet de savoir le nomnbre de profils correspondant a une recherche """
    total_profiles = browser.find_element_by_xpath('/html/body/main/div[1]/div/div/div/div/div/button[1]/span[1]').text
    print('------------------------------')
    print(total_profiles, ' profiles must be contacted')
    return total_profiles # car parfois ce n'est pas un int !!


