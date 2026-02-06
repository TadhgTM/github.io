from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Callable


@dataclass
class GAConfig:
    population: int = 100
    generations: int = 200
    crossover_rate: float = 0.8
    mutation_rate: float = 0.1
    mutation_scale: float = 0.05
    elite_share: float = 0.1
    seed: int | None = None


def genetic_optimize(
    objective: Callable[[np.ndarray], float],
    bounds: tuple[np.ndarray, np.ndarray],
    config: GAConfig,
) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng(config.seed)

    low, high = bounds
    dim = low.shape[0]

    pop = rng.uniform(low, high, size=(config.population, dim))
    scores = np.array([objective(ind) for ind in pop])

    elite_n = max(1, int(config.elite_share * config.population))

    for _ in range(config.generations):
        order = np.argsort(scores)[::-1]
        pop = pop[order]
        scores = scores[order]

        elites = pop[:elite_n]

        # Selection (tournament)
        def tournament_select(k: int = 3) -> np.ndarray:
            idx = rng.integers(0, config.population, size=k)
            best = idx[np.argmax(scores[idx])]
            return pop[best]

        new_pop = [elites[i].copy() for i in range(elite_n)]
        while len(new_pop) < config.population:
            parent1 = tournament_select()
            parent2 = tournament_select()

            if rng.random() < config.crossover_rate:
                cross_point = rng.integers(1, dim)
                child = np.concatenate([parent1[:cross_point], parent2[cross_point:]])
            else:
                child = parent1.copy()

            if rng.random() < config.mutation_rate:
                noise = rng.normal(0.0, config.mutation_scale, size=dim)
                child = child + noise

            child = np.clip(child, low, high)
            new_pop.append(child)

        pop = np.array(new_pop)
        scores = np.array([objective(ind) for ind in pop])

    best_idx = np.argmax(scores)
    return pop[best_idx], scores[best_idx]
