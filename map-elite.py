#!/usr/bin/env python3
"""
A simple MAP-Elites implementation for Micropolis (gym-city).
Generates diverse city layouts across pollution and traffic descriptors.
"""
import random
import numpy as np
import time
import asyncio
import threading
from gym_city.envs.env import MicropolisEnv

from gi.repository import Gtk

# === PARAMETERS ===
MAP_WIDTH = 16            # width and height of the square map
default_SIM_STEPS = 100   # simulation ticks per evaluation
POPULATION_SIZE = 50      # number of genomes per generation
GENERATIONS = 100         # total MAP-Elites generations to run
GRID_BINS = 5             # resolution of the 2D archive
MUTATIONS_PER_CHILD = 1   # how many tiles to randomly flip per child
sum_fitnesses = []
HEADLESS = True
LIVE = False

csvoutput = "Genome," + "," + ",".join([str(i) for i in range(GENERATIONS)]) + "\n"
csvtable = []
env = MicropolisEnv()
env.setMapSize(MAP_WIDTH)

# === GENOME UTILITIES ===
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
        if not HEADLESS and LIVE:
            env.render()


def evaluate(genome, sim_steps=default_SIM_STEPS, csvoutput=csvoutput):
    """
    Build the city from genome, run for sim_steps ticks,
    and return (fitness, descriptor1, descriptor2).
    fitness = final population
    descriptor1 = pollution level
    descriptor2 = traffic density
    """
    env.reset()
    genome_to_layout(genome)
    for i in range(sim_steps):
        env.postact()
    if not HEADLESS:
        env.render()
    env.micro.getDensityMaps()
    fitness = env.getPop()
    # desc1 = env.micro.total_traffic
    # desc2 = env.micro.land_value
    desc1 = env.micro.pollution
    desc2 = env.micro.crimerate
    return fitness, desc1, desc2


def cell_index(value, min_val, max_val, bins=GRID_BINS):
    """
    Map a descriptor value into an integer cell index [0, bins-1].
    """
    # Avoid division by zero
    span = max_val - min_val if max_val > min_val else 1
    ratio = (value - min_val) / span
    idx = int(ratio * bins)
    return max(0, min(bins - 1, idx))


def mutate(genome, num_mutations=MUTATIONS_PER_CHILD):
    """Return a copy of genome with num_mutations random tiles changed."""
    child = genome.copy()
    for _ in range(num_mutations):
        i = random.randrange(len(child))
        child[i] = random.randrange(0, 20)
    return child

def main( csvoutput=csvoutput, csvtable=csvtable ):
    with open("output.csv", "w") as file:
        file.write("")
    # 1. Initialize empty archive and fitness grid
    archive = [[None for _ in range(GRID_BINS)] for _ in range(GRID_BINS)]
    fitnesses = [[-1          for _ in range(GRID_BINS)] for _ in range(GRID_BINS)]

    # 2. Generate initial random population
    population = [init_genome() for _ in range(POPULATION_SIZE)]

    # 3. Warm-up: estimate descriptor bounds over the initial pop
    # d1_vals, d2_vals = [], []
    # for g in population:
    #     _, d1, d2 = evaluate(g)
    #     d1_vals.append(d1)
    #     d2_vals.append(d2)
    # min_d1, max_d1 = min(d1_vals), max(d1_vals)
    # min_d2, max_d2 = min(d2_vals), max(d2_vals)

    # traffic 500; land value 2000;
    min_d1, max_d1 = 0, 500
    min_d2, max_d2 = 0, 2000

    # 4. MAP-Elites main loop
    stopupdate = False
    def update():
        while not stopupdate:
            if not HEADLESS:
                env.render()
    if not HEADLESS:
        thread = threading.Thread(target=update)
        thread.start()
        print("30 seconds to prepare a screen capture...")
        time.sleep(10)
        print("20 seconds to prepare a screen capture...")
        time.sleep(10)
        print("10 seconds to prepare a screen capture...")
        time.sleep(1)
        print("9 seconds to prepare a screen capture...")
        time.sleep(1)
        print("8 seconds to prepare a screen capture...")
        time.sleep(1)
        print("7 seconds to prepare a screen capture...")
        time.sleep(1)
        print("6 seconds to prepare a screen capture...")
        time.sleep(1)
        print("5 seconds to prepare a screen capture...")
        time.sleep(1)
        print("4 seconds to prepare a screen capture...")
        time.sleep(1)
        print("3 seconds to prepare a screen capture...")
        time.sleep(1)
        print("2 seconds to prepare a screen capture...")
        time.sleep(1)
        print("1 seconds to prepare a screen capture...")
        time.sleep(1)
        stopupdate = True
        thread.join()
    firsttable = True
    for gen in range(GENERATIONS):
        nome = 0
        for genome in population:
            if firsttable:
                csvtable.append(str(nome) + ",")
            else:
                csvtable[nome] += ","
            fit, d1, d2 = evaluate(genome)
            x = cell_index(d1, min_d1, max_d1)
            y = cell_index(d2, min_d2, max_d2)
            csvtable[nome] += str(fit)
            if not HEADLESS:
                print(f"Generation:{gen}\tGenome:{nome}\tFitness:{fit}")
            nome += 1
            if fit >= fitnesses[x][y]:
                archive[x][y]   = genome
                fitnesses[x][y] = fit
        firsttable = False
        sum_fitnesses.append(sum([sum(row) for row in fitnesses]))
        filled = sum(1 for row in archive for g in row if g is not None)
        print(f"Generation {gen}: {filled}/{GRID_BINS * GRID_BINS} cells filled")
        # f"fitnesses: {fitnesses}"

        # 5. Create next generation by mutating existing elites
        elites = [g for row in archive for g in row if g is not None]
        if not elites:
            # If nothing filled yet, re-randomize
            population = [init_genome() for _ in range(POPULATION_SIZE)]
        else:
            population = [mutate(random.choice(elites)) for _ in range(POPULATION_SIZE)]
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(' '.join(map(str, sum_fitnesses)))

    max_value = float('-inf')
    max_pos = (-1, -1)

    for i, row in enumerate(fitnesses):
        for j, value in enumerate(row):
            if value > max_value:
                max_value = value
                max_pos = (i, j)

    best = archive[max_pos[0]][max_pos[1]]
    f, d1, d2 = evaluate(best)
    with open('lastfitnesses.txt', 'w', encoding='utf-8') as f:
        for row in fitnesses:
            f.write(" ".join(map(str, row)) + "\n")
    print(d1, d2)
    csvoutput += "\n".join(csvtable)
    with open("output.csv", "w") as file:
        file.write(csvoutput)
    exit()

if __name__ == "__main__":
    main()
    # test = init_genome()
    # print(evaluate(test))

    Gtk.main()