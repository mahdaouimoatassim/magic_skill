

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Boolean, Date, Float, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import or_
import hashlib
import datetime
from dateutil import relativedelta
import numpy as np

utilisateur="postgres"
mot_de_passe="Data"
serveur="localhost"
port=5432
base_de_donnees="magic_skill"
lien_connexion="postgresql://"+utilisateur+":"+mot_de_passe+"@"+serveur+":"+str(port)+"/"+base_de_donnees

print (lien_connexion)
#-------------------------------------- Declaration des tables  ---------------------------------------------------------
#postgresql://postgres:postgresql123@localhost:5433/magic_skill
Base = declarative_base()
engine = create_engine(lien_connexion)
DBSession = sessionmaker(bind=engine)
session = DBSession()
conn = engine.connect()


# Table Agences
class Agences(Base):
    __tablename__ = 'agences'
    agence_id = Column(Integer, primary_key=True)
    nom = Column(String(200))
    adresse = Column(String(200))
    ville = Column(String(30))


# Table Competences
class Competences(Base):
    __tablename__ = 'competences'
    competence_id = Column(Integer, primary_key=True)
    nom = Column(String(50))
    categorie = Column(String(50))


# Table Collaborateurs
class Collaborateurs(Base):
    __tablename__ = 'collaborateurs'
    collaborateur_id = Column(Integer, primary_key=True)
    agence_id = Column(Integer, ForeignKey('agences.agence_id'))
    nom = Column(String(30))
    prenon = Column(String(30))
    status = Column(String(30))
    experience_globale = Column(Float)
    seniorite = Column(String(30))
    date_entre = Column(Date)
    date_sortie = Column(Date)
    mobilite = Column(Integer)
    region_mobilite = Column(String(200))
    lien = Column(Text)
    date_maj = Column(DateTime)
    disponibilite = Column(DateTime)

# Table Entreprises
class Entreprises(Base):
    __tablename__ = 'entreprises'
    entreprise_id = Column(Integer, primary_key=True)
    nom = Column(String(50))
    secteur_activite = Column(String(50))
    region = Column(String(50))
    description=Column(Text)


# Table Missions
class Missions(Base):
    __tablename__ = 'missions'
    mission_id = Column(Integer, primary_key=True)
    entreprise_id = Column(Integer, ForeignKey('entreprises.entreprise_id'))
    description_mission = Column(Text)
    date_debut = Column(Date)
    date_fin = Column(Date)
    duree=Column(Float)


# Table Missions
class Experiences(Base):
    __tablename__ = 'experiences'
    mission_id = Column(Integer, ForeignKey('missions.mission_id'), primary_key=True, )
    competence_id = Column(Integer, ForeignKey('competences.competence_id'), primary_key=True)
    collaborateur_id = Column(Integer, ForeignKey('collaborateurs.collaborateur_id'), primary_key=True)
    role_collaborateur = Column(Date)
    score = Column(Date)


Base.metadata.bind = engine
Base.metadata.create_all(engine)
#------------------------------------------------------------------------------------------------------------------
# Rechercher l'identifiant du collaboraeur en se basant sur le nom et prenom
def rechercherCollaborateur(session,nom_collab,prenom_collab):
    u = session.query(Collaborateurs.collaborateur_id,Collaborateurs.nom, Collaborateurs.prenon, Collaborateurs.date_entre).filter(  Collaborateurs.nom.like(nom_collab), Collaborateurs.prenon.like(prenom_collab) ).first()
    if u is not None:
        return u.collaborateur_id
    else:
        return 'none'

# Rechercher l'identifiant de l'agence en se basant sur le nom de l'agence
def rechercherAgence(session,nom_agence):
    u = session.query(Agences.agence_id).filter(  Agences.nom.like(nom_agence) ).first()
    if u is not None:
        return u.agence_id
    else:
        return 'none'

# Rechercher l'identifiant de l'entreprise en se basant sur le nom
def rechercherEntreprise(session,nom_entreprise):
    u = session.query(Entreprises.entreprise_id).filter(  Entreprises.nom.like(nom_entreprise) ).first()
    if u is not None:
        return u.entreprise_id
    else:
        return 'none'

# Rechercher l'identifiant de la competence en se basant sur le nom de la competence
def rechercherCompetence(session,nom_competence):
    u = session.query(Competences.competence_id).filter(  Competences.nom.like(nom_competence)).first()
    if u is not None:
        return u.competence_id
    else:
        return 'none'

# Rechercher l'identifiant de la competence en se basant sur le nom de la competence
def rechercherMaxCompetenceId(session):
    u = session.query(Competences.competence_id).order_by( Competences.competence_id.desc()).first()
    if u is not None:
        return u.competence_id
    else:
        return 0

def rechercherMaxEntrepriseId(session):
    u = session.query(Entreprises.entreprise_id).order_by( Entreprises.entreprise_id.desc()).first()
    if u is not None:
        return u.entreprise_id
    else:
        return 0

def rechercherMaxMissionId(session):
    u = session.query(Missions.mission_id).order_by( Missions.mission_id.desc()).first()
    if u is not None:
        return u.mission_id
    else:
        return 0

def rechercherMaxAgenceId(session):
    u = session.query(Agences.agence_id).order_by( Agences.agence_id.desc()).first()
    if u is not None:
        return u.agence_id
    else:
        return 0

def rechercherMaxCollaborateurId(session):
    u = session.query(Collaborateurs.collaborateur_id).order_by( Collaborateurs.collaborateur_id.desc()).first()
    if u is not None:
        return u.collaborateur_id
    else:
        return 0

def calculerScore(session):
    today_date = datetime.date.today()
    dates = session.query(Experiences.competence_id, func.min(Missions.date_debut)).filter(
        Experiences.mission_id == Missions.mission_id).group_by(
        Experiences.competence_id).order_by(Experiences.competence_id).all()
    u = session.query(Missions, Experiences).filter(Missions.mission_id == Experiences.mission_id)
    if u is not None:
        for row in u:
            min_date = dates[row[1].competence_id - 1][1]
            delta = relativedelta.relativedelta(today_date, min_date)
            max_months = delta.years * 12 + delta.months
            scr = integraleRacineCarre(row[0].date_debut, row[0].duree, max_months, min_date)
            x = session.query(Experiences).filter(Experiences.mission_id == row[1].mission_id).filter(
                Experiences.collaborateur_id == row[1].collaborateur_id).filter(
                Experiences.competence_id == row[1].competence_id).update({Experiences.score: scr})
            session.commit()
    else:
        print("Nothing to print")


def integraleLineaire(date_debut, duree, months, min_date):
    max_linear = months ** 2 / 2
    min_delta = relativedelta.relativedelta(date_debut, min_date)
    min_months = min_delta.years*12 + min_delta.months
    max_months = min_months + duree
    return (((max_months**2/2) - (min_months**2/2))/max_linear)*10

def integraleExponentielle(date_debut, duree, months, min_date):
    max_expo = np.exp(months)
    min_delta = relativedelta.relativedelta(date_debut, min_date)
    min_months = min_delta.years*12 + min_delta.months
    max_months = min_months + duree
    return ((np.exp(max_months) - np.exp(min_months))/max_expo)*10

def integraleRacineCarre(date_debut, duree, months, min_date):
    max_racine = 1 / 2 * np.sqrt(months)
    min_delta = relativedelta.relativedelta(date_debut, min_date)
    min_months = min_delta.years*12 + min_delta.months
    max_months = min_months + duree
    return ((1/2*(np.sqrt(max_months) - np.sqrt(min_months)))/max_racine)*10


#----------------------------------------------------------------------------------------------------------------
#-------------------------------- Fonction qui permet de vider la base de données--------------------------------

def vider_base_donnees(session):
    NB_experience_deleted = session.query(Experiences).delete()
    NB_missions_deleted = session.query(Missions).delete()
    NB_competences_deleted = session.query(Competences).delete()
    NB_entreprises_deleted = session.query(Entreprises).delete()
    NB_collaborateurs_deleted = session.query(Collaborateurs).delete()
    session.commit()