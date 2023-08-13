import time, datetime as dt
from sys import path
path[:0] = ["../Auxilliaire/"]

from auxilliaire import CustomSession, modify_db
from data_API import token # ~ Le token permettant d'accéder à l'API WG

class Ship:
	def __init__(self, id, session=None):
		self.id = id
		self.request = f"https://api.worldofwarships.eu/wows/encyclopedia/ships/?application_id={token}&ship_id={id}"
		self.s = session
		if self.s == None:
			self.s = CustomSession()
		self.json = self.s.get(self.request).json()
		self.data = self.json["data"][str(id)]

		if self.data == None:
			self.name, self.type, self.tier, self.nation = [None] *4
			return

		self.name = self.data["name"]
		self.type = self.data["type"]
		self.tier = self.data["tier"]
		self.nation = self.data["nation"]

	def __str__(self):
		return f"{self.type} {self.tier} {self.name}"

	def __eq__(self, other):
		if not type(self) == type(other):
			return False
		return self.id == other.id

class Player:
	def __init__(self, id, session=None):
		self.id = id
		self.request = f"https://api.worldofwarships.eu/wows/account/info/?application_id={token}&account_id={id}"
		self.s = session
		if self.s == None:
			self.s = CustomSession()
		self.json = self.s.get(self.request).json()
		self.data = self.json["data"][str(id)]
		self.shipstats = self.s.get(f"https://api.worldofwarships.eu/wows/ships/stats/?application_id={token}&account_id={id}").json()["data"]#[str(id)]
		if not str(id) in self.shipstats:
			print(self.shipstats)
		else:
			self.shipstats = self.shipstats[str(id)]

		self.name = self.data["nickname"]
		ships = [ship["ship_id"] for ship in self.shipstats]
		self.ships = list(map(lambda e: Ship(e, self.s), ships))
		self.discord_mention = self.name

	def __str__(self):
		return f"{self.name}"

	def __len__(self):
		return len(self.ships)

	def __eq__(self, other):
		if not type(self) == type(other):
			return False
		return self.id == other.id

	def __getitem__(self, key):
		return self.ships[key]

	def serialise(self):
		return f"{self.name}!" + "!".join(list(map(lambda e: e.name, self.ships)))

class Clan:
	def __init__(self, id, session=None):
		self.id = id
		self.request = f"https://api.worldofwarships.eu/wows/clans/info/?application_id={token}&clan_id={id}"
		self.s = session
		if self.s == None:
			self.s = CustomSession()
		self.json = self.s.get(self.request).json()
		self.data = self.json["data"][str(id)]

		self.name = self.data["name"]
		self.tag = self.data["tag"]
		self.members = self.data["members_ids"]
		self.leader = self.data["leader_name"]

	def __str__(self):
		return f"[{self.tag}] {self.name}"

	def __len__(self):
		return len(self.members)

	def __eq__(self, other):
		if not type(self) == type(other):
			return False
		return self.id == other.id

	def __getitem__(self, key):
		return self.members[key]

	def getPlayers(self):
		self.members = list(map(lambda e: Player(e, self.s), self.members))

	def serialise(self, filename):
		self.getPlayers()
		modify_db(filename, [p.name for p in self.members], [p.serialise() for p in self.members])
		with open(filename, 'w') as file:
			for player in self.members:
				file.write(player.serialise())
				file.write("!\n")

def getClanID(tag:str, session=None):
	s = session
	if s == None:
		s = CustomSession()
	if len(tag) > 5:
		raise Exception("Tag invalide")
	response = s.get(f"https://api.worldofwarships.eu/wows/clans/list/?application_id={token}&search={tag}")
	clans = response.json()["data"]
	for clan in clans:
		if clan["tag"] == tag:
			return clan["clan_id"]
	raise Exception(f"Aucun clan ne correspond à [{tag}]")
