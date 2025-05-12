import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

data = []
with open('best_fitness.txt', 'r', encoding='utf-8') as f:
    for line in f:
        row = list(map(int, line.strip().split()))
        data.append(row)

traffic_land = sns.heatmap(data, annot=True, fmt=".2f")
plt.title("2D Heatmap")
plt.xlabel('land value')
plt.ylabel('traffic density')
x_labels = [400, 800, 1200, 1600, 2000]
y_labels = [100, 200, 300, 400, 500]
traffic_land.set_xticklabels(x_labels)
traffic_land.set_yticklabels(y_labels)
plt.show()

with open('fitnesses_in_generations.txt', 'r', encoding='utf-8') as f:
    y = [int(x) for x in f.read().strip().split()]

x = list(range(len(y)))
plt.plot(x, y, marker='o')
plt.xlabel('generation')
plt.ylabel('sum of fitnesses')
plt.title('micropolis')
plt.grid(True)
plt.show()
    