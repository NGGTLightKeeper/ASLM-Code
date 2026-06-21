# Copyright NGGT.LightKeeper. All Rights Reserved.

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# Raised when configuration cannot be resolved into a valid run context.
class ConfigError(ValueError):
    pass


# Lifecycle states a single run can be in.
class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ABORTED = "aborted"
    FAILED = "failed"


# Frozen engine coordinates resolved for one run.
@dataclass(frozen=True)
class EngineConfig:
    engine: str
    sub_engine: str | None = None
    base_url: str = ""
    api_key: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    # Return a JSON-serializable representation of the engine config.
    def as_dict(self) -> dict[str, Any]:
        return {
            "engine": self.engine,
            "sub_engine": self.sub_engine,
            "base_url": self.base_url,
            "api_key": self.api_key,
            "extra": dict(self.extra),
        }

    # Rebuild an engine config from a serialized mapping.
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EngineConfig":
        data = data or {}
        return cls(
            engine=str(data.get("engine") or ""),
            sub_engine=data.get("sub_engine"),
            base_url=str(data.get("base_url") or ""),
            api_key=str(data.get("api_key") or ""),
            extra=dict(data.get("extra") or {}),
        )


# Operator-imposed limits that the run core enforces during execution.
@dataclass(frozen=True)
class RunLimits:
    request_timeout_s: float = 180.0
    total_run_timeout_s: float | None = None
    max_tool_rounds: int = 40
    max_subagents: int = 4

    # Return a JSON-serializable representation of the run limits.
    def as_dict(self) -> dict[str, Any]:
        return {
            "request_timeout_s": self.request_timeout_s,
            "total_run_timeout_s": self.total_run_timeout_s,
            "max_tool_rounds": self.max_tool_rounds,
            "max_subagents": self.max_subagents,
        }

    # Rebuild run limits from a serialized mapping.
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunLimits":
        data = data or {}
        defaults = cls()
        return cls(
            request_timeout_s=float(data.get("request_timeout_s", defaults.request_timeout_s)),
            total_run_timeout_s=data.get("total_run_timeout_s", defaults.total_run_timeout_s),
            max_tool_rounds=int(data.get("max_tool_rounds", defaults.max_tool_rounds)),
            max_subagents=int(data.get("max_subagents", defaults.max_subagents)),
        )


# Minimal summary of what one model is physically capable of.
@dataclass(frozen=True)
class LimitsSummary:
    context_window: int | None = None
    max_output_tokens: int | None = None
    supports_tools: bool = False
    supports_vision: bool = False
    supports_thinking: bool = False
    supports_files: bool = False

    # Return a JSON-serializable representation of the limits summary.
    def as_dict(self) -> dict[str, Any]:
        return {
            "context_window": self.context_window,
            "max_output_tokens": self.max_output_tokens,
            "supports_tools": self.supports_tools,
            "supports_vision": self.supports_vision,
            "supports_thinking": self.supports_thinking,
            "supports_files": self.supports_files,
        }

    # Rebuild a limits summary from a serialized mapping.
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LimitsSummary":
        data = data or {}
        return cls(
            context_window=data.get("context_window"),
            max_output_tokens=data.get("max_output_tokens"),
            supports_tools=bool(data.get("supports_tools", False)),
            supports_vision=bool(data.get("supports_vision", False)),
            supports_thinking=bool(data.get("supports_thinking", False)),
            supports_files=bool(data.get("supports_files", False)),
        )


# Frozen, fully-resolved execution context carried by a run across any backend.
@dataclass(frozen=True)
class ResolvedConfig:
    engine: EngineConfig
    model: str
    limits: RunLimits
    model_limits: LimitsSummary
    tool_server_ids: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)

    # Return a JSON-serializable representation of the resolved config.
    def as_dict(self) -> dict[str, Any]:
        return {
            "engine": self.engine.as_dict(),
            "model": self.model,
            "limits": self.limits.as_dict(),
            "model_limits": self.model_limits.as_dict(),
            "tool_server_ids": list(self.tool_server_ids),
            "options": dict(self.options),
        }

    # Rebuild a resolved config from a serialized mapping.
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResolvedConfig":
        data = data or {}
        return cls(
            engine=EngineConfig.from_dict(data.get("engine") or {}),
            model=str(data.get("model") or ""),
            limits=RunLimits.from_dict(data.get("limits") or {}),
            model_limits=LimitsSummary.from_dict(data.get("model_limits") or {}),
            tool_server_ids=list(data.get("tool_server_ids") or []),
            options=dict(data.get("options") or {}),
        )


# Per-run overrides layered on top of the resolved defaults at start time.
@dataclass
class RunOverrides:
    engine: str | None = None
    sub_engine: str | None = None
    model: str | None = None
    limits: dict[str, Any] | None = None
    tool_server_ids: list[str] | None = None
    options: dict[str, Any] | None = None


# Serializable description of one run, the only input that crosses a backend.
@dataclass
class RunSpec:
    resolved: ResolvedConfig
    messages: list[dict[str, Any]] = field(default_factory=list)
    system_prompt: str = ""
    chat_id: str = ""
    parent_run_id: str | None = None

    # Return a JSON-serializable representation of the run spec.
    def as_dict(self) -> dict[str, Any]:
        return {
            "resolved": self.resolved.as_dict(),
            "messages": list(self.messages),
            "system_prompt": self.system_prompt,
            "chat_id": self.chat_id,
            "parent_run_id": self.parent_run_id,
        }

    # Rebuild a run spec from a serialized mapping.
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunSpec":
        data = data or {}
        return cls(
            resolved=ResolvedConfig.from_dict(data.get("resolved") or {}),
            messages=list(data.get("messages") or []),
            system_prompt=str(data.get("system_prompt") or ""),
            chat_id=str(data.get("chat_id") or ""),
            parent_run_id=data.get("parent_run_id"),
        )


# One append-only event emitted by a run worker and replayed to subscribers.
@dataclass
class RunEvent:
    seq: int
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)

    # Return a JSON-serializable representation of the run event.
    def as_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "type": self.type,
            "payload": dict(self.payload),
            "ts": self.ts,
        }

    # Rebuild a run event from a serialized mapping.
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunEvent":
        data = data or {}
        return cls(
            seq=int(data.get("seq") or 0),
            type=str(data.get("type") or ""),
            payload=dict(data.get("payload") or {}),
            ts=float(data.get("ts") or 0.0),
        )


# Metadata snapshot describing the current state of one run.
@dataclass
class RunInfo:
    run_id: str
    status: RunStatus
    spec: RunSpec
    last_seq: int = 0
    error: str | None = None

    # Return a JSON-serializable representation of the run info.
    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status.value,
            "spec": self.spec.as_dict(),
            "last_seq": self.last_seq,
            "error": self.error,
        }

    # Rebuild run info from a serialized mapping.
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunInfo":
        data = data or {}
        return cls(
            run_id=str(data.get("run_id") or ""),
            status=RunStatus(str(data.get("status") or RunStatus.PENDING.value)),
            spec=RunSpec.from_dict(data.get("spec") or {}),
            last_seq=int(data.get("last_seq") or 0),
            error=data.get("error"),
        )
