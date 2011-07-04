import ai
import ai_exceptions
AIClass="OliAI2"
from math import sin, cos, pi, sqrt
import random




class Squad(object):

	def __init__(self,unit):
		self.SQUAD_MAX = 0
		self.FORM_SPACE = 3
		self.SPIRAL_MODIFIER = 30.0
		self.MAPSIZE = 99
		self.units = []
		self.add(unit)
		self.is_sentry = 0
		self.is_guard = 0
		self.is_scout = 0		
		self.is_patrol = 0
		self.id = 0
	
	@property
	def count(self):
		return len(self.units)
				
	@property
	def position(self):
		return (self.units[0].position[0], self.units[0].position[1] - self.FORM_SPACE)
		
	@property
	def visible_baddies(self):
		visible_baddies = []
		for unit in self.units:
			if unit.visible_enemies:
				visible_baddies = visible_baddies + unit.visible_enemies
		return visible_baddies

		
	def contains(self, unit):
		return unit in self.units
		
	def add(self, unit):
		self.units.append(unit)
	
	def remove(self, unit):
		self.units.remove(unit)
		

	def attack(self,pos):
		for unit in self.units:
			if unit.calcDistance(pos) < unit.sight:
				unit.shoot(pos)
			else:
				unit.move(pos)

	def move_spiral(self, pos, current_turn):
		i=0.0
		for unit in self.units:
			x = pos[0]+int(self.FORM_SPACE * sin((((current_turn % self.SPIRAL_MODIFIER) / self.SPIRAL_MODIFIER) +(i/self.count)) * 2 * pi))
			y = pos[1]+int(self.FORM_SPACE * cos((((current_turn % self.SPIRAL_MODIFIER) / self.SPIRAL_MODIFIER) +(i/self.count)) * 2 * pi))
		
			if x < 0:
				x = 0
			elif x > self.MAPSIZE:
				x = self.MAPSIZE
			if y < 0:
				y = 0
			elif y > self.MAPSIZE:
				y = self.MAPSIZE
				
			unit.move((x,y))
			i=i+1

	
	def nearest_friendly_building(self, friendly_buildings):
		s = self.units[0].calcDistance(friendly_buildings[0].position)
		target = friendly_buildings[0]
		for building in friendly_buildings:
			if self.units[0].calcDistance(building.position) < s:
				s = self.units[0].calcDistance(building.position)
				target = building
		return target
		
		
		
	def move(self, pos):
		i=0.0
		for unit in self.units:
			x = pos[0]+int(self.FORM_SPACE * sin((i/self.count) * 2 * pi))
			y = pos[1]+int(self.FORM_SPACE * cos((i/self.count) * 2 * pi))
		
			if x < 0:
				x = 0
			elif x > self.MAPSIZE:
				x = self.MAPSIZE
			if y < 0:
				y = 0
			elif y > self.MAPSIZE:
				y = self.MAPSIZE
				
			unit.move((x,y))
			i=i+1

	
	def explore(self, heat_map, unexplored_squares):
		
		potential_squares = unexplored_squares.copy()
	
		square = potential_squares.pop()
	
		best_score = heat_map[square[0]][square[1]] - self.units[0].calcDistance(square)
		chosen_square = square
		
		while len(potential_squares):
			square = potential_squares.pop()
			score = heat_map[square[0]][square[1]] - self.units[0].calcDistance(square)
			if score > best_score:
				chosen_square = square
				best_score = score	
		
		self.move(chosen_square)
			
				
	def siege(self, building):
		for unit in self.units:
			if not unit.is_capturing:
				if unit.position == building.position:
					unit.capture(building)
				else:
					unit.move(building.position)


	def tuple_sum(self, a, b):
		return (a[0] + b[0], a[1] + b[1])

	
	def random_walk(self):
		while True:
			try:
				square = self.tuple_sum(self.position, random.choice([(-5,0),(5,0),(0,-5),(0,5)]))
				self.move(square)
				break
			except ai_exceptions.IllegalSquareException:
				pass

		
		
class OliAI2(ai.AI):

	def _init(self):
		self.my_squads = []
		self.squad_id_counter = 1
		self.heat_map = [[1]*(self.mapsize+1) for x in xrange(self.mapsize+1)]
		self.unexplored_squares = set([(x,y) for y in xrange(self.mapsize+1) for x in xrange(self.mapsize+1)])
		self.known_buildings = set()	
		self.have_scout = 0
		
				
				
	def _spin(self):

		new_squares = self.unexplored_squares & self.visible_squares
		self.unexplored_squares -= self.expanded(new_squares, 8)
		
		if self.new_buildings:
			for building in self.new_buildings:
				building.has_sentry = 0
				building.has_guard = 0
				
		if self.lost_buildings:
			for building in self.lost_buildings:
				if building.has_sentry:
					for squad in self.my_squads:
						if squad.is_sentry:
							if squad.id == building.sentry_id:
								squad.is_sentry = 0
								squad.is_patrol = 1
								squad.SQUAD_MAX = 2
								break
				if building.has_guard:
					for squad in self.my_squads:
						if squad.is_guard:
							if squad.id == building.guard_id:
								squad.is_guard = 0
								squad.is_patrol = 1
								squad.SQUAD_MAX = 2	
								break			
		
		if self.visible_buildings:
			for building in self.visible_buildings:
				if not building in self.known_buildings:
					self.known_buildings.add(building)
					

		for squad in self.my_squads:
			if squad.is_sentry:
				if squad.visible_baddies:
					squad.attack(max(set(squad.visible_baddies), key=squad.visible_baddies.count).position)
				else:
					pass
					
			elif squad.is_scout:
				if self.unexplored_squares:	
					squad.explore(self.heat_map, self.unexplored_squares)
				else:
					pass
					
			elif squad.is_guard:
				if squad.visible_baddies:
					squad.attack(max(set(squad.visible_baddies), key=squad.visible_baddies.count).position)
				else:
					if self.my_buildings:
						squad.move_spiral(squad.nearest_friendly_building(self.my_buildings).position, self.current_turn)
					else:
						pass
				pass
				
			elif squad.is_patrol:
				if squad.visible_baddies:
					squad.attack(max(set(squad.visible_baddies), key=squad.visible_baddies.count).position)
				else:
					if squad.count <= 0.5 * squad.SQUAD_MAX:
						if self.my_buildings:
							squad.move(squad.nearest_friendly_building(self.my_buildings).position)
						else:
							pass
					else:
						for building in self.known_buildings:
							if building.team != self.team:
								squad.siege(building)
								break
						else:
							if self.unexplored_squares:	
								squad.explore(self.heat_map, self.unexplored_squares)
							else:
								squad.random_walk()
								squad.FORM_SPACE = 8

								



		for unit in self.my_units:
			self.highlight_for_unit(unit)
		
			

	def _unit_died(self, unit):
		
		for squad in self.my_squads:
			if squad.contains(unit):
				squad.remove(unit)
				if squad.count == 0:
					if squad.is_sentry:
						for building in self.my_buildings:
							if building.sentry_id == squad.id:
								building.has_sentry = 0
					elif squad.is_guard:
						for building in self.my_buildings:
							if building.guard_id == squad.id:
								building.has_guard = 0
					elif squad.is_scout:
						self.have_scout = 0
					self.my_squads.remove(squad)
							
		
	def _unit_spawned(self, unit):	
	
		if self.current_turn == 1:
			self.seed_heat_map()
			for building in self.my_buildings:
				building.has_sentry = 0
				building.has_guard = 0
		
						
						
		for building in self.my_buildings:
			if unit.position == building.position:
				if not building.has_sentry:
					self.my_squads.append(self.create_squad("sentry", unit, building))
					return 0
		else:
			if self.unexplored_squares and not self.have_scout:
				self.my_squads.append(self.create_squad("scout", unit))
				return 0
			else:
				for building in self.my_buildings:
					if unit.position == building.position:
						if building.has_guard:
							for squad in self.my_squads:
								if squad.id == building.guard_id:
									if squad.count < squad.SQUAD_MAX:
										squad.add(unit)
										return 0
									else:
										for squad in self.my_squads:
											if squad.is_patrol:
												if squad.count < squad.SQUAD_MAX:
													squad.add(unit)
													return 0
										else:
											self.my_squads.append(self.create_squad("patrol", unit))
											return 0
							else:
								pass
						else:
							self.my_squads.append(self.create_squad("guard", unit, building))
							return 0							
																		
									
	
	
	#MY DEFINED FUNCTIONS
			
	def create_squad(self, type, unit, building = 0):
		new_squad = Squad(unit)
		new_squad.id = self.squad_id_counter
		self.squad_id_counter += 1
		new_squad.MAPSIZE = settings.map.size - 1

		if type == "sentry":
			new_squad.is_sentry = 1
			new_squad.SQUAD_MAX = 1
			new_squad.FORM_SPACE = 0
			if building:
				building.sentry_id = new_squad.id
				building.has_sentry = 1
			else:
				pass
				
		elif type == "scout":	
			new_squad.is_scout = 1
			new_squad.SQUAD_MAX = 1
			new_squad.FORM_SPACE = 5
			self.have_scout = 1
			
		elif type == "guard":
			new_squad.is_guard = 1
			new_squad.SQUAD_MAX = 3
			new_squad.FORM_SPACE = 8
			if building:
				building.guard_id = new_squad.id
				building.has_guard = 1
			else:
				pass
				
		elif type == "patrol":	
			new_squad.is_patrol = 1
			new_squad.SQUAD_MAX = 3
			new_squad.FORM_SPACE = 3
		
		return new_squad

	
	def seed_heat_map(self):
		for building in self.my_buildings:
				for x in xrange(self.mapsize+1):
					for y in xrange(self.mapsize+1):
						value = int(50 - sqrt( ((building.position[0] - x)*(building.position[0] - x)) + ((building.position[1] - y)*(building.position[1] - y)) ))
						if value < 1:
							self.heat_map[x][y] = 1
						else:
							self.heat_map[x][y] = value
	
	
	def expanded( self, visible_squares , expansion_param):
		expanded_squares = visible_squares.copy()
			
		for square in visible_squares: 
			for i in range(-expansion_param, expansion_param + 1):
				for j in range(-expansion_param, expansion_param + 1):
					if not ( square[0]+i < 0 or square[0]+i > self.mapsize or square[1]+j < 0 or square[1]+j > self.mapsize ):
						expanded_squares.add((square[0]+i,square[1]+j))
		return expanded_squares
	
	
	def highlight_for_unit(self, unit):
		temp = unit.visible_squares.copy()
		square = temp.pop()
		xmax = square[0]
		xmin = square[0]
		ymax = square[1]
		ymin = square[1]
		
		while len(temp):
			square = temp.pop()
			x = square[0]
			y = square[1]
			if x > xmax:
				xmax = x
			elif x < xmin:
				xmin = x
			if y > ymax:
				ymax = y
			elif y < ymin:
				ymin = y
		
		self.highlightRegion((xmin,ymin),(xmax+1,ymax+1))
	
	
	def remove_from_squad(self, unit):
		for squad in self.my_squads:
			if squad.contains(unit):
				squad.remove(unit)
				if squad.count == 0:
					self.my_squads.remove(squad)
					
				
	def assign_to_squad(self, unit):
		for squad in self.my_squads:
				if squad.count < squad.SQUAD_MAX:
					squad.add(unit)
					return 0
		self.my_squads.append(Squad(unit))
