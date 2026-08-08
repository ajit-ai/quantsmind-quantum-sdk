"""
Evolutionary Optimizer Module

This module provides evolutionary optimization algorithms for the QuantsMind SDK.

Purpose
-------
Provide genetic algorithm and particle swarm optimization algorithms.

Classes
-------
EvolutionaryOptimizer: Base evolutionary optimizer
GeneticAlgorithm: Genetic algorithm optimizer
ParticleSwarmOptimizer: Particle swarm optimization

Responsibilities
----------------
- Optimize functions using population-based methods
- Support evolutionary algorithms
- Track population evolution
- Handle constraints

Dependencies
------------
typing (standard library)
quantsmind.core.math_object (MathObject)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple
import random
import math


class EvolutionaryOptimizer:
    """Base evolutionary optimizer.

    This class provides the base functionality for population-based optimization.

    Attributes:
        _name: Optimizer name
        _population_size: Population size
        _max_iterations: Maximum iterations
        _tolerance: Convergence tolerance
        _metadata: Additional metadata

    Example:
        >>> optimizer = EvolutionaryOptimizer("ga", population_size=50)
        >>> result = optimizer.optimize(lambda x: x**2, bounds=(-10, 10))
    """

    def __init__(
        self,
        name: str,
        population_size: int = 50,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an EvolutionaryOptimizer.

        Args:
            name: Optimizer name
            population_size: Population size
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            metadata: Additional metadata

        Example:
            >>> optimizer = EvolutionaryOptimizer("ga", population_size=50)
        """
        self._name = name
        self._population_size = population_size
        self._max_iterations = max_iterations
        self._tolerance = tolerance
        self._metadata = metadata or {}

    @property
    def name(self) -> str:
        """Get the optimizer name.

        Returns:
            Optimizer name

        Example:
            >>> name = optimizer.name
        """
        return self._name

    @property
    def population_size(self) -> int:
        """Get the population size.

        Returns:
            Population size

        Example:
            >>> size = optimizer.population_size
        """
        return self._population_size

    def optimize(
        self,
        func: Callable[[float], float],
        bounds: Tuple[float, float],
    ) -> Tuple[float, List[float]]:
        """Optimize a function.

        Args:
            func: Objective function
            bounds: Search bounds (lower, upper)

        Returns:
            Tuple of (optimal_x, history)

        Example:
            >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
        """
        raise NotImplementedError("Subclasses must implement optimize")

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(optimizer)
        """
        return f"EvolutionaryOptimizer(name={self._name}, pop_size={self._population_size})"


class GeneticAlgorithm(EvolutionaryOptimizer):
    """Genetic algorithm optimizer.

    This class implements the genetic algorithm for optimization.

    Attributes:
        _mutation_rate: Mutation probability
        _crossover_rate: Crossover probability
        _elite_size: Number of elite individuals to preserve

    Example:
        >>> optimizer = GeneticAlgorithm(population_size=50, mutation_rate=0.01)
        >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
    """

    def __init__(
        self,
        population_size: int = 50,
        mutation_rate: float = 0.01,
        crossover_rate: float = 0.8,
        elite_size: int = 2,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a GeneticAlgorithm.

        Args:
            population_size: Population size
            mutation_rate: Mutation probability
            crossover_rate: Crossover probability
            elite_size: Number of elite individuals
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            metadata: Additional metadata

        Example:
            >>> optimizer = GeneticAlgorithm(population_size=50, mutation_rate=0.01)
        """
        super().__init__("genetic_algorithm", population_size, max_iterations, tolerance, metadata)
        self._mutation_rate = mutation_rate
        self._crossover_rate = crossover_rate
        self._elite_size = elite_size

    def optimize(
        self,
        func: Callable[[float], float],
        bounds: Tuple[float, float],
    ) -> Tuple[float, List[float]]:
        """Optimize using genetic algorithm.

        Args:
            func: Objective function
            bounds: Search bounds (lower, upper)

        Returns:
            Tuple of (optimal_x, history)

        Example:
            >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
        """
        lower, upper = bounds

        # Initialize population
        population = [random.uniform(lower, upper) for _ in range(self._population_size)]
        history = []

        for _ in range(self._max_iterations):
            # Evaluate fitness
            fitness = [func(x) for x in population]

            # Track best solution
            best_idx = fitness.index(min(fitness))
            best_x = population[best_idx]
            history.append(best_x)

            # Check convergence
            if len(history) > 1 and abs(history[-1] - history[-2]) < self._tolerance:
                break

            # Selection (tournament)
            selected = self._tournament_selection(population, fitness)

            # Crossover
            offspring = self._crossover(selected, bounds)

            # Mutation
            offspring = self._mutate(offspring, bounds)

            # Elitism
            elite_indices = sorted(range(len(fitness)), key=lambda i: fitness[i])[:self._elite_size]
            for i in range(self._elite_size):
                offspring[i] = population[elite_indices[i]]

            population = offspring

        best_fitness = [func(x) for x in population]
        best_idx = best_fitness.index(min(best_fitness))
        return (population[best_idx], history)

    def _tournament_selection(
        self,
        population: List[float],
        fitness: List[float],
        tournament_size: int = 3,
    ) -> List[float]:
        """Tournament selection.

        Args:
            population: Current population
            fitness: Fitness values
            tournament_size: Tournament size

        Returns:
            Selected individuals
        """
        selected = []
        for _ in range(len(population)):
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness[i] for i in tournament_indices]
            winner_idx = tournament_indices[tournament_fitness.index(min(tournament_fitness))]
            selected.append(population[winner_idx])
        return selected

    def _crossover(
        self,
        population: List[float],
        bounds: Tuple[float, float],
    ) -> List[float]:
        """Crossover operation.

        Args:
            population: Population
            bounds: Search bounds

        Returns:
            Offspring
        """
        offspring = []
        for i in range(0, len(population) - 1, 2):
            parent1 = population[i]
            parent2 = population[i + 1]

            if random.random() < self._crossover_rate:
                # Arithmetic crossover
                alpha = random.random()
                child1 = alpha * parent1 + (1 - alpha) * parent2
                child2 = (1 - alpha) * parent1 + alpha * parent2
                offspring.extend([child1, child2])
            else:
                offspring.extend([parent1, parent2])

        if len(population) % 2 == 1:
            offspring.append(population[-1])

        return offspring

    def _mutate(
        self,
        population: List[float],
        bounds: Tuple[float, float],
    ) -> List[float]:
        """Mutation operation.

        Args:
            population: Population
            bounds: Search bounds

        Returns:
            Mutated population
        """
        lower, upper = bounds
        for i in range(len(population)):
            if random.random() < self._mutation_rate:
                # Gaussian mutation
                population[i] += random.gauss(0, 0.1 * (upper - lower))
                population[i] = max(lower, min(upper, population[i]))
        return population


class ParticleSwarmOptimizer(EvolutionaryOptimizer):
    """Particle swarm optimization.

    This class implements particle swarm optimization for finding global optima.

    Attributes:
        _w: Inertia weight
        _c1: Cognitive coefficient
        _c2: Social coefficient

    Example:
        >>> optimizer = ParticleSwarmOptimizer(population_size=30)
        >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
    """

    def __init__(
        self,
        population_size: int = 30,
        w: float = 0.7,
        c1: float = 1.5,
        c2: float = 1.5,
        max_iterations: int = 1000,
        tolerance: float = 1e-6,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a ParticleSwarmOptimizer.

        Args:
            population_size: Population size (number of particles)
            w: Inertia weight
            c1: Cognitive coefficient
            c2: Social coefficient
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            metadata: Additional metadata

        Example:
            >>> optimizer = ParticleSwarmOptimizer(population_size=30)
        """
        super().__init__("particle_swarm", population_size, max_iterations, tolerance, metadata)
        self._w = w
        self._c1 = c1
        self._c2 = c2

    def optimize(
        self,
        func: Callable[[float], float],
        bounds: Tuple[float, float],
    ) -> Tuple[float, List[float]]:
        """Optimize using particle swarm optimization.

        Args:
            func: Objective function
            bounds: Search bounds (lower, upper)

        Returns:
            Tuple of (optimal_x, history)

        Example:
            >>> result, history = optimizer.optimize(lambda x: x**2, (-10, 10))
        """
        lower, upper = bounds

        # Initialize particles
        positions = [random.uniform(lower, upper) for _ in range(self._population_size)]
        velocities = [random.uniform(-1, 1) for _ in range(self._population_size)]

        # Personal best
        personal_best_positions = positions.copy()
        personal_best_values = [func(x) for x in positions]

        # Global best
        global_best_idx = personal_best_values.index(min(personal_best_values))
        global_best_position = personal_best_positions[global_best_idx]
        global_best_value = personal_best_values[global_best_idx]

        history = [global_best_position]

        for _ in range(self._max_iterations):
            for i in range(self._population_size):
                # Update velocity
                r1 = random.random()
                r2 = random.random()

                cognitive = self._c1 * r1 * (personal_best_positions[i] - positions[i])
                social = self._c2 * r2 * (global_best_position - positions[i])

                velocities[i] = self._w * velocities[i] + cognitive + social

                # Update position
                positions[i] += velocities[i]
                positions[i] = max(lower, min(upper, positions[i]))

                # Evaluate
                value = func(positions[i])

                # Update personal best
                if value < personal_best_values[i]:
                    personal_best_positions[i] = positions[i]
                    personal_best_values[i] = value

                # Update global best
                if value < global_best_value:
                    global_best_position = positions[i]
                    global_best_value = value

            history.append(global_best_position)

            # Check convergence
            if len(history) > 1 and abs(history[-1] - history[-2]) < self._tolerance:
                break

        return (global_best_position, history)


__all__ = [
    "EvolutionaryOptimizer",
    "GeneticAlgorithm",
    "ParticleSwarmOptimizer",
]
