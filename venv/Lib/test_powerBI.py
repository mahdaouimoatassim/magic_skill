

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Boolean, Date, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import or_
import hashlib

Base = declarative_base()
engine = create_engine('postgresql://postgres:postgresql123@localhost:5433/magic_skill')
DBSession = sessionmaker(bind=engine)
session = DBSession()
conn = engine.connect()
#-------------------------------------- Declaration des tables  ---------------------------------------------------------

#-------------------------------------- Declaration des tables  ---------------------------------------------------------
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


# Table Entreprises
class Entreprises(Base):
    __tablename__ = 'entreprises'
    entreprise_id = Column(Integer, primary_key=True)
    nom = Column(String(50))
    secteur_activite = Column(String(50))
    region = Column(String(50))


# Table Missions
class Missions(Base):
    __tablename__ = 'missions'
    mission_id = Column(Integer, primary_key=True)
    entreprise_id = Column(Integer, ForeignKey('entreprises.entreprise_id'))
    description_mission = Column(Text)
    date_debut = Column(Date)
    date_fin = Column(Date)


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

#-------------------------------------- la partie des requetes---------------------------------------------------------
session.add_all([
         Agences(agence_id=15,nom='Agence de lille',adresse='318 rue de Fougères	N° SIRET 4843484870001435200 Rennes',ville='Lille')
    ])
session.commit()
session.close()

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
    u = session.query(Competences.competence_id).filter(  Competences.nom.like(nom_competence) ).first()
    if u is not None:
        return u.competence_id
    else:
        return 'none'
