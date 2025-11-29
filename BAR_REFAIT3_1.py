#!/bin/env python3

import asyncio
import sys
import time
import re

# -------------------- Logable --------------------

class Logable:
    def __init__(self, name, verbose=True):
        self.name = name
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(f"[{self.name}] {msg}", flush=True)

# -------------------- Accessoires --------------------

class Pic(Logable):
    """Pile LIFO des post-its (commandes à préparer)"""
    def __init__(self, name, verbose=True):
        super().__init__(name, verbose)
        self.queue = asyncio.LifoQueue()

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
    """File FIFO des commandes prêtes à servir"""
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

# -------------------- Clients --------------------

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
        if len(self.commandes) == 0:
            return None
        while True:
            if time.time() >= self.commandes[-1][0]:
                return self.commandes.pop()[1]
            await asyncio.sleep(0.05)  # rend la main à la boucle

# -------------------- Employés --------------------

class Employe(Logable):
    """Base pour Serveur et Bariste"""
    def __init__(self, pic, bar, clients, name, verbose=True):
        super().__init__(name, verbose)
        self.pic = pic
        self.bar = bar
        self.clients = clients

class Serveur(Employe):
    """Serveur: prend les commandes et sert"""
    async def prendre_commande(self):
        while True:
            cmd = await self.clients.commande()
            if not cmd:
                break
            self.log("prêt pour prendre une nouvelle commande...")
            self.log(f"j'ai la commande '{cmd}'")
            self.log(f"j'écris sur le post-it '{cmd}'")
            await self.pic.embrocher(cmd)
            await asyncio.sleep(0)  # rend la main

    async def servir(self):
        while True:
            commande = await self.bar.evacuer()
            if commande is None:
                break
            self.log(f"j'apporte la commande '{commande}'")
            for conso in commande:
                self.log(f"je sers '{conso}'")
                await asyncio.sleep(0.3)  # temps de service
            await asyncio.sleep(0)  # rend la main

class Bariste(Employe):
    """Bariste: prépare les commandes"""
    async def preparer(self):
        while True:
            cmd = await self.pic.liberer()
            if cmd is None:
                break
            self.log(f"je commence la fabrication de '{cmd}'")
            for conso in cmd:
                self.log(f"je prépare '{conso}'")
                await asyncio.sleep(0.4)  # temps de préparation
            await self.bar.recevoir(cmd)
            self.log(f"la commande {cmd} est prête")
            await asyncio.sleep(0)  # rend la main

# -------------------- MAIN --------------------

def usage():
    print(f"usage: {sys.argv[0]} fichier")
    sys.exit(1)

async def main_async(fichier):
    clients = Clients(fichier)

    le_pic = Pic(name="le_pic", verbose=False)
    le_bar = Bar(name="le_bar", verbose=False)

    # Bariste
    bob = Bariste(le_pic, le_bar, clients, name="bob", verbose=True)
    
    # Deux serveurs
    alice = Serveur(le_pic, le_bar, clients, name="alice", verbose=True)
    prosper = Serveur(le_pic, le_bar, clients, name="prosper", verbose=True)

    # Lancement concurrent: serveurs prennent commandes + bariste prépare
    await asyncio.gather(
        alice.prendre_commande(),
        prosper.prendre_commande(),
        bob.preparer()
    )

    # Ensuite, serveurs servent les commandes en parallèle
    await asyncio.gather(
        alice.servir(),
        prosper.servir()
    )

def main():
    if len(sys.argv) != 2:
        usage()
    fichier = sys.argv[1]
    asyncio.run(main_async(fichier))

if __name__ == "__main__":
    main()
