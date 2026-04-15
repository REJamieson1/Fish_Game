import pygame
import random as rand
import time

'''
NOTES:
Ideas
    unpixelize
    terrain
    water momentum vector field
Menu
    4th menu option
    time scale
    tank size
    exit back to menu
continuous traits
    speed
    agression 
    reproduction size
    field of vision 
    Hunting and fleeing decisivness
continuous traits to impliment
    preditor precission
    Phenotypic plasticity
descrete traits
    fish (classic)
        cells randomly thrown
        based on size
    snake
        first in first out
    wall bound
        forced to wall
        less energy
descrete traits to impliment
    Single cell offspring
        maybe uses targeting to stay close to parent

    mold
        eats one grows two in that direction
        does not move beside growing
    pathogen
        single cell
        ats any size
    enzyme of disinigration
        turns target to food
        requires mass
    chameleon
        id fluid
        requires energy
Cleaning
    readme
Game
    player fish being eaten

'''

POS_X_MAX = 1200
POS_Y_MAX = 600
COORD_X_MAX = 200
COORD_Y_MAX = COORD_X_MAX // 2
CELL_SIZE = int(POS_X_MAX / COORD_X_MAX)
FAM = 0
FRAMES = 0
ALL_SPECIES = []
FULL_SPACE = []
START_MENU = True
SIMULATE_GAME = False
PLAYER_GAME = False
TWO_PLAYER_GAME = False
NUMBER_OF_PLAYER_FISH = 0
NUMBER_OF_GENUS = 4

running = True
pygame.init()
screen = pygame.display.set_mode((POS_X_MAX, POS_Y_MAX))
total_fish_newness = 0
background = (7, 10, 20)
menu_font = pygame.font.Font('freesansbold.ttf', 30)
ALL_FOOD = []
ALL_FISH = []


def pos_to_coord(pos):
    '''
    Docstring for pos_to_coord
    
    :param pos: A pixel coordinates 
    :returns tuple: Cell coordinates
    '''
    return (int(pos[0] // CELL_SIZE), int(pos[1] // CELL_SIZE))


def coord_to_rect(coord):
    '''
    Docstring for coord_to_rect
    
    :param coord: Cell coordinates
    :returns pygame Rect object: The cell square to be drawn
    '''
    return pygame.Rect(coord[0] * CELL_SIZE, coord[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def in_bound(coord):
    '''
    Docstring for in_bound
    
    :param coord: Cell coordinates
    :returns boolean: Wether or not the cell is in the screen frame
    '''
    if coord[0] >= 0 and coord[0] < COORD_X_MAX and coord[1] >= 0 and coord[1] < COORD_Y_MAX:
        return True
    return False


class Food():
    '''
    Docstring for Food
    Class for food objects
    '''

    def __init__(self, start):
        '''
        Docstring for __init__
        Sets individual characteristics 
            flakyness
            weight

        :param start: Starting coordinate
        '''
        self.coords = start
        self.flakey = rand.randint(3, 15) 
        self.weight = rand.randint(1, 30) 


    def move(self):
        '''
        Docstring for move
        Pulls food downward and other directions
        '''
        if rand.randint(0, self.weight): 
            new_coords = (self.coords[0] + rand.choice([-1] + [0] * self.flakey +[1]), self.coords[1] + 1)
            if new_coords[1] > COORD_Y_MAX - 1 or new_coords[0] > COORD_X_MAX - 1 or new_coords[0] < 1 or new_coords in FULL_SPACE:
                if self.coords not in FULL_SPACE:
                    FULL_SPACE.append(self.coords)
                return
            if self.coords in FULL_SPACE:
                FULL_SPACE.remove(self.coords)
            self.coords = new_coords


class Fish():
    '''
    Docstring for Fish
    Class for individual fish objects
    '''

    def __init__(self, id=None, genes=()):
        '''
        Docstring for __init__
        Creates new fish from sctratch or inherited genes
        
        :param id: New id and familiy indicator
        :param genes: Tuple of genes includes cells, color, aggression, division size, field of vew, decisivness, inherited id, genus(shape)
        '''
        if genes: # inheritance
            self.cells, self.color, self.speed, self.agro, self.division, self.vision, self.decisivness, self.id, self.genus = genes 
        else: # if new fish
            self.cells = [(rand.randint(0, COORD_X_MAX - 1), rand.randint(0, COORD_Y_MAX - 1))]
            if not rand.randint(0, 2):
                self.cells.append((self.cells[0][0] - 1, self.cells[0][1]))
            self.speed = rand.randint(10, 30)
            self.agro = rand.randint(0, 100) 
            self.division = rand.randint(4, 100)
            self.speed += self.division // 8
            self.vision = rand.randint(10, 40)
            self.decisivness = rand.randint(0, 99)
            self.id = id
            self.genus = rand.choices(range(NUMBER_OF_GENUS), weights=[5, 1, 3, 2], k=1)[0]
            
            if (self.agro / 101) > 1:
                g = 255
            else:
                g = 255 * (self.agro / 101)

            if ((self.speed - 10) / 21) > 1:
                r = 255
            else:
                r = 255 * ((self.speed - 10) / 21)

            if ((self.vision - 10) / 31) > 1:
                b = 255
            else:
                b = 255 * ((self.vision - 10) / 31)

            self.color = (r, g, b)

        
        self.energy = 200
        self.food_targets = []
        self.fish_targets = []
        self.hunt = False
        self.danger = []
        self.targ_count = 0
        self.target = None
        ALL_SPECIES.append(self.id)


    def radar_and_lock(self):
        '''
        Docstring for radar_and_lock
        Searches for food or small fish within FOV and sets a target
        '''
        self.danger = []
        self.targ_count = 0

        for food in ALL_FOOD:
            if food.coords[0] < self.cells[0][0] + self.vision:
                if food.coords[0] > self.cells[0][0] - self.vision:
                    if food.coords[1] < self.cells[0][1] + self.vision:
                        if food.coords[1] > self.cells[0][1] - self.vision:
                            self.food_targets.append(food)
                            self.targ_count += 1

        for fish in ALL_FISH:
            if fish.cells[0][0] < self.cells[0][0] + self.vision:
                if fish.cells[0][0] > self.cells[0][0] - self.vision:
                    if fish.cells[0][1] < self.cells[0][1] + self.vision:
                        if fish.cells[0][1] > self.cells[0][1] - self.vision:
                            if self.id != fish.id:
                                if len(fish.cells) <= len(self.cells) / 2:
                                    if len(self.cells) > 1:
                                        if ((self.target != my_fish) and (self.target != my_fish_2)) or self.target.cells[0] != (60, 30): # design is bad
                                            self.fish_targets.append(fish)
                                            self.targ_count += 1
                                elif len(fish.cells) >= len(self.cells) / 2:
                                    for _ in fish.cells:
                                        self.danger.append(fish)

        tag_type = rand.choice(['food'] * (100 - self.agro) + ['fish'] * (self.agro))
        if tag_type == 'food':
            targ_type = self.food_targets
        else:
            targ_type = self.fish_targets
        if targ_type:
            self.hunt = True
            self.target = rand.choice(targ_type)
        else:
            self.target = None


    def use_energy(self):
        '''
        Docstring for use_energy
        Removes energy and decays if out of energy
        '''
        self.energy -= 1
        if self.energy < 0:
            self.decay


    def mitosis(self):
        '''
        Docstring for mitosis
        Removes half of the cells and creates a mutated fish with them
        '''
        ALL_FISH.append(Fish(genes = (self.cells[self.division // 2:], self.color, self.speed, self.agro, self.division, self.vision, self.decisivness, self.id, self.genus)))
        ALL_FISH[-1].mutate()
        self.cells = self.cells[:self.division//2]


    def eat_target(self):
        '''
        Docstring for eat_target
        Removes cell from target and adds it to self
        '''
        if ((self.target != my_fish) and (self.target != my_fish_2)) or self.target.cells[0] != (60, 30):
            self.cells.append(self.cells[0])
            self.target.cells.remove(self.cells[0])
        if not len(self.target.cells):
            if self.target == my_fish:
                game_over(my_fish)
            elif self.target == my_fish_2:
                game_over(my_fish_2)
            else:
                ALL_FISH.remove(self.target)
        

    def eat_food(self):
        '''
        Docstring for eat_food
        Removes food object and adds cell to fish
        '''
        ALL_FOOD.remove(self.target)
        if self.target.coords in FULL_SPACE:
            FULL_SPACE.remove(self.target.coords)
        self.cells.append(self.cells[0])
        return True
        
    def flee(self):
        '''
        Docstring for flee
        Chooses a predator and moves fish in opposite direction
        '''
        pred = rand.choice(self.danger)
        if pred.cells:
            coords = pred.cells[0]
            if rand.choice([1] * (abs(self.cells[0][0] - coords[0]) + 1) + [0] * (abs(self.cells[0][1] - coords[1]) + 1)):
                if coords[0] > self.cells[0][0]:
                    new_coords = (self.cells[0][0] - 1, self.cells[0][1])
                else:
                    new_coords = (self.cells[0][0] + 1, self.cells[0][1])
            else:
                if coords[1] > self.cells[0][1]:
                    new_coords = (self.cells[0][0], self.cells[0][1] - 1)
                else:
                    new_coords = (self.cells[0][0], self.cells[0][1] + 1)
            
            if in_bound(new_coords):
                del self.cells[-1]
                self.cells.insert(0, new_coords)
        else:
            self.danger.remove(pred)


    def random_direction(self):
        '''
        Docstring for random_direction
        Moves cells in small random directions
        For idling or less presicion
        '''
        r_direction = rand.randint(1, 6)
        if 1 <= r_direction <= 2:
            new_coords = (self.cells[0][0] + 1, self.cells[0][1])
        elif 3 <= r_direction <= 4:
            new_coords = (self.cells[0][0] - 1, self.cells[0][1])
        elif r_direction == 5:
            new_coords = (self.cells[0][0], self.cells[0][1] + 1)
        else:
            new_coords = (self.cells[0][0], self.cells[0][1] - 1)
        if in_bound(new_coords):
            del self.cells[-1]
            self.cells.insert(0, new_coords)


    def chase(self, coords):
        '''
        Docstring for chase
        Moves fish in direction of a coordinate
        
        :param coords: Desired coordinates for fish
        '''
        if rand.choice([1] * (100 * abs(self.cells[0][0] - coords[0]) + 1) + [0] * (100 * abs(self.cells[0][1] - coords[1]) + 1)):
            if coords[0] > self.cells[0][0]:
                new_coords = (self.cells[0][0] + 1, self.cells[0][1])
            else:
                new_coords = (self.cells[0][0] - 1, self.cells[0][1])
        else:
            if coords[1] > self.cells[0][1]:
                new_coords = (self.cells[0][0], self.cells[0][1] + 1)
            else:
                new_coords = (self.cells[0][0], self.cells[0][1] - 1)
        if in_bound(new_coords):
            del self.cells[-1]
            self.cells.insert(0, new_coords)
        

    def move(self):
        '''
        Docstring for move
        A fish's move wher they use energy, mainyani shape, check for division, check for eating, fleeing and chasing
        '''
        self.use_energy()
        self.build_genus()

        if len(self.cells) > self.division:
            self.mitosis()

        #eating target
        if self.target in set(ALL_FISH):
            coords = self.target.cells[0]
            if self.cells[0] == coords:
                self.eat_target()
                return

        #eating food
        elif self.target in set(ALL_FOOD):
            coords = self.target.coords
            if self.cells[0] == coords:
                self.eat_food()
                return
            
        # flee or random
        else:
            if (not self.hunt and self.danger) or rand.randint(0,len(self.danger)): # encorperate inverse agro
                self.flee()
            
            if not rand.randint(0, 3): # encorperate precission
                self.random_direction()

            self.hunt = False
            return

        self.chase(coords)
        


    def build_genus(self):
        '''
        Docstring for build_genus
        Does specific genus action based on set genus
        '''
        if self.genus == 0:
            self.genus_classic()
        elif self.genus == 1:
            self.genus_snake()
        elif self.genus == 2:
            self.genus_wall_ball()
        elif self.genus == 3:
            self.genus_dense()


    def fluff_cells(self, width=1, density=1):
        '''
        Docstring for fluff_cells
        Moves cells to sides of fish
        
        :param width: The maximumwidth for a specific fish
        :param density: The density of cells within the width
        '''
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        rand.shuffle(directions)
        for i in range(width):
            for direction in directions:
                if density and rand.randint(0, 10):
                    if i > 2:
                        swap_coord = rand.randint(1, int(i / 2))
                        if direction[0]:
                            a = i - swap_coord
                            b = swap_coord
                        else:
                            a = swap_coord
                            b = i - swap_coord
                    else:
                        a = i
                        b = i
                    side_coords = (self.cells[0][0] + direction[0] * a, self.cells[0][1] + direction[1] * b)
                    if side_coords not in set(self.cells) and in_bound(side_coords):
                        del self.cells[-1]
                        self.cells.insert(1, side_coords)
                        density -= 1


    def genus_classic(self):
        '''
        Docstring for genus_classic
        Adds "fluff" cells using convoluted method
        '''
        a, b = rand.choice([(0, 1),(0, -1),(1, 0),(-1, 0)])
        side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
        if side_coords not in set(self.cells) and in_bound(side_coords):
            del self.cells[-1]
            self.cells.insert(1, side_coords)

        if len(self.cells) > 15:
            a, b = rand.choice([(0, 1),(0, -1),(1, 0),(-1, 0)])
            side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
            if side_coords not in set(self.cells) and in_bound(side_coords):
                del self.cells[-1]
                self.cells.insert(1, side_coords)

            if len(self.cells) > 25:
                a, b = rand.choice([(0, 2),(0, -2),(2, 0),(-2, 0), (-1, 1), (1, 1), (1, -1), (-1, -1)])
                side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
                if side_coords not in set(self.cells) and in_bound(side_coords):
                    del self.cells[-1]
                    self.cells.insert(1, side_coords)

                if len(self.cells) > 35:
                    a, b = rand.choice([(0, 2),(0, -2),(2, 0),(-2, 0), (-1, 1), (1, 1), (1, -1), (-1, -1)])
                    side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
                    if side_coords not in set(self.cells) and in_bound(side_coords):
                        del self.cells[-1]
                        self.cells.insert(1, side_coords)


    def genus_snake(self):
        '''
        Docstring for genus_snake
        Turns one in four snakes thick
        '''
        if not self.id % 4:
            self.fluff_cells()


    def genus_wall_ball(self):
        '''
        Docstring for genus_wall_ball
        Forces a fish to one direction and gives them more energy
        '''
        if not self.id % 4:
            new_coords = (self.cells[0][0] + 1, self.cells[0][1])
        elif self.id % 4 == 1:
            new_coords = (self.cells[0][0] - 1, self.cells[0][1])
        elif self.id % 4 == 2:
            new_coords = (self.cells[0][0], self.cells[0][1] + 1)
        else:
            new_coords = (self.cells[0][0], self.cells[0][1] - 1)
        if in_bound(new_coords):
            if rand.randint(0, 70):
                del self.cells[-1]
            self.cells.insert(0, new_coords)
        if rand.randint(0, 3):
            self.energy += 1


    def genus_dense(self):
        '''
        Docstring for genus_dense
        Moves cells to the sides of the fish solidly
        '''
        self.fluff_cells(int(((len(self.cells) // 10) + 1) ** 0.7), (int(((len(self.cells) // 10) + 1) ** 0.7)))


    def decay(self):
        '''
        Docstring for decay
        Removes cells and replenishes energy
        Turns fish to food if out of cells
        '''
        if len(self.cells) == 1:
            ALL_FOOD.append(Food(self.cells[0]))
            if self == my_fish:
                game_over(my_fish)
            elif self == my_fish_2:
                game_over(my_fish_2)
            else:
                ALL_FISH.remove(self)
        else:
            for _ in range(int(len(self.cells) // 8)):
                del self.cells[-1]
            self.energy = 200


    def mutate(self):
        '''
        Docstring for mutate
        Slightly changes speed, agression, reproduction size, and FOV in offspring
        Small chance of familiy or genus mutation
        '''
        new_color = (self.color[0] + rand.randint(-15, 15), self.color[1] + rand.randint(-15, 15), self.color[2] + rand.randint(-15, 15))
        if 0 <= list(new_color)[0] <= 255 and 0 <= list(new_color)[1] <= 255 and 0 <= list(new_color)[2] <= 255:
            self.color = new_color
        for gene in [self.speed, self.agro, self.division, self.vision]:
            gene += rand.randint(-2, 2)
        if not rand.randint(0, 115):
            self.genus = rand.randint(0, NUMBER_OF_GENUS)
        if not rand.randint(0, 15):
            global FAM
            self.id = FAM
            FAM += 1


def my_move(arrows, fish):
    '''
    Docstring for my_move
    Moves fish and uses energy based on user input

    :param arrows: Four booleans representing left, right, up, down
    :param fish: my_fish or my_fish_2
    '''
    if True in arrows and rand.randint(-1, (fish.speed)) > 0 and not FRAMES % 3:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        direction_options = []

        for i, arrow in enumerate(arrows):
            if arrow:
                a, b = directions[i]
                direction_options.append((fish.cells[0][0] + a, fish.cells[0][1] + b))        
        
        if len(direction_options) > 1:
            new_coord = rand.choice(direction_options)
        else:
            new_coord = rand.choices([direction_options[0] , [rand.choice([(fish.cells[0][0] - 1, fish.cells[0][1]), (fish.cells[0][0] + 1, fish.cells[0][1]), (fish.cells[0][0], fish.cells[0][1] - 1), (fish.cells[0][0], fish.cells[0][1] + 1)])][0]], weights=[10, 1], k=1)[0]
        if in_bound(new_coord):
            del fish.cells[-1]
            fish.cells.insert(0, new_coord)

        fish.build_genus()
        fish.use_energy()

    
def my_eat_fish(selfish, prey):
    '''
    Docstring for my_eat_fish
    If player fish is eating fish, removes cell from prey and adds to player fish
    
    :param selfish: my_fish or my_fish_2
    :param prey: Autonomus fish
    '''
    if len(prey.cells) <= len(selfish.cells) / 2:
        if selfish.cells[0] in prey.cells:
            prey.cells.remove(selfish.cells[0])
            if not len(prey.cells):
                ALL_FISH.remove(prey) 
            selfish.cells.append(selfish.cells[0])


def my_eat_food(selfish, food):
    '''
    Docstring for my_eat_food
    If player fish is eating food, removes food and add cell to player fish
   
    :param selfish: my_fish or my_fish_2
    :param food: Any food
    '''
    if food.coords == selfish.cells[0]:
        ALL_FOOD.remove(food)
        if food in FULL_SPACE:
            FULL_SPACE.remove(food.coords)
        selfish.cells.append(food.coords)


def player_attack(player_1, player_2):
    '''
    Docstring for player_attack
    If player fish is eating other player fish, then tranfer cells or game over
    
    :param player_1: my_fish or my_fish_2
    :param player_2: The other player fish
    '''
    if len(player_2.cells) <= len(player_1.cells) / 2:
        if player_1.cells[0] in player_2.cells and player_2.cells[0] != (60, 30):
            player_1.cells.append(player_1.cells[0])
            player_2.cells.remove(player_1.cells[0])
            if not len(player_2.cells):
                game_over(player_2)    

    else:
        if player_2.cells[0] in player_1.cells and player_2.cells[0] != (60, 30):
            player_2.cells.append(player_2.cells[0])
            player_1.cells.remove(player_2.cells[0])
            if not len(player_1.cells):
                game_over(player_1)            


def game_over(player):
    '''
    Docstring for game_over
    Respawns player fish after death
    For now
    
    :param player: Player's fish who lost all cells
    '''
    player.cells = [(60, 30), (60, 31)]
    player.energy = 200


def present_start_menu():
    '''
    Docstring for present_start_menu
    Draws start menu options and text
    '''
    menu_options = ['Feed Fish', 'One Fish', 'Two Fish', 'Coming Soonish']
    x_text_vals = [530, 535, 535, 480]
    for i in range(4):
        pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(450, 200 + 60 * i, 300, 40))
        screen.blit(menu_font.render(menu_options[i], True, (0, 0, 0)), (x_text_vals[i], 205 + 60 * i))


def select_game_mode(coords):
    '''
    Docstring for select_game_mode
    Sets game mode global variable to True if chosen

    :param coords: coordinates of mouse when clicked during start screen
    :returns boolean: whether or not a game mode was selected
    '''
    # Maybe do this iteratively?
    global SIMULATE_GAME
    global PLAYER_GAME
    global TWO_PLAYER_GAME
    if coords[0] >= 450:
        if coords[0] <= 750:
            if 200 <= coords[1] and coords[1] <= 240:
                SIMULATE_GAME = True
                return True
            if 260 <= coords[1] <= 300:
                PLAYER_GAME = True
                return True
            if 320 <= coords[1] <= 340:
                PLAYER_GAME = True
                TWO_PLAYER_GAME = True
                return True
            if 380 <= coords[1] <= 420:
                return False
    return False

my_fish = Fish(genes = ([(80, 30), (80, 31)], (220, 60, 60), 29, 50, 50, 20, 80, -1, 0)) 
my_fish_2 = Fish(genes = ([(40, 30), (40, 31)], (60, 60, 220), 29, 50, 50, 20, 80, -2, 0))


while running:
    time.sleep(0.001)
    FRAMES += 1
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_pressed()[0] and not FRAMES % 6:
        if START_MENU and select_game_mode(mouse_pos):
            START_MENU = False
            if PLAYER_GAME and not TWO_PLAYER_GAME:
                my_fish.cells = [(60, 30), (60, 31)]
        elif SIMULATE_GAME:
            ALL_FOOD.append(Food(pos_to_coord(mouse_pos)))

    if PLAYER_GAME:
        my_move([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]], my_fish)
        if TWO_PLAYER_GAME:
            my_move([keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s]], my_fish_2)

    if not START_MENU:
        if len(ALL_FISH) < 60: # difficulty attribute here
            if not rand.randint(0, 10):
                if rand.randint(0, 2): # 1/41 * 4/5 = 4/205; FRAMES * (4 / 205) = predicted FAM
                    ALL_FISH.append(Fish(FAM))
                    FAM += 1
                else:
                    ALL_FOOD.append(Food((rand.randint(0, COORD_X_MAX), 0)))

    screen.fill(background) # drawing starts here
            
    if START_MENU:
        present_start_menu()

    else:
        for food in ALL_FOOD:
            if not rand.randint(0, 19):
                food.move()
            if not FRAMES % 3 and PLAYER_GAME:
                my_eat_food(my_fish, food)
                if TWO_PLAYER_GAME:
                    my_eat_food(my_fish_2, food)

            pygame.draw.rect(screen, (20, 157, 25), coord_to_rect(food.coords), border_radius = CELL_SIZE // 4)

        for fish in ALL_FISH:
    
            if fish.id:
                if ((not fish.hunt and rand.randint(0, 8)) or not rand.randint(-170, int(0.7 * (fish.decisivness // (fish.targ_count + 1))))):
                    fish.radar_and_lock()
                if rand.randint(-100, (fish.speed)) > 0: 
                    fish.move()

                if not (FRAMES + 2) % 3 and PLAYER_GAME: 
                    my_eat_fish(my_fish, fish)
                    if TWO_PLAYER_GAME:
                        my_eat_fish(my_fish_2, fish)

                for cell in fish.cells:
                    pygame.draw.rect(screen, fish.color, coord_to_rect(cell))

        if not (FRAMES + 3) % 3 and TWO_PLAYER_GAME:
            player_attack(my_fish, my_fish_2)

        if PLAYER_GAME:
            for cell in my_fish.cells:
                pygame.draw.rect(screen, my_fish.color, coord_to_rect(cell))
            if TWO_PLAYER_GAME:
                for cell in my_fish_2.cells:
                    pygame.draw.rect(screen, my_fish_2.color, coord_to_rect(cell))

    pygame.display.flip()

pygame.quit()