#!/bin/env python3

import asyncio
import sys
import time
import re
import datetime

# ----------------------------------------------------------
#  Logable
# ----------------------------------------------------------
logf = None

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
            if logf:
                print(f"[{self.name}] {msg}", file=logf, flush=True)

# ----------------------------------------------------------
#  ACCESSOIRES (Pic et Bar)
# ----------------------------------------------------------
class Pic(Logable):
    """Tickets de commande (pile LIFO)"""
    def __init__(self, name, verbose=True):
        super().__init__(name, verbose)
        self.queue = asyncio.Queue()

    async def embrocher(self, postit):
        await self.queue.put(postit)
        self.log(f"post-it '{postit}' embrochée, {self.queue.qsize()} post-it(s) à traiter")

    async def liberer(self):
        if self.queue.empty():
            return None
        postit = await self.queue.get()
        self.log(f"post-it '{postit}' libéré, {self.queue.qsize()} post-it(s) à traiter")
        return postit

class Bar(Logable):
    """Commandes préparées (FIFO)"""
    def __init__(self, name, verbose=True):
        super().__init__(name, verbose)
        self.queue = asyncio.Queue()

    async def recevoir(self, commande):
        await self.queue.put(commande)
        self.log(f"'{commande}' posée, {self.queue.qsize()} commande(s) à servir")

    async def evacuer(self):
        if self.queue.empty():
            return None
        commande = await self.queue.get()
        self.log(f"'{commande}' évacuée, {self.queue.qsize()} commande(s) à servir")
        return commande

# ----------------------------------------------------------
#  CLIENTS
# ----------------------------------------------------------
class Clients:
    def __init__(self,fname):
        self.commandes = []
        start = time.time()
        fmt = re.compile(r"(\d+)\s+(.*)")
        with open(fname,"r", encoding="utf-8") as f:
            for line in f:
                found = fmt.search(line)
                if found:
                    when = int(found.group(1))
                    what = found.group(2)
                    self.commandes.append((start + when, what.split(",")))
        self.commandes = self.commandes[::-1]  # inverse pour pop()

    async def commande(self):
        if len(self.commandes) == 0:
            return None
        while True:
            if time.time() >= self.commandes[-1][0]:
                return self.commandes.pop()[1]
            await asyncio.sleep(0.1)  # rendre la main à la boucle

# ----------------------------------------------------------
#  EMPLOYÉS
# ----------------------------------------------------------
class Employe(Logable):
    """Base pour Serveur et Bariste"""
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
            await asyncio.sleep(0)  # coopératif

    async def servir(self):
        while True:
            if self.bar.queue.empty() and self.pic.queue.empty() and not self.clients.commandes:
                break
            try:
                commande = await asyncio.wait_for(self.bar.evacuer(), timeout=0.1)
            except asyncio.TimeoutError:
                commande = None
            if commande:
                self.log(f"j'apporte la commande '{commande}'")
                for conso in commande:
                    self.log(f"je sers '{conso}'")
                    await asyncio.sleep(0.3)
            else:
                await asyncio.sleep(0)  # coopératif

class Bariste(Employe):
    async def preparer(self):
        while True:
            if self.pic.queue.empty() and not self.clients.commandes:
                break
            try:
                postit = await asyncio.wait_for(self.pic.liberer(), timeout=0.1)
            except asyncio.TimeoutError:
                postit = None
            if postit:
                self.log(f"je commence la fabrication de '{postit}'")
                for conso in postit:
                    self.log(f"je prépare '{conso}'")
                    await asyncio.sleep(0.4)
                await self.bar.recevoir(postit)
                self.log(f"la commande {postit} est prête")
            else:
                await asyncio.sleep(0)

# ----------------------------------------------------------
#  MAIN
# ----------------------------------------------------------
def usage():
    print(f"usage: {sys.argv[0]} fichier")
    exit(1)

async def main_async(fichier):
    global logf
    logfile = "fichierlog.log"
    print(f"logging in {logfile}...")
    logf = open(logfile,"w", encoding="utf-8")
    print("\n---", file=logf, flush=True)

    les_clients = Clients(fichier)
    le_pic = Pic(name="le_pic", verbose=False)
    le_bar = Bar(name="le_bar", verbose=False)

    bob = Bariste(le_pic, le_bar, les_clients, name="bob", verbose=False)
    alice = Serveur(le_pic, le_bar, les_clients, name="alice", verbose=True)

    # Lancement des tâches concurremment
    await asyncio.gather(
        alice.prendre_commande(),
        bob.preparer(),
        alice.servir()
    )

def main():
    if len(sys.argv) != 2:
        usage()
    fichier = sys.argv[1]
    asyncio.run(main_async(fichier))

if __name__ == "__main__":
    main()
