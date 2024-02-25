import math
import numpy
import pygame
import pygame.gfxdraw
pygame.init()

screenSize=(1600, 900)
screen=pygame.display.set_mode(screenSize)
pygame.display.set_caption("Jelly Wizards")

halfScreen = list(map(round, [screenSize[0]/2, screenSize[1]/2]))

clock = pygame.time.Clock()
framerate = 30
realFps = 30

def getClosestPoint(line, p):
	if line[0][0]-line[1][0] == 0:
		closeP = [line[0][0], p[1]]
	else:
		lM = (line[1][1]-line[0][1])/(line[1][0]-line[0][0])
		lB = -lM*line[0][0]+line[0][1]
		if lM == 0:
			closeP = [p[0], line[0][1]]
		else:
			pM = -1/lM
			pB = pM*-p[0]+p[1]
			if pM - lM == 0:
				return None
			else:
				x = (lB-pB)/(pM-lM)
				y = pM*x + pB
				closeP = [x, y]
	if ((closeP[0] > line[0][0]) ^ (closeP[0] > line[1][0])) or \
		((closeP[1] > line[0][1]) ^ (closeP[1] > line[1][1])):
		return closeP
	else:
		d1 = (closeP[0]-line[0][0])**2+(closeP[1]-line[0][1])**2
		d2 = (closeP[0]-line[1][0])**2+(closeP[1]-line[1][1])**2
		if d1<d2:
			return line[0]
		else:
			return line[1]

SIZE = [800, 1000]
AREAS = [
	[[-100, -300], [100, -300], [300, -100], [300, 100], [100, 300], [-100, 300], [-300, 100], [-300, -100]],

	[[-600, 100], [-600, -200], [-300, 100]],
	[[600, -100], [600, 200], [300, -100]],
	[[0, 200], [200, 0], [0, -200], [-200, 0]],

	[[-800, -1000], [0, -1000], [-800, 0]],
	[[800, -1000], [0, -1000], [800, 0]],
	[[800, 1000], [0, 1000], [800, 0]],
	[[-800, 1000], [0, 1000], [-800, 0]],

	[[-400, -1000], [400, -1000], [400, -800], [-400, -800]],
	[[-400, 1000], [400, 1000], [400, 800], [-400, 800]],
	[[-800, -500], [-800, 500], [-600, 500], [-600, -500]],
	[[800, -500], [800, 500], [600, 500], [600, -500]],

	[[-300, -100], [-300, -200], [-200, -300], [-100, -300]],
	[[300, -100], [300, -200], [200, -300], [100, -300]],
	[[300, 100], [300, 200], [200, 300], [100, 300]],
	[[-300, 100], [-300, 200], [-200, 300], [-100, 300]],

	[[-700, 200], [-200, 200], [-300, 100], [-700, 100]],
	[[700, -200], [200, -200], [300, -100], [700, -100]],

	[[-200, -600], [200, -600], [200, -500], [0, -400], [-200, -500]],
	[[-200, 600], [200, 600], [200, 500], [0, 400], [-200, 500]],
]
EFFECTS = [
	["ice"],
	["lava"],
	["lava"],
	["lava"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
	["wall"],
]
CENTERS = []
for area in AREAS:
	totalX = 0
	totalY = 0
	for point in area:
		totalX += point[0]
		totalY += point[1]
	middle = [totalX/len(area), totalY/len(area)]
	CENTERS.append(middle)
COLORS = {"wall": (0, 255, 0, 50), "ice": (255, 255, 255, 100), "lava": (255, 0, 0, 100)}

GAME = {
	"zc": {
		"areas": [
			[[-600, 250], [-600, 200], [-300, 200], [-200, 300], [-400, 500]],
			[[600, -250], [600, -200], [300, -200], [200, -300], [400, -500]],
			[[200, 300], [400, 500], [600, 250], [600, 200], [400, 0], [300, 100], [300, 200]],
			[[-200, -300], [-400, -500], [-600, -250], [-600, -200], [-400, 0], [-300, -100], [-300, -200]],
		],
		"control": [
			[-1, [0, 0]],
			[-1, [0, 0]],
			[-1, [0, 0]],
			[-1, [0, 0]],
		],
		"spawns": [
			[[0, 700]],
			[[0, -700]]
		]
	},
	"ctf": {
		"flag": [
			[0, 700],
			[0, -700]
		],
		"spawns": [
			[[-300, 500], [300, 500]],
			[[-300, -500], [300, -500]]
		]
	}
}
TEAMCOLORS = [(255, 0, 255, 100), (0, 255, 255, 100)]

gameMode = "ctf"

class WIZARD:
	def __init__(self, ID, team):
		self.ID = ID
		self.team = team
		self.alive = False
		self.respawnRot = 0
		self.respawnTime = 0
		self.pos = [0, 0]
		self.vel = [0, 0]
		self.accel = 10
		self.friction = 1
		self.radius = 10
		self.maxSpeed = 10
		self.keys = {
			"up": [119, False],
			"down": [115, False],
			"left": [97, False],
			"right": [100, False]}
	def spawn(self):
		if self.alive:
			return
		if self.respawnTime <= 0:
			teamSpawns = GAME[gameMode]["spawns"][self.team]
			if self.respawnRot == len(teamSpawns):
				self.respawnRot = 0
			self.pos = teamSpawns[self.respawnRot].copy()
			self.vel = [0, 0]
			self.alive = True
			self.respawnRot += 1
		else:
			self.respawnTime -= 1/realFps
	def move(self):
		if not self.alive:
			return
		thisAccel = self.accel/realFps
		angle = [0, 0]
		if self.keys["up"][1]:
			angle[1] -= 1
		if self.keys["down"][1]:
			angle[1] += 1
		if self.keys["left"][1]:
			angle[0] -= 1
		if self.keys["right"][1]:
			angle[0] += 1
		if angle != [0, 0]:
			realA = math.atan2(angle[1], angle[0])
			self.vel[0] += math.cos(realA)*thisAccel
			self.vel[1] += math.sin(realA)*thisAccel

	def applyVel(self):
		self.vel[0] *= 1-(self.friction/realFps)
		self.vel[1] *= 1-(self.friction/realFps)
		self.pos[0] += self.vel[0]
		self.pos[1] += self.vel[1]
		currentSpeed = math.sqrt(self.vel[0]**2 + self.vel[1]**2)
		self.radius = 10 + round(currentSpeed)

	def collide(self):
		self.friction = 1
		for j, area in enumerate(AREAS):
			closestPoint = 0
			closestDistance = math.inf
			for i, point in enumerate(area):
				n = 1
				if i == len(area)-1:
					n = -i
				closeP = getClosestPoint([point, area[i+n]], self.pos)
				d = (closeP[0]-self.pos[0])**2 + (closeP[1]-self.pos[1])**2
				if d<closestDistance:
					closestPoint = closeP
					closestDistance = d
			centerP = CENTERS[j]
			meToCent = (centerP[0]-self.pos[0])**2 + (centerP[1]-self.pos[1])**2
			pntToCent = (centerP[0]-closestPoint[0])**2 + (centerP[1]-closestPoint[1])**2
			if meToCent < pntToCent:
				if "wall" in EFFECTS[j]:
					angle = math.atan2(closestPoint[1]-self.pos[1], closestPoint[0]-self.pos[0])
					velocity = math.sqrt(meToCent)-math.sqrt(pntToCent)
					self.vel[0] -= math.cos(angle)*velocity
					self.vel[1] -= math.sin(angle)*velocity
				if "ice" in EFFECTS[j]:
					self.friction = 0.2
				if "lava" in EFFECTS[j] and self.alive:
					self.alive = False
					self.respawnTime = 5
		for wiz in Wizards:
			if wiz.ID != self.ID:
				xDiff = self.pos[0]-wiz.pos[0]
				yDiff = self.pos[1]-wiz.pos[1]
				wizD = math.sqrt(xDiff**2 + yDiff**2)
				totRad = self.radius+wiz.radius
				if wizD < totRad:
					angle = math.atan2(yDiff, xDiff)
					self.vel[0] += math.cos(angle)*(wizD/totRad/2)
					self.vel[1] += math.sin(angle)*(wizD/totRad/2)

Wizards = [WIZARD(0, 0), WIZARD(1, 0)]

while True:
	clock.tick(framerate)
	realFps = clock.get_fps()
	if realFps == 0:
		realFps = framerate
	events = pygame.event.get()

	for event in events:
		if event.type == pygame.QUIT:
			pygame.quit()
			quit()
		if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
			for key in Wizards[0].keys:
				if Wizards[0].keys[key][0] == event.key:
					if event.type == pygame.KEYDOWN:
						Wizards[0].keys[key][1] = True
					else:
						Wizards[0].keys[key][1] = False

	screen.fill((0, 0, 0))

	for wizard in Wizards:
		wizard.spawn()
		if wizard.ID == 0:
			wizard.move()
		wizard.collide()
		wizard.applyVel()

	pX = round(Wizards[0].pos[0])
	pY = round(Wizards[0].pos[1])
	xFixed = False
	yFixed = False

	if pX+halfScreen[0] > SIZE[0]:
		pX = SIZE[0]-screenSize[0]
		xFixed = True
	elif pX-halfScreen[0] < -SIZE[0]:
		pX = -SIZE[0]
		xFixed = True
	if pY+halfScreen[1] > SIZE[1]:
		pY = SIZE[1]-screenSize[1]
		yFixed = True
	elif pY-halfScreen[1] < -SIZE[1]:
		pY = -SIZE[1]
		yFixed = True
	if not xFixed:
		pX = pX - halfScreen[0]
	if not yFixed:
		pY = pY - halfScreen[1]

	for i, area in enumerate(AREAS):
		color = COLORS[EFFECTS[i][0]]
		newArea = numpy.copy(area)
		newArea[:,0] -= pX
		newArea[:,1] -= pY
		pygame.gfxdraw.filled_polygon(screen, newArea, color)
		pygame.gfxdraw.polygon(screen, newArea, color[:3])

	for wizard in Wizards:
		color = TEAMCOLORS[wizard.team]
		if not wizard.alive:
			color = [200, 200, 200, 100]
		x = round(wizard.pos[0])-pX
		y = round(wizard.pos[1])-pY
		pygame.gfxdraw.filled_circle(screen, x, y, wizard.radius, color)
		pygame.gfxdraw.circle(screen, x, y, wizard.radius, color[:3])

	pygame.display.flip()
