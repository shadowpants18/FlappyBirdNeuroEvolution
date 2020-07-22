import pygame as pg
import random
import time
import nn
import numpy as np
import sys
import os

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


pg.init()

winsize = width, height = 128*4, 196*4
nnsize = [4,3,1]
FPS = 60

screen = pg.display.set_mode(winsize)
clock = pg.time.Clock()
game_active = True
fitness = 0
generation = 0
font = pg.font.Font('images/04B_19__.ttf',24)
deathfont = pg.font.Font('images/04B_19__.ttf',24)
#colors
black = 0,0,0
white = 255,255,255

#stackoverflow copy and pasted for exe
floorurl = resource_path('images/floor.png')
birdurl = resource_path('images/bird.png')
bgurl = resource_path('images/bg2.png')
pipetopurl = resource_path('images/pipetop.png')
pipeboturl = resource_path('images/pipebot.png')





#pull images
bird_images = pg.transform.scale(pg.image.load(birdurl), (64, 64)).convert_alpha()
bgsurface = pg.transform.scale(pg.image.load(bgurl), winsize).convert_alpha()
ground = pg.transform.scale(pg.image.load(floorurl), (1024, 256)).convert_alpha()
ground_x = -256
pipetop = pg.transform.scale(pg.image.load(pipetopurl), (64, 512)).convert_alpha()
pipebot = pg.transform.scale(pg.image.load(pipeboturl), (64, 512)).convert_alpha()
pipelist = []

SPAWNPIPE = pg.USEREVENT
pg.time.set_timer(SPAWNPIPE, int(60000/FPS))


    
def displayscore(generation, fitness):

    string = 'Fitness: {0}'.format(fitness)
    string2 = 'Generation: {0}'.format(generation)
    scoresurface = font.render(string, True, white)
    scorerect = scoresurface.get_rect(midleft = (25, 25))
    
    scoresurface1 = font.render(string2, True, white)
    scorerect1 = scoresurface1.get_rect(midleft = (25, 75))
    
    screen.blit(scoresurface, scorerect)
    screen.blit(scoresurface1, scorerect1)
    
def deathscreen():
    deathsurf = deathfont.render('You died, hit spacebar to try again...', True, white)
    deathrect = deathsurf.get_rect(center = (width/2, height/3))
    screen.blit(deathsurf, deathrect)
class Bird:
    def __init__(self):
        self.x = width/5
        self.yvel = 0
        self.jumpvel = height * .0125
        self.gravity = height * .00075
        self.Alive = True
            
        self.ri = random.randrange(100000)
        self.fitness = 0
        self.start = time.time() * 100
        
        self.body = bird_images
        self.rect = self.body.get_rect(center = (100, height/2))
        self.rect = self.rect.inflate(-40, -40)
        
        self.brain = nn.NeuralNetwork(nnsize, seed = self.ri)
    def jump(self):
        self.yvel = -self.jumpvel
    def rotatebird(self):
        newbird = pg.transform.rotozoom(self.body, 30 , 1)
        return newbird
    def move(self):
        self.yvel += self.gravity
        #self.rotatedbird = self.rotatebird()
        self.rect.y += self.yvel
        
    def lose(self):
        self.fitness = time.time() * 100 - self.start
        self.Alive = False
    
    def checkcol(self, pipes):
        for pipe in pipes:
            if self.rect.colliderect(pipe.toprect):
                self.lose()
                return True
            elif self.rect.colliderect(pipe.botrect):
                self.lose()
                return True
        if self.rect.bottom > height/1.3:
            self.lose()
            return True
        if self.rect.top <= 0:
            self.rect.top = 0
            return False
        return False
    def update(self, pipes):
        if self.Alive:
            self.move()
            self.think(pipes)
            self.draw()
            self.checkcol(pipes.pipes)
    def think(self, pipes):
        inputs = np.empty((4,1))
        
        if not pipes:
            inputs[1] = 1
            inputs[2] = 2
            inputs[3] = 2
        else:
# =============================================================================
#             close = pipes[0]
#             dis = abs(pipes[0].toprect.left - self.x)
#             
#             for pipe in pipes:
#                 if pipe.toprect.left - self.x < dis:
#                     close = pipe
#                     dis = pipe.toprect.left - self.x
# =============================================================================
            
            inputs[1] = pipes.close.toprect.y/height
            inputs[2] = pipes.close.botrect.y/height
            inputs[3] = pipes.close.toprect.x/width
        inputs[0] = self.rect.y/height
        
        output = self.brain.forward(inputs)
        if output[0] > .5:
            self.jump()
            
    def draw(self):

        screen.blit(self.body, self.rect)
        
class Pipe():

    def __init__(self):
        self.ri = random.randrange(2 , 5)
        self.rr = random.randrange(60, 120)
        self.pipetop = pipetop
        self.toprect = self.pipetop.get_rect(midtop = (512, -height/self.ri - 60))
        self.toprect = self.toprect.inflate(0 , -25)
        
        self.pipebot = pipebot
        self.botrect = self.pipebot.get_rect(midtop = (512, self.toprect.y + height - self.rr))
        self.botrect = self.botrect.inflate(0 , -25)
        self.candraw = True
        self.canAdd = True
        self.scored = False
    def move(self):
        self.toprect.centerx -= 5
        self.botrect.centerx -= 5
      
    def checkscore(self):
        if self.toprect.x <  75 and not self.scored:
            self.scored = True
            return 1
        else:
            return 0
    def draw(self):
        if self.candraw:
            screen.blit(self.pipetop, self.toprect)
            screen.blit(self.pipebot, self.botrect)
        
    def delete(self):
        if self.toprect.x <-10:
            return True
        else:
            return False
    def update(self):
        self.move()
        self.draw()
        self.delete()
class PipeList():
    def __init__(self):
        self.pipes = []
        self.close = None
        self.last = None
        self.update()
    def update(self):
        if not self.pipes:
            self.last = Pipe()
            self.pipes.append(self.last)
            self.close = self.last
        self.pipes.sort(key=lambda x: x.toprect.centerx, reverse = True)
        for pipe in self.pipes:
            if pipe.toprect.centerx > 100 and pipe.toprect.centerx < 250:
                self.close = pipe
            pipe.update()
        if self.pipes[0].toprect.centerx < width * .6 and self.pipes[0].canAdd:
            self.spawnpipe()
    def spawnpipe(self):
        self.pipes.append(Pipe())
class BirdList():
    def __init__(self, population):
        self.birds = []
        self.startgen(population)
    
    def startgen(self, pop):
        self.birds = []
        for i in range(pop):
            self.birds.append(Bird())
    
    def update(self, pipes):
        num_alive = 0
        for b in self.birds:
            if b.Alive:
                b.update(pipes)
                num_alive += 1
        return num_alive
    def makebebe(p1, p2):
        child = Bird()
        child.brain = nn.NeuralNetwork(nnsize, seed = None)
        child.brain.crossover(p1, p2)
        return child
    def fitness(self):
        fitlist = self.birds
        fitlist.sort(key=lambda x: x.fitness, reverse = True)
        return fitlist
    def newgen(self, pop, mrate):
        new = []
        fitlist = self.fitness()
        for i in range(pop):
            choice1 = random.choice(fitlist[3:6])
            choice2 = random.choice(fitlist[0:3])
            child = BirdList.makebebe(choice1.brain, choice2.brain)
            child.brain.mutate(mrate)

            new.append(child)
        
        self.birds = new
pop= 250
mrate = .1
canspawn = True
birds = BirdList(pop)
pipes = PipeList()
generation = 0
fitness = 0
while True:
    clock.tick(FPS)
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            
            
    if game_active:
        #draw bg/fground        
        
        screen.blit(bgsurface, (0,0))
        ground_x -= 1
        if ground_x <= -512:
            ground_x = -256
        screen.blit(ground, (ground_x, height/1.4))
        
        #draw pipes
        pipes.update()
        
        
# =============================================================================
#         for pipe in pipelist:
#             pipe.move()
#             pipe.draw()
#             pipe.checkoverlap(pipelist)
#             if pipe.delete():
#                 pipelist.remove(pipe)
# =============================================================================
        #birds stuff
        fitness += 1
        displayscore(generation, fitness)
                
        if birds.update(pipes) == 0:
            fitness = 0
            pipes.pipes.clear()
            canspawn = False
            generation += 1
            
            birds.newgen(pop, mrate)
            canspawn = True
            clock.tick(FPS)
    pg.display.update()
        