"""
Category Module

This module provides category definitions for the Knowledge package.

Purpose
-------
Provide category management for ontologies.

Responsibilities
----------------
- Define category structure
- Support category operations
- Support category validation
- Support category hierarchy

Dependencies
------------
typing (standard library)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any

from quantsmind.knowledge.exceptions import OntologyError
from quantsmind.knowledge.types import CategoryID, ValidationResult


class Category:
    """Concrete implementation of a category.

    This class provides category functionality.

    Attributes:
        _id: Category ID
        _name: Category name
        _parent_id: Parent category ID
        _children: Child category IDs
        _description: Category description
        _metadata: Category metadata

    Example:
        >>> category = Category("category_001", "Science")
        >>> category.name
    """

    def __init__(
        self,
        category_id: CategoryID,
        name: str,
        parent_id: CategoryID | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a Category.

        Args:
            category_id: Category ID
            name: Category name
            parent_id: Parent category ID
            description: Category description
            metadata: Category metadata

        Example:
            >>> category = Category("category_001", "Science")
        """
        if not category_id:
            raise OntologyError("Category ID cannot be empty")

        if not name:
            raise OntologyError("Category name cannot be empty")

        self._id = category_id
        self._name = name
        self._parent_id = parent_id
        self._children: list[CategoryID] = []
        self._description = description
        self._metadata = metadata or {}

    @property
    def id(self) -> CategoryID:
        """Get the category ID.

        Returns:
            Category ID

        Example:
            >>> cid = category.id
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the category name.

        Returns:
            Category name

        Example:
            >>> name = category.name
        """
        return self._name

    @property
    def parent_id(self) -> CategoryID | None:
        """Get the parent category ID.

        Returns:
            Parent category ID

        Example:
            >>> parent_id = category.parent_id
        """
        return self._parent_id

    @property
    def children(self) -> list[CategoryID]:
        """Get the child category IDs.

        Returns:
            Child category IDs

        Example:
            >>> children = category.children
        """
        return self._children.copy()

    @property
    def description(self) -> str | None:
        """Get the category description.

        Returns:
            Category description

        Example:
            >>> description = category.description
        """
        return self._description

    @property
    def metadata(self) -> dict[str, Any]:
        """Get the category metadata.

        Returns:
            Category metadata

        Example:
            >>> metadata = category.metadata
        """
        return self._metadata.copy()

    def set_parent(self, parent_id: CategoryID) -> None:
        """Set the parent category.

        Args:
            parent_id: Parent category ID

        Example:
            >>> category.set_parent("parent_001")
        """
        self._parent_id = parent_id

    def add_child(self, child_id: CategoryID) -> None:
        """Add a child category.

        Args:
            child_id: Child category ID

        Example:
            >>> category.add_child("child_001")
        """
        if child_id not in self._children:
            self._children.append(child_id)

    def remove_child(self, child_id: CategoryID) -> bool:
        """Remove a child category.

        Args:
            child_id: Child category ID

        Returns:
            True if removed

        Example:
            >>> removed = category.remove_child("child_001")
        """
        if child_id in self._children:
            self._children.remove(child_id)
            return True
        return False

    def get_depth(self) -> int:
        """Get the depth of this category in the hierarchy.

        Returns:
            Depth level (0 for root)

        Example:
            >>> depth = category.get_depth()
        """
        # Placeholder - would need access to parent category
        return 0

    def validate(self) -> ValidationResult:
        """Validate the category.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = category.validate()
        """
        errors = []

        if not self._id:
            errors.append("Category ID cannot be empty")

        if not self._name:
            errors.append("Category name cannot be empty")

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Category definition

        Example:
            >>> data = category.to_dict()
        """
        return {
            "id": self._id,
            "name": self._name,
            "parent_id": self._parent_id,
            "children": self._children,
            "description": self._description,
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(category)
        """
        return f"Category(id={self._id}, name={self._name}, children={len(self._children)})"


class CategoryHierarchy:
    """Hierarchy of categories.

    This class provides category hierarchy functionality.

    Attributes:
        _categories: Categories in the hierarchy
        _root_categories: Root category IDs

    Example:
        >>> hierarchy = CategoryHierarchy()
        >>> hierarchy.add_category(Category("cat_001", "Science"))
    """

    def __init__(self, categories: list[Category] | None = None) -> None:
        """Initialize a CategoryHierarchy.

        Args:
            categories: Initial categories

        Example:
            >>> hierarchy = CategoryHierarchy()
        """
        self._categories: dict[CategoryID, Category] = {}
        self._root_categories: list[CategoryID] = []

        if categories:
            for category in categories:
                self.add_category(category)

    def add_category(self, category: Category) -> None:
        """Add a category to the hierarchy.

        Args:
            category: Category to add

        Example:
            >>> hierarchy.add_category(Category("cat_001", "Science"))
        """
        self._categories[category.id] = category

        if category.parent_id is None:
            if category.id not in self._root_categories:
                self._root_categories.append(category.id)
        else:
            # Add as child to parent
            if category.parent_id in self._categories:
                self._categories[category.parent_id].add_child(category.id)

    def remove_category(self, category_id: CategoryID) -> bool:
        """Remove a category from the hierarchy.

        Args:
            category_id: Category ID

        Returns:
            True if removed

        Example:
            >>> removed = hierarchy.remove_category("cat_001")
        """
        if category_id in self._categories:
            category = self._categories[category_id]

            # Remove from parent's children
            if category.parent_id and category.parent_id in self._categories:
                self._categories[category.parent_id].remove_child(category_id)

            # Remove from root if applicable
            if category_id in self._root_categories:
                self._root_categories.remove(category_id)

            # Remove children's parent reference
            for child_id in category.children:
                if child_id in self._categories:
                    self._categories[child_id]._parent_id = None
                    self._root_categories.append(child_id)

            del self._categories[category_id]
            return True
        return False

    def get_category(self, category_id: CategoryID) -> Category | None:
        """Get a category by ID.

        Args:
            category_id: Category ID

        Returns:
            Category or None

        Example:
            >>> category = hierarchy.get_category("cat_001")
        """
        return self._categories.get(category_id)

    def get_root_categories(self) -> list[Category]:
        """Get root categories.

        Returns:
            List of root categories

        Example:
            >>> roots = hierarchy.get_root_categories()
        """
        return [self._categories[cid] for cid in self._root_categories if cid in self._categories]

    def get_path(self, category_id: CategoryID) -> list[Category]:
        """Get the path from root to a category.

        Args:
            category_id: Category ID

        Returns:
            List of categories in path

        Example:
            >>> path = hierarchy.get_path("cat_001")
        """
        path = []
        current = self._categories.get(category_id)

        while current:
            path.append(current)
            if current.parent_id:
                current = self._categories.get(current.parent_id)
            else:
                break

        path.reverse()
        return path

    def get_subtree(self, category_id: CategoryID) -> list[Category]:
        """Get all categories in the subtree of a category.

        Args:
            category_id: Category ID

        Returns:
            List of categories in subtree

        Example:
            >>> subtree = hierarchy.get_subtree("cat_001")
        """
        result = []
        category = self._categories.get(category_id)

        if category:
            result.append(category)
            for child_id in category.children:
                result.extend(self.get_subtree(child_id))

        return result

    def validate(self) -> ValidationResult:
        """Validate the hierarchy.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = hierarchy.validate()
        """
        errors = []

        # Check for cycles
        visited = set()
        for category_id in self._categories:
            if category_id not in visited:
                path = []
                current = self._categories.get(category_id)
                while current:
                    if current.id in path:
                        errors.append(f"Cycle detected involving category {current.id}")
                        break
                    path.append(current.id)
                    if current.parent_id:
                        current = self._categories.get(current.parent_id)
                    else:
                        break
                visited.update(path)

        return (len(errors) == 0, errors)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Hierarchy definition

        Example:
            >>> data = hierarchy.to_dict()
        """
        return {
            "categories": [cat.to_dict() for cat in self._categories.values()],
            "root_categories": self._root_categories,
            "count": len(self._categories),
        }

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(hierarchy)
        """
        return f"CategoryHierarchy(categories={len(self._categories)}, roots={len(self._root_categories)})"


# Export
__all__ = [
    "Category",
    "CategoryHierarchy",
]
