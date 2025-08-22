import pygame
import random as rand

'''
NEXT:
decisiveness 
color rep 
- r
- g
- b
- sum
movement affects scarriness
'''

POS_X_MAX = 1200
POS_Y_MAX = 600
COORD_X_MAX = 120
COORD_Y_MAX = COORD_X_MAX // 2
CELL_SIZE = int(POS_X_MAX / COORD_X_MAX)
FAM = 0
all_coords = []

for x in range(COORD_X_MAX):
    for y in range(COORD_Y_MAX):
        all_coords.append((x, y))

running = True
pygame.init()
screen = pygame.display.set_mode((POS_X_MAX, POS_Y_MAX))
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

    def move(self):
        self.coords = (self.coords[0] + rand.choice([-1] + [0] * 9 +[1]), self.coords[1] + 1)
        if self.coords[1] > COORD_Y_MAX or self.coords[0] > COORD_X_MAX:
            ALL_FOOD.remove(self)


class Fish():
    def __init__(self, id=None, genes=()):
        if genes:
            self.cells, self.color, self.speed, self.agro, self.division, self.vision, self.id = genes
        else:
            self.cells = [(rand.randint(0, COORD_X_MAX - 1), rand.randint(0, COORD_Y_MAX - 1))]
            if not rand.randint(0, 2):
                self.cells.append((self.cells[0][0] - 1, self.cells[0][1]))
            self.color = (rand.randint(0, 255), rand.randint(0, 255), rand.randint(0, 255))
            self.speed = rand.randint(20, 80) #find bits
            self.agro = rand.randint(0, 100)
            self.division = rand.randint(4, 90)
            self.vision = rand.randint(10, 30)
            self.id = id
        self.energy = 200
        self.food_targets = []
        self.fish_targets = []
        self.hunt = False
        self.targ_count = 0

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
            ALL_FISH.append(Fish(genes = (self.cells[self.division // 2:], self.color, self.speed, self.agro, self.division, self.vision, self.id)))
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
                self.cells.append(self.cells[0])
                return
            
        else:
            if (not self.hunt and self.danger) or rand.randint(0,len(self.danger)): #put agro in here
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
            
        a, b = rand.choice([(0, 1),(0, -1),(1, 0),(-1, 0)])
        side_coords = (self.cells[0][0] + a, self.cells[0][1] + b)
        if side_coords not in set(self.cells) and in_bound(side_coords):
            del self.cells[-1]
            self.cells.insert(1, side_coords)

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
            self.id += 1


# hendersons = Fish(genes = ([(10, 10), (10, 11)], (255, 0, 0), 7, 100, 4, 200, -1))
# hendersons.energy = 1600
# benson = Fish(genes = ([(70, 10), (70, 11), (71, 10), (72, 10), (73, 10)], (80, 200, 200), 26, 90, 400, 200, -2))
# benson.energy = 16000000
# the_pacifisht = Fish(genes = ([(30, 10), (30, 11)], (150, 150, 150), 7, 0, 50, 200, -2))
# the_pacifisht.energy = 16000
# ALL_FISH.append(hendersons)
# ALL_FISH.append(benson)
# ALL_FISH.append(the_pacifisht)


while running:
    screen.fill(background)
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            ALL_FOOD.append(Food(pos_to_coord(mouse_pos)))

    if len(ALL_FISH) < 60:
        if not rand.randint(0, 200):
            if rand.randint(0, 5):
                ALL_FISH.append(Fish(FAM))
                FAM += 1
            else:
                ALL_FOOD.append(Food((rand.randint(0, COORD_X_MAX), 0)))

    for each_food in ALL_FOOD:
        if not rand.randint(0, 100):
            each_food.move()
        pygame.draw.rect(screen, (205, 157, 20), coord_to_rect(each_food.coords), border_radius = CELL_SIZE // 4)

    for fish in ALL_FISH:
        if (not fish.hunt and rand.randint(0, 100)) or not rand.randint(-1000, fish.targ_count * 2): #replace 2 with desisiveness
            fish.radar_and_lock()
        if not rand.randint(0, (fish.speed)):
            fish.move()
        for cell in fish.cells:
            pygame.draw.rect(screen, fish.color, coord_to_rect(cell))


    pygame.display.flip()

pygame.quit()