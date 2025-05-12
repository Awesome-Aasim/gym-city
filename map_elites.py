#!/usr/bin/env python3
"""
A simple MAP-Elites implementation for Micropolis (gym-city).
Generates diverse city layouts across pollution and traffic descriptors.
"""
import random
import numpy as np
from gym_micropolis.envs.corecontrol import MicropolisControl

# === PARAMETERS ===
MAP_WIDTH = 16            # width and height of the square map
default_SIM_STEPS = 100   # simulation ticks per evaluation
POPULATION_SIZE = 50      # number of genomes per generation
GENERATIONS = 100         # total MAP-Elites generations to run
GRID_BINS = 10            # resolution of the 2D archive
MUTATIONS_PER_CHILD = 5   # how many tiles to randomly flip per child

# === GENOME UTILITIES ===
def random_genome():
    """Return a random genome: a list of MAP_WIDTH*MAP_WIDTH integers in {0,1,2,3}"""
    return [random.randint(0, 3) for _ in range(MAP_WIDTH * MAP_WIDTH)]


def genome_to_layout(genome, env):
    """Apply a genome to the MicropolisControl env by placing tiles."""
    for idx, tile_type in enumerate(genome):
        x = idx % MAP_WIDTH
        y = idx // MAP_WIDTH
        if tile_type == 0:
            env.placeRoad(x, y)
        elif tile_type == 1:
            env.placeResidential(x, y)
        elif tile_type == 2:
            env.placeCommercial(x, y)
        # tile_type == 3 => leave empty


def evaluate(genome, sim_steps=default_SIM_STEPS):
    """
    Build the city from genome, run for sim_steps ticks,
    and return (fitness, descriptor1, descriptor2).
    fitness = final population
    descriptor1 = pollution level
    descriptor2 = traffic density
    """
    env = MicropolisControl(MAP_W=MAP_WIDTH, MAP_H=MAP_WIDTH)
    genome_to_layout(genome, env)
    for _ in range(sim_steps):
        env.step()
    fitness = env.getPopulation()
    desc1 = env.getPollutionLevel()
    desc2 = env.getTrafficDensity()
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
        child[i] = random.randint(0, 3)
    return child


def main():
    # 1. Initialize empty archive and fitness grid
    archive = [[None for _ in range(GRID_BINS)] for _ in range(GRID_BINS)]
    fitnesses = [[-1          for _ in range(GRID_BINS)] for _ in range(GRID_BINS)]

    # 2. Generate initial random population
    population = [random_genome() for _ in range(POPULATION_SIZE)]

    # 3. Warm-up: estimate descriptor bounds over the initial pop
    d1_vals, d2_vals = [], []
    for g in population:
        _, d1, d2 = evaluate(g)
        d1_vals.append(d1)
        d2_vals.append(d2)
    min_d1, max_d1 = min(d1_vals), max(d1_vals)
    min_d2, max_d2 = min(d2_vals), max(d2_vals)

    # 4. MAP-Elites main loop
    for gen in range(GENERATIONS):
        for genome in population:
            fit, d1, d2 = evaluate(genome)
            x = cell_index(d1, min_d1, max_d1)
            y = cell_index(d2, min_d2, max_d2)
            if fit > fitnesses[x][y]:
                archive[x][y]   = genome
                fitnesses[x][y] = fit

        filled = sum(1 for row in archive for g in row if g is not None)
        print(f"Generation {gen}: {filled}/{GRID_BINS * GRID_BINS} cells filled")

        # 5. Create next generation by mutating existing elites
        elites = [g for row in archive for g in row if g is not None]
        if not elites:
            # If nothing filled yet, re-randomize
            population = [random_genome() for _ in range(POPULATION_SIZE)]
        else:
            population = [mutate(random.choice(elites)) for _ in range(POPULATION_SIZE)]


if __name__ == "__main__":
    main()
