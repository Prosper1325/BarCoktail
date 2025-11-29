#!/bin/env python3
import threading 

import sys
import  time
import datetime
import logging
import asyncio

# Obtenez l'heure actuelle
maintenant = datetime.datetime.now()
# Extrayez l'heure, les minutes et les secondes
heure = maintenant.hour
minute = maintenant.minute
seconde = maintenant.second

logging.basicConfig(filename=f"execution_{datetime.date.today()}'_'{heure}'_' {minute}'_'{seconde}", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
dateactuale=time.time()
class Accessoire:
    def __init__(self) : 
      self.liste=[]
      self.etat=[]

class Pic(Accessoire):
    
    """ Un pic peut embrocher un post-it par-dessus les post-it déjà présents
        et libérer le dernier embroché. """
    def __init__(self):
        super().__init__()
    def embrocher(self,postit):
        
        print(f"[{self.__class__.__name__}] post-it '{postit}' embroché")
        self.liste.append(postit)
        self.etat.append(postit)
        print(f"[{self.__class__.__name__}] état={self.etat}")

        logging.info(f"[{self.__class__.__name__}] le temps d'execution d'embrocher est {time.time()-dateactuale}")
    def liberer(self, index):
        if not index:
           #print(f"[{self.__class__.__name__}] état={Pic.etat}")
           postit = self.liste.pop()
           self.etat.remove(postit)
           print(f"[{self.__class__.__name__}] post-it '{postit}' libéré " )
           return postit
        else:
            print(f"[{self.__class__.__name__}] état={self.etat}")

        logging.info(f"[{self.__class__.__name__}] le temps d'execution de liberer est {time.time()-dateactuale}")
class Bar(Accessoire):
    
    """ Un bar peut recevoir des plateaux, et évacuer le dernier reçu """

    def __init__(self):
        super().__init__()
    async def recevoir(self,plateau):
       
        self.etat.append(plateau)
        print(f"[{self.__class__.__name__}]  '{plateau}' reçu" )
        self.liste.append(plateau)
        print(f"[{self.__class__.__name__}] état={self.etat}")

        logging.info(f"[{self.__class__.__name__}] le temps d'execution de recevoir est {time.time()-dateactuale}")
    def evacuer(self, index):
        if not index:
           #print(f"[{self.__class__.__name__}]  état={Bar.etat}")
           plateau = self.liste.pop()
           print(f"[{self.__class__.__name__}]  '{plateau}' évacué")
           self.etat.remove(plateau)
           return plateau
        else:
            print(f"[{self.__class__.__name__}]  état={self.etat}")

        logging.info(f"[{self.__class__.__name__}] le temps d'execution d'evacuer est {time.time()-dateactuale}")



class Serveur:
    def __init__(self, Pic, Bar, commandes):
        self.pic = Pic
        self.bar = Bar
        self.commandes = commandes
        self.lock = threading.Lock()  

    def getlongueur_commande(self):
        return len(self.commandes)

    def prendre_commande(self):
        """ Prend une commande et embroche un post-it. """
        print(f"[{self.__class__.__name__}] je suis prêt pour le service")
        commandes = list(reversed(self.commandes))

        for i in range(len(commandes)):
            print(f"[{self.__class__.__name__}] je prends commande de '{commandes[i]}'")

            self.pic.embrocher(commandes[i])  # No need to await in threads
            time.sleep(1)
        print(f"[{self.__class__.__name__}] il n'y a plus de commande à prendre")
        print("plus de commande à prendre")
        logging.info(f"[{self.__class__.__name__}] le temps d'execution de prendre commande est {time.time() - dateactuale}")

    def servir(self):
        """ Prend un plateau sur le bar. """
        for _ in range(len(self.commandes)):
            print(f" [{self.__class__.__name__}] je sers '{self.bar.liste[0]}'")
            self.bar.evacuer(False)  # No need to await in threads
            time.sleep(1)
        self.bar.evacuer(True)
        print(" Bar est vide")

        logging.info(f"[{self.__class__.__name__}] le temps d'execution de servir est {time.time() - dateactuale}")

class Barman:

    def __init__(self, Pic, Bar, server):
        print(f" [{self.__class__.__name__}] je suis prêt pour le service ")
        self.pic = Pic
        self.bar = Bar
        self.server = server

    def preparer(self):
        """ Prend un post-it, prépare la commande et la dépose sur le bar. """
        for _ in range(self.server.getlongueur_commande()):
            postit = self.pic.liberer(index=False)
            print(f" [{self.__class__.__name__}] je commence la fabrication '{postit}' ")
            print(f" [{self.__class__.__name__}] je termine la fabrication '{postit}' ")
            self.bar.recevoir(postit)  # No need to await in threads
            time.sleep(1)
        self.pic.liberer(index=True)
        print("Pic est vide")
        logging.info(f"[{self.__class__.__name__}] le temps d'execution de préparer est {time.time() - dateactuale}")

def main():
    commandes = sys.argv[1:]

    pic = Pic()
    bar = Bar()
    serveur = Serveur(pic, bar, commandes)
    barman = Barman(pic, bar, serveur)

    # Create threads for each operation
    prendre_commande_thread = threading.Thread(target=serveur.prendre_commande)
    preparer_thread = threading.Thread(target=barman.preparer)
    servir_thread = threading.Thread(target=serveur.servir)

    # Start the threads
    prendre_commande_thread.start()
    preparer_thread.start()
    servir_thread.start()

    # Wait for all threads to finish
    prendre_commande_thread.join()
    preparer_thread.join()
    servir_thread.join()

if __name__ == "__main__":
    main()