import random
import pygame
import math

pygame.init()
pygame.mixer.init()

testing = False
invincibility = False

high_fps = 60
fps = 16  # standard is 12
width = 224
height = 288  # maze is 224x256, show score above
volume = 0.05

black = (0, 0, 0)
white = (255, 255, 255)

pygame.display.set_mode((width, height))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()
GameExit = False
pac_font = pygame.font.Font("./Fonts/pac_font.ttf", 8)
pac_font.set_bold(True)

pac_chomp = pygame.mixer.Sound("./Sounds/pacman_chomp.wav")
pac_eatpallet = pygame.mixer.Sound("./Sounds/pacman_eatpallet.wav")  # is actually fruit eating sound from game
pac_chomp_channel = pygame.mixer.Channel(0)
pac_chomp_channel.set_volume(volume)

siren = pygame.mixer.Sound("./Sounds/pacman_siren_cropped.wav")
siren_channel = pygame.mixer.Channel(6)
siren_channel.set_volume(volume)

pac_eatghost = pygame.mixer.Sound("./Sounds/pacman_eatghost.wav")
ghost_death = pygame.mixer.Sound("./Sounds/pacman_intermission.wav")
ghost_death_channel = pygame.mixer.Channel(2)
ghost_death_channel.set_volume(volume)

pac_death = pygame.mixer.Sound("./Sounds/pacman_death.wav")
pac_death_channel = pygame.mixer.Channel(4)
pac_death_channel.set_volume(volume)

ghost_eat_scores = pygame.image.load("./Sprites/misc/ghost_eat_scores.png")


def game_over():
    Screen.update()
    pac_chomp_channel.stop()
    siren_channel.stop()
    game_over_image = pygame.image.load("./Sprites/misc/game_over.png")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.quit()
                pygame.quit()
                quit()

        Screen.screen.blit(game_over_image, (112 - 39, 16 + 17*8))
        pygame.display.update()

        clock.tick(fps)


# maze is 28x31

class Maze(object):
    def __init__(self):
        self.grid = [
            list("wwwwwwwwwwwwwwwwwwwwwwwwwwww"),
            list("wffffffffffffwwffffffffffffw"),
            list("wfwwwwfwwwwwfwwfwwwwwfwwwwfw"),
            list("wfwwwwfwwwwwfwwfwwwwwfwwwwfw"),
            list("wPwwwwfwwwwwfwwfwwwwwfwwwwPw"),
            list("wffffffffffffffffffffffffffw"),
            list("wfwwwwfwwfwwwwwwwwfwwfwwwwfw"),
            list("wfwwwwfwwfwwwwwwwwfwwfwwwwfw"),
            list("wffffffwwffffwwffffwwffffffw"),
            list("wwwwwwfwwwwwowwowwwwwfwwwwww"),
            list("wwwwwwfwwwwwowwowwwwwfwwwwww"),
            list("wwwwwwfwwoooooooooowwfwwwwww"),
            list("wwwwwwfwwowwwwwwwwowwfwwwwww"),
            list("wwwwwwfwwowGGGGGGwowwfwwwwww"),
            list("oooooofooowGGGGGGwooofoooooo"),
            list("wwwwwwfwwowGGGGGGwowwfwwwwww"),
            list("wwwwwwfwwowwwwwwwwowwfwwwwww"),
            list("wwwwwwfwwoooooooooowwfwwwwww"),
            list("wwwwwwfwwowwwwwwwwowwfwwwwww"),
            list("wwwwwwfwwowwwwwwwwowwfwwwwww"),
            list("wffffffffffffwwffffffffffffw"),
            list("wfwwwwfwwwwwfwwfwwwwwfwwwwfw"),
            list("wfwwwwfwwwwwfwwfwwwwwfwwwwfw"),
            list("wPffwwfffffffoofffffffwwffPw"),
            list("wwwfwwfwwfwwwwwwwwfwwfwwfwww"),
            list("wwwfwwfwwfwwwwwwwwfwwfwwfwww"),
            list("wffffffwwffffwwffffwwffffffw"),
            list("wfwwwwwwwwwwfwwfwwwwwwwwwwfw"),
            list("wfwwwwwwwwwwfwwfwwwwwwwwwwfw"),
            list("wffffffffffffffffffffffffffw"),
            list("wwwwwwwwwwwwwwwwwwwwwwwwwwww"),
                 ]

        def __repr__(self):
            return self.grid




# w is wall
# f is food
# o is open
# P is power pallet
# G is Ghost house

maze = Maze()
level = 0


def get_food_left():
    maze_ref = []
    for y in range(len(maze.grid)):
        for x in range(len(maze.grid[y])):
            maze_ref.append(maze.grid[y][x])
    return len(filter(lambda pos: pos == "f", maze_ref))

max_food = get_food_left()


class Fruit(object):        # fruit is (0, level*20, 14, 14)
    def __init__(self):
        self.x = 13
        self.y = 17
        self.time_left = 7*fps
        self.available = False
        self.sprite = pygame.image.load("./Sprites/misc/fruits.png")
        self.score_frames = 0
        self.score_sprite = pygame.image.load("./Sprites/misc/fruit_scores.png")

    def check_availability(self):
        if not self.available:
            if get_food_left() == 160:
                self.available = True
            elif get_food_left() == 80:
                self.available = True
        else:
            self.time_left -= 1
            if self.time_left == 0:
                self.available = False
                self.time_left = 7*fps

    def draw(self):
        if self.available:
            fruit_surface = pygame.Surface((14, 14))
            fruit_surface.blit(self.sprite, (0, 0),
                               (0, level*20 if level < 7 else 7*20, 14, 14))
            fruit_surface.set_colorkey((0, 0, 0))
            Screen.screen.blit(fruit_surface, (self.x*8 - 3, self.y*8 + 16 - 3))

        if self.score_frames > 0:
            self.score_frames -= 1
            score_surface = pygame.Surface((22, 9))
            score_surface.blit(self.score_sprite, (0, 0),
                               (0, level*20 if level < 7 else 7*20, 22, 9))
            score_surface.set_colorkey((0, 0, 0))
            Screen.screen.blit(score_surface, (self.x*8 - 7, self.y*8 + 16))

        fruit_surface = pygame.Surface((14*(level + 1), 14))
        for fruit in range(level + 1 if level < 7 else 7):
            fruit_surface.blit(self.sprite, (14*(level + 1) - 14*(fruit + 1), 0),
                               (0, fruit*20, 40, 40))
        Screen.screen.blit(fruit_surface, (208 - 14*level if level < 7 else 208 - 14*7, 272))

fruit = Fruit()


class ScreenClass(object):
    def __init__(self):
        self.screen = pygame.display.set_mode((width, height))
        self.maze = pygame.image.load("./Sprites/misc/pac-man_maze.png")
        self.food = pygame.image.load("./Sprites/misc/food.png")
        self.power_p = pygame.image.load("./Sprites/misc/powerp.png")
        self.life = pygame.image.load("./Sprites/misc/life.png")

    def update(self):
        self.screen.fill(black)
        self.screen.blit(self.maze, (0, 8))
        
        for y in range(len(maze.grid)):
            for x in range(len(maze.grid[y])):
                if maze.grid[y][x] == "f":
                    self.screen.blit(self.food, (8*x, 16 + 8*y))
                elif maze.grid[y][x] == "P":
                    if frames % 2 == 0:
                        self.screen.blit(self.power_p, (8*x, 16 + 8*y))

        score_word = pac_font.render("SCORE", 1, white)
        score_value = pac_font.render("0" * (5 - len(str(pac_man.score))) + str(pac_man.score), 1, white)
        self.screen.blit(score_word, (73, -2))
        self.screen.blit(score_value, (73, 6))

        for life in range(pac_man.lives):
            self.screen.blit(self.life, (life*12, 274))

        if frames % 2 == 0:
            fruit.check_availability()

        fruit.draw()

        pac_man.draw()
        shadow.draw()
        pinky.draw()
        bashful.draw()
        pokey.draw()

        pygame.display.update()

Screen = ScreenClass()


class PacMan(object):

    directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]

    def __init__(self):
        self.x = 14
        self.y = 23
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.frame = 0
        self.sprites = [pygame.image.load("./Sprites/pac/pac_open.png"),
                        pygame.image.load("./Sprites/pac/pac_mid.png"),
                        pygame.image.load("./Sprites/pac/pac_closed.png"),]
        self.sprites.append(self.sprites[1])
        self.score = 0
        self.powered = 0
        self.has_moved = False
        self.lives = 3
        self.ghosts_destroyed = 0
        self.death_animation_image = pygame.image.load("./Sprites/pac/death_animation.png")
        # 5 extra down per frame
        self.has_eaten = False
        self.dead = False

    def draw(self):
        if not self.dead:
            rotated = pygame.transform.rotate(self.sprites[self.frame], 90*self.directions.index(self.direction))
            rotated.set_colorkey((0, 0, 0))
            Screen.screen.blit(rotated, (self.x*8 - 3, 16 + self.y*8 - 3))

    def death_animation(self):
        pac_chomp_channel.stop()
        siren_channel.stop()
        pac_death_channel.play(pac_death)
        death_surface = pygame.Surface((14, 14))
        for frame in range(11):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.quit()
                    pygame.quit()
                    quit()
            Screen.update()
            death_surface.blit(self.death_animation_image, (0, 0), (20*frame, 0, 15, 14))
            death_surface.set_colorkey((0, 0, 0))
            Screen.screen.blit(death_surface, (8*self.x - 3, 16 + 8*self.y - 3))
            pygame.display.flip()
            clock.tick(8)
        while pac_death_channel.get_busy():
            clock.tick(fps)

    def die(self):
        self.dead = True
        global frames
        shadow.__init__("shadow")
        pinky.__init__("pinky")
        bashful.__init__("bashful")
        pokey.__init__("pokey")
        pac_chomp_channel.stop()
        siren_channel.stop()
        self.death_animation()
        self.lives -= 1
        self.x = 14
        self.y = 23
        frames = 0
        self.dead = False
        if self.lives > 0:
            intro()
        else:
            game_over()

    def eat_pallet(self):
        pac_chomp_channel.play(pac_eatpallet)
        while pac_chomp_channel.get_busy():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.quit()
                    pygame.quit()
                    quit()
            Screen.update()
            clock.tick(fps)

    def move(self):
        if not invincibility:
            for ghost in [shadow, pinky, bashful, pokey]:
                if (self.x == ghost.x and self.y == ghost.y) or\
                        (self.x + self.direction[0] == ghost.x and self.y + self.direction[1] == ghost.y) or\
                        (self.x == ghost.x + ghost.direction[0] and self.y == ghost.y + ghost.direction[1]):
                    if ghost.mode == "scared":
                        ghost.die()
                        self.score += 100*2**self.ghosts_destroyed
                        self.ghosts_destroyed += 1
                    elif ghost.mode != "dead":
                        self.die()

        opens = []
        for direction in self.directions:
            if len(maze.grid[self.y]) > self.x + direction[0] >= 0:
                if len(maze.grid) > self.y + direction[1] >= 0:
                    if maze.grid[self.y + direction[1]][self.x + direction[0]] != "w":
                        opens.append(direction)

        if self.next_direction in opens:
            self.direction = self.next_direction

        if self.x + self.direction[0] < 0:
            self.x = 27
            self.has_moved = True
        elif self.x + self.direction[0] > 27:
            self.x = 0
            self.has_moved = True
        elif maze.grid[self.y + self.direction[1]][self.x + self.direction[0]] != "w":
            self.y += self.direction[1]
            self.x += self.direction[0]
            self.has_moved = True
        else:
            self.has_moved = False

        if maze.grid[self.y][self.x] == "f":
            maze.grid[self.y][self.x] = "o"
            self.score += 10
            self.has_eaten = True
        elif maze.grid[self.y][self.x] == "P":
            maze.grid[self.y][self.x] = "o"
            self.has_eaten = True
            self.ghosts_destroyed = 0
            self.powered = 10 * fps
            self.score += 50
            self.eat_pallet()
            for ghost in [shadow, pinky, bashful, pokey]:
                if ghost.mode != "trapped":
                    ghost.mode = "scared"
        elif (self.x, self.y) == (fruit.x, fruit.y):
            fruit.__init__()
            self.score += [100, 300, 500, 700, 1000, 2000, 3000, 5000][level] if level < 7 else 5000
            fruit.score_frames = 2*fps
            self.eat_pallet()

pac_man = PacMan()


def get_distance(pos1, pos2):
    # pos1 and pos2 are both tuples
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


class GhostClass(object):

    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    def __init__(self, name, scatter_target):
        self.name = name
        self.scatter_target = scatter_target
        self.x = 14
        self.y = 11
        self.direction = (-1, 0)
        self.target = (10, 20)
        self.mode = "normal"
        self.scared_frame = 0
        self.walk_frame = 0
        self.sprites = {
            "normal": pygame.image.load("./Sprites/ghosts/%s.png" % self.name),
            "scared": [pygame.image.load("./Sprites/ghosts/scared1.png"),
                       pygame.image.load("./Sprites/ghosts/scared2.png")],
            "dead": pygame.image.load("./Sprites/ghosts/dead.png"),
            "trapped": pygame.image.load("./Sprites/ghosts/%s_trapped.png" % self.name)
        }

    def __repr__(self):
        return self.name

    def get_target(self):
        self.target = (pac_man.x, pac_man.y)

    def move(self):
        self.get_target()

        opens = []
        for direction in self.directions:
            if direction != (-self.direction[0], -self.direction[1]):
                if len(maze.grid[self.y]) > self.x + direction[0] >= 0:
                    if len(maze.grid) > self.y + direction[1] >= 0:
                        if maze.grid[self.y + direction[1]][self.x + direction[0]] != "w":
                            opens.append(direction)

        distances = {}
        for direction in opens:
            distances[direction] = get_distance((self.x + direction[0], self.y + direction[1]), self.target)

        opens = sorted(opens, key=lambda x: distances[x])

        if len(opens) > 0:
            self.direction = opens[0]

        self.x = (self.x + self.direction[0]) % 28
        self.y += self.direction[1]

    def draw(self):
        ghost_surface = pygame.Surface((14, 14))
        if self.mode == "normal" or self.mode == "scatter":
            ghost_surface.blit(self.sprites["normal"], (0, 0),
                               (self.directions.index(self.direction)*40 + 40 - (self.walk_frame + 1)*20, 0, 14, 14))
        elif self.mode == "scared":
            ghost_surface.blit(self.sprites["scared"][self.scared_frame], (0, 0),
                               (20*self.walk_frame, 0, 14, 14))
        elif self.mode == "dead":
            ghost_surface.blit(self.sprites["dead"], (0, 0),
                               (self.directions.index(self.direction)*20, 0, 14, 14))
        elif self.mode == "trapped":
            ghost_surface.blit(self.sprites["trapped"], (0, 0))

        ghost_surface.set_colorkey((0, 0, 0))
        Screen.screen.blit(ghost_surface, (8*self.x - 3, 16 + 8*self.y - 3))

    def die(self):
        pac_chomp_channel.stop()
        siren_channel.stop()
        ghost_death_channel.play(pac_eatghost)
        self.target = (14, 11)
        self.mode = "dead"
        while ghost_death_channel.get_busy():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.quit()
                    pygame.quit()
                    quit()
            Screen.update()
            score_surface = pygame.Surface((16, 7))
            score_surface.blit(ghost_eat_scores, (0, 0), (pac_man.ghosts_destroyed*20, 0, 16, 7))
            score_surface.set_colorkey((0, 0, 0))
            Screen.screen.blit(score_surface, (pac_man.x*8 - 3, pac_man.y*8))
            pygame.display.flip()
            clock.tick(fps)

        ghost_death_channel.play(ghost_death)
        ghost_death_channel.stop()

    def get_mode(self):
        if self.mode != "trapped" and self.mode != "scared" and self.mode != "dead":
            secs = frames/fps
            if secs < 7:                # scatter for 7 seconds (up to 7)
                self.mode = "scatter"
            elif secs < 27:             # normal for 20 seconds (up to 27)
                self.mode = "normal"
            elif secs < 34:             # scatter for 7 seconds (up to 34)
                self.mode = "scatter"
            elif secs < 54:             # normal for 20 seconds (up to 54)
                self.mode = "normal"
            elif secs < 59:             # scatter for 5 seconds (up to 59)
                self.mode = "scatter"
            elif secs < 79:             # normal for 20 seconds (up to 79)
                self.mode = "normal"
            elif secs < 84:             # scatter for 5 seconds (up to 84)
                self.mode = "scatter"
            else:                       # normal forever
                self.mode = "normal"


class Shadow(GhostClass):
    def __init__(self, name):
        GhostClass.__init__(self, name, (25, -2))

    def get_target(self):
        self.get_mode()
        if self.mode == "normal":
            self.target = (pac_man.x, pac_man.y)
        elif self.mode == "scared":
            self.target = (random.randint(0, 27), random.randint(0, 27))
        elif self.mode == "scatter":
            self.target = self.scatter_target


class Pinky(GhostClass):
    def __init__(self, name):
        GhostClass.__init__(self, name, (2, -2))
        self.x = 13.5
        self.y = 14
        self.mode = "trapped"

    def get_target(self):
        self.get_mode()
        if self.mode == "normal":
            self.target = (pac_man.x + 4*pac_man.direction[0], pac_man.y + 4*pac_man.direction[1])
        elif self.mode == "scared":
            self.target = (random.randint(0, 27), random.randint(0, 27))
        elif self.mode == "scatter":
            self.target = self.scatter_target


class Bashful(GhostClass):
    def __init__(self, name):
        GhostClass.__init__(self, name, (25, 33))
        self.x = 11.5
        self.y = 14
        self.mode = "trapped"

    def get_target(self):
        self.get_mode()
        if self.mode == "normal":
            self.target = (shadow.x + 2*(pac_man.x - shadow.x),
                           shadow.y + 2*(pac_man.y - shadow.y))
        elif self.mode == "scared":
            self.target = (random.randint(0, 27), random.randint(0, 27))
        elif self.mode == "scatter":
            self.target = self.scatter_target


class Pokey(GhostClass):
    def __init__(self, name):
        GhostClass.__init__(self, name, (0, 33))
        self.x = 15.5
        self.y = 14
        self.mode = "trapped"

    def get_target(self):
        self.get_mode()
        if self.mode == "normal":
            if get_distance((self.x, self.y), (pac_man.x, pac_man.y)) <= 8:
                self.target = (pac_man.x, pac_man.y)
            else:
                self.target = (0, 29)
        elif self.mode == "scared":
            self.target = (random.randint(0, 27), random.randint(0, 27))
        elif self.mode == "scatter":
            self.target = self.scatter_target

shadow = Shadow("shadow")
pinky = Pinky("pinky")
bashful = Bashful("bashful")
pokey = Pokey("pokey")
ghostlist = [shadow, pinky, bashful, pokey]

frames = 0


def intro():
    music = pygame.mixer.Sound("./Sounds/pacman_beginning.wav")
    music_channel = pygame.mixer.Channel(1)
    music_channel.set_volume(volume)
    ready = pygame.image.load("./Sprites/misc/ready.png")
    Screen.update()
    Screen.screen.blit(ready, (112 - 23, 16 + 17*8))
    music_channel.play(music)
    while music_channel.get_busy():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.quit()
                pygame.quit()
                quit()
        pygame.display.flip()

if not testing:
    intro()

siren_channel.play(siren, -1)

while not GameExit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GameExit = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                pac_man.next_direction = (0, 1)
            elif event.key == pygame.K_UP:
                pac_man.next_direction = (0, -1)
            elif event.key == pygame.K_LEFT:
                pac_man.next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                pac_man.next_direction = (1, 0)

    if any([ghost.mode == "dead" for ghost in ghostlist]):
        if siren_channel.get_sound() != ghost_death:
            siren_channel.play(ghost_death)
        for ghost in ghostlist:
            if ghost.mode == "dead":
                ghost.move()
                if (ghost.x, ghost.y) == ghost.target:
                    ghost.mode = "normal"
                    siren_channel.play(siren, -1)
    elif not siren_channel.get_busy():
        siren_channel.play(siren, -1)

    if pac_man.has_moved:
        pac_man.frame = (pac_man.frame + 1) % 4
        for ghost in [shadow, pinky, bashful, pokey]:
            ghost.walk_frame = (ghost.walk_frame + 1) % 2
        if frames % 2 == 0:
            if pac_man.has_eaten:
                if not pac_chomp_channel.get_queue():
                    pac_chomp_channel.queue(pac_chomp)
                    pac_man.has_eaten = False
            else:
                pac_chomp_channel.stop()

    if frames % 2 == 0:
        pac_man.move()
        for ghost in [shadow, pinky, bashful, pokey]:
            if ghost.mode != "trapped" and ghost.mode != "dead":
                ghost.move()

    if pac_man.powered > 0:
        pac_man.powered -= 1
        if pac_man.powered < 2*fps:
            shadow.scared_frame = (shadow.scared_frame + 1) % 2
            pinky.scared_frame = (pinky.scared_frame + 1) % 2
            bashful.scared_frame = (bashful.scared_frame + 1) % 2
    else:
        shadow.frame = bashful.frame = pinky.frame = 0
        for ghost in ghostlist:
            if ghost.mode != "trapped":
                ghost.mode = "normal"
                ghost.get_mode()

    if frames == 3*fps and pinky.mode == "trapped":
        pinky.y = 11
        pinky.x = 14
        pinky.mode = "normal"

    if max_food - get_food_left() >= 30 and bashful.mode == "trapped":
        bashful.y = 11
        bashful.x = 14
        bashful.mode = "normal"

    if get_food_left()/float(max_food) <= 0.333333 and pokey.mode == "trapped":
        pokey.y = 11
        pokey.x = 14
        pokey.mode = "normal"

    if get_food_left() == 0:
        siren_channel.stop()
        maze.__init__()
        for ghost in ghostlist:
            ghost.__init__(ghost.name)
        pac_man.x, pac_man.y = 14, 23
        level += 1
        intro()

    Screen.update()
    frames += 1
    if frames > 2000:
        frames = 1000
    clock.tick(fps)

pygame.mixer.quit()
pygame.quit()
quit()
