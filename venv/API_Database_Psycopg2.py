import os

os.getcwd() #Endroit ou va pointer Python
os.chdir('C:/Users/e.mahdaoui/Desktop/Projet Magic Skills') #Modification de l'espace ou pointe Python
os.getcwd() #Verification
print(os.listdir('.'))

import psycopg2
import hashlib
import sys

def new_agence(nom,adresse,ville):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected')
    except psycopg2.Error:
        sys.stdout.write('connection failed...\n')
        sys.exit()

    cursor = conn.cursor()
    cursor.execute('INSERT INTO agences (nom,adresse,ville) values (%s,%s,%s) ',(nom,adresse,ville))
    conn.commit()
    conn.close()

def new_competence(nom,categorie):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected')
    except psycopg2.Error:
        sys.stdout.write('connection failed...\n')
        sys.exit()

    cursor = conn.cursor()
    cursor.execute('INSERT INTO competences (nom,categorie) values (%s,%s) ',(nom,categorie))
    conn.commit()
    conn.close()
    
def new_entreprise(nom,secteur_activite,region):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected')
    except psycopg2.Error:
        sys.stdout.write('connection failed...\n')
        sys.exit()

    cursor = conn.cursor()
    cursor.execute('INSERT INTO entreprises (nom,secteur_activite,region) values (%s,%s,%s) ',(nom,secteur_activite,region))
    conn.commit()
    conn.close()

def new_mission(entreprise_id,description_mission,date_debut,date_fin):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected')
    except psycopg2.Error:
        sys.stdout.write('connection failed...\n')
        sys.exit()

    cursor = conn.cursor()
    cursor.execute('INSERT INTO missions (entreprise_id,description_mission,date_debut,date_fin) values (%s,%s,%s,%s) ',(entreprise_id,description_mission,date_debut,date_fin))
    conn.commit()
    conn.close()
    

def new_collaborateur(agence_id,nom,prenom,status,experience_globale,seniorite,date_entre,date_sortie,mobilite,region_mobilite,lien,date_maj):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected')
    except psycopg2.Error:
        sys.stdout.write('connection failed...\n')
        sys.exit()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO collaborateurs (agence_id,nom,prenon,status,experience_globale,seniorite,date_entre,date_sortie,mobilite,region_mobilite,lien,date_maj) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ',(agence_id,nom,prenom,status,experience_globale,seniorite,date_entre,date_sortie,mobilite,region_mobilite,lien,date_maj))
    conn.commit()
    conn.close()

def new_experience(mission_id,collaborateur_id,competence_id,role_collaborateur,score):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected')
    except psycopg2.Error:
        sys.stdout.write('connection failed...\n')
        sys.exit()

    cursor = conn.cursor()
    cursor.execute('INSERT INTO experiences (mission_id,collaborateur_id,competence_id,role_collaborateur,score) values (%s,%s,%s,%s,%s) ',(mission_id,collaborateur_id,competence_id,role_collaborateur,score))
    conn.commit()
    conn.close()

def get_agence_id(nom_agence):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected \n')
        cursor = conn.cursor()
        requete='select agence_id from agences where nom= \'{0}\''.format(nom_agence)
        print(requete+'\n')
        cursor.execute(requete)
        print("Selecting rows from mobile table using cursor.fetchall")
        agence_records = cursor.fetchone()
        if (agence_records != None):
            return agence_records[0]
#        for row in agence_records:
#            print("agence  = ", row[0], "\n")
           
    except psycopg2.Error:
        sys.stdout.write('erreur lors de la récupération de l agence_id \n')
        sys.exit() 
    finally:
    #closing database connection.
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")


def get_entreprise_id(nom_entreprise):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected \n')
        cursor = conn.cursor()
        requete='select entreprise_id from entreprises where nom= \'{0}\''.format(nom_entreprise)
        print(requete+'\n')
        cursor.execute(requete)
        print("Selecting rows from mobile table using cursor.fetchall")
        entreprise_records = cursor.fetchone()
        if (entreprise_records != None):
            return entreprise_records[0]
#        for row in agence_records:
#            print("agence  = ", row[0], "\n")
           
    except psycopg2.Error:
        sys.stdout.write('erreur lors de la récupération de l agence_id \n')
        sys.exit() 
    finally:
    #closing database connection.
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
            
def get_id(nom,nom_table,nom_colonne):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected \n')
        cursor = conn.cursor()
        requete='select '+nom_table[:(len(nom_table)-1)]+'_id from '+nom_table +' where '+nom_colonne+'= \'{0}\''.format(nom)
        print(requete+'\n')
        cursor.execute(requete)
        print("Selecting rows from mobile table using cursor.fetchall")
        records = cursor.fetchone()
        if (records != None):
            return records[0]
#        for row in agence_records:
#            print("agence  = ", row[0], "\n")
           
    except psycopg2.Error:
        sys.stdout.write('erreur lors de la récupération de l agence_id \n')
        sys.exit() 
    finally:
    #closing database connection.
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

print(get_agence_id('User'))
print(get_id('User','agences','nom'))
print(get_entreprise_id('nom'))


def delete_collaborateur(mission_id,collaborateur_id,competence_id):
    try:
        conn = psycopg2.connect(dbname='magic_skill', user='postgres', password='Data', host='127.0.0.1', port=5432)
        sys.stdout.write('Connected')
    except psycopg2.Error:
        sys.stdout.write('connection failed...\n')
        sys.exit()

    cursor = conn.cursor()
    cursor.execute('DELETE FROM collaborateurs WHERE UPPER(NOM)=UPPER('+nom+')')
    conn.commit()
    conn.close()