import random

type = ("Mention", "Loi", "Projet", "Déclaration", "Réforme", "Campagne")
nouns_fascist = ("Censure", "Collectivisation", "Militarisation", "Protection", "Relance", "Taxe", "Purge", "Discrédit", "Privatisation", "Confiscation", "Recensement", "Revue")
nouns_liberal = ("Libéralisation", "Congolexicomatisation", "Négociation", "Paix", "Médecine", "Démilitarisation", "Diplomatie", "Prudence", "Diagnostic", "Sollicitude", "Souvenir")
adjectives = ("agressive", "générale", "rapide", "locale", "douce", "intrinsèque", "crédible", "correcte", "exceptionnelle", "banale", "forte", "festive", "admirable", "absolue", "nationale", "équitable", "orthogonale", "approximative", "médiocre", "relative")

def get_law_name(pattern):
    return pattern.format(type = random.choice(type), noun_fascist = random.choice(nouns_fascist), noun_liberal = random.choice(nouns_liberal), adjective = random.choice(adjectives))
