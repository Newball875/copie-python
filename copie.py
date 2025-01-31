# Python 3.12

import sys
from io import StringIO
import configparser
import json
import os
import pandas as pd
import subprocess

# On dit si on envoie sur le disque ou l'inverse
to_disque = True
to_force = False
if(len(sys.argv) > 1):
	match sys.argv[1]:
		case '0':
			pass
		case '1':
			to_disque = False
		case '2':
			to_force = True
		case '3':
			to_disque = False
			to_force = True
		case _:
			print("Mauvais argement passé en paramètre !")
			print("Voici les arguments :")
			print("\t 0 => Serveur vers Disque normal")
			print("\t 1 => Disque vers Serveur normal")
			print("\t 2 => Serveur vers Disque force")
			print("\t 3 => Disque vers Serveur force")
			print("\t autre => Affichage de cette aide")
			exit(0)
			
# On lit le fichier de config
config = configparser.ConfigParser()
config.read("config.ini")
config = config["DOSSIERS"]

# On définit les tableaux de sources et de dossiers racines
sources = json.loads(config["sources"])
racines = json.loads(config["racines"])

# On définit les grandes sources
disque = sources[0]
serveur = sources[1]

# On définit tous les sous-dossiers
df = pd.read_json(StringIO(config["racines"]))
df.columns = ["disque", "serveur"]

i=0
while i<len(df):
	# D'abord, on définit la source et la destination
	if to_disque:
		root = serveur + df["serveur"][i]
		dest = disque + df["disque"][i]
	else:
		dest = serveur + df["serveur"][i]
		root = disque + df["disque"][i]
		
	# Ensuite, on doit voir si la racine de la destination existe
	if not os.path.isdir(dest):
		subprocess.run(["mkdir", "-p", dest])
	
	# Ensuite on parcourt tous les fichiers du dossier de l'origine
	for racine, dossiers, fichiers in os.walk(root):
		split = racine.split(root)
		split.remove('')
		for fichier in fichiers:
			origin = ''
			destination = ''
			# On définit le fichier d'origine, et son emplacement de destination
			if split[0] == '':
				origin = root+'/'+fichier
				destination = dest+"/"
			else:
				origin = root+split[0]+"/"+fichier
				destination = dest+split[0]+"/"
				
			# On vérifie si le fichier n'est pas déjà présent et s'il existe
			if to_force or (not os.path.isfile(destination+fichier) and os.path.isfile(origin)):
				# Si c'est le cas, on le copie, en créeant les sous-dossiers nécessaires
				if(to_force):
					print(origin + " envoyé de force à " + destination)
				else:
					print(origin + " envoyé à " + destination)
				subprocess.run(["rsync", "-a", origin, destination])
	i=i+1