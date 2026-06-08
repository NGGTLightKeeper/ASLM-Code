// Copyright NGGT.LightKeeper. All Rights Reserved.

import { aslmChatAdapter } from './aslm-chat.js';
import { googleGenAiAdapter } from './google-genai.js';
import { lmsAdapter } from './lms.js';
import { ollamaServiceAdapter } from './ollama-service.js';
import { openAiAdapter } from './openai.js';

const ENGINE_ADAPTERS = [
  aslmChatAdapter,
  ollamaServiceAdapter,
  lmsAdapter,
  openAiAdapter,
  googleGenAiAdapter
];

const adaptersById = new Map(
  ENGINE_ADAPTERS.map(function mapAdapter(adapter) {
    return [adapter.id, adapter];
  })
);

const aliasMap = new Map();

ENGINE_ADAPTERS.forEach(function registerAdapter(adapter) {
  aliasMap.set(adapter.id, adapter.id);

  (adapter.aliases || []).forEach(function registerAlias(alias) {
    aliasMap.set(String(alias || '').trim().toLowerCase(), adapter.id);
  });
});

// Engine lookup helpers.
// Normalize any engine alias into a canonical engine id.
export function normalizeEngineValue(engine) {
  const normalized = String(engine || '').trim().toLowerCase();
  return aliasMap.get(normalized) || normalized || aslmChatAdapter.id;
}

// Resolve one engine adapter from the registry.
export function getEngineAdapter(engine) {
  return adaptersById.get(normalizeEngineValue(engine)) || aslmChatAdapter;
}

// Resolve the backend engine used for model parameters and presets.
export function resolveParameterEngine(facadeEngine, subEngine) {
  const facade = normalizeEngineValue(facadeEngine);
  if (facade === aslmChatAdapter.id) {
    return normalizeEngineValue(subEngine || 'ollama-service');
  }
  return facade;
}

// Report whether the engine supports presets.
export function isPresetCapableEngine(engine) {
  return !!getEngineAdapter(engine).supportsPresets;
}
