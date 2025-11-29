#!/bin/env python3

import threading
import time
from collections import deque

# ----------------------------------------------------------
#  Classes de base
# ----------------------------------------------------------

class Accessoire:
    pass

# Pic = tickets de commande (FIFO)
class Pic(Accessoire):
    def __init__(self):
        self.postits = deque()
        self.lock = threading.Lock()

    def embrocher(self, postit):
        with self.lock:
            self.postits.append(postit)

    def liberer(self):
        with self.lock:
            if self.postits:
                return self.postits.popleft()  # FIFO
            return None

# Bar = commandes prêtes (FIFO)
class Bar(Accessoire):
    def __init__(self):
        self.plateaux = deque()
        self.lock = threading.Lock()

    def recevoir(self, plateau):
        with self.lock:
            self.plateaux.append(plateau)

    def evacuer(self):
        with self.lock:
            if self.plateaux:
                return self.plateaux.popleft()  # FIFO
            return None

# ----------------------------------------------------------
#  Serveur
# ----------------------------------------------------------

class Serveur:
    def __init__(self, pic, bar):
        self.pic = pic
        self.bar = bar
        print("Serveur: prêt pour le service")

    def prendre_commande(self, commandes):
        for c in commandes:
            print(f"Serveur: prêt pour prendre une commande : {c}")
            print(f"Serveur: j'ai la commande '{c}'")
            liste = c.split(",")
            print(f"Serveur: j'écris sur le post-it '{liste}'")
            self.pic.embrocher(liste)
            time.sleep(0.3)

        print("Serveur: prêt pour prendre une commande : ")

    def servir(self):
        while True:
            plateau = self.bar.evacuer()
            if plateau:
                print(f"Serveur: j'apporte la commande '{plateau}'")
                for conso in plateau:
                    print(f"Serveur: je sers '{conso}'")
                    time.sleep(0.3)
            else:
                break

# ----------------------------------------------------------
#  Bariste
# ----------------------------------------------------------

class Bariste:
    def __init__(self, pic, bar):
        self.pic = pic
        self.bar = bar
        print("Bariste: prêt pour le service")

    def preparer(self):
        while True:
            commande = self.pic.liberer()
            if commande:
                print(f"Bariste: je commence la fabrication de '{commande}'")
                for conso in commande:
                    print(f"Bariste: je prépare '{conso}'")
                    time.sleep(0.4)

                self.bar.recevoir(commande)
                print(f"Bariste: la commande {commande} est prête")
            else:
                break

# ----------------------------------------------------------
#  Main
# ----------------------------------------------------------

def main():
    pic = Pic()
    bar = Bar()

    commandes = [
        "planteur,piña colada",
        "tequila sunrise,margarita"
    ]

    bariste = Bariste(pic, bar)
    serveur = Serveur(pic, bar)

    # Lancement des threads
    t1 = threading.Thread(target=serveur.prendre_commande, args=(commandes,))
    t2 = threading.Thread(target=bariste.preparer)

    t1.start()
    t1.join()

    t2.start()
    t2.join()

    serveur.servir()

if __name__ == "__main__":
    main()
