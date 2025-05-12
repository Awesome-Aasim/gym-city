import matplotlib.pyplot as plt

# === Define behavior ranges for normalization ===
BEHAVIOR_RANGES = {
    "pop": [0, 1000],        # Population range
    "traffic": [0, 500],     # Traffic range
    "crime": [0, 100],       # Crime rate range
    "pollution": [0, 100]    # Pollution level range
}

GRID_BINS = 20  # Number of discrete bins per dimension


# === Metric averaging functions ===

def average_population(env, steps=50):
    """Compute average population over a number of simulation ticks."""
    total = 0
    for _ in range(steps):
        env.micro.simTick()
        total += env.getPop()
    return total / steps

def average_traffic(env, steps=50):
    """Compute average traffic over a number of simulation ticks."""
    total = 0
    for _ in range(steps):
        env.micro.simTick()
        total += env.getTraffic()
    return total / steps

def average_crime(env, steps=50):
    """Compute average crime over a number of simulation ticks."""
    total = 0
    for _ in range(steps):
        env.micro.simTick()
        total += getattr(env.micro.map, 'city_crime', 0)  # Fallback to 0 if attribute not found
    return total / steps

def average_pollution(env, steps=50):
    """Compute average pollution over a number of simulation ticks."""
    total = 0
    for _ in range(steps):
        env.micro.simTick()
        total += getattr(env.micro.map, 'city_pollution', 0)  # Fallback to 0 if attribute not found
    return total / steps


# === Evaluation function ===

def evaluate(genome):
    """
    Simulate a genome in the Micropolis environment and compute its fitness and behavior signature.
    """
    env = MicropolisEnv(render_mode="none")
    env.reset()

    for action in genome:
        env.step(action)

    # Compute metrics
    pop = average_population(env)
    traffic = average_traffic(env)
    crime = average_crime(env)
    pollution = average_pollution(env)

    # Fitness function: maximize population, minimize traffic, crime, and pollution
    fitness = pop - 2.0 * traffic - 5.0 * crime - 3.0 * pollution

    # Behavior signature dictionary
    behavior = {
        "pop": pop,
        "traffic": traffic,
        "crime": crime,
        "pollution": pollution
    }

    return fitness, behavior


# === Behavior mapping to N-dimensional grid ===

def cell_index(behavior_metrics):
    """
    Map multi-dimensional behavior metrics to discrete grid coordinates.

    Args:
        behavior_metrics (dict): e.g. {"pop": 850, "traffic": 200, "crime": 5, "pollution": 30}

    Returns:
        tuple: N-dimensional grid index (e.g. (17, 8, 1, 6))
    """
    coords = []
    for key, value in behavior_metrics.items():
        if key not in BEHAVIOR_RANGES:
            raise ValueError(f"Range for behavior '{key}' not defined.")
        min_val, max_val = BEHAVIOR_RANGES[key]
        norm = (value - min_val) / (max_val - min_val)
        idx = min(int(norm * GRID_BINS), GRID_BINS - 1)
        coords.append(idx)

    return tuple(coords)