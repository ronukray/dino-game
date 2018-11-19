import pygame
from pygame.locals import *
import random
from datetime import datetime
import time

#window properites
HEIGHT = 300
WIDTH = 600
BACKGROUND = (0, 191, 255)

SPEED = 9

#minumum spacing of cacti
MIN_CACTUS_GAP = 90


#Note the probablitity is 1/CACTI_CHANCE, so as you increase the number the
#probablity goes down.
CACTI_CHANCE = 40

#controls speed of dino jumps:
GRAVITY = 1
VELOCITY = 18

#Can be decimal
POINT_INCREASE_RATE = 0.1

# def resource_path(relative_path):
	# if hasattr(sys, '_MEIPASS'):
		# return os.path.join(sys._MEIPASS, relative_path)
	# return os.path.join(os.path.abspath("."), relative_path)
	
class Dino(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		image = pygame.image.load("dino1.png")
		self.image = image 
		self.rect = image.get_rect()
		self.rect.bottomleft = 0, HEIGHT
		self.jumping = False
		self.velocity = 0
		
		#initialize frame counter for running animation
		self.frame = 0
		
		#enables pixel perfect collision later on
		self.mask = pygame.mask.from_surface(self.image) 
	def update(self):
		#print("test")
		
		"""
		Implementation of Dino Running Animation
		The dino's image starts at dino1 and switches to dino2 when
		the frame counter passes 9. When it passes eighteen it resets to 0
		and the image becomes dino1 again. Repeat indefinetly.
		"""
		self.frame = self.frame + 1
		if(self.frame >= 18):
			image = pygame.image.load("dino1.png")
			self.image = image
			self.frame = 0
		if(self.frame >= 9):
			image = pygame.image.load("dino2.png")
			self.image = image
		
	
		#Physics Implementation. Decrease velocity as time goes on.
		if(self.jumping):
			self.velocity = self.velocity - GRAVITY
			newpos = self.rect.bottomleft[1] - self.velocity
			self.rect.bottomleft = 0, newpos
			
			#stop jumping when dino hits bottom
			if(self.rect.bottomleft[1] > HEIGHT):
				self.jumping = False
				self.rect.bottomleft = 0, HEIGHT
	
	def jump(self):
		if(self.jumping == False): #to prevent doublejumping	
			self.jumping = True
			self.velocity = VELOCITY
			
class Cactus(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) #call Sprite initializer
		image = pygame.image.load("cactusBigC.png")
		self.image = image
		self.rect = image.get_rect()
		self.rect.bottomright = WIDTH, HEIGHT
		self.mask = pygame.mask.from_surface(self.image)
	def update(self):
		#move to the left SPEED units
		self.rect.bottomright = self.rect.bottomright[0] - \
		SPEED, self.rect.bottomright[1]

class FloorBg(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		image = pygame.image.load("floorbgC.png")
		self.image = image
		self.rect = image.get_rect()
		self.rect.bottomleft = 0, HEIGHT
	def update(self):
		self.rect.left = self.rect.left - SPEED

#return true if cactus created
def genCactus(cacti):
	#1 / CACTI_CHANCE probablity of a cactus being added 
	if(random.randint(0, CACTI_CHANCE) == 0):
		cactus = Cactus()
		cacti.add(cactus)
		return True
	return False

def updateFloors(floor1, floor2):
	"""
	Implementation of scrolling floor background
	If one background has reached the edge of the screen, tack the other
	background on the first background's right edge. Repeat indefinetely.
	"""
	if(floor2.rect.right < WIDTH):
		floor1.rect.left = floor2.rect.right
	if(floor1.rect.right < WIDTH):
		floor2.rect.left = floor1.rect.right


pygame.init()

#keeps track of whether game is over or not
freeze = False

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dinosaur Game")

dino = Dino()
allsprites = pygame.sprite.RenderPlain((dino))

#intialize cacti group to be filled in later with genCactus
cacti = pygame.sprite.RenderPlain(())

#create two floor objects to be switched back and forth to keep up constant 
#scrolling background. 
floor1 = FloorBg()
floor2 = FloorBg()
floor2.rect.left = floor1.rect.right
scrollingFloor = pygame.sprite.RenderPlain((floor1, floor2))

clock = pygame.time.Clock()

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(BACKGROUND)

"""
Keeps track of minimum separation between cacti to prevent them 
being too close together. cactuscooldown is the time since the last cactus
was formed. cactuscooldown_start is set to true when the first cactus
is formed.
"""
cactuscooldown = 0
cactuscooldown_start = False

#time counter of when the last "Game Over" happened.
cooldowntime = 0

#set up rendering of "Game over" font
if pygame.font:
        font = pygame.font.Font("Minecraft.ttf", 36)
        fontPoints = pygame.font.Font("Minecraft.ttf", 15)
		
        text = font.render("Game Over", 1, (153, 76, 0))
        textpos = text.get_rect(centerx=background.get_width()/2, \
								centery=background.get_height()/2)
points = 0
playing = True

while playing:
	clock.tick(60)
	
	#Render points.
	pointText = fontPoints.render(str(int(points)), 1, (153, 76, 0))
	textpos2 = pointText.get_rect()
	textpos2.topleft = 10, 10
	
	textpos2.width = textpos2.width + 10
	textpos2.height = textpos2.height + 10
	background.fill(BACKGROUND, textpos2)
	background.blit(pointText, textpos2) 
	
	#increases the time recording how long ago "Game Over" happened
	if(freeze):
		cooldowntime = cooldowntime + 1
		
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			playing = False
			
		elif event.type == KEYDOWN and event.key == K_SPACE:
			"""
			If game is over, pressing start restarts the game.
			First it checks how long it's been since the game is over.
			It has to have been a minimum of 20 frames.
			This helps cut down on accidentally starting the game.
			If it has been, remove all cacti, destroy and create new dino.
			Reset all countdown variables.
			"""
			if(freeze and cooldowntime >= 20):
				for cactus in cacti:
					cactus.kill()
				dino.kill()
				dino = Dino()
				allsprites.add(dino)
				background.fill(BACKGROUND) #overwrite "Game Over" message
				cooldowntime = 0
				cactuscooldown = 0
				points = 0
				freeze = False #tracks if game is over
			
			#make dinosaur jump when space bar pressed
			dino.jump()

	screen.blit(background, (0, 0))
	
	#draw everything on screen regardless if game over or not
	scrollingFloor.draw(screen)
	cacti.draw(screen)
	allsprites.draw(screen)
	
	
	if(freeze == False):
		#update all game variables if game ongoing
		updateFloors(floor1, floor2)
		scrollingFloor.update()
		cacti.update()
		allsprites.update()
		points = points + POINT_INCREASE_RATE
		
		if(cactuscooldown_start):
			#increment time since last cactus created
			cactuscooldown = cactuscooldown + 1
			if(cactuscooldown >= MIN_CACTUS_GAP):
				
				#if we're safely past the minimum cactus separation interval,
				#try to create a cactus
				if(genCactus(cacti)):
					#if a cactus created, reset counter as to when the last
					#cactus was created
					cactuscooldown = 0
					#cactuscooldown_start = True

		#Keep trying to create the first cactus. When this happens,
		#set cooldown_start to true
		if(cactuscooldown_start == False):
			cactuscooldown_start = genCactus(cacti)
	
	#checks if dino bumped into cacti, if true then it displays "Game Over"
	for cactus in pygame.sprite.spritecollide(dino, cacti, False, \
	pygame.sprite.collide_mask):
		freeze = True
		background.blit(text, textpos)
	
	pygame.display.flip()
pygame.quit()