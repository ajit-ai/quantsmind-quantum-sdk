"""
Dataset Package

This package provides dataset management for the Knowledge package.

Purpose
-------
Provide comprehensive dataset definitions and operations.

Modules
-------
- dataset: Base dataset class
- scientific_dataset: Scientific dataset with measurement support
- quantum_dataset: Quantum dataset with quantum state support
- tensor_dataset: Tensor dataset with multi-dimensional array support
- image_dataset: Image dataset with image processing support
- graph_dataset: Graph dataset with network data support
- simulation_dataset: Simulation dataset with simulation output support
- dataset_registry: Dataset registration and management
"""

from __future__ import annotations

from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.dataset.dataset_registry import DatasetRegistry
from quantsmind.knowledge.dataset.graph_dataset import GraphDataset
from quantsmind.knowledge.dataset.image_dataset import ImageDataset
from quantsmind.knowledge.dataset.quantum_dataset import QuantumDataset
from quantsmind.knowledge.dataset.scientific_dataset import ScientificDataset
from quantsmind.knowledge.dataset.simulation_dataset import SimulationDataset
from quantsmind.knowledge.dataset.tensor_dataset import TensorDataset

__all__ = [
    "Dataset",
    "ScientificDataset",
    "QuantumDataset",
    "TensorDataset",
    "ImageDataset",
    "GraphDataset",
    "SimulationDataset",
    "DatasetRegistry",
]
