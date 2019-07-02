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
import sys


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
#------  Rcuperer la date de dernière modification du fichier----------------------------------

def date_derniere_modification_fichier(lien):
    return datetime.datetime.strptime(time.ctime(os.path.getmtime(lien)), "%a %b %d %H:%M:%S %Y")


#----------------------------------------------------------------------------------------------
#--------Convertir le texte de la durée en nombre de mois--------------------------------------

def dureeMission(time):
    t = time.split(' ')
    an = 0
    mois = 0
    count = 0
    for word in t:
        if ("an" in word.lower()):
            an = t[count-1]
        if ("mois" in word.lower()):
            mois = t[count-1]
        count = count + 1
    return (int(an)*12 + int(mois))

#-----------------------------------------------------------------------------------------------
#---------Récuperer une date a partir d'une chaine de caracteres--------------------------------

def recuperer_date_texte(texte):
    texte = texte.lower().replace('janvier','january').replace('février','february').replace('mars','march').replace('avril','april')\
        .replace('mai', 'may').replace('juin', 'june').replace('juillet', 'july').replace('aout', 'august').replace('septembre','september')\
    .replace('octobre', 'october').replace('novembre', 'november').replace('decembre', 'december')
    date = datefinder.find_dates(texte)
    print(1)
    return next(date)

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
        if (" an" in line.lower()) or (" mois" in line.lower()):
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
        if (('compétence' in content[i].lower())  ):
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
            listeMot=my_split(line, [",", "/", " et ", "(", ")",":"])
            for mot in listeMot:
                if(mot != ''):
                    if mot[len(mot)-1] == ".":
                        ListeCompetence.append(mot.strip()[:len(mot.strip())-1])
                    else:
                        ListeCompetence.append(mot.strip())
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
            for competence in ListeCompetence:
                if ( competence.lower() in detail):
                    listeMissionCompetence.append(competence)
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
    collaborateur.prenon=str(nom_prenom[0]).lower()
    collaborateur.nom = str(nom_prenom[1]).lower()
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
    collaborateur.date_maj=date_derniere_modification_fichier("C:/Users/e.mahdaoui/Desktop/Stage Fin d'Etude/Application MagicSkills/Code Python"+'/'+lien_cv)
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
        if rechercherEntreprise(session, entreprise) != 'none':
            Entreprise_id=rechercherEntreprise(session, entreprise) #recuperer l'ide de l'ntreprise si elle existe
        else:
            Entreprise_id = rechercherMaxEntrepriseId(session)+1
            ent_dict_sect=chercher_secteur_activite_entreprise(entreprise)
            session.add_all([
                Entreprises(entreprise_id=Entreprise_id, nom=entreprise, secteur_activite=ent_dict_sect['secteur'], region='',description=ent_dict_sect['definition'])
            ])
            session.commit()        #inserer l'entreprise si elle existe pas

        Mission_id = 1 if rechercherMaxMissionId(session) == 0 else rechercherMaxMissionId(session)+1

        session.add_all([
            Missions(mission_id=Mission_id, entreprise_id=Entreprise_id, description_mission='',
                     date_debut='2019-05-02',
                     date_fin='2019-05-02',duree=duree_mission)
        ])
        for competence in mission['Competences']:
            if rechercherCompetence(session, competence.lower()) != 'none':
                Competence_id=rechercherCompetence(session, competence.lower())
            else:
                Competence_id = rechercherMaxCompetenceId(session)+1
                session.add_all([
                    Competences(competence_id=Competence_id, nom=competence.lower(), categorie='non renseigne')
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
    content = convertWordToText("C:/Users/e.mahdaoui/Desktop/Stage Fin d'Etude/Application MagicSkills/Code Python"+'/'+lien_cv)
    missions_detail = cvMissionDetail(content, cvMission(content))
    listecompetence = cvCompetenceMission(cvListeCompetence(missions_detail[0].get('detail')), missions_detail)
    insererCompetence(session, content, listecompetence,lien_cv,dossier)
    return True

#-----------------------------------------------------------------------------------------------------------
#-------------------------------Lister les CV sous format word qui se trouve dans un dossier----------------

def lister_fichier_word(lien):
    for file in listdir(lien):
        if (".docx" in file) and ("~$" not in file):
            yield file

#-----------------------------------------------------------------------------------------------------------
#-------------------------------Lancer l'extraction des competences pour chaque CV----------------------------

def extraction_competence_process(dossier):
    for fichier in lister_fichier_word(dossier):
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