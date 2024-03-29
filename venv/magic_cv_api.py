import os
import time
import datetime
import datefinder
import unicodedata
import docx2txt
import re
import wikipedia
from os import listdir
from os.path import isfile, join
from SQLAlchemyAPI import *
from datetime import date
import sys

folder = "C:/Users/e.mahdaoui/Desktop/Projet Magic Skills/CV"
seniorite_seuil= 60
secteur_activite=["bancaire","télécommunication", "banque", "assurance" ,"grande distribution", "transport","informatique", "technologie", "pharmacie","pétroliers"]


#-----------------------------------------------------------------------------------------------
#---------Convertir le fichier word en txt------------------------------------------------------
def convertWordToText(Lien):
    text= docx2txt.process(Lien)
    text = unicodedata.normalize("NFKD", text)
    # Spliter le texte en lignes
    content = []
    for line in text.splitlines():
        if (line.strip() != ''):
            content.append(line.replace(u'\t', u' ').strip())
    return content

#----------------------------------------------------------------------------------------------
#--------Rcuperer la date de dernière modification du fichier----------------------------------

def date_derniere_modification_fichier(lien):
    return datetime.datetime.strptime(time.ctime(os.path.getmtime(lien)), "%a %b %d %H:%M:%S %Y")


#----------------------------------------------------------------------------------------------
#--------Convertir le texte de la durée en nombre de mois--------------------------------------

def dureeMission(time):
    time=time.replace(',','.')
    t = time.split(' ')
    an = 0
    mois = 0
    count = 0
    try:
        for word in t:
            if ("an" in word.lower()):
                an = t[count-1]
            if ("mois" in word.lower()):
                mois = t[count-1]
            count = count + 1
        resultat =(float(an)*12 + float(mois))
    except ValueError-1:
        return
    except:
        return -1
    return resultat

#-----------------------------------------------------------------------------------------------
#---------Récuperer une date a partir d'une chaine de caracteres--------------------------------

def recuperer_date_texte(texte):
    try:
        texte = texte.lower().replace('janvier','january').replace('février','february').replace('mars','march').replace('avril','april')\
            .replace('mai', 'may').replace('juin', 'june').replace('juillet', 'july').replace('aout', 'august').replace('septembre','september')\
        .replace('octobre', 'october').replace('novembre', 'november').replace('decembre', 'december')
        date = datefinder.find_dates(texte)
        date = next(date)
    except:
        return "9999-12-31"
    return date


#-----------------------------------------------------------------------------------------------
#---------Spliter une chaine de caractere par rapport à plusieurs séparateurs-------------------
#---------liste des chaine de caractère de competences.-----------------------------------------
def my_split(s, seps):
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res

#-----------------------------------------------------------------------------------------------
#---------Extraire la liste des missions sous forme de dictionnaire-----------------------------
#--------- (Index_debut,Entreprise,Ville,Date,Duree)

def cvMission(content):
    time_b = 0
    time = ""
    date = ""
    city = ""
    company = ""
    count = 0
    ListMission=[]
    Mission={}
    cpt=0
    numero_mission=0
    for line in content:
        if (time_b == 1):
            x = re.search(".*([1-3][0-9]{3})", line)
            if (x is not None):
                cpt=cpt+1
                if (cpt!=1):
                    Mission['Index_fin']= count-4
                    ListMission.append(Mission)
                    Mission={}
                    date = line
                    Mission['Index_debut']= count-3
                    if "(" in content[count-3]:
                        Mission['Entreprise']= content[count-4]
                    else:
                        Mission['Entreprise']= content[count-3]
                    Mission['Ville']=content[count-2]
                    Mission['Date']=line
                    Mission['Role'] = content[count+1]
                    Mission['Duree']=dureeMission(time)
                    debut_paragraphe = count-3
                else:
                    Mission={}
                    date = line
                    city = content[count-2]
                    company = content[count-3]
                    Index_debut=count-3
                    Mission['Index_debut']= count-3
                    if "(" in content[count-3]:
                        Mission['Entreprise']= content[count-4]
                    else:
                        Mission['Entreprise']= content[count-3]
                    Mission['Ville']=city
                    Mission['Date']=date
                    Mission['Role'] = content[count + 1]
                    Mission['Duree']=dureeMission(time)

            time_b = 0
        if (" an" in line.lower()) or (" mois" in line.lower()) or (" ans" in line.lower()):
            time_b = 1
            time = line
        count = count + 1
    Mission['Index_fin']=count-1
    ListMission.append(Mission)
    return ListMission


#-----------------------------------------------------------------------------------------------
#---------Retourner le paragraphe des competences avec toutes les missions----------------------
#---------Dictionnaire {Mission Description, detail}--------------------------------------------

def cvMissionDetail(content,ListMission):
    cpt=0
    ListMissionDetail=[]
    MissionDetail={}
    competenceTechnique=''
    actif=False
    for i in range (3,ListMission[0].get('Index_debut')-1):
        if (('compétence' in content[i].lower())  or ('competence' in content[i].lower()) ):
         #   and ('technique' in content[i].lower())
            actif=True
        if (actif==True):
            competenceTechnique=competenceTechnique+'\n'+content[i]
    MissionDetail={}
    MissionDetail['missionDesc']= 'Competence technique'
    MissionDetail['detail']=competenceTechnique
    ListMissionDetail.append(MissionDetail)
    for element in ListMission:
        cpt=cpt+1
        Debut=element.get('Index_debut')
        fin=element.get('Index_fin')
        MissionDetailCH=''
        for i in range(Debut+4, fin):
            MissionDetailCH=MissionDetailCH+' '+content[i]
        MissionDetail={}
        MissionDetail['missionDesc']= element
        MissionDetail['detail']=MissionDetailCH
        ListMissionDetail.append(MissionDetail)
    return ListMissionDetail

#-----------------------------------------------------------------------------------------------
#---------Extraire la liste des competence à partir de la section competence--------------------
#---------liste des chaine de caractère de competences.-----------------------------------------


def cvListeCompetence(Texte):
    #Texte=Texte.lower().replace()
    listetexte=Texte.split('\n')
    ListeCompetence=[]
    for line in listetexte:
        if (',' in line) or ("/" in line) or ("(" in line) or (")" in line)or (":" in line):
            catégorie=""
            if (":" in line):
                line0= line.split(":")
                catégorie=line0[0]
                line=line0[1]
            listeMot=my_split(line, [",", " et ", "(", ")",":"])
            for mot in listeMot:
                if(len(mot.strip()) >= 1):
                    if mot[len(mot)-1] == ".":
                        mot_coupe = mot.strip()[:len(mot.strip())-1]
                        if (mot_coupe != '') and (mot_coupe != '.'):
                            ListeCompetence.append(mot_coupe+"--"+catégorie)
                    else:
                        ListeCompetence.append(mot.strip()+"--"+catégorie)
    print("--------------------------------------------------------------------------------------")
    print(ListeCompetence)
    return ListeCompetence

#-----------------------------------------------------------------------------------------------
#---------la liste des missions avec les différent competence utilisé pour chaque mission
#---------parametre (liste de competence, liste de mission avec desription )
#---------retourne Dictionnaire(Mission , Liste Competence)
def cvCompetenceMission(ListeCompetence,ListMissionDetail):
    cpt=0
    Mission={}
    listeMission=[]
    for MissionDetail in ListMissionDetail:
        cpt=cpt+1
        detail=MissionDetail.get('detail').lower()
        listeMissionCompetence=[]
        if (cpt> 1):
            for couple in ListeCompetence:
                ligne=couple.split("--")
                competence=ligne[0]
                categorie=ligne[1]
                if ( competence.lower() in detail):
                    listeMissionCompetence.append(couple)
            Mission={}
            Mission['ID']=MissionDetail.get('missionDesc')
            Mission['Competences']=listeMissionCompetence
            listeMission.append(Mission)
    return listeMission

#-----------------------------------------------------------------------------------------------
#---------Extraire les informations du collaborateur depuis les premiers lignes du CV-----------

def extraire_information_collaborateur(texte_collaborateur,lien_cv,dossier):
    collaborateur=Collaborateurs()
    collaborateur.agence_id=1
    nom_prenom=texte_collaborateur[1].split(' ')
    collaborateur.prenon=str(nom_prenom[0]).lower().capitalize()
    collaborateur.nom = str(nom_prenom[1]).lower().capitalize()
    if rechercherCollaborateur(session,collaborateur.nom,collaborateur.prenon) != 'none':
        collaborateur.collaborateur_id=rechercherCollaborateur(session, collaborateur.nom, collaborateur.prenon)
    else:
        collaborateur.collaborateur_id= 1 if rechercherMaxCollaborateurId(session) == 0 else rechercherMaxCollaborateurId(session) + 1
    collaborateur.status='non renseigne'
    collaborateur.experience_globale=dureeMission(texte_collaborateur[0])
    collaborateur.seniorite='Senior' if collaborateur.experience_globale > seniorite_seuil else 'Junior'
    collaborateur.date_entre='2012-02-01'
    collaborateur.date_sortie='9999-12-31'
    collaborateur.mobilite=-1
    collaborateur.region_mobilite='non renseigne'
    collaborateur.lien=dossier+'/'+lien_cv
    collaborateur.date_maj=date_derniere_modification_fichier(folder+'/'+lien_cv)
#    str(sys.argv[1])

    for line in texte_collaborateur:
        if ("disponibilit" in line.lower()):
            collaborateur.disponibilite=recuperer_date_texte(line)
    return collaborateur

#-----------------------------------------------------------------------------------------------------------
#---------Insérer le collaborateurs, entreprises, missions et competences dans la base de données-----------

def insererCompetence(session,content,listeMission,file,dossier):
    index_mission_1=listeMission[0]['ID']['Index_debut']
    collaborateur=extraire_information_collaborateur(content[0:index_mission_1],file,dossier) # recuperer les informations du collab
    if collaborateur.collaborateur_id > rechercherMaxCollaborateurId(session):
        session.add_all([
            collaborateur
        ])
    session.commit() # inserer le collaborateur
    for mission in listeMission:
        duree_mission=mission['ID']['Duree']
        entreprise = mission['ID']['Entreprise']
        role=mission['ID']['Role']
        listeCompetence=mission['Competences']
        date_debut_fin = recuperer_date_debut_fin_mission(mission['ID']['Date'])
        if len(date_debut_fin) == 2:
            date_debut = date_debut_fin[0]
            date_fin = date_debut_fin[1]
        elif len(date_debut_fin) == 1:
            date_debut = date_debut_fin[0]
            date_fin = date(9999, 12, 30)
        if rechercherEntreprise(session, entreprise) != 'none':
            Entreprise_id=rechercherEntreprise(session, entreprise) #recuperer l'ide de l'ntreprise si elle existe
        else:
            Entreprise_id = rechercherMaxEntrepriseId(session)+1
 #           ent_dict_sect=""
            ent_dict_sect=chercher_secteur_activite_entreprise(entreprise)
            session.add_all([
                Entreprises(entreprise_id=Entreprise_id, nom=entreprise, secteur_activite=ent_dict_sect['secteur'], region='',description=ent_dict_sect['definition'])
            ])
            session.commit()        #inserer l'entreprise si elle existe pas

        Mission_id = 1 if rechercherMaxMissionId(session) == 0 else rechercherMaxMissionId(session)+1

        session.add_all([
            Missions(mission_id=Mission_id, entreprise_id=Entreprise_id, description_mission='',
                     date_debut=date_debut,
                     date_fin=date_fin,duree=duree_mission)
        ])
        for couple in mission['Competences']:
            ligne=couple.split("--")
            competence=ligne[0]
            categorie=ligne[1]
 #           print("-------------------------------------------")
 #           print(couple)
            if rechercherCompetence(session, competence.upper()) != 'none':
                Competence_id=rechercherCompetence(session, competence.upper())
            else:
                Competence_id = rechercherMaxCompetenceId(session)+1
                session.add_all([
                    Competences(competence_id=Competence_id, nom=competence.upper(), categorie=categorie)
                ])
                session.commit()
            session.add_all([
                Experiences(mission_id=Mission_id,collaborateur_id=collaborateur.collaborateur_id,competence_id=Competence_id, role_collaborateur=role, score=0)
            ])
            session.commit()
    return True


#-----------------------------------------------------------------------------------------------------------
#-------------------------------Fonction qui enchaine les traitements  d'extraction des competences---------


def traitement_cv(lien_cv,dossier,session):

#    str(sys.argv[1])
    content = convertWordToText(folder+'/'+lien_cv)
 #   print(content)
    missions_detail = cvMissionDetail(content, cvMission(content))
    listecompetence = cvCompetenceMission(cvListeCompetence(missions_detail[0].get('detail')), missions_detail)
    insererCompetence(session, content, listecompetence,lien_cv,dossier)
    return True

#-----------------------------------------------------------------------------------------------------------
#-------------------------------Lister les CV sous format word qui se trouve dans un dossier----------------

def lister_fichier_word(lien):
    for file in listdir(lien):
        if (".docx" in file.lower()) and ("~$" not in file):
            yield file

#-----------------------------------------------------------------------------------------------------------
#-------------------------------Lancer l'extraction des competences pour chaque CV----------------------------

def extraction_competence_process(dossier):
    cpt=0
    for fichier in lister_fichier_word(dossier):
       # print(fichier)
        traitement_cv(fichier, dossier,  session)
    return True

#-----------------------------------------------------------------------------------------------------------
#-------------------------------Retourner le secteur d'activite d'une entreprise----------------------------

def chercher_secteur_activite_entreprise(entreprise):
    wikipedia.set_lang("fr")
    trouve = False
    secteur="none"
    dictionnaire ={}
    try:
        for mot in secteur_activite:
            if mot in str(entreprise).lower():
                trouve = True
                dictionnaire['secteur'] = mot
                dictionnaire['definition'] = ''
        if trouve == False:
            resume = str(wikipedia.summary(entreprise)).lower()
            for mot in secteur_activite:
                if mot in resume:
                    trouve=True
                    dictionnaire['secteur'] = mot
                    dictionnaire['definition']=str(resume).split(".")[0]
        secteur="banque" if secteur=="bancaire" else secteur
        return dictionnaire if trouve==True else {'secteur':'domaine non reconnu','definition':''}
    except wikipedia.DisambiguationError as e:
        dictionnaire['secteur']='nom entreprise ambigue'
        dictionnaire['definition']=''
        return dictionnaire
    except wikipedia.exceptions.PageError  as s:
        dictionnaire['secteur']='nom entreprise non reconnu pour wikipedia'
        dictionnaire['definition']=''
        return dictionnaire


# -----------------------------------------------------------------------------------------------------------
# -------------------------------Retourner la date de début et du fin de la mission--------------------------

def recuperer_date_debut_fin_mission(texte):
    it=datefinder.find_dates(texte)
    cpt=0
    tabelau_date=[]
    resultat_table=[]
    for element in it:
        tabelau_date.append(element)
        cpt=cpt+1
    if cpt == 0:
        if ("-" in texte):
            texte=texte.split("-")
        elif ("/" in texte):
            texte = texte.split("/")
        date_debut = date(int(texte[0]), 1, 1) if int(texte[0]) < int(texte[1]) else date(int(texte[1]), 1, 1)
        date_fin = date(int(texte[1]), 1, 1) if int(texte[0]) < int(texte[1]) else date(int(texte[0]), 1, 1)
        resultat_table.append(date_debut)
        resultat_table.append(date_fin)
    elif cpt == 1:
        date_debut=tabelau_date[0]
        resultat_table.append(date_debut)
    elif cpt == 2:
        date_debut=tabelau_date[0]
        date_fin=tabelau_date[1]
#        date_debut = date1 if date2-date1 > 0 else date2
#        date_fin = date2 if date2-date1 > 0 else date1
        resultat_table.append(date_debut)
        resultat_table.append(date_fin)
    else:
        date_debut=tabelau_date[0]
        date_fin=tabelau_date[0]
        resultat_table.append(date_debut)
        resultat_table.append(date_fin)
    return resultat_table