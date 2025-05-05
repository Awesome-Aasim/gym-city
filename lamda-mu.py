from pdb import set_trace as breakpoint

from gi.repository import Gtk
# Gtk.Window.show     = lambda *args, **kwargs: None
# Gtk.Window.show_all = lambda *args, **kwargs: None
# Gtk.Window.show_now = lambda *args, **kwargs: None

# Gtk.Window.map     = lambda *args, **kwargs: None
# Gtk.Window.map_event = lambda *args, **kwargs: None

from gym_city.envs.env import MicropolisEnv
import numpy as np
import copy

m = MicropolisEnv()
m.setMapSize(20)


def countfitness(action_map):
    m.reset()
    for i in range(action_map.shape[0]):
        for j in range(action_map.shape[1]):
            if action_map[i][j] != 17:
                m.micro.takeAction([action_map[i][j], i, j])
    
    # fitness for residential zone

    # zone_map = m.micro.map.zoneMap[-1]
    # f = np.count_nonzero(zone_map == 0)

    # fitness for population
    for _ in range(100):
        m.postact()
        
    return m.getPop()

def init_genome():
    """Return an initial genome: a list of MAP_WIDTH*MAP_WIDTH integers 17"""
    initge = [17] * (MAP_WIDTH * MAP_WIDTH)
    initge[2 * MAP_WIDTH + 2] = 0
    initge[1 * MAP_WIDTH + 10] = 13
    for i in range(5):
        initge[i] = 8
        initge[4 * MAP_WIDTH + i] = 8
        initge[i * MAP_WIDTH] = 8
        initge[i * MAP_WIDTH + 4] = 8
    for i in range(5):
        initge[2 * MAP_WIDTH + 4 + i] = 6
    return initge

def genome_to_layout(genome):
    """Apply a genome to the MicropolisControl env by placing tiles."""
    for idx, tile_type in enumerate(genome):
        if tile_type != 17:
            x = idx % MAP_WIDTH
            y = idx // MAP_WIDTH
            env.micro.takeAction([tile_type, x, y])

population = []
fitness = []
population_size = 20
max_iteration = 30
iteration = 0
rng = np.random.default_rng()
mutation_step_size = 5
offspring_size = 140

population = [init_genome() for _ in range(POPULATION_SIZE)]
fitness = [countfitness(genome) for genome in population]

f = open('output.txt', 'w')
for iteration in range(max_iteration):
    success = 0
    offspring = []
    offspring_fitness = []

    for i in range (offspring_size):
        r = rng.integers(0, population_size)
        a = copy.deepcopy(population[r])
        for mutation_step in range(mutation_step_size):
            x = rng.integers(0, 20)
            y = rng.integers(0, 20)
            z = rng.integers(0, 20) 
            a[x][y] = z
        # offspring.append(a)
        # offspring_fitness.append(countfitness(a))
        population.append(a)
        fitness.append(countfitness(a))
        # offspring_fitness.append(np.count_nonzero(offspring[i] == 0))
        # if offspring_fitness[i] > fitness[r]:
        #    success += 1
    
    indexed_lst = list(enumerate(fitness))
    indexed_lst.sort(key=lambda x: x[1], reverse=True)
    best_index_tuples = indexed_lst[:population_size]
    best_indices = [x[0] for x in best_index_tuples]
    population = list(np.array(population)[best_indices])
    fitness = list(np.array(fitness)[best_indices])
    # i = 0
    # for idx, val in best_indices:
    #     population[i] = offspring[idx]
    #     fitness[i] = offspring_fitness[idx]
    #     i += 1
    print(f'fitnesses: {fitness}')
    f.write(','.join(map(str, fitness)))
    f.write('\n')

    
    # if 5 * success > offspring_size:
    #     mutation_step_size *= 1.5
    # else:
    #     mutation_step_size *= 0.82

f.close()
solution = population[0]

m.reset()
for i in range(solution.shape[0]):
        for j in range(solution.shape[1]):
            if solution[i][j] != 17:
                m.micro.takeAction([solution[i][j], i, j])

print(solution)
m.printMap()

Gtk.main()