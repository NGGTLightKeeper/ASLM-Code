# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

from Settings import settings as runtime_settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_METADATA_PATH = BASE_DIR / "Tools" / "model_runtime_metadata.json"
RUNTIME_CORE_PATH = BASE_DIR / "Settings" / "runtime.json"

# Default core knobs for the run engine when no override file is present.
RUNTIME_CORE_DEFAULTS: dict[str, Any] = {
    "request_timeout_s": 180.0,
    "total_run_timeout_s": None,
    "max_tool_rounds": 40,
    "max_subagents": 4,
    "default_subagent_engine": None,
    "default_subagent_model": None,
    "default_backend": "thread",
}


# Read engine selection, endpoints, and credentials from the shared settings store.
class SettingsSource:

    name = "settings"

    # Return the effective backend engine the user is currently driving.
    def active_engine(self) -> str:
        return runtime_settings.get_effective_backend_engine()

    # Return the configured facade engine name.
    def facade_engine(self) -> str:
        return runtime_settings.get_llm_engine()

    # Return the backend sub-engine resolved behind the facade.
    def sub_engine(self) -> str:
        return runtime_settings.get_llm_sub_engine()

    # Return the resolved base URL for one engine.
    def engine_url(self, engine: str) -> str:
        try:
            return runtime_settings.get_engine_url(engine)
        except Exception:
            logger.debug("Failed to resolve engine url for %s", engine, exc_info=True)
            return ""

    # Return the resolved API key for one engine.
    def engine_api_key(self, engine: str) -> str:
        try:
            return runtime_settings.get_engine_api_key(engine)
        except Exception:
            logger.debug("Failed to resolve engine api key for %s", engine, exc_info=True)
            return ""

    # Return per-engine runtime settings shared with the frontend.
    def runtime_engine_settings(self) -> dict[str, Any]:
        try:
            data = runtime_settings.get_runtime_engine_settings()
        except Exception:
            logger.debug("Failed to read runtime engine settings", exc_info=True)
            return {}
        return data if isinstance(data, dict) else {}

    # Return the list of engine ids the user has enabled.
    def enabled_engines(self) -> list[str]:
        try:
            return list(runtime_settings.get_enabled_engine_ids())
        except Exception:
            logger.debug("Failed to read enabled engine ids", exc_info=True)
            return []


# Read active model, capabilities, and limits from the model metadata catalog.
class ModelMetadataSource:

    name = "model_metadata"

    # Bind the source to the metadata file and prepare its mtime cache.
    def __init__(self, path: Path = MODEL_METADATA_PATH) -> None:
        self._path = path
        self._lock = threading.RLock()
        self._cache: dict[str, Any] = {}
        self._cache_mtime_ns: int | None = None

    # Return the parsed metadata document, refreshing only when the file changes.
    def _load(self) -> dict[str, Any]:
        try:
            mtime_ns = self._path.stat().st_mtime_ns
        except OSError:
            return {}

        with self._lock:
            if mtime_ns == self._cache_mtime_ns and self._cache:
                return self._cache

            try:
                parsed = json.loads(self._path.read_text(encoding="utf-8") or "{}")
            except (OSError, json.JSONDecodeError):
                logger.debug("Failed to read model metadata from %s", self._path, exc_info=True)
                parsed = {}

            self._cache = parsed if isinstance(parsed, dict) else {}
            self._cache_mtime_ns = mtime_ns
            return self._cache

    # Build the catalog key used to look up one engine/model pair.
    def _model_key(self, engine: str, model: str) -> str:
        return f"{str(engine or '').strip()}:{str(model or '').strip()}"

    # Return the recorded active engine and model selection.
    def active(self) -> dict[str, str]:
        active = self._load().get("active")
        if not isinstance(active, dict):
            return {"engine": "", "model": ""}
        return {
            "engine": str(active.get("engine") or "").strip(),
            "model": str(active.get("model") or "").strip(),
        }

    # Return the raw catalog entry for one engine/model pair.
    def model_entry(self, engine: str, model: str) -> dict[str, Any]:
        models = self._load().get("models")
        if not isinstance(models, dict):
            return {}
        entry = models.get(self._model_key(engine, model))
        return entry if isinstance(entry, dict) else {}

    # Return the capability flags recorded for one engine/model pair.
    def capabilities(self, engine: str, model: str) -> dict[str, Any]:
        caps = self.model_entry(engine, model).get("capabilities")
        return caps if isinstance(caps, dict) else {}

    # Return the limit values recorded for one engine/model pair.
    def limits(self, engine: str, model: str) -> dict[str, Any]:
        limits = self.model_entry(engine, model).get("limits")
        return limits if isinstance(limits, dict) else {}


# Read the run engine's own tunable knobs, layered over built-in defaults.
class RuntimeCoreSource:

    name = "runtime_core"

    # Bind the source to the optional override file.
    def __init__(self, path: Path = RUNTIME_CORE_PATH) -> None:
        self._path = path

    # Return the merged core settings (defaults overlaid with the override file).
    def values(self) -> dict[str, Any]:
        merged = dict(RUNTIME_CORE_DEFAULTS)
        try:
            if self._path.exists():
                parsed = json.loads(self._path.read_text(encoding="utf-8") or "{}")
                if isinstance(parsed, dict):
                    merged.update(parsed)
        except (OSError, json.JSONDecodeError):
            logger.debug("Failed to read runtime core settings from %s", self._path, exc_info=True)
        return merged

    # Return one core setting value with a fallback default.
    def get(self, key: str, default: Any = None) -> Any:
        return self.values().get(key, default)
