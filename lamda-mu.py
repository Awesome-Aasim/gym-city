
from gi.repository import Gtk


Gtk.Window.show     = lambda *args, **kwargs: None
Gtk.Window.show_all = lambda *args, **kwargs: None
Gtk.Window.show_now = lambda *args, **kwargs: None

Gtk.Window.map     = lambda *args, **kwargs: None
Gtk.Window.map_event = lambda *args, **kwargs: None

from gym_city.envs.env import MicropolisEnv
import numpy as np
import copy

def countfitness(action_map):
    m = MicropolisEnv()
    m.setMapSize(20)
    m.reset()
    for i in range(action_map.shape[0]):
        for j in range(action_map.shape[1]):
            if action_map[i][j] < 17:
                m.micro.takeAction([action_map[i][j], i, j])
    zone_map = m.micro.map.zoneMap[-1]
    f = np.count_nonzero(zone_map == 0)
    print(action_map)
    m.printMap()
    m.close()
    # Gtk.main_quit()
    return f

population = []
fitness = []
population_size = 20
max_iteration = 30
iteration = 0
rng = np.random.default_rng()
mutation_step_size = 5
offspring_size = 140

for i in range(population_size):
    population.append(np.full((20, 20), 17))
    
    fitness.append(countfitness(population[i]))
    # fitness.append(np.count_nonzero(population[i] == 0))

for iteration in range(max_iteration):
    success = 0
    offspring = []
    offspring_fitness = []

    for i in range (offspring_size):
        r = rng.integers(0, population_size)
        a = copy.deepcopy(population[r])
        for mutation_step in range(int(mutation_step_size)):
            x = rng.integers(0, 20)
            y = rng.integers(0, 20)
            z = rng.integers(0, 18) 
            a[x][y] = z
        offspring.append(a)
        offspring_fitness.append(countfitness(a))
        # offspring_fitness.append(np.count_nonzero(offspring[i] == 0))
        if offspring_fitness[i] > fitness[r]:
            success += 1
    
    indexed_lst = list(enumerate(offspring_fitness))
    indexed_lst.sort(key=lambda x: x[1], reverse=True)
    best_indices = indexed_lst[:population_size]
    i = 0
    for idx, val in best_indices:
        population[i] = offspring[idx]
        fitness[i] = offspring_fitness[idx]
        i += 1
    with open('output.txt', 'a', encoding='utf-8') as f:
        f.write(','.join(map(str, fitness)))
        f.write('\n')

    
    if 5 * success > offspring_size:
        mutation_step_size *= 1.5
    else:
        mutation_step_size *= 0.82

best = max(fitness)
print(fitness)
solution = fitness.index(best)
# population[solution].printMap()
# population[solution].render()

# Gtk.main()
countfitness(population[solution])
