import pygame
import random as rand
import time

POS_X_MAX = 1200
POS_Y_MAX = 600
COORD_X_MAX = 200
COORD_Y_MAX = COORD_X_MAX // 2
CELL_SIZE = int(POS_X_MAX / COORD_X_MAX)
FAM = 0
FRAMES = 0
ALL_SPECIES = []
FULL_SPACE = []
SIMULATE_GAME = False
PLAYER_GAME = False
TWO_PLAYER_GAME = False
NUMBER_OF_PLAYER_FISH = 0
NUMBER_OF_DISCRETE = 4
ALL_FOOD = []
ALL_FISH = []

# wall ball

class Food():
    '''
    Docstring for Food
    Class for food objects
    '''

    def __init__(self, start):
        '''
        Docstring for __init__
        Sets individual characteristics
            flakiness
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
        Creates new fish from scratch or inherited genes
        
        :param id: New id and family indicator
        :param genes: Tuple of genes includes cells, color, aggression, division size, field of view, decisiveness, inherited id, discrete(shape)
        '''
        if genes: # inheritance
            self.cells, self.color, self.speed, self.agro, self.division, self.vision, self.decisiveness, self.id, self.discrete = genes
        else: # if new fish
            self.cells = [(rand.randint(0, COORD_X_MAX - 1), rand.randint(0, COORD_Y_MAX - 1))]
            if not rand.randint(0, 2):
                self.cells.append((self.cells[0][0] - 1, self.cells[0][1]))
            self.speed = rand.randint(10, 30)
            self.agro = rand.randint(0, 100)
            self.division = rand.randint(4, 100)
            self.speed += self.division // 8
            self.vision = rand.randint(10, 40)
            self.decisiveness = rand.randint(0, 99)
            self.id = id
            self.discrete = rand.choices(range(NUMBER_OF_DISCRETE), weights=[5, 1, 30, 2], k=1)[0]
            # Set color
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
        add_fish = []

        if PLAYER_GAME:
            add_fish.append(my_fish)
            if TWO_PLAYER_GAME:
                add_fish.append(my_fish_2)

        for food in ALL_FOOD:
            if pythagorean_distance(self.cells[0], food.coords) < self.vision:
                self.food_targets.append(food)
                self.targ_count += 1

        for fish in ALL_FISH + add_fish:
            if pythagorean_distance(self.cells[0], fish.cells[0]) < self.vision:
                if self.id != fish.id:
                    if len(fish.cells) <= len(self.cells) / 2:
                        if len(self.cells) > 1:
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


    def use_energy(self, energy_expend=1):
        '''
        Docstring for use_energy
        Removes energy and decays if out of energy

        :param energy_expend: pos int for how much energy to remove
        '''
        if rand.randint(0, len(self.cells)):
            self.energy -= energy_expend
        if self.energy < 0:
            self.decay()


    def mitosis(self):
        '''
        Docstring for mitosis
        Removes half of the cells and creates a mutated fish with them
        '''
        ALL_FISH.append(Fish(genes = (self.cells[self.division // 2:], self.color, self.speed, self.agro, self.division, self.vision, self.decisiveness, self.id, self.discrete)))
        ALL_FISH[-1].mutate()
        self.cells = self.cells[:self.division//2]


    def eat_target(self):
        '''
        Docstring for eat_target
        Removes cell from target and adds it to self
        '''
        #if ((self.target != my_fish) and (self.target != my_fish_2)) or self.target.cells[0] != (60, 30):
        if self.target.cells[0] != (60, 30):
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
        For idling or less precision
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
        A fish's move where they use energy, maintain shape, check for division, check for eating, fleeing and chasing
        '''
        self.use_energy()

        if len(self.cells) > self.division:
            self.mitosis()

        #eating target
        if (self.target in set(ALL_FISH)) or (self.target in (my_fish, my_fish_2)):
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
            if (not self.hunt and self.danger) or rand.randint(0,len(self.danger)): # incorporate inverse agro
                self.flee()
            if not rand.randint(0, 3): # incorporate precision
                self.random_direction()
            self.hunt = False
            return
        
        self.chase(coords)

        self.build_discrete()


    def build_discrete(self):
        '''
        Docstring for build_discrete
        Does specific discrete action based on set discrete
        '''
        if self.discrete == 0:
            self.discrete_classic()
        elif self.discrete == 1:
            self.discrete_snake()
        elif self.discrete == 2:
            self.discrete_wall_ball()
        elif self.discrete == 3:
            self.discrete_dense()


    def fluff_cells(self, width=1, density=1):
        '''
        Docstring for fluff_cells
        Moves cells to sides of fish
        
        :param width: The maximum width for a specific fish
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


    def discrete_classic(self):
        '''
        Docstring for discrete_classic
        Adds "fluff" cells using convoluted method
        '''
        size = len(self.cells)
        a, b = rand.choice([(0, 1),(0, -1),(1, 0),(-1, 0)])
        side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
        if side_coords not in set(self.cells) and in_bound(side_coords):
            del self.cells[-1]
            self.cells.insert(1, side_coords)
        if size > 15:
            a, b = rand.choice([(0, 1),(0, -1),(1, 0),(-1, 0)])
            side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
            if side_coords not in set(self.cells) and in_bound(side_coords):
                del self.cells[-1]
                self.cells.insert(1, side_coords)
            if size > 25:
                a, b = rand.choice([(0, 2),(0, -2),(2, 0),(-2, 0), (-1, 1), (1, 1), (1, -1), (-1, -1)])
                side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
                if side_coords not in set(self.cells) and in_bound(side_coords):
                    del self.cells[-1]
                    self.cells.insert(1, side_coords)
                if size > 35:
                    a, b = rand.choice([(0, 2),(0, -2),(2, 0),(-2, 0), (-1, 1), (1, 1), (1, -1), (-1, -1)])
                    side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
                    if side_coords not in set(self.cells) and in_bound(side_coords):
                        del self.cells[-1]
                        self.cells.insert(1, side_coords)


    def discrete_snake(self):
        '''
        Docstring for discrete_snake
        Turns one in four snakes thick
        '''
        if not self.id % 4:
            self.fluff_cells()


    def discrete_wall_ball(self):
        '''
        Docstring for discrete_wall_ball
        Forces a fish to one direction and gives them more energy
        '''
        growth_pattern = [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0)]
        # add another one for each level
        vert_ud = [(0, -1), (0, 1)] 
        horizontal_lr = [(-1, 0), (1, 0)]
        rand.shuffle(vert_ud)
        rand.shuffle(horizontal_lr)
        
        if not self.id % 4:
            growth_pattern = [(0, 0)] + horizontal_lr + vert_ud
            new_coords = (self.cells[0][0] + 1, self.cells[0][1])
        elif self.id % 4 == 1:
            growth_pattern = [(0, 0)] + horizontal_lr + vert_ud
            new_coords = (self.cells[0][0] - 1, self.cells[0][1])
        elif self.id % 4 == 2:
            growth_pattern = [(0, 0)] + vert_ud + horizontal_lr
            new_coords = (self.cells[0][0], self.cells[0][1] + 1)
        else:
            growth_pattern = [(0, 0)] + vert_ud + horizontal_lr
            new_coords = (self.cells[0][0], self.cells[0][1] - 1)

        for a4, b4 in growth_pattern:
            for a3, b3 in growth_pattern:
                for a2, b2 in growth_pattern:
                    for a1, b1 in growth_pattern:
                        if (new_coords[0] + a1 + a2 + a3 + a4, new_coords[1] + b1 + b2 + b3 + b4) not in self.cells and in_bound((new_coords[0] + a1 + a2 + a3 + a4, new_coords[1] + b1 + b2 + b3 + b4)):
                            new_coords = (new_coords[0] + a1 + a2 + a3 + a4, new_coords[1] + b1 + b2 + b3 + b4)

                            del self.cells[-1]
                            self.cells.insert(0, new_coords)

                            return
        if rand.randint(0, 3):
            self.energy += 1
            if not rand.randint(0, 70):
                self.cells.append(self.cells[0])


    def discrete_dense(self):
        '''
        Docstring for discrete_dense
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
            del self.cells[-1]
            self.energy = 200


    def mutate(self):
        '''
        Docstring for mutate
        Slightly changes speed, aggression, reproduction size, and FOV in offspring
        Small chance of family or discrete mutation
        '''
        new_color = (self.color[0] + rand.randint(-15, 15), self.color[1] + rand.randint(-15, 15), self.color[2] + rand.randint(-15, 15))
        if 0 <= list(new_color)[0] <= 255 and 0 <= list(new_color)[1] <= 255 and 0 <= list(new_color)[2] <= 255:
            self.color = new_color
        for gene in [self.speed, self.agro, self.division, self.vision]:
            gene += rand.randint(-2, 2)
        if not rand.randint(0, 50):
            self.discrete = rand.randint(0, NUMBER_OF_DISCRETE)
        if not rand.randint(0, 15):
            global FAM
            self.id = FAM
            FAM += 1


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
    :returns boolean: Whether or not the cell is in the screen frame
    '''
    if coord[0] >= 0 and coord[0] < COORD_X_MAX and coord[1] >= 0 and coord[1] < COORD_Y_MAX:
        return True
    return False


def pythagorean_distance(point_1, point_2):
    '''
    Docstring for pythagorean_distance

    :param point_1: Tuple coordinates (x, y)
    :param point_2: The other point
    :returns int: Distance between the two points
    '''
    return int((abs(point_1[0] - point_2[0]) + abs(point_1[1] - point_2[1])) ** 0.5)


def my_move(direction_keys, fish):
    '''
    Docstring for my_move
    Moves fish and uses energy based on user input

    :param direction_keys: Four booleans representing left, right, up, down
    :param fish: my_fish or my_fish_2
    '''
    if True in direction_keys and rand.randint(-1, (fish.speed)) > 0 and not FRAMES % 3:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        direction_options = []

        for i, arrow in enumerate(direction_keys):
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
        fish.build_discrete()
        fish.use_energy()

  
def my_eat_fish(selfish, prey):
    '''
    Docstring for my_eat_fish
    If player fish is eating fish, removes cell from prey and adds to player fish
    
    :param selfish: my_fish or my_fish_2
    :param prey: Autonomous fish
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
    If player fish is eating other player fish, then transfer cells or game over
    
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


start_menu = True
running = True
pygame.init()
screen = pygame.display.set_mode((POS_X_MAX, POS_Y_MAX))
background = (7, 10, 20)
menu_font = pygame.font.Font('freesansbold.ttf', 30)

my_fish = Fish(genes = ([(80, 30), (80, 31)], (220, 60, 60), 29, 50, 50, 20, 80, -1, 0))
my_fish_2 = Fish(genes = ([(40, 30), (40, 31)], (60, 60, 220), 29, 50, 50, 20, 80, -2, 0))

# Game loop
while running:
    time.sleep(0.004)
    FRAMES += 1
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_pressed()[0] and not FRAMES % 6:
        if start_menu and select_game_mode(mouse_pos):
            start_menu = False
            if PLAYER_GAME and not TWO_PLAYER_GAME:
                my_fish.cells = [(60, 30), (60, 31)]
        elif SIMULATE_GAME:
            ALL_FOOD.append(Food(pos_to_coord(mouse_pos)))

    if PLAYER_GAME:
        my_move([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]], my_fish)
        if TWO_PLAYER_GAME:
            my_move([keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s]], my_fish_2)

    if not start_menu:
        if len(ALL_FISH) < 60: # difficulty attribute here
            if not rand.randint(0, 10):
                if rand.randint(0, 2): # 1/41 * 4/5 = 4/205; FRAMES * (4 / 205) = predicted FAM
                    ALL_FISH.append(Fish(FAM))
                    FAM += 1
                else:
                    ALL_FOOD.append(Food((rand.randint(0, COORD_X_MAX), 0)))

    screen.fill(background) # drawing starts here
            
    if start_menu:
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
                if (fish.hunt and not rand.randint(0, abs(80 + (100 * int(fish.decisiveness - fish.targ_count + 1))))) or not fish.hunt: # very rare edgecase where dumb fish locks in
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