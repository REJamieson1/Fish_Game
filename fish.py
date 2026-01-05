import pygame
import random as rand
import time

'''
NEXT:
player.thickify
single player start position
game mode option text
4th menu option
secret fish
design a fish
Play as fish
- fish shape
fix shape/gaps in fish
Accuracy allil
Colorless background problem
Overall more leathal
movement affects scarriness
diff movement types
camping?
give them brains
clean whole code 😩
'''

POS_X_MAX = 1200
POS_Y_MAX = 600
COORD_X_MAX = 120
COORD_Y_MAX = COORD_X_MAX // 2
CELL_SIZE = int(POS_X_MAX / COORD_X_MAX)
FAM = 0
all_coords = []
FRAMES = 0
ALL_SPECIES = []
FULL_SPACE = []
START_MENU = True
SIMULATE_GAME = False
PLAYER_GAME = False
TWO_PLAYER_GAME = False
NUMBER_OF_PLAYER_FISH = 0

for x in range(COORD_X_MAX):
    for y in range(COORD_Y_MAX):
        all_coords.append((x, y))

running = True
pygame.init()
screen = pygame.display.set_mode((POS_X_MAX, POS_Y_MAX))
total_fish_newness = 0
background = (7, 10, 20)
ALL_FOOD = []
ALL_FISH = []

def pos_to_coord(pos):
    return (int(pos[0] // CELL_SIZE), int(pos[1] // CELL_SIZE))

def coord_to_rect(coord):
    return pygame.Rect(coord[0] * CELL_SIZE, coord[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)

def in_bound(coord):
    if coord[0] >= 0 and coord[0] < COORD_X_MAX and coord[1] >= 0 and coord[1] < COORD_Y_MAX:
        return True
    return False


class Food():
    def __init__(self, start):
        self.coords = start
        self.flakey = rand.randint(3, 15) 
        self.weight = rand.randint(1, 30) 

    def move(self):
        #why are ther false full spaces?
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
    def __init__(self, id=None, genes=()):
        if genes:
            self.cells, self.color, self.speed, self.agro, self.division, self.vision, self.decisivness, self.id = genes
        else:
            self.cells = [(rand.randint(0, COORD_X_MAX - 1), rand.randint(0, COORD_Y_MAX - 1))]
            if not rand.randint(0, 2):
                self.cells.append((self.cells[0][0] - 1, self.cells[0][1]))
            self.speed = rand.randint(10, 30)
            self.agro = rand.randint(0, 100) 
            self.division = rand.randint(4, 100)
            self.speed += self.division // 10
            self.vision = rand.randint(10, 40)
            self.decisivness = rand.randint(0, 99)
            self.id = id
            #vision score = (self.vision - 10) / 31
            #agro score = self.agro / 101
            #speed_score = (self.speed - 10) / 21
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

    def move(self):
        self.energy -= 1
        if self.energy < 0:
            self.decay()

        if len(self.cells) > self.division:
            ALL_FISH.append(Fish(genes = (self.cells[self.division // 2:], self.color, self.speed, self.agro, self.division, self.vision, self.decisivness, self.id)))
            ALL_FISH[-1].mutate()
            self.cells = self.cells[:self.division//2]

        if self.target in set(ALL_FISH):
            coords = self.target.cells[0]
            if self.cells[0] == coords:
                if ((self.target != my_fish) and (self.target != my_fish_2)) or self.target.cells[0] != (60, 30):
                    self.cells.append(self.cells[0])
                    self.target.cells.remove(coords)
                if not len(self.target.cells):
                    if self.target == my_fish:
                        game_over(my_fish)
                    elif self.target == my_fish_2:
                        game_over(my_fish_2)
                    else:
                        ALL_FISH.remove(self.target)
                return
            
        elif self.target in set(ALL_FOOD):
            coords = self.target.coords
            if self.cells[0] == coords:
                ALL_FOOD.remove(self.target)
                if self.target.coords in FULL_SPACE:
                    FULL_SPACE.remove(self.target.coords)
                self.cells.append(self.cells[0])
                return
            
        else:
            if (not self.hunt and self.danger) or rand.randint(0,len(self.danger)): #put -agro here
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
            
            if not rand.randint(0, 3):
                r_direction = rand.randint(1, 6)
                if 1 <= r_direction <=2:
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
            self.hunt = False
            return

        if rand.choice([1] * (abs(self.cells[0][0] - coords[0]) + 1) + [0] * (abs(self.cells[0][1] - coords[1]) + 1)):
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

        self.thickify() # rand based on size


    def thickify(self): # shape atribute here
        # a, b = rand.choice([(0, 1),(0, -1),(1, 0),(-1, 0)])
        # side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
        # if side_coords not in set(self.cells) and in_bound(side_coords):
        #     del self.cells[-1]
        #     self.cells.insert(1, side_coords)

        # if self == my_fish:
        #         print('my')
        # elif self.id == 1:
        #     print('oo')
        # if len(self.cells) >= 5:
            
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
    
    def thickify_2(self):
        for _ in range(len(self.cells) // 2):
            a, b = rand.choice([(0, 1),(0, -1),(1, 0),(-1, 0)])
            side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
            if side_coords not in set(self.cells) and in_bound(side_coords):
                del self.cells[-1]
                self.cells.insert(1, side_coords)
    
    def decay(self):
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
            self.energy = 100
                
    def mutate(self):
        '''
        self.cells, self.color, self.speed, self.agro, self.division, self.vision, self.id
        '''
        new_color = (self.color[0] + rand.randint(-15, 15), self.color[1] + rand.randint(-15, 15), self.color[2] + rand.randint(-15, 15))
        if 0 <= list(new_color)[0] <= 255 and 0 <= list(new_color)[1] <= 255 and 0 <= list(new_color)[2] <= 255:
            self.color = new_color
        for gene in [self.speed, self.agro, self.division, self.vision]:
            gene += rand.randint(-2, 2)
        if not rand.randint(0, 15):
            global FAM
            self.id = FAM
            FAM += 1
    

def background_check():
    #if FRAMES > 50:

    ALL_SPECIES.sort()
    len(ALL_SPECIES) - len(past_fish)
    pass


def my_move(directions, fish):
    '''
    Docstring for my_move
    
    :param directions: left, right, up, down
    :param fish: fish
    '''
    direction_options = []

    if directions[0]:
        direction_options.append((fish.cells[0][0] - 1, fish.cells[0][1]))
    if directions[1]:
        direction_options.append((fish.cells[0][0] + 1, fish.cells[0][1]))
    if directions[2]:
        direction_options.append((fish.cells[0][0], fish.cells[0][1] - 1))
    if directions[3]:
        direction_options.append((fish.cells[0][0], fish.cells[0][1] + 1))
    if direction_options and rand.randint(-1, (fish.speed)) > 0 and not FRAMES % 3:
        
        if len(direction_options) > 1:
            new_coord = rand.choice(direction_options)
        else:
            new_coord = rand.choices([direction_options[0] , [rand.choice([(fish.cells[0][0] - 1, fish.cells[0][1]), (fish.cells[0][0] + 1, fish.cells[0][1]), (fish.cells[0][0], fish.cells[0][1] - 1), (fish.cells[0][0], fish.cells[0][1] + 1)])][0]], weights=[10, 1], k=1)[0]
        if in_bound(new_coord):
            del fish.cells[-1]
            fish.cells.insert(0, new_coord)

        if not rand.randint(0, 3):
            fish.thickify_2()

        fish.energy -= 1
        if fish.energy < 0:
            fish.decay()

    if not (FRAMES + 2) % 15:
        fish.energy -= 1
        if fish.energy < 0:
            fish.decay()

    
def my_eat_fish(selfish, prey):
    '''
    Docstring for my_eat_fish
    
    :param selfish: my_fish or my_fish_2
    :param prey: any non-payer fish
    '''
    if len(prey.cells) <= len(selfish.cells) / 2:
        if selfish.cells[0] in prey.cells:
            prey.cells.remove(selfish.cells[0])
            if not len(prey.cells):
                ALL_FISH.remove(prey) #edgecase 
            selfish.cells.append(selfish.cells[0])


def my_eat_food(selfish, food):
    if food.coords == selfish.cells[0]:
        ALL_FOOD.remove(food)
        if food in FULL_SPACE:
            FULL_SPACE.remove(food.coords)
        selfish.cells.append(food.coords)


def player_attack(player_1, player_2):
    '''
    Docstring for player_attack
    
    :param player_1: my_fish
    :param player_2: my_fish_2
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
    #pygame.draw.rect(screen, player.color, pygame.Rect(0, 0, 1200, 600))
    #time.sleep(0.5)
    #pygame.quit()
    player.cells = [(60, 30), (60, 31)]
    player.energy = 200


def present_start_menu():
    pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(450, 200, 300, 40))
    pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(450, 260, 300, 40))
    pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(450, 320, 300, 40))
    pygame.draw.rect(screen, (220, 220, 220), pygame.Rect(450, 380, 300, 40))


def select_game_mode(coords):
    '''
    Docstring for select_game_mode
    
    :param coords: 
    coordinates of mouse if clicked during start screen
    '''
    # do this iteratively?
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


my_fish = Fish(genes = ([(80, 30), (80, 31)], (220, 60, 60), 29, 50, 50, 20, 80, -1)) # (75, 107, 80)
my_fish_2 = Fish(genes = ([(40, 30), (40, 31)], (60, 60, 220), 29, 50, 50, 20, 80, -2))
# hendersons = Fish(genes = ([(10, 10), (10, 11)], (255, 0, 0), 7, 100, 4, 200, -1))
# hendersons.energy = 1600
# benson = Fish(genes = ([(70, 10), (70, 11), (71, 10), (72, 10), (73, 10)], (80, 200, 200), 26, 90, 400, 200, -2))
# benson.energy = 16000000
# the_pacifisht = Fish(genes = ([(30, 10), (30, 11)], (150, 150, 150), 7, 0, 50, 200, -2))
# the_pacifisht.energy = 16000

# ALL_FISH.append(hendersons)
# ALL_FISH.append(benson)
# ALL_FISH.append(the_pacifisht)

if PLAYER_GAME:
    ALL_FISH.append(my_fish)
    NUMBER_OF_PLAYER_FISH += 1
    if TWO_PLAYER_GAME:
        ALL_FISH.append(my_fish_2)
        NUMBER_OF_PLAYER_FISH += 1

while running:
    time.sleep(0.01)
    FRAMES += 1
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_pressed()[0] and not FRAMES % 6:
        if select_game_mode(mouse_pos):
            START_MENU = False
        elif SIMULATE_GAME:
            ALL_FOOD.append(Food(pos_to_coord(mouse_pos)))

    if PLAYER_GAME:
        my_move([keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]], my_fish)
        if TWO_PLAYER_GAME:
            my_move([keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_w], keys[pygame.K_s]], my_fish_2)

    if not START_MENU:
        if len(ALL_FISH) < 60: #difficulty attribute here
            if not rand.randint(0, 30):
                if rand.randint(0, 3): # 1/41 * 4/5 = 4/205; FRAMES * (4 / 205) = predicted FAM
                    ALL_FISH.append(Fish(FAM))
                    FAM += 1
                else:
                    ALL_FOOD.append(Food((rand.randint(0, COORD_X_MAX), 0)))

    #drawing starts here
    
    screen.fill(background)
            
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

            elif rand.randint(0, 3): # why did it work before the menu?
                if PLAYER_GAME:
                    my_fish.thickify()
                    if TWO_PLAYER_GAME:
                        my_fish_2.thickify()


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