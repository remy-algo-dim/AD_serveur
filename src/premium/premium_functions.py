import os, random, sys, time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
import re
import json
from random import randrange
from datetime import date
import logging

# Logger
logger = logging.getLogger("premium_functions.py")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

def Linkedin_connexion(browser, username, password):
    """Connexion to Linkedin platform"""
    elementID = browser.find_element_by_id('username')
    elementID.send_keys(username)

    elementID = browser.find_element_by_id('password')
    elementID.send_keys(password)

    elementID.submit()

def connect_add_note_single(browser, profile_link, message_file_path):
    """ Permet de se connecter a une personne et d'ajouter une note """
    with open(os.path.join(os.path.dirname(__file__),message_file_path)) as f:
        customMessage = f.read()
    browser.get(profile_link)
    try:
        time.sleep(randrange(2, 5))
        # Menu Ajout
        logger.info('On retrieve le name')
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
        #browser.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/div/button[2]').click()
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
        print('Len today list ', len(today_list))
        if len(today_list) > 20:
            break
        # On envoie
        name, profile_link = connect_add_note_single(browser, profile, message_file_path)
        print(name)
        print('------------------')
        time.sleep(randrange(5, 8))
        if name != 'echec':
            # Ici on a reussi a envoyer
            # On update de suite le csv
            new_row = {'Personnes':name, 'Links':profile_link, 'Dates':str(today)}
            df = df.append(new_row, ignore_index=True)
            df.to_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';')
            # On update egalement le JSON
            logger.info('Message envoye')
            update_json_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON)
        else:
            print('Echec de connexion pour : ', name)


def just_connect(browser, profile_link):
    """ Permet seulement de se connecter a la personne """
    # Menu Ajout
    try:
        time.sleep(randrange(1, 4))
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/button').click()
        # Connexion
        name = retrieve_name(browser)
        time.sleep(randrange(1, 4))
        browser.find_element_by_xpath('/html/body/main/div[1]/div[2]/div/div[2]/div[1]/div[3]/div/div/div/div/div[1]/div/ul/li[1]/div/div[1]').click()
        #browser.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/div/button[2]').click()
        return name
    except:
        logger.info('Impossible de se connecter')
        return 'echec'



def connect_list_profile(df, browser, list_profiles, nb2scrap, pendings, CONTACTS_CSV, CONTACTS_JSON):
    """ Permet d'envoyer des ajouts a une liste de profiles et rescence egalement les echecs et les succes """
    today = date.today()
    for profile in list_profiles:
        # On check si on a pas deja envoye 20 msg AUJOURD'HUI (en utilisant les dates pr eviter tout pb)
        today_list = df['Dates'].tolist()
        today_list = [date for date in today_list if date==str(today)]
        print('Len today list ', len(today_list))
        if len(today_list) > 20:
            break
        # On envoie
        name = just_connect(browser, profile_link)
        print('------------------')
        time.sleep(randrange(5, 8))
        if output != 'echec':
            # Ici on a reussi a envoyer
            # On update de suite le csv
            new_row = {'Personnes':name, 'Links':profile, 'Dates':str(today)}
            df = df.append(new_row, ignore_index=True)
            df.to_csv(os.path.join(os.path.dirname(__file__),CONTACTS_CSV), sep=';')
            # On update egalement le JSON
            update_json_connect_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON)
        else:
            print('Echec de connexion pour : ', name)



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
        if len(final_list_of_profiles) >= 40:
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
                    "Total envoyes aujourd'hui":len(today_list)+1,
                    "Personnes a contacter pour ce filtre": nb2scrap,
                    "Pending invit": pendings}
                    
    with open(os.path.join(os.path.dirname(__file__), CONTACTS_JSON), 'w') as json_file:
        json.dump(updated_json, json_file)

def update_json_connect_file(df, today_list, nb2scrap, pendings, CONTACTS_JSON):
    """ Cette fonction met a jour le json file afin de mettre a jour egalement les stats ainsi que le dashboard,
    On mettra autant de parametres ds la fonction qu'il y a de parametres dans le json """
    updated_json = {"Total connexions envoyees":len(df),
                    "Total envoyes aujourd'hui":len(today_list)+1,
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
    return int(total_profiles)


