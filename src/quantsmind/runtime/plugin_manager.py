"""
Runtime Plugin Manager Module

This module provides plugin management for the Runtime package.

Purpose
-------
Provide plugin management for the QuantsMind SDK.

Responsibilities
----------------
- Manage plugin lifecycle
- Handle plugin discovery
- Track plugin dependencies
- Support plugin capabilities

Dependencies
------------
typing (standard library)
logging (standard library)
threading (standard library)
quantsmind.runtime.constants (runtime constants)
quantsmind.runtime.types (runtime types)
quantsmind.runtime.enums (runtime enumerations)
quantsmind.runtime.exceptions (runtime exceptions)
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from quantsmind.runtime.constants import DEFAULT_PLUGIN_TIMEOUT, DEFAULT_PLUGIN_VERSION
from quantsmind.runtime.enums import PluginState
from quantsmind.runtime.exceptions import PluginDependencyError, PluginError, PluginLoadError
from quantsmind.runtime.types import PluginCapabilities, PluginID, PluginVersion

logger = logging.getLogger(__name__)


class PluginManager:
    """Concrete implementation of a plugin manager.

    This class provides plugin management capabilities.

    Attributes:
        _plugins: Registered plugins
        _plugin_states: Plugin states
        _plugin_dependencies: Plugin dependencies
        _plugin_capabilities: Plugin capabilities
        _lock: Thread lock

    Example:
        >>> manager = PluginManager()
        >>> manager.load_plugin("my_plugin", MyPlugin)
    """

    def __init__(self) -> None:
        """Initialize a PluginManager.

        Example:
            >>> manager = PluginManager()
        """
        self._plugins: Dict[PluginID, Any] = {}
        self._plugin_states: Dict[PluginID, PluginState] = {}
        self._plugin_dependencies: Dict[PluginID, List[PluginID]] = {}
        self._plugin_capabilities: Dict[PluginID, PluginCapabilities] = {}
        self._lock = threading.Lock()
        logger.debug("Created plugin manager")

    @property
    def plugin_count(self) -> int:
        """Get the number of loaded plugins.

        Returns:
            Number of plugins

        Example:
            >>> print(f"Plugin count: {manager.plugin_count}")
        """
        with self._lock:
            return len(self._plugins)

    def load_plugin(
        self,
        plugin_id: PluginID,
        plugin: Any,
        dependencies: Optional[List[PluginID]] = None,
        capabilities: Optional[PluginCapabilities] = None,
        version: PluginVersion = DEFAULT_PLUGIN_VERSION,
    ) -> bool:
        """Load a plugin.

        Args:
            plugin_id: Plugin identifier
            plugin: Plugin instance
            dependencies: Plugin dependencies
            capabilities: Plugin capabilities
            version: Plugin version

        Returns:
            True if loaded, False otherwise

        Raises:
            PluginLoadError: If plugin loading fails
            PluginDependencyError: If dependencies are not satisfied

        Example:
            >>> manager.load_plugin("my_plugin", MyPlugin)
        """
        with self._lock:
            if plugin_id in self._plugins:
                raise PluginLoadError(f"Plugin already loaded: {plugin_id}", plugin_id=plugin_id)

            # Check dependencies
            if dependencies:
                for dep_id in dependencies:
                    if dep_id not in self._plugins:
                        raise PluginDependencyError(
                            f"Dependency not found: {dep_id}",
                            plugin_id=plugin_id,
                        )

            self._plugin_states[plugin_id] = PluginState.LOADING

        try:
            # Initialize plugin if it has an initialize method
            if hasattr(plugin, "initialize"):
                plugin.initialize()

            with self._lock:
                self._plugins[plugin_id] = plugin
                self._plugin_states[plugin_id] = PluginState.LOADED
                self._plugin_dependencies[plugin_id] = dependencies or []
                self._plugin_capabilities[plugin_id] = capabilities or []
            
            logger.info(f"Loaded plugin: {plugin_id}")
            return True
        except Exception as e:
            with self._lock:
                self._plugin_states[plugin_id] = PluginState.ERROR
            raise PluginLoadError(f"Plugin loading failed: {str(e)}", plugin_id=plugin_id) from e

    def unload_plugin(self, plugin_id: PluginID) -> bool:
        """Unload a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if unloaded, False otherwise

        Example:
            >>> unloaded = manager.unload_plugin("my_plugin")
        """
        with self._lock:
            if plugin_id not in self._plugins:
                return False

            # Check if other plugins depend on this one
            for pid, deps in self._plugin_dependencies.items():
                if plugin_id in deps:
                    logger.warning(f"Cannot unload plugin {plugin_id}: plugin {pid} depends on it")
                    return False

            self._plugin_states[plugin_id] = PluginState.UNLOADING

        try:
            plugin = self._plugins[plugin_id]
            
            # Cleanup plugin if it has a cleanup method
            if hasattr(plugin, "cleanup"):
                plugin.cleanup()

            with self._lock:
                del self._plugins[plugin_id]
                del self._plugin_states[plugin_id]
                del self._plugin_dependencies[plugin_id]
                del self._plugin_capabilities[plugin_id]
            
            logger.info(f"Unloaded plugin: {plugin_id}")
            return True
        except Exception as e:
            with self._lock:
                self._plugin_states[plugin_id] = PluginState.ERROR
            logger.error(f"Plugin unloading failed: {plugin_id}", exc_info=True)
            return False

    def get_plugin(self, plugin_id: PluginID) -> Optional[Any]:
        """Get a plugin by ID.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin or None

        Example:
            >>> plugin = manager.get_plugin("my_plugin")
        """
        with self._lock:
            return self._plugins.get(plugin_id)

    def has_plugin(self, plugin_id: PluginID) -> bool:
        """Check if a plugin is loaded.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if loaded, False otherwise

        Example:
            >>> if manager.has_plugin("my_plugin"):
            ...     print("Plugin is loaded")
        """
        with self._lock:
            return plugin_id in self._plugins

    def get_plugin_state(self, plugin_id: PluginID) -> Optional[PluginState]:
        """Get plugin state.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin state or None

        Example:
            >>> state = manager.get_plugin_state("my_plugin")
        """
        with self._lock:
            return self._plugin_states.get(plugin_id)

    def get_plugin_capabilities(self, plugin_id: PluginID) -> PluginCapabilities:
        """Get plugin capabilities.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin capabilities

        Example:
            >>> capabilities = manager.get_plugin_capabilities("my_plugin")
        """
        with self._lock:
            return self._plugin_capabilities.get(plugin_id, [])

    def activate_plugin(self, plugin_id: PluginID) -> bool:
        """Activate a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if activated, False otherwise

        Example:
            >>> activated = manager.activate_plugin("my_plugin")
        """
        with self._lock:
            if plugin_id not in self._plugins:
                return False
            
            if self._plugin_states[plugin_id] != PluginState.LOADED:
                return False

            self._plugin_states[plugin_id] = PluginState.ACTIVE
        
        logger.info(f"Activated plugin: {plugin_id}")
        return True

    def deactivate_plugin(self, plugin_id: PluginID) -> bool:
        """Deactivate a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if deactivated, False otherwise

        Example:
            >>> deactivated = manager.deactivate_plugin("my_plugin")
        """
        with self._lock:
            if plugin_id not in self._plugins:
                return False
            
            if self._plugin_states[plugin_id] != PluginState.ACTIVE:
                return False

            self._plugin_states[plugin_id] = PluginState.INACTIVE
        
        logger.info(f"Deactivated plugin: {plugin_id}")
        return True

    def list_plugins(self) -> List[PluginID]:
        """List all loaded plugins.

        Returns:
            List of plugin IDs

        Example:
            >>> plugins = manager.list_plugins()
        """
        with self._lock:
            return list(self._plugins.keys())

    def get_status(self) -> Dict[str, Any]:
        """Get plugin manager status.

        Returns:
            Plugin manager status

        Example:
            >>> status = manager.get_status()
        """
        with self._lock:
            return {
                "plugin_count": self.plugin_count,
                "plugins": self.list_plugins(),
                "states": {
                    pid: state.value for pid, state in self._plugin_states.items()
                },
            }


# Export
__all__ = [
    "PluginManager",
]
