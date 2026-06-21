# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import logging
from typing import Any

from Runtime.config.sources import (
    ModelMetadataSource,
    RuntimeCoreSource,
    SettingsSource,
)
from Runtime.types import (
    ConfigError,
    EngineConfig,
    LimitsSummary,
    ResolvedConfig,
    RunLimits,
    RunOverrides,
)

logger = logging.getLogger(__name__)


# Single read-only entry point that aggregates every configuration source.
class ConfigAggregator:

    # Compose the aggregator from its backing sources.
    def __init__(
        self,
        settings_source: SettingsSource | None = None,
        metadata_source: ModelMetadataSource | None = None,
        core_source: RuntimeCoreSource | None = None,
    ) -> None:
        self.settings = settings_source or SettingsSource()
        self.metadata = metadata_source or ModelMetadataSource()
        self.core = core_source or RuntimeCoreSource()

    # Return the effective backend engine the user is currently driving.
    def active_engine(self) -> str:
        return self.settings.active_engine()

    # Return the active model for one engine, defaulting to the current engine.
    def active_model(self, engine: str | None = None) -> str:
        engine = str(engine or self.active_engine()).strip()
        active = self.metadata.active()
        if active.get("model") and (not engine or active.get("engine") == engine):
            return active["model"]
        return ""

    # Return the list of engine ids the user has enabled.
    def available_engines(self) -> list[str]:
        return self.settings.enabled_engines()

    # Return the capability flags for one engine/model pair.
    def model_caps(self, engine: str, model: str) -> dict[str, Any]:
        return self.metadata.capabilities(engine, model)

    # Return the limit values for one engine/model pair.
    def model_limits(self, engine: str, model: str) -> dict[str, Any]:
        return self.metadata.limits(engine, model)

    # Build the frozen model-capability summary for one engine/model pair.
    def _limits_summary(self, engine: str, model: str) -> LimitsSummary:
        caps = self.model_caps(engine, model)
        limits = self.model_limits(engine, model)
        return LimitsSummary(
            context_window=limits.get("context_window"),
            max_output_tokens=limits.get("max_output_tokens"),
            supports_tools=bool(caps.get("tools", False)),
            supports_vision=bool(caps.get("vision", False)),
            supports_thinking=bool(caps.get("thinking", False)),
            supports_files=bool(caps.get("files", False)),
        )

    # Build the frozen engine coordinates for one engine.
    def _engine_config(self, engine: str, sub_engine: str | None) -> EngineConfig:
        return EngineConfig(
            engine=engine,
            sub_engine=sub_engine,
            base_url=self.settings.engine_url(engine),
            api_key=self.settings.engine_api_key(engine),
            extra=self.settings.runtime_engine_settings(),
        )

    # Merge built-in limits with the core source and per-run overrides.
    def _run_limits(self, overrides: RunOverrides | None) -> RunLimits:
        base = RunLimits.from_dict(
            {
                "request_timeout_s": self.core.get("request_timeout_s"),
                "total_run_timeout_s": self.core.get("total_run_timeout_s"),
                "max_tool_rounds": self.core.get("max_tool_rounds"),
                "max_subagents": self.core.get("max_subagents"),
            }
        )
        if overrides and overrides.limits:
            return RunLimits.from_dict({**base.as_dict(), **overrides.limits})
        return base

    # Freeze defaults and overrides into one validated run configuration.
    def resolve(self, overrides: RunOverrides | None = None) -> ResolvedConfig:
        overrides = overrides or RunOverrides()

        engine = str(overrides.engine or self.active_engine()).strip()
        if not engine:
            raise ConfigError("No active engine is configured for this run.")

        sub_engine = overrides.sub_engine or self.settings.sub_engine()
        model = str(overrides.model or self.active_model(engine)).strip()
        if not model:
            raise ConfigError(f"No model is selected for engine '{engine}'.")

        summary = self._limits_summary(engine, model)
        # Only reject a tools-incapable model when the catalog is explicit about it.
        entry = self.metadata.model_entry(engine, model)
        if entry and not summary.supports_tools:
            raise ConfigError(
                f"Model '{engine}:{model}' does not support tools and cannot run as an agent."
            )

        return ResolvedConfig(
            engine=self._engine_config(engine, sub_engine),
            model=model,
            limits=self._run_limits(overrides),
            model_limits=summary,
            tool_server_ids=list(overrides.tool_server_ids or []),
            options=dict(overrides.options or {}),
        )


# Print a resolved snapshot of the current active configuration for smoke testing.
def main() -> None:
    aggregator = ConfigAggregator()
    print(f"active_engine = {aggregator.active_engine()!r}")
    print(f"active_model  = {aggregator.active_model()!r}")
    print(f"engines       = {aggregator.available_engines()}")
    try:
        resolved = aggregator.resolve()
    except ConfigError as exc:
        print(f"resolve() failed: {exc}")
        return

    import json

    print("resolved =")
    print(json.dumps(resolved.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
