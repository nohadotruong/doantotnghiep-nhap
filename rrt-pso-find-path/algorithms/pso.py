import math
import numpy as np

from utils.core import path_length, smoothness_penalty


class PSOOptimizer:
    def __init__(
        self,
        environment,
        original_path,
        num_particles=30,
        iterations=100,
        w=0.7,
        c1=1.5,
        c2=1.5,
        w_length=0.3,
        w_safety=0.4,
        w_smoothness=0.3,
    ):
        self.environment = environment
        self.original_path = original_path
        self.num_particles = num_particles
        self.iterations = iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2

        self.w_length = w_length
        self.w_safety = w_safety
        self.w_smoothness = w_smoothness

        total_weight = self.w_length + self.w_safety + self.w_smoothness

        if not np.isclose(total_weight, 1.0):
            print(f"[Warning] Weights sum to {total_weight:.2f}, not 1.0")
            if total_weight > 0:
                self.w_length /= total_weight
                self.w_safety /= total_weight
                self.w_smoothness /= total_weight
                print(
                    f"[Normalized] Weights: length={self.w_length:.2f}, safety={self.w_safety:.2f}, "
                    f"smoothness={self.w_smoothness:.2f}"
                )

        self.num_waypoints = len(original_path) - 2
        self.start = original_path[0]
        self.goal = original_path[-1]

        self.straight_line_distance = math.sqrt(
            (self.goal[0] - self.start[0]) ** 2 + (self.goal[1] - self.start[1]) ** 2
        )
        self.particles = []
        self.velocities = []
        self.best_positions = []
        self.best_fitness = []

        self._init_particles()

    def _init_particles(self):
        x_min, x_max = 0, self.environment.width
        y_min, y_max = 0, self.environment.height

        for _ in range(self.num_particles):
            particle = self._path_to_particle(self.original_path)

            for i in range(len(particle)):
                if i % 2 == 0:
                    particle[i] += np.random.uniform(-5, 5)
                    particle[i] = np.clip(particle[i], x_min, x_max)
                else:
                    particle[i] += np.random.uniform(-5, 5)
                    particle[i] = np.clip(particle[i], y_min, y_max)

            self.particles.append(particle)

            velocity = np.random.uniform(-1, 1, len(particle))
            self.velocities.append(velocity)

            self.best_positions.append(particle.copy())

            fitness = self._fitness(particle)
            self.best_fitness.append(fitness)

        best_idx = np.argmin(self.best_fitness)
        self.global_best_position = self.best_positions[best_idx].copy()
        self.global_best_fitness = self.best_fitness[best_idx]

    def _path_to_particle(self, path):
        particle = []

        for i in range(1, len(path) - 1):
            particle.append(path[i][0])
            particle.append(path[i][1])

        return np.array(particle)

    def _particle_to_path(self, particle):
        path = [self.start]

        for i in range(0, len(particle), 2):
            path.append((particle[i], particle[i + 1]))
        path.append(self.goal)

        return path

    def _fitness(self, particle):
        path = self._particle_to_path(particle)

        length = path_length(path)
        if length > 0:
            length_norm = self.straight_line_distance / length
            length_norm = min(1.0, length_norm)
        else:
            length_norm = 0

        collision_count = 0
        for i in range(len(path) - 1):
            if self.environment.is_collision(path[i], path[i + 1]):
                collision_count += 1

        if collision_count > 0:
            return 1.0
        else:
            min_distance = float("inf")
            for point in path:
                dist = self._min_distance_to_obstacles(point)
                min_distance = min(min_distance, dist)

            safety_margin = 10.0
            if min_distance >= safety_margin:
                safety_norm = 1.0
            elif min_distance <= 0:
                safety_norm = 0
            else:
                safety_norm = min_distance / safety_margin

            smooth_value = smoothness_penalty(path)
            smoothness_norm = 1.0 / (1.0 + smooth_value)

            fitness = (
                self.w_length * (1.0 - length_norm)
                + self.w_safety * (1.0 - safety_norm)
                + self.w_smoothness * (1.0 - smoothness_norm)
            )

            return fitness

    def _min_distance_to_obstacles(self, point):
        if not self.environment or not self.environment.obstacles:
            return float("inf")

        min_dist = float("inf")
        x, y = point

        for ox, oy, ow, oh in self.environment.obstacles:
            dist_x = max(ox - x, 0, x - (ox + ow))
            dist_y = max(oy - y, 0, y - (oy + oh))
            dist = math.sqrt(dist_x**2 + dist_y**2)
            min_dist = min(min_dist, dist)

        return min_dist if min_dist != float("inf") else 100

    def _clip_position(self, position):
        for i in range(len(position)):
            if i % 2 == 0:
                position[i] = np.clip(position[i], 0, self.environment.width)
            else:
                position[i] = np.clip(position[i], 0, self.environment.height)

        return position

    def optimize(self):
        print(f"\n[PSO] Start optimization...")
        print(
            f"\n[PSO] Weights: Length = {self.w_length * 100:.0f}%, Safety = {self.w_safety * 100:.0f}%, Smoothness = {self.w_smoothness * 100:.0f}%"
        )
        print(f"[PSO] First fitness: {self.global_best_fitness:.4f}")

        for iteration in range(self.iterations):
            for i in range(self.num_particles):
                r1 = np.random.random(len(self.particles[i]))
                r2 = np.random.random(len(self.particles[i]))

                cognitive = self.c1 * r1 * (self.best_positions[i] - self.particles[i])

                social = self.c2 * r2 * (self.global_best_position - self.particles[i])

                self.velocities[i] = self.w * self.velocities[i] + self.velocities[i]

                self.particles[i] = self._clip_position(self.particles[i])

                fitness = self._fitness(self.particles[i])

                if fitness < self.best_fitness[i]:
                    self.best_fitness[i] = fitness
                    self.best_positions[i] = self.particles[i].copy()

                    if fitness < self.global_best_fitness:
                        self.global_best_fitness = fitness
                        self.global_best_position = self.particles[i].copy()

        if (iteration + 1) % 20 == 0:
            print(
                f"[PSO] Iteration {iteration + 1} / {self.iterations}: Best fitness = {self.global_best_fitness:.4f}"
            )

        print(
            f"[PSO] Optimization complete!\n[PSO] Final fitness: {self.global_best_fitness:.4f}"
        )

        optimized_path = self._particle_to_path(self.global_best_position)
        return optimized_path
