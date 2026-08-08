"""
Image Dataset Module

This module provides image dataset definitions for the Knowledge package.

Purpose
-------
Provide image dataset management with image processing support.

Responsibilities
----------------
- Define image dataset structure
- Support image data
- Support image metadata
- Support image operations
- Support image validation

Dependencies
------------
typing (standard library)
quantsmind.knowledge.dataset.dataset (dataset)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from quantsmind.knowledge.dataset.dataset import Dataset
from quantsmind.knowledge.enums import DatasetType
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.types import (
    DatasetData,
    DatasetSchema,
    ValidationResult,
)


class ImageDataset(Dataset):
    """Concrete implementation of an image dataset.

    This class provides image dataset functionality with image processing support.

    Attributes:
        _images: Image records
        _image_format: Image format
        _image_size: Image size (width, height)
        _channels: Number of channels

    Example:
        >>> dataset = ImageDataset("image_data", image_size=(256, 256))
        >>> dataset.add_image({"data": b"...", "format": "PNG"})
    """

    def __init__(
        self,
        name: str,
        image_size: Optional[Tuple[int, int]] = None,
        channels: int = 3,
        image_format: str = "PNG",
        schema: Optional[DatasetSchema] = None,
        data: Optional[DatasetData] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an ImageDataset.

        Args:
            name: Dataset name
            image_size: Image size (width, height)
            channels: Number of channels
            image_format: Image format
            schema: Dataset schema
            data: Dataset data
            metadata: Dataset metadata

        Example:
            >>> dataset = ImageDataset("image_data", image_size=(256, 256))
        """
        super().__init__(
            name=name,
            dataset_type=DatasetType.IMAGE,
            schema=schema,
            data=data,
            metadata=metadata,
        )
        self._image_size = image_size
        self._channels = channels
        self._image_format = image_format
        self._images: List[Dict[str, Any]] = []

    @property
    def image_size(self) -> Optional[Tuple[int, int]]:
        """Get the image size.

        Returns:
            Image size (width, height)

        Example:
            >>> size = dataset.image_size
        """
        return self._image_size

    @property
    def channels(self) -> int:
        """Get the number of channels.

        Returns:
            Number of channels

        Example:
            >>> channels = dataset.channels
        """
        return self._channels

    @property
    def image_format(self) -> str:
        """Get the image format.

        Returns:
            Image format

        Example:
            >>> format = dataset.image_format
        """
        return self._image_format

    @property
    def images(self) -> List[Dict[str, Any]]:
        """Get the images.

        Returns:
            Image records

        Example:
            >>> images = dataset.images
        """
        return self._images.copy()

    def add_image(self, image: Dict[str, Any]) -> None:
        """Add an image to the dataset.

        Args:
            image: Image data

        Raises:
            DatasetError: If image is invalid

        Example:
            >>> dataset.add_image({"data": b"...", "format": "PNG"})
        """
        if not isinstance(image, dict):
            raise DatasetError("Image must be a dictionary", {"image": image})

        image_data = image.get("data")
        if image_data is None:
            raise DatasetError("Image must have data", {"image": image})

        # Validate format
        image_format = image.get("format", self._image_format)
        if not isinstance(image_format, str):
            raise DatasetError("Image format must be a string", {"format": image_format})

        self._images.append(image)
        self._updated_at = self._updated_at

    def add_images(self, images: List[Dict[str, Any]]) -> None:
        """Add multiple images to the dataset.

        Args:
            images: Image data list

        Example:
            >>> dataset.add_images([{"data": b"..."}, {"data": b"..."}])
        """
        for image in images:
            self.add_image(image)

    def get_image_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get image by index.

        Args:
            index: Image index

        Returns:
            Image data or None

        Example:
            >>> image = dataset.get_image_by_index(0)
        """
        if 0 <= index < len(self._images):
            return self._images[index]
        return None

    def get_images_by_format(self, format: str) -> List[Dict[str, Any]]:
        """Get images with specific format.

        Args:
            format: Image format

        Returns:
            Image records

        Example:
            >>> images = dataset.get_images_by_format("PNG")
        """
        return [image for image in self._images if image.get("format") == format]

    def get_images_by_size(self, size: Tuple[int, int]) -> List[Dict[str, Any]]:
        """Get images with specific size.

        Args:
            size: Image size (width, height)

        Returns:
            Image records

        Example:
            >>> images = dataset.get_images_by_size((256, 256))
        """
        return [image for image in self._images if image.get("size") == size]

    def calculate_dataset_statistics(self) -> Dict[str, Any]:
        """Calculate dataset statistics.

        Returns:
            Statistics dictionary

        Example:
            >>> stats = dataset.calculate_dataset_statistics()
        """
        if not self._images:
            return {}

        formats = {}
        sizes = {}

        for image in self._images:
            fmt = image.get("format", "unknown")
            formats[fmt] = formats.get(fmt, 0) + 1

            size = image.get("size")
            if size:
                sizes[size] = sizes.get(size, 0) + 1

        return {
            "total_images": len(self._images),
            "formats": formats,
            "sizes": sizes,
        }

    def resize_images(self, target_size: Tuple[int, int]) -> None:
        """Resize all images to target size.

        Args:
            target_size: Target size (width, height)

        Note:
            This is a placeholder. Actual implementation would require image processing library.

        Example:
            >>> dataset.resize_images((512, 512))
        """
        self._image_size = target_size
        for image in self._images:
            image["size"] = target_size
        self._updated_at = self._updated_at

    def validate(self) -> ValidationResult:
        """Validate the image dataset.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = dataset.validate()
        """
        errors = []

        # Validate base dataset
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate images
        for i, image in enumerate(self._images):
            if "data" not in image:
                errors.append(f"Image {i} missing data")

            if "format" in image and not isinstance(image["format"], str):
                errors.append(f"Image {i} format must be a string")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dataset definition

        Example:
            >>> data = dataset.to_dict()
        """
        data = super().to_dict()
        data.update({
            "image_size": self._image_size,
            "channels": self._channels,
            "image_format": self._image_format,
            "images_count": len(self._images),
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(dataset)
        """
        return f"ImageDataset(id={self._id}, name={self._name}, size={self._image_size}, format={self._image_format}, images={len(self._images)})"


# Export
__all__ = [
    "ImageDataset",
]
