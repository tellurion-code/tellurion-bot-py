import random

type = ("Mention", "Loi", "Projet", "Déclaration", "Réforme", "Campagne")
nouns_fascist = ("Censure", "Collectivisation", "Militarisation", "Relance", "Taxe", "Purge", "Privatisation", "Confiscation", "Revue", "Délibération")
nouns_liberal = ("Libéralisation", "Congolexicomatisation", "Négociation", "Paix", "Médecine", "Démilitarisation", "Prudence", "Sollicitude", "Projection", "Protection")
adjectives = ("agressive", "générale", "rapide", "locale", "douce", "intrinsèque", "crédible", "correcte", "exceptionnelle", "banale", "forte", "festive", "admirable", "absolue", "nationale", "équitable", "orthogonale", "approximative", "médiocre", "relative")

def get_law_name(pattern):
    return pattern.format(type = random.choice(type), noun_fascist = random.choice(nouns_fascist), noun_liberal = random.choice(nouns_liberal), adjective = random.choice(adjectives))
