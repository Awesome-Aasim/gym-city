# metrics_utils.py
import matplotlib.pyplot as plt

def average_population(env, steps=500):
    total = 0
    for _ in range(steps):
        env.randomStep()
        total += env.getPopulation()
    return total / steps

def average_traffic(env, steps=500):
    total = 0
    for _ in range(steps):
        env.randomStep()
        total += env.getTraffic()
    return total / steps

def plot_metrics_over_time(env, steps=500):
    population_list = []
    traffic_list = []

    for _ in range(steps):
        env.randomStep()
        population_list.append(env.getPopulation())
        traffic_list.append(env.getTraffic())

    plt.figure(figsize=(10, 5))
    plt.plot(population_list, label='Population', color='skyblue')
    plt.plot(traffic_list, label='Traffic', color='orange')
    plt.xlabel("Simulation Step")
    plt.ylabel("Value")
    plt.title("City Metrics Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


POP_RANGE = [0, 1000]
TRAFFIC_RANGE = [0, 500]
GRID_BINS = 20
def evaluate(genome):
    env = MicropolisEnv(render_mode="none")
    env.reset()
    for action in genome:
        env.step(action)
    pop = average_population(env, steps=50)
    traffic = average_traffic(env, steps=50)
    fitness = pop - 2.0 * traffic
    return fitness, pop, traffic

def cell_index(pop, traffic):
    pop_norm = (pop - POP_RANGE[0]) / (POP_RANGE[1] - POP_RANGE[0])
    traffic_norm = (traffic - TRAFFIC_RANGE[0]) / (TRAFFIC_RANGE[1] - TRAFFIC_RANGE[0])
    x = min(int(pop_norm * GRID_BINS), GRID_BINS - 1)
    y = min(int(traffic_norm * GRID_BINS), GRID_BINS - 1)
    return x, y