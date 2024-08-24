import sys
import pygame
import math
import time
import os
import random

BASE_IMG_PATH = 'images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def draw_rectangle(surface, color, pos, width, height):
  pygame.draw.rect(surface, color, pygame.Rect(pos[0], pos[1], width, height))

def sum_list(l):
    t = 0
    for i in l:
        t += l
    return l

def find_score(pars_list, strokes_list, time_d): # constraint: pars_list and strokes_list of same length
    sum_of_squares = 0
    for i in range(len(pars_list)):
        if pars_list[i] > strokes_list[i]:
            sum_of_squares += (pars_list[i] - strokes_list[i])**2
        else:
            sum_of_squares -= (pars_list[i] - strokes_list[i])**2
    if sum_of_squares >= 0:
        sum_of_squares = int(sum_of_squares * math.sqrt(time_d))
    else:
        sum_of_squares = sum_of_squares // math.sqrt(time_d)
    return sum_of_squares

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.angle = 0  # initial angle of rotation
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        if self.velocity[0] > 0:
            if self.velocity[0] < 0.07:
                self.velocity[0] = 0
            else:
                self.velocity[0] = self.velocity[0] - 0.01
        elif self.velocity[0] < 0:
            if self.velocity[0] > -0.07:
                self.velocity[0] = 0
            else:
                self.velocity[0] = self.velocity[0] + 0.01
        
        if self.collisions['down'] or self.collisions['up']:
            if self.velocity[1] > 1.5:
                self.velocity[1] = -self.velocity[1] / 2.5
            else:
                self.velocity[1] = 0

        if self.collisions['right'] or self.collisions['left']:
            if self.velocity[0] < 0:
                self.velocity[0] = -(self.velocity[0] + 0.5)
            elif self.velocity[0] > 0:
                self.velocity[0] = -(self.velocity[0] - 0.5)
    
    def rotate(self, angle):
        self.angle += angle
        if self.angle >= 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
    
    def render(self, surf, o_type):
        rotated_image = pygame.transform.rotate(self.game.assets[o_type], self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect().center)
        surf.blit(rotated_image, rotated_rect.topleft)

import pygame

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, level, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.level = level
        self.tilemap = {}
        self.offgrid_tiles = []

        if self.level == 1:
            # vertical
            for i in range(15):
                self.tilemap['0;'+ str(i)] = {'type': 'stone', 'variant': 0, 'pos': (0, i)}
                self.tilemap['10;' + str(5 + i)] = {'type': 'stone', 'variant': 0, 'pos': (10, 5 + i)}
                self.tilemap['19;'+ str(i)] = {'type': 'stone', 'variant': 0, 'pos': (19, i)}

            # horizontal
            for i in range(1, 18):
                self.tilemap[str(i) + ';14'] = {'type': 'grass', 'variant': 0, 'pos': (i, 14)}
            self.tilemap['20;14'] = {'type': 'grass', 'variant': 0, 'pos': (20, 14)}

        if self.level == 2:
            # horizontal
            for i in range(3, 20):
                self.tilemap[str(i) + ';5'] = {'type': 'stone', 'variant': 8, 'pos': (i, 5)}
            for i in range(16):
                self.tilemap[str(i) + ';9'] = {'type': 'stone', 'variant': 8, 'pos': (i, 9)}
            for i in range(2, 20):
                self.tilemap[str(i) + ';14'] = {'type': 'stone', 'variant': 8, 'pos': (i, 14)}

            # vertical
            for i in range(16):
                self.tilemap['0;'+ str(i)] = {'type': 'stone', 'variant': 0, 'pos': (0, i)}
                self.tilemap['19;'+ str(i)] = {'type': 'stone', 'variant': 0, 'pos': (19, i)}
            
            for i in range(7,9):
                self.tilemap['10;' + str(i)] = {'type': 'stone', 'variant': 0, 'pos': (10, i)}
            for i in range(6,8):
                self.tilemap['12;' + str(i)] = {'type': 'stone', 'variant': 0, 'pos': (12, i)}
    
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def render(self, surf):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], tile['pos'])
            
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('GoGolf')
        self.level = 1
        self.text_bg_colors = [(0, 255, 255), (0, 0, 128)]
        self.pars = [4, 6]
        self.strokeslist = []
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        self.assets = {
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'arrow': load_image('arrow.png'),
            'ball': load_image('ball.png'),
        }
        
        self.arrow = PhysicsEntity(self, 'arrow', (50, 50), (8, 15))
        self.ball = PhysicsEntity(self, 'ball', (100, 100), (8, 15))
        
        self.strokes = 0
        try:
            pygame.mixer.music.load('music/bgm.mp3')
            pygame.mixer.music.play(-1)
        except:
            pass

    def finalmessage(self, score):
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        font = pygame.font.Font('freesansbold.ttf', 12)

        partext = font.render('You have finished the game! \nYour score: ' + str(score), True, (255, 255, 255), (1, 1, 1))
        partextRect = partext.get_rect()
        partextRect.center = (100, 100)

        self.display.fill((0, 0, 0))
        self.display.blit(partext, partextRect)

        self.screen.blit(self.display, (0, 0))
        pygame.display.flip()
        
        # freeze for 5 secs
        pygame.time.wait(5000)  

        
    def run(self):
        hitstrength = 0
        holding_mouse = False
        arrow_flag = False

        hardhit = pygame.mixer.Sound("sfx/hardhit.wav")
        normalhit = pygame.mixer.Sound("sfx/put.wav")
        
        font = pygame.font.Font('freesansbold.ttf', 12)
        self.strokes_total = 0
        self.start_time = time.time()

        while True:
            self.ball.rotate((random.randint(0,1) - 0.5) * 10) # either -5 or 5
            par = self.pars[self.level - 1]
            self.tilemap = Tilemap(self, self.level, tile_size=16)
            leveltext = font.render('Level: ' + str(self.level), True, (255, 255, 255), self.text_bg_colors[self.level-1])
            leveltextRect = leveltext.get_rect()
            leveltextRect.center = (230, 25)

            partext = font.render('Par: ' + str(par), True, (255, 255, 255), self.text_bg_colors[self.level-1])
            partextRect = partext.get_rect()
            partextRect.center = (230, 45)

            strokestext = font.render('Strokes: ' + str(self.strokes), True, (255 if (self.strokes >= par) else 0, 255 if (self.strokes <= par) else 0, 0), self.text_bg_colors[self.level-1])
            strokestextRect = strokestext.get_rect()
            strokestextRect.center = (230, 65)


            self.display.fill((14, 219, 248))
            bg = pygame.image.load(BASE_IMG_PATH + "bg" + str(self.level) + ".png")
            self.display.blit(bg, (0,0))
            self.display.blit(leveltext, leveltextRect)
            self.display.blit(partext, partextRect)
            self.display.blit(strokestext, strokestextRect)
            
            
            self.tilemap.render(self.display)
            
            
            self.arrow.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            
            self.ball.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.ball.render(self.display, 'ball')
          
            mouseposition = pygame.mouse.get_pos()
            dx = mouseposition[0] - self.arrow.pos[0]*2
            dy = mouseposition[1] - self.arrow.pos[1]*2
            #print("Magnitude:", math.sqrt(dx**2 + dy**2))
            direction = 0
            if dy == 0:
                if dx <= 0:
                    direction = 0
                else:
                    direction = 180
            else:
                angle_magnitude = abs(math.atan(dx/dy)*180/math.pi)
            
            if dy > 0:
                if dx >= 0:
                    direction = 180 - angle_magnitude
                else:
                    direction = 180 + angle_magnitude

            elif dy < 0:
                if dx >= 0:
                    direction = angle_magnitude
                elif dx < 0:
                    direction = 360 - angle_magnitude
            direction = 360 - direction
            #print("Direction:", int(direction))

            if arrow_flag:
                self.arrow.render(self.display, 'arrow')

            if self.ball.velocity == [0, 0]:
                    self.arrow.render(self.display, 'arrow')
                    arrow_flag = True
                    self.arrow.pos[0] = self.ball.pos[0]
                    self.arrow.pos[1] = self.ball.pos[1]
            
            if self.ball.pos[1] > 250 or self.ball.pos[0] > 330:
                #print("You won")
                self.level += 1
                self.ball.pos = [280, 10]
                self.ball.velocity = [0, 0]
                self.strokeslist.append(self.strokes)
                self.strokes = 0
                if self.level > len(self.pars):
                    return find_score(self.pars, self.strokeslist, time.time() - self.start_time)



            
            for event in pygame.event.get():
                if holding_mouse:
                    hitstrength += increase

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.arrow.rotate(direction - self.arrow.angle + 45)
                
                if hitstrength == 100:
                    increase = -1
                if hitstrength == 0:
                    increase = 1

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        holding_mouse = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.ball.velocity[0] != 0 or self.ball.velocity[1] != 0:
                            holding_mouse = False
                            #print("Ball hit with strength", hitstrength, "in", direction)
                            self.strokes += 1
                            self.strokes_total += 1
                            self.ball.velocity[1] = -hitstrength/15 * math.cos(direction*math.pi/180)
                            self.ball.velocity[0] = -hitstrength/15 * math.sin(direction*math.pi/180)
                            if hitstrength > 70:
                                pygame.mixer.Sound.play(hardhit)
                            else:
                                pygame.mixer.Sound.play(normalhit)
                            hitstrength = 0
                        else:
                            pass
                            #print("Cannot hit the ball while it's moving!")

                

            draw_rectangle(self.display, (128, 128, 128), (20, 20), 100, 20)
            draw_rectangle(self.display, (0, 255, 0), (20, 20), hitstrength, 20)
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            
            pygame.display.update()
            self.clock.tick(60)

def main():
    g = Game()
    score = g.run()
    g.finalmessage(score)   

if __name__ == '__main__':
    main()

