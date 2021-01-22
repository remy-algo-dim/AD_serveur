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


# Logger
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
LOGGER.setLevel(logging.WARNING)

def lets_apply_filters(browser, df_filtres):
    """ Cette fonction a pour but d'appliquer tous les filtres pour effectuer
    une recherche """
    # FILTRES - on obtient pr chaque filtre une liste avec les input du user
    browser.get('https://www.linkedin.com/sales/search/people?viewAllFilters=true')

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
        

    time.sleep(randrange(5, 8))
    for location in LOCATION:
        premium_filters.location_filter(browser, location)
        time.sleep(randrange(2, 4))
    logger.debug("Premier filtres appliqués")
    langue_filter = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[8]/div/div/div/div')
    langue_filter.click()
    for langue in LANGUE:
        premium_filters.langue_filter(browser, langue)
        time.sleep(randrange(2, 4))
    for secteur in SECTEUR:
        premium_filters.secteur_filter(browser, secteur)
        time.sleep(randrange(2, 4))
    degre_filter = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[1]/ul/li[5]/div/div/div/div')
    degre_filter.click()
    for degre in DEGRE:
        premium_filters.degre_filter(browser, degre)
        time.sleep(randrange(4, 6))
    for ecole in ECOLE:
        premium_filters.ecole_filter(browser, ecole)
        time.sleep(randrange(2, 4))
    hierarchie_filter = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[1]/div/div/div/div')
    hierarchie_filter.click()
    for hierarchie in HIERARCHIE:
        premium_filters.niveau_hierarchique_filter(browser, hierarchie)
        time.sleep(randrange(2, 4))
    anciennete_filter = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[2]/div/div/div/div')
    anciennete_filter.click()
    for anciennete_poste in ANCIENNETE_POSTE:
        premium_filters.anciennete_poste_actuel_filter(browser, anciennete_poste)
        time.sleep(randrange(2, 4))
    anciennete_entreprise_filter = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[3]/div/div/div/div')
    anciennete_entreprise_filter.click()
    for anciennete_entreprise in ANCIENNETE_ENTREPRISE:
        premium_filters.anciennete_entreprise_actuelle_filter(browser, anciennete_entreprise)
        time.sleep(randrange(2, 4))
    for fonction in FONCTION:
        premium_filters.fonction_filter(browser, fonction)
        time.sleep(randrange(2, 4))
    for titre in TITRE:
        premium_filters.titre_filter(browser, titre)
        time.sleep(randrange(2, 4))
    annee_exp_filter = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[2]/ul/li[6]/div/div/div/div/div/label')
    annee_exp_filter.click()
    for exp in EXPERIENCE:
        premium_filters.experience(browser, exp)
        time.sleep(randrange(2, 4))
    for entreprise in ENTREPRISE:
        premium_filters.entreprise_filter(browser, entreprise)
        time.sleep(randrange(2, 4))
    effectif_filter = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[2]/div/div/div/div')
    effectif_filter.click()
    for effectif in EFFECTIF:
        premium_filters.effectif_entreprise_filter(browser, effectif)
        time.sleep(randrange(2, 4))
    logger.debug('on est enfin ici bordel de merde')                     
    type_entreprise_filter = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/div[2]/div/section[3]/ul/li[3]/div/div/div/div')
    type_entreprise_filter.click()
    for type_ in TYPE:
        print(type_)
        premium_filters.type_entreprise_filter(browser, type_)
        time.sleep(randrange(2, 4))



