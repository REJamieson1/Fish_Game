import pygame
import random as rand
import time

'''
NEXT:
Play as fish
- fish shape
- death
- 2nd fish
fix shape/gaps in fish
Accuracy
Colorless background problem
Overall more leathal
movement affects scarriness
diff movement types
camping?
give them neurons
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
                self.target.cells.remove(coords)
                if not len(self.target.cells):
                    ALL_FISH.remove(self.target)
                self.cells.append(self.cells[0])
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

        self.thickify()


    def thickify(self): # shape atribute here
        # a, b = rand.choice([(0, 1),(0, -1),(1, 0),(-1, 0)])
        # side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
        # if side_coords not in set(self.cells) and in_bound(side_coords):
        #     del self.cells[-1]
        #     self.cells.insert(1, side_coords)

        if len(self.cells) > 5:
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
    
    def decay(self):
        if len(self.cells) == 1:
            ALL_FOOD.append(Food(self.cells[0]))
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


def my_fish_catch(fish):
    # What is the fastest way to find a fish the fish and cell of fish at a given coordinate?
    pass
    

def background_check():
    #if FRAMES > 50:

    ALL_SPECIES.sort()
    len(ALL_SPECIES) - len(past_fish)
    pass

    

my_fish = Fish(genes = ([(60, 30), (61, 30)], (75, 107, 80), 29, 50, 50, 20, 80, -1))

# hendersons = Fish(genes = ([(10, 10), (10, 11)], (255, 0, 0), 7, 100, 4, 200, -1))
# hendersons.energy = 1600
# benson = Fish(genes = ([(70, 10), (70, 11), (71, 10), (72, 10), (73, 10)], (80, 200, 200), 26, 90, 400, 200, -2))
# benson.energy = 16000000
# the_pacifisht = Fish(genes = ([(30, 10), (30, 11)], (150, 150, 150), 7, 0, 50, 200, -2))
# the_pacifisht.energy = 16000
ALL_FISH.append(my_fish)
# ALL_FISH.append(hendersons)
# ALL_FISH.append(benson)
# ALL_FISH.append(the_pacifisht)

while running:
    time.sleep(0.01)
    FRAMES += 1
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    direction_options = []


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

            

    if pygame.mouse.get_pressed()[0] and not FRAMES % 6:
        ALL_FOOD.append(Food(pos_to_coord(mouse_pos)))

    if keys[pygame.K_LEFT]:
        direction_options.append((my_fish.cells[0][0] - 1, my_fish.cells[0][1]))
    if keys[pygame.K_RIGHT]:
        direction_options.append((my_fish.cells[0][0] + 1, my_fish.cells[0][1]))
    if keys[pygame.K_UP]:
        direction_options.append((my_fish.cells[0][0], my_fish.cells[0][1] - 1))
    if keys[pygame.K_DOWN]:
        direction_options.append((my_fish.cells[0][0], my_fish.cells[0][1] + 1))
    if direction_options and rand.randint(-1, (my_fish.speed)) > 0 and not FRAMES % 3:
        
        if len(direction_options) > 1:
            new_coord = rand.choice(direction_options)
        else:
            new_coord = rand.choices([direction_options[0] , [rand.choice([(my_fish.cells[0][0] - 1, my_fish.cells[0][1]), (my_fish.cells[0][0] + 1, my_fish.cells[0][1]), (my_fish.cells[0][0], my_fish.cells[0][1] - 1), (my_fish.cells[0][0], my_fish.cells[0][1] + 1)])][0]], weights=[10, 1], k=1)[0]
        if in_bound(new_coord):
            del my_fish.cells[-1]
            my_fish.cells.insert(0, new_coord)

        if not rand.randint(0, 25):
            my_fish.thickify()

        my_fish.energy -= 1
        if my_fish.energy < 0:
            my_fish.decay()

    if not (FRAMES + 2) % 8:
        my_fish.energy -= 1
        if my_fish.energy < 0:
            my_fish.decay()

    if len(ALL_FISH) < 60:
        if not rand.randint(0, 30):
            if rand.randint(0, 3): # 1/41 * 4/5 = 4/205; FRAMES * (4 / 205) = predicted FAM
                ALL_FISH.append(Fish(FAM))
                FAM += 1
            else:
                ALL_FOOD.append(Food((rand.randint(0, COORD_X_MAX), 0)))

    #drawing starts here
    
    screen.fill(background)
            
    for food in ALL_FOOD:
        if not rand.randint(0, 19):
            food.move()
        if not FRAMES % 4:
            if food.coords == my_fish.cells[0]:
                ALL_FOOD.remove(food)
                if food in FULL_SPACE:
                    FULL_SPACE.remove(food.coords)
                
                my_fish.cells.append(food.coords)

        pygame.draw.rect(screen, (20, 157, 25), coord_to_rect(food.coords), border_radius = CELL_SIZE // 4)

    for fish in ALL_FISH:
        if fish.id > 1:
            if ((not fish.hunt and rand.randint(0, 8)) or not rand.randint(-170, int(0.7 * (fish.decisivness // (fish.targ_count + 1))))):
                fish.radar_and_lock()
            if rand.randint(-100, (fish.speed)) > 0: 
                fish.move()
            if not (FRAMES + 2) % 4: 
                if len(fish.cells) <= len(my_fish.cells) / 2:
                    if my_fish.cells[0] in fish.cells:
                        fish.cells.remove(my_fish.cells[0])
                        if not len(fish.cells):
                            ALL_FISH.remove(fish)
                        my_fish.cells.append(my_fish.cells[0])

            for cell in fish.cells:
                pygame.draw.rect(screen, fish.color, coord_to_rect(cell))

        else:
            if not rand.randint(0, 3):
                my_fish.thickify()

    for cell in my_fish.cells:
        pygame.draw.rect(screen, my_fish.color, coord_to_rect(cell))

    pygame.display.flip()

pygame.quit()