import pandas as pd

"""
Ce fichier a pour but de transformer le format des filtres que l'on telecharge depuis le drive (format CSV),
en bon format pour notre algo. On renseignera donc en input : 
- CSV = path du csv telecharge depuis DRIVE
- NON_CLIENT = il s'agit du nom du client figurant dans la premiere colonne du CSV
- id_ = C'est l'id du client dans MYSQL
"""

CSV = ""
NOM_CLIENT = ""
id_ = ""

df = pd.read_csv(CSV)
df = df[df['Nom - Prénom - Nom société'] == NOM_CLIENT]
df.to_excel("/Users/remyadda/Desktop/AD/Projets/AD_serveur/src/premium/Config/filtres_"+str(id_)+".xlsx")