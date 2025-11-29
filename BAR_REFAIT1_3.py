#!/bin/env python3

import threading
import time
import re
import sys
from collections import deque
import datetime
import logging
# ----------------------------------------------------------
#  Logable
# ----------------------------------------------------------

# Obtenez l'heure actuelle
maintenant = datetime.datetime.now()
# Extrayez l'heure, les minutes et les secondes
heure = maintenant.hour
minute = maintenant.minute
seconde = maintenant.second

logging.basicConfig(filename=f"execution_{datetime.date.today()}'_'{heure}'_' {minute}'_'{seconde}",
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')



class Logable:
    """
    Classe de base pour disposer d'une méthode log
    """
    def __init__(self, name, verbose=True):
        self.name = name
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(f"[{self.name}] {msg}")
            print(f"[{self.name}] {msg}", file=logf, flush=True)

# ----------------------------------------------------------
#  ACCESSOIRES
# ----------------------------------------------------------

class Accessoire(Logable, deque):
    """Classe de base pour Pic et Bar"""
    def __init__(self, name, verbose=True):
        Logable.__init__(self, name, verbose)
        self.lock = threading.Lock()
        self.items = deque()

class Pic(Accessoire):
    """Tickets de commande (FIFO)"""
    def embrocher(self, postit):
        with self.lock:
            self.items.append(postit)
            self.log(f"post-it '{postit}' embrochée, {len(self.items)} post-it(s) à traiter")

    def liberer(self):
        with self.lock:
            if self.items:
                postit = self.items.popleft()
                self.log(f"post-it '{postit}' libéré, {len(self.items)} post-it(s) à traiter")
                return postit
            return None

class Bar(Accessoire):
    """Commandes préparées (FIFO)"""
    def recevoir(self, commande):
        with self.lock:
            self.items.append(commande)
            self.log(f"'{commande}' posée, {len(self.items)} commande(s) à servir")

    def evacuer(self):
        with self.lock:
            if self.items:
                commande = self.items.popleft()
                self.log(f"'{commande}' évacuée, {len(self.items)} commande(s) à servir")
                return commande
            return None

# ----------------------------------------------------------
#  CLIENTS
# ----------------------------------------------------------

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

# ----------------------------------------------------------
#  EMPLOYÉS
# ----------------------------------------------------------

class Employe(Logable):
    """Base pour Serveur et Bariste"""
    def __init__(self, pic, bar, clients, name, verbose=True):
        Logable.__init__(self, name, verbose)
        self.pic = pic
        self.bar = bar
        self.clients = clients
        self.step = 0
        self.log("prêt pour le service")

class Serveur(Employe):
    def prendre_commande(self):
        while True:
            cmd = self.clients.commande()
            if not cmd:
                break
            self.log("prêt pour prendre une nouvelle commande...")
            self.log(f"j'ai la commande '{cmd}'")
            self.log(f"j'écris sur le post-it '{cmd}'")
            self.pic.embrocher(cmd)

    def servir(self):
        while True:
            plateau = self.bar.evacuer()
            if plateau:
                self.log(f"j'apporte la commande '{plateau}'")
                for conso in plateau:
                    self.log(f"je sers '{conso}'")
                    time.sleep(0.3)
            else:
                break

class Bariste(Employe):
    def preparer(self):
        while True:
            cmd = self.pic.liberer()
            if cmd:
                self.log(f"je commence la fabrication de '{cmd}'")
                for conso in cmd:
                    self.log(f"je prépare '{conso}'")
                    time.sleep(0.4)
                self.bar.recevoir(cmd)
                self.log(f"la commande {cmd} est prête")
            else:
                break

# ----------------------------------------------------------
#  MAIN
# ----------------------------------------------------------

def usage():
    print(f"usage: {sys.argv[0]} fichier")
    exit(1)

def main():
    if len(sys.argv) != 2:
        usage()
    fichier = sys.argv[1]

    global logf
    logfile = "fichierlog.log"
    print(f"logging in {logfile}...")
    logf = open(logfile,"w", encoding="utf-8")
    print("\n---", file=logf, flush=True)

    les_clients = Clients(fichier)

    # Création des accessoires et employés avec logging
    le_pic = Pic(name="le_pic", verbose=False)
    le_bar = Bar(name="le_bar", verbose=False)

    bob = Bariste(le_pic, le_bar, les_clients, name="bob", verbose=False)
    alice = Serveur(le_pic, le_bar, les_clients, name="alice", verbose=True)

    # Threads pour serveur et bariste
    t_serveur = threading.Thread(target=alice.prendre_commande)
    t_bariste = threading.Thread(target=bob.preparer)

    t_serveur.start()
    t_serveur.join()

    t_bariste.start()
    t_bariste.join()

    alice.servir()

if __name__ == "__main__":
    main()
