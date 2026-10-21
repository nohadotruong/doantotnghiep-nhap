import numpy as np
import random

from math import sqrt
from utils import path_length


class PSOTSP:
    def __init__(self, points, start_point, num_particles=20, max_iterations=100):
        self.points = points
        self.start_point = start_point
        self.num_particles = num_particles
        self.max_iterations = max_iterations

        self.num_points = len(points)
        self.start_idx = points.index(start_point)

        self.w = 0.7
        self.c1 = 1.5
        self.c2 = 1.5

        self.positions = []
        self.velocities = []
        self.pbest_positions = []
        self.pbest_fitness = []
        self.fitness = []

        self.gbest_position = None
        self.gbest_fitness = float("inf")

        self._initialize_swarm()

    def _initialize_swarm(self):
        for i in range(self.num_particles):
            position = list(self.points)
            random.shuffle(position)
            self.positions.append(position)

            velocity = []
            self.velocities.append(velocity)

            fit = self._calculate_path_length(position)
            self.fitness.append(fit)

            self.pbest_positions.append(position[:])
            self.pbest_fitness.append(fit)

            if fit < self.gbest_fitness:
                self.gbest_fitness = fit
                self.gbest_position = position[:]

    def _calculate_path_length(self, path):
        tsp_path = path + [path[0]]
        return path_length(tsp_path)

    def _apply_swaps(self, position, swaps):
        new_position = position.copy()
        for i, j in swaps:
            new_position[i], new_position[j] = new_position[j], new_position[i]

        return new_position

    def _update_velocity(self, particle_idx):
        current_pos = self.positions[particle_idx]
        pbest_pos = self.pbest_positions[particle_idx]
        gbest_pos = self.gbest_position

        pbest_swaps = self._find_swaps(current_pos, pbest_pos)
        gbest_swaps = self._find_swaps(current_pos, gbest_pos)

        new_velocity = []

        if random.random() < self.c1 / 10:
            if pbest_swaps:
                num_swaps = random.randint(1, len(pbest_swaps))
                new_velocity.extend(random.sample(pbest_swaps, num_swaps))

        if random.random() < self.c2 / 10:
            if gbest_swaps:
                num_swaps = random.randint(1, len(gbest_swaps))
                new_velocity.extend(random.sample(gbest_swaps, num_swaps))

        self.velocities[particle_idx] = new_velocity

    def _find_swaps(self, current_pos, target_pos):
        temp_pos = current_pos[:]
        swaps = []

        for i in range(len(temp_pos)):
            if temp_pos[i] != target_pos[i]:
                j = temp_pos.index(target_pos[i])
                swaps.append((i, j))
                temp_pos[i], temp_pos[j] = temp_pos[j], temp_pos[i]

        return swaps
