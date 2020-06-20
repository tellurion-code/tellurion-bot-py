import random

type = ("Mention", "Loi", "Projet", "Déclaration", "Réforme", "Campagne")
nouns_fascist = ("Censure", "Congolexicomatisation", "Collectivisation", "Militarisation", "Protection", "Relance", "Taxe", "Purge", "Discrédit", "Privatisation", "Confiscation", "Evalutaion")
nouns_liberal = ("Libéralisation", "Congolexicomatisation", "Négociation", "Paix", "Expédition", "Médecine", "Démilitarisation", "Diplomatie", "Prudence", "Attention")
adjectives = ("agressive", "générale", "rapide", "locale", "cool", "intrinsèque", "crédible", "exceptionnelle", "banale", "forte", "festive", "admirable", "absolue", "nationale", "équitable", "orthogonale")

def get_law_name(pattern):
    return pattern.format(type = random.choice(type), noun_fascist = random.choice(nouns_fascist), noun_liberal = random.choice(nouns_liberal), adjective = random.choice(adjectives))
