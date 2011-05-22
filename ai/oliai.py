#!/usr/bin/env python2.3
#
#  oliai.py
#  
#
#  Created by Oliver Barter on 21/05/2011.
#  Copyright (c) 2011 Cambridge University. All rights reserved.
#

import random
import ai
AIClass="OliAI"
import logging
log = logging.getLogger(AIClass)

class OliAI(ai.AI):
	
	def _init(self):
	# Called once when AI is created. 
	# Useful for creating containers to be used later (eg).
		self.olis_dead_units = set()
		self.moved_once = set()
		
	def _spin(self):
		for unit in self.my_units:
			unit.move((50,50))
				
		
		
		
	def _unit_died(self, unit):
		self.olis_dead_units.add(unit)
		
		for unit in self.olis_dead_units:
			print unit
			
		
	def _unit_spawned(self, unit):
		log.info("Recieved a new unit: %s", unit)
