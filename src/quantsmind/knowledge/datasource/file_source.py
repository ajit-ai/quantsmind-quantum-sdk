"""
File Source Module

This module provides file datasource definitions for the Knowledge package.

Purpose
-------
Provide file-based datasource management.

Responsibilities
----------------
- Define file datasource structure
- Support file operations
- Support file validation
- Support file metadata

Dependencies
------------
typing (standard library)
pathlib (standard library)
quantsmind.knowledge.datasource.datasource (datasource)
quantsmind.knowledge.enums (knowledge enumerations)
quantsmind.knowledge.exceptions (knowledge exceptions)
quantsmind.knowledge.types (knowledge types)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from quantsmind.knowledge.datasource.datasource import DataSource
from quantsmind.knowledge.enums import DataSourceType
from quantsmind.knowledge.exceptions import DatasetError
from quantsmind.knowledge.types import ValidationResult


class FileSource(DataSource):
    """Concrete implementation of a file data source.

    This class provides file datasource functionality.

    Attributes:
        _file_path: File path
        _file_format: File format
        _encoding: File encoding

    Example:
        >>> source = FileSource("source_001", "data.csv")
        >>> source.connect()
    """

    def __init__(
        self,
        source_id: str,
        file_path: str,
        file_format: str = "csv",
        encoding: str = "utf-8",
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a FileSource.

        Args:
            source_id: Source ID
            file_path: File path
            file_format: File format
            encoding: File encoding
            config: Source configuration
            metadata: Source metadata

        Example:
            >>> source = FileSource("source_001", "data.csv")
        """
        super().__init__(
            source_id=source_id,
            source_type=DataSourceType.FILE,
            config=config,
            metadata=metadata,
        )
        self._file_path = file_path
        self._file_format = file_format
        self._encoding = encoding
        self._config.update({
            "file_path": file_path,
            "file_format": file_format,
            "encoding": encoding,
        })

    @property
    def file_path(self) -> str:
        """Get the file path.

        Returns:
            File path

        Example:
            >>> path = source.file_path
        """
        return self._file_path

    @property
    def file_format(self) -> str:
        """Get the file format.

        Returns:
            File format

        Example:
            >>> fmt = source.file_format
        """
        return self._file_format

    @property
    def encoding(self) -> str:
        """Get the encoding.

        Returns:
            File encoding

        Example:
            >>> encoding = source.encoding
        """
        return self._encoding

    def connect(self) -> bool:
        """Connect to the file source.

        Returns:
            True if connected

        Raises:
            DatasetError: If file doesn't exist

        Example:
            >>> connected = source.connect()
        """
        path = Path(self._file_path)
        if not path.exists():
            raise DatasetError("File does not exist", {"file_path": self._file_path})

        self._connection = {
            "connected": True,
            "source_id": self._source_id,
            "file_path": self._file_path,
            "file_size": path.stat().st_size,
        }
        return True

    def read(self) -> Any:
        """Read data from the file.

        Returns:
            File data

        Raises:
            DatasetError: If read fails

        Example:
            >>> data = source.read()
        """
        if not self.is_connected():
            raise DatasetError("Not connected to file source", {"source_id": self._source_id})

        path = Path(self._file_path)

        if self._file_format == "csv":
            import csv
            with open(path, "r", encoding=self._encoding) as f:
                reader = csv.DictReader(f)
                return list(reader)
        elif self._file_format == "json":
            import json
            with open(path, "r", encoding=self._encoding) as f:
                return json.load(f)
        else:
            with open(path, "r", encoding=self._encoding) as f:
                return f.read()

    def write(self, data: Any) -> bool:
        """Write data to the file.

        Args:
            data: Data to write

        Returns:
            True if written

        Raises:
            DatasetError: If write fails

        Example:
            >>> written = source.write(data)
        """
        if not self.is_connected():
            raise DatasetError("Not connected to file source", {"source_id": self._source_id})

        path = Path(self._file_path)

        if self._file_format == "csv":
            import csv
            with open(path, "w", encoding=self._encoding, newline="") as f:
                if isinstance(data, list) and data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        elif self._file_format == "json":
            import json
            with open(path, "w", encoding=self._encoding) as f:
                json.dump(data, f, indent=2)
        else:
            with open(path, "w", encoding=self._encoding) as f:
                f.write(str(data))

        return True

    def validate(self) -> ValidationResult:
        """Validate the file source.

        Returns:
            Validation result

        Example:
            >>> is_valid, errors = source.validate()
        """
        errors = []

        # Validate base source
        base_valid, base_errors = super().validate()
        errors.extend(base_errors)

        # Validate file path
        if not self._file_path:
            errors.append("File path cannot be empty")

        # Validate file format
        valid_formats = ["csv", "json", "txt", "parquet", "feather"]
        if self._file_format not in valid_formats:
            errors.append(f"File format must be one of {valid_formats}")

        # Check if file exists
        if self._file_path:
            path = Path(self._file_path)
            if not path.exists():
                errors.append(f"File does not exist: {self._file_path}")

        return (len(errors) == 0, errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Source definition

        Example:
            >>> data = source.to_dict()
        """
        data = super().to_dict()
        data.update({
            "file_path": self._file_path,
            "file_format": self._file_format,
            "encoding": self._encoding,
        })
        return data

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String representation

        Example:
            >>> repr(source)
        """
        return f"FileSource(id={self._source_id}, path={self._file_path}, format={self._file_format}, connected={self.is_connected()})"


# Export
__all__ = [
    "FileSource",
]
