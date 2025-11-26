#!/bin/env python3
from abc import ABC, abstractmethod
import  time
import datetime
import logging
import threading
import asyncio
import sys
maintenant = datetime.datetime.now()
heure = maintenant.hour
minute = maintenant.minute
seconde = maintenant.second
mon_verrou1 = threading.Lock() 
mon_verrou2 = threading.Lock() 
mon_verrou3 = threading.Lock() 
mon_verrou4 = threading.Lock() 
mon_verrou5= threading.Lock() 
mon_verrou6= threading.Lock() 
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
    def embrocher(self,postit, verbose):
            
            if verbose==2 or verbose==3:
               print(f"[{self.__class__.__name__}] post-it '{postit}' embroché")
            self.liste.append(postit)
            self.etat.append(postit)
            if verbose==3:
               print(f"[{self.__class__.__name__}] état={self.etat}")
            logging.info(f"[{self.__class__.__name__}] le temps d'execution d'embrocher est {time.time()-dateactuale}")
    def liberer(self, index, verbose):
        if not index:
               if len(self.liste)!=0:
                  postit = self.liste.pop()
                  self.etat.remove(postit)
                  if verbose==2 or verbose==3:
                      print(f"[{self.__class__.__name__}] post-it '{postit}' libéré " )
                  return postit
        else:
            if verbose==3:
               print(f"[{self.__class__.__name__}] état={self.etat}")
        logging.info(f"[{self.__class__.__name__}] le temps d'execution de liberer est {time.time()-dateactuale}")
class Bar(Accessoire):
    
    """ Un bar peut recevoir des plateaux, et évacuer le dernier reçu """

    def __init__(self):
        super().__init__()
    def recevoir(self,plateau, verbose):
            self.etat.append(plateau)
            if verbose==2 or verbose==3:
               print(f"[{self.__class__.__name__}]  '{plateau}' reçu" )
            self.liste.append(plateau)
            if verbose==3:
               print(f"[{self.__class__.__name__}] état={self.etat}")
            logging.info(f"[{self.__class__.__name__}] le temps d'execution de recevoir est {time.time()-dateactuale}")
    def evacuer(self, index, postit, verbose):
        if not index :
               self.liste.remove(postit)
               if verbose==2 or verbose==3:
                  print(f"[{self.__class__.__name__}]  '{postit}' évacué")
               return postit
        else:
            if verbose==3:
                print(f"[{self.__class__.__name__}]  état={self.etat}")
        logging.info(f"[{self.__class__.__name__}] le temps d'execution d'evacuer est {time.time()-dateactuale}")

class Serveur(threading.Thread):
    def __init__(self, Pic, Bar, commandes, verbose):
        threading.Thread.__init__(self)
        self.pic = Pic
        self.bar = Bar
        self.verbose=verbose
        self.commandeclient=[]
        self.commandes = commandes
    def getlongueur_commande(self):
        return len(self.commandes)
    
    async def prendre_commande(self):
        print(f"[{self.__class__.__name__}] je suis prêt pour le service")
        commandes = list(reversed(self.commandes))
        commande =list(reversed(commandes))
        for _ in  range(len(commande)):
               postit = commande.pop()
               print(f"[{self.__class__.__name__}] je prends commande de '{postit}'")
               #await self.pic.embrocher(postit, self.verbose)
               self.pic.embrocher(postit, self.verbose)
               logging.info(f"[{self.__class__.__name__}] le temps d'execution de prendre commande est {time.time() - dateactuale}")
               await asyncio.sleep(0.4)
        print(f"[{self.__class__.__name__}] il n'y a plus de commande à prendre")
        if self.verbose==2 or self.verbose==3:
           print("plus de commande à prendre")
        logging.info(f"[{self.__class__.__name__}] le temps d'execution de prendre commande est {time.time() - dateactuale}")
        

    async def servirr(self):
            for _ in range(len(self.commandes)):
                   while len(self.bar.etat)==0:
                        #time.sleep(1)
                        pass
                   postit= self.bar.etat.pop()
                   print(f" [{self.__class__.__name__}] je sers '{postit}'")
                   self.commandeclient.append(self.bar.evacuer(False, postit, self.verbose))
                   logging.info(f"[{self.__class__.__name__}] le temps d'execution de servir est {time.time() - dateactuale}")
                   await asyncio.sleep(1.5)
            self.bar.evacuer(True, postit, self.verbose)
            logging.info(f"[{self.__class__.__name__}] le temps d'execution de servir est {time.time() - dateactuale}")
    

    async def main2(self):
         await asyncio.gather(self.prendre_commande(),self.servirr())
    
    
    def run(self):
        asyncio.run(self.main2())
         
class Barman(threading.Thread):
    def __init__(self, Pic, Bar, server, verbose):
        threading.Thread.__init__(self)
        print(f" [{self.__class__.__name__}] je suis prêt pour le service ")
        self.pic = Pic
        self.bar = Bar
        self.server = server
        self.verbose=verbose

    async def preparer(self):
            
            for _ in  range(len(self.server.commandes)):        
                    postit = self.pic.liberer(index=False, verbose=self.verbose)
                    while postit is None:
                        #time.sleep(1) 
                        postit = self.pic.liberer(index=False, verbose=self.verbose)
                    print(f" [{self.__class__.__name__}] je commence la fabrication '{postit}' ")
                    print(f" [{self.__class__.__name__}] je termine la fabrication '{postit}' ")
                    self.bar.recevoir(postit, self.verbose)
                    logging.info(f"[{self.__class__.__name__}] le temps d'execution de préparer est {time.time() - dateactuale}")
                    await asyncio.sleep(1)

            self.pic.liberer(index=True, verbose=self.verbose)
            
            if self.verbose==2 or self.verbose==3:
               print("Pic est vide")
            logging.info(f"[{self.__class__.__name__}] le temps d'execution de préparer est {time.time() - dateactuale}")


    async def encaisser(self):
         for _ in range(len(self.server.commandes)):
                   
                   while len(self.server.commandeclient)==0:
                        #time.sleep(1)
                        pass
                   while len(self.server.commandeclient)!=0:
                      postit= self.server.commandeclient.pop()
                      if self.verbose==2 or self.verbose==3:
                         print(f" [{self.__class__.__name__}] j'encaisse le client qui a demandé la commande '{postit}'")
                   logging.info(f"[{self.__class__.__name__}] le temps d'execution de encaisser est {time.time() - dateactuale}")
                   await asyncio.sleep(1)
         logging.info(f"[{self.__class__.__name__}] le temps d'execution de encaisser est {time.time() - dateactuale}")    
    async def main1(self):
         await asyncio.gather(self.preparer(),self.encaisser())

    def run(self):
        asyncio.run(self.main1())

def main():

    commandes = sys.argv[1:]
    pic=Pic()
    bar = Bar()
    verbose =int(input("Pour avoir le permier affichage taper 1, pour le deuxieme taper 2 et pour le dernier taper 3 "))

    
    while verbose < 1 or 3 < verbose:
         print("S'il vous plait la verbosité doit entre 1 et 3")
         verbose =int(input("pour avoir le permier affichage taper 1, pour le deuxieme taper 2 et pour le dernier taper 3 "))

    serveur = Serveur(pic, bar, commandes, verbose)
    barman = Barman(pic, bar, serveur, verbose)
   
    serveur.start()
    barman.start()
    serveur.join()
    barman.join()

if __name__ == "__main__":
    main()