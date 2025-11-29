#!/bin/env python3

import threading
import time
import re
import sys
from collections import deque

# -----------------------------
# ACCESSOIRES
# -----------------------------

class Pic:
    """Contient les tickets de commande (FIFO)"""
    def __init__(self):
        self.postits = deque()
        self.lock = threading.Lock()

    def embrocher(self, postit):
        with self.lock:
            self.postits.append(postit)

    def liberer(self):
        with self.lock:
            if self.postits:
                return self.postits.popleft()
            return None

class Bar:
    """Contient les boissons préparées (FIFO)"""
    def __init__(self):
        self.plateaux = deque()
        self.lock = threading.Lock()

    def recevoir(self, plateau):
        with self.lock:
            self.plateaux.append(plateau)

    def evacuer(self):
        with self.lock:
            if self.plateaux:
                return self.plateaux.popleft()
            return None

# -----------------------------
# CLIENTS
# -----------------------------

class Clients:
    def __init__(self,fname):
        self.commandes = []
        start = time.time()
        fmt = re.compile(r"(\d+)\s+(.*)")
        with open(fname,"r") as f:
            for line in f:
                found = fmt.search(line)
                if found:
                    when = int(found.group(1))
                    what = found.group(2)
                    self.commandes.append((start + when, what.split(",")))
        self.commandes = self.commandes[::-1]  # inverse pour pop()

    def commande(self):
        if len(self.commandes) > 0:
            while True:
                if time.time() >= self.commandes[-1][0]:
                    return self.commandes.pop()[1]
        else:
            return None

# -----------------------------
# ACTEURS
# -----------------------------

class Serveur:
    def __init__(self, pic, bar, clients):
        self.pic = pic
        self.bar = bar
        self.clients = clients
        print("Serveur: prêt pour le service")

    def prendre_commande(self):
        while True:
            cmd = self.clients.commande()
            if not cmd:
                break
            print("Serveur: prêt pour prendre une nouvelle commande...")
            print(f"Serveur: j'ai la commande '{cmd}'")
            print(f"Serveur: j'écris sur le post-it '{cmd}'")
            self.pic.embrocher(cmd)

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

class Bariste:
    def __init__(self, pic, bar):
        self.pic = pic
        self.bar = bar
        print("Bariste: prêt pour le service")

    def preparer(self):
        while True:
            cmd = self.pic.liberer()
            if cmd:
                print(f"Bariste: je commence la fabrication de '{cmd}'")
                for conso in cmd:
                    print(f"Bariste: je prépare '{conso}'")
                    time.sleep(0.4)
                self.bar.recevoir(cmd)
                print(f"Bariste: la commande {cmd} est prête")
            else:
                break

# -----------------------------
# MAIN
# -----------------------------

def usage():
    print(f"usage: {sys.argv[0]} fichier")
    exit(1)

def main():
    if len(sys.argv) != 2:
        usage()
    fichier = sys.argv[1]

    le_pic = Pic()
    le_bar = Bar()
    les_clients = Clients(fichier)

    bariste = Bariste(le_pic, le_bar)
    serveur = Serveur(le_pic, le_bar, les_clients)

    # Threads pour serveur et bariste
    t_serveur = threading.Thread(target=serveur.prendre_commande)
    t_bariste = threading.Thread(target=bariste.preparer)

    t_serveur.start()
    t_serveur.join()

    t_bariste.start()
    t_bariste.join()

    serveur.servir()
if __name__ == "__main__":
    main()
