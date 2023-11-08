# ~ Lis une DB
def read_db(filename:str):
	database = list()
	with open(filename, 'r') as file:
		for line in file:
			ligne = list()
			word = ""
			sList = list()
			if not line[-1] == '!':
				line += '!'
			for elt in line:
				if elt != '!' and elt != ';':
					word += elt
				elif elt == ';':
					sList.append(word.strip())
					word = ""
				elif elt == '!':
					if len(sList) != 0:
						ligne.append(sList)
						sList = list()
					else:
						ligne.append(word.strip())
						word = ""
			database.append(ligne)
	return database

# ~ Copie une DB en supprimant une ligne
# ~ nom de fichier + début de la ligne à supprimer
def copy_without(filename:str, line_start:str):
	with open(filename, "r") as file:
		lines = file.readlines()

	with open(filename, "w") as file:
		for line in lines:
			if not line.startswith(line_start):
				file.write(line)

# ~ Écris dans une DB, mode "w" ou "a" sinon erreur
# ~ nom de fichier + liste de listes
def write_db(filename:str, content:list, mode="w"):
	with open(filename, mode) as file:
		for line in content:
			for elt in line:
				if type(elt) in (list, tuple):
					for e in elt:
						file.write(f"{e};")
				else:
					file.write(str(elt))
				file.write("!")
			file.write("\n")

# ~ Modifie les lignes d'une DB existante
# ~ nom de fichier + premier élément de l'ancienne db + nouvelle ligne de la db
# ~ new_lines de la forme ["+", [machin]] va ajouter machin après l'ancien contenu de la ligne
# ~ Les anciens débuts de lignes sont supprimés
def modify_db(filename:str, old_starts:list, new_lines:list):
	db = read_db(filename)
	new_db = list()
	found = [False] * len(old_starts)
	for i in range(len(db)):
		test = True
		for j in range(len(old_starts)):
			if db[i][0] == str(old_starts[j]):
				found[j] = True
				if new_lines[0] == "+":
					nl = db[i]
					for elt in new_lines[j+1]:
						nl.append(elt)
					new_db.append(nl)
				else:
					new_db.append(new_lines[j])
				test = False
		if test:
			new_db.append(db[i])
	for i in range(len(found)):
		if not found[i]:
			new_db.append([old_starts[i], new_lines[i+int(new_lines[0] == "+")]])
			found[i] = True
	write_db(filename, new_db)
