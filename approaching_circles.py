
"""This code creates circles that move to/from a set destination point.
Controls:
			Left mouse button: 
					on/off switch for creating new circles.
			Right mouse button:  
					with respect of movement vector:
							1. circles that are moving towards mouse move to (x,y) the mouse was at the moment of a click;
							2. circles that are not moving towards the mouse start moving toward the mouse.
			middle mouse button: 
					switches movement direction to/from target.
			space bar: 
					stops all circles. stops making new circles.
			f button:
					makes all circles move towards the mouse.
			ESC:
					exit program 
			"""


import pygame as pg
import sys
from random import randint
import math
import pickle

pg.init()

W,H = 800,600											#screen size			
PROX = 4												# distance from the target at which the circles stop approaching it
SIGN = 1												# -/+ vector direction of circles  #should be moved to GLOBGAME class
LENGTH = 50												# max distance the circles can go
#colors
BLACK = 255,255,255			
GREY = 100,100,100
COLOR = lambda: (randint(0,255),randint(0,255),randint(0,255))		#random color
TIMER = lambda: pg.time.get_ticks()									#get time from last call
MOUSE = lambda: pg.mouse.get_pos()									#get x,y mouse position

def COMPAREPOS(pos1,pos2):								#difference between two positions returned as (x,y)
	x1,y1 = pos1
	x2,y2 = pos2
	result = x1-x2,y1-y2
	return result


#creates a circle instance
class myCircle:											
	def __init__(self):
		self.speed = 3#randint (1,3)
		self.pos = MOUSE()
		self.distance = 0								#how long should the circle move
		self.target = self.circle_me()					#point to which the circle should move
		self.dx = self.dy = 0							#change in x, y
		self.color = COLOR()
		self.birth = TIMER()
		self.follow = 0									#state follow/not the mouse

	
	def circle_me(self):								#set a target
		num = LENGTH
		x,y = self.pos
		nx,ny =  max(0, x+randint(-num,num)), max(0,y+randint(-num,num)) 		#sets and limits(min/max) target pos in LENGTH from current pos. returns (x,y)
		#print(math.hypot(nx-x, ny-y))
		self.distance = num
		return (nx,ny) if math.hypot(x-nx, y-ny) < num  else self.circle_me()	#diagonal movement length limits


	def clickfollow(self):								#"follow the mouse" state switch. returns (x,y)
		if self.follow:
			self.follow = 0
			self.target = self.circle_me()
		else: self.follow = 1
		return self.target
	
	def at_target(self):								#checks whether the circle is at the target pos. returns True/False 
		d1,d2 = COMPAREPOS(self.pos, self.target)
		return abs(d1) < PROX and abs(d2) < PROX		

	
	def trigs(self):									#calculates the distance and moves to the target
		if self.follow: 
			self.distance = LENGTH						#keep following
			self.target = MOUSE()
			if self.at_target():						#if circle the the mouse pos - stop following it
				self.clickfollow()

		if self.distance >0:							#if still moving
			x,y = self.pos
			mx,my = self.target
			self.distance = int(math.hypot(mx-x, my-y)) / self.speed	#approach
			rads = math.atan2(my-y, mx-x)
			self.dx = math.cos(rads) * self.speed						#change in x * speed
			self.dy = math.sin(rads) * self.speed						#change in y * speed
			self.pos = int(self.pos[0]+(SIGN*self.dx)), int(self.pos[1]+(SIGN*self.dy))			#change position with respect of direction (to/from) the target
			self.distance -=1 


#core for the game instance, no actial need to create a sigleton
class Game:
	def __init__(self):
		self.screen = pg.display.set_mode((W,H),pg.HWSURFACE|pg.DOUBLEBUF|pg.RESIZABLE)
		self.clock = pg.time.Clock()
		self.circles = []
		self.color = COLOR()								#random starting color for background
		self.ticker = TIMER()
		self.grad = (1,1,1)									#color for the background
		self.vomit = 0										#state switch for creating/not new circles

	def change_color(self):									#gradient change of background
		rgb = list(self.color)								#gets color
		grad = list(self.grad)
		for c in range(3):									#three times for 1.r 2.g 3.b
			if not(1 <= self.color[c] <= 254):
				grad[c] = 1 if self.color[c] <= 0 else -1	#changes gradient +/- direction if rgb color is at limit
			rgb[c]+= grad[c]								#changes color by gradients
		self.grad, self.color = tuple(grad), tuple(rgb)

	def draw(self):											#draws everything
		self.change_color()									#changes background
		self.screen.fill(self.color)					
		for c in self.circles:
			c.trigs()										#move circles
			pg.draw.circle(self.screen, c.color, c.pos, 6)	#draw circles
		pg.display.flip()

	def spawn(self):										#create a new circle
		self.circles.append(myCircle())

	def mainloop(self):										#mainloop
		global SIGN											
		#SIGN variable should be moved to GLOBGAME class to avoid changin it through "global" command							
		while True:
			self.clock.tick(30)								#FPS
			self.draw()										#updates the screen
			if self.vomit:									
				self.spawn()								#creates a circle

			for event in pg.event.get():					#controls
				if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
					GLOBGAME.quit()							#proper game exit on ESC
				if event.type == pg.KEYDOWN:				#keyboard controls
					if event.key == pg.K_l:
						GLOBGAME.load()						#loads game
					if event.key == pg.K_s:
						GLOBGAME.save()						#saves game
						GLOBGAME.load()
					if event.key == pg.K_SPACE:				#stops all circles and creation of new circles
						for c in self.circles:
							self.vomit = c.follow = c.distance = 0
					if event.key == pg.K_f:					#makes all circles follow the mouse
						SIGN = 1
						for c in self.circles:
							c.follow = 1
							c.distance = LENGTH
				if event.type == pg.MOUSEBUTTONDOWN:		#mouse controls
					if event.button == 1:					#left mouse click
						self.vomit = abs(self.vomit) -1		#starts/stops creating new circles on left mouse button
					if event.button == 2:					#middle mouse click
						SIGN *=-1							#changes the vector to/from target on middle mouse button
					if event.button == 3:					#right mouse click
						for c in self.circles:
							c.follow = abs(c.follow)-1		#"follow/not the mouse" switch on right mouse button


#class for save/load control
class GLOBGAME: 
	g = Game()

	@staticmethod
	def load():												#loads last saved game and restores unpickleble data structures
		with open('imsave', 'rb') as f:
			print(f)
			g = pickle.load(f)
		g.screen = pg.display.set_mode((W,H),pg.HWSURFACE|pg.DOUBLEBUF|pg.RESIZABLE)
		g.clock = pg.time.Clock()
		GLOBGAME.g = g
		GLOBGAME.g.mainloop()

	@staticmethod					
	def save():												#saves game
		g = GLOBGAME.g
		with open('imsave', 'wb') as f:
			g.screen = g.clock = False						#deconstructs unpickleble elements, mouse pos not saved
			pickle.dump(g, f)

	@staticmethod
	def quit():												#saves and quits the game
		GLOBGAME.save()
		pg.quit()
		sys.exit()


if __name__ == '__main__':
	play = GLOBGAME()
	try: 												
		GLOBGAME.load()										#tries to load a save on start
	except Exception as e:
		print(e)
		play.g.mainloop()									#creats a new game if no saves