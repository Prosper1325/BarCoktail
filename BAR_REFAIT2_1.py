#!/bin/env python3

import asyncio
import time
import re
import sys
from collections import deque
import datetime

# ----------------------------------------------------------
#  Logable
# ----------------------------------------------------------
class Logable:
    def __init__(self, name, verbose=True):
        self.name = name
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(f"[{self.name}] {msg}", flush=True)
            print(f"[{self.name}] {msg}", file=logf, flush=True)

# ----------------------------------------------------------
#  ACCESSOIRES
# ----------------------------------------------------------
class Accessoire(Logable):
    def __init__(self, name, verbose=True):
        super().__init__(name, verbose)
        self.items = deque()
        self.lock = asyncio.Lock()

class Pic(Accessoire):
    async def embrocher(self, postit):
        async with self.lock:
            self.items.append(postit)
            self.log(f"post-it '{postit}' embrochée, {len(self.items)} post-it(s) à traiter")

    async def liberer(self):
        async with self.lock:
            if self.items:
                postit = self.items.popleft()
                self.log(f"post-it '{postit}' libéré, {len(self.items)} post-it(s) à traiter")
                return postit
            return None

class Bar(Accessoire):
    async def recevoir(self, commande):
        async with self.lock:
            self.items.append(commande)
            self.log(f"'{commande}' posée, {len(self.items)} commande(s) à servir")

    async def evacuer(self):
        async with self.lock:
            if self.items:
                commande = self.items.popleft()
                self.log(f"'{commande}' évacuée, {len(self.items)} commande(s) à servir")
                return commande
            return None

# ----------------------------------------------------------
#  CLIENTS
# ----------------------------------------------------------
class Clients:
    def __init__(self, fname):
        self.commandes = []
        start = time.time()
        fmt = re.compile(r"(\d+)\s+(.*)")
        with open(fname, "r", encoding="utf-8") as f:
            for line in f:
                found = fmt.search(line)
                if found:
                    when = int(found.group(1))
                    what = found.group(2)
                    self.commandes.append((start + when, what.split(",")))
        self.commandes = self.commandes[::-1]  # inverse pour pop()

    async def commande(self):
        if self.commandes:
            while True:
                if time.time() >= self.commandes[-1][0]:
                    return self.commandes.pop()[1]
                await asyncio.sleep(0.05)
        else:
            return None

# ----------------------------------------------------------
#  EMPLOYÉS
# ----------------------------------------------------------
class Employe(Logable):
    def __init__(self, pic, bar, clients, name, verbose=True):
        super().__init__(name, verbose)
        self.pic = pic
        self.bar = bar
        self.clients = clients

class Serveur(Employe):
    async def prendre_commande(self):
        while True:
            cmd = await self.clients.commande()
            if cmd is None:
                break
            self.log("prêt pour prendre une nouvelle commande...")
            self.log(f"j'ai la commande '{cmd}'")
            self.log(f"j'écris sur le post-it '{cmd}'")
            await self.pic.embrocher(cmd)

    async def servir(self):
        while True:
            plateau = await self.bar.evacuer()
            if plateau is None:
                await asyncio.sleep(0.05)
                continue
            self.log(f"j'apporte la commande '{plateau}'")
            for conso in plateau:
                self.log(f"je sers '{conso}'")
                await asyncio.sleep(0.3)
            # terminer si plus de commandes et pic vide
            if not self.bar.items and not self.pic.items:
                break

class Bariste(Employe):
    async def preparer(self):
        while True:
            postit = await self.pic.liberer()
            if postit is None:
                await asyncio.sleep(0.05)
                if not self.clients.commandes and not self.pic.items:
                    break
                continue
            self.log(f"je commence la fabrication de '{postit}'")
            for conso in postit:
                self.log(f"je prépare '{conso}'")
                await asyncio.sleep(0.4)
            await self.bar.recevoir(postit)
            self.log(f"la commande {postit} est prête")

# ----------------------------------------------------------
#  MAIN
# ----------------------------------------------------------
def usage():
    print(f"usage: {sys.argv[0]} fichier")
    exit(1)

async def main():
    if len(sys.argv) != 2:
        usage()
    fichier = sys.argv[1]

    global logf
    logfile = "fichierlog.log"
    print(f"logging in {logfile}...")
    logf = open(logfile, "w", encoding="utf-8")
    print("\n---", file=logf, flush=True)

    les_clients = Clients(fichier)

    le_pic = Pic(name="le_pic", verbose=False)
    le_bar = Bar(name="le_bar", verbose=False)
    bob = Bariste(le_pic, le_bar, les_clients, name="bob", verbose=True)
    alice = Serveur(le_pic, le_bar, les_clients, name="alice", verbose=True)

    # lancement concurrent des 3 tâches
    await asyncio.gather(
        alice.prendre_commande(),
        bob.preparer(),
        alice.servir()
    )

if __name__ == "__main__":
    asyncio.run(main())

# Effectivement toutes les taches ne sont pas terminées en même temps