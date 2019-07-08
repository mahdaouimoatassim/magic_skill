
#!pip install SQLAlchemyAPI

from SQLAlchemyAPI import *
from magic_cv_api import *
import wikipedia
import spacy
import sys

from spacy.lang.fr.examples import sentences
nlp_fr = spacy.load('fr_core_news_sm')
nlp_en = spacy.load('en_core_web_sm')

# Debut du decompte du temps
start_time = time.time()

# Mettez votre code ici…

# Affichage du temps d execution

from os import listdir
#print(listdir("C:/Users/e.mahdaoui/Desktop/Stage Fin d'Etude/Application MagicSkills/Code Python"))
#Dossier_cv='C:/Users/e.mahdaoui/Desktop/Stage Fin d\'Etude/Application MagicSkills/Code Python'
#sys.argv[1]='C:/Users/e.mahdaoui/Desktop/Stage Fin d\'Etude/Application MagicSkills/Code Python'

#print(sys.argv[1])


#folder = "C:/Users/e.mahdaoui/Desktop/Projet Magic Skills"
##extraction_competence_process(sys.argv[1])
vider_base_donnees(session)
extraction_competence_process(folder)


#print(wikipedia.search("google"))
#wikipedia.set_lang("fr")

#ny2 = wikipedia.page("leroy merlin", preload=True)


#tableau=ny2.content.split('\n')
#print(tableau[0])

#print(wikipedia.summary("ELIGI"))



#u = session.query(Entreprises.nom)

#for i in u:
#    print(str(i)+'---'+str(chercher_secteur_activite_entreprise(i)))


""""
#print(chercher_secteur_activite_entreprise(""))

def motPhrase(doc):
    for token in doc:
        print(token.text, token.pos_, token.dep_)
    return 1

doc = nlp_fr('banque , assurance , grande distribution, retial, energitique')
motPhrase(doc)
"""
session.commit()
session.close()

#for arg in sys.argv:
#    print( sys.argv[1])

print("Temps d execution : %s secondes ---" % (time.time() - start_time))


