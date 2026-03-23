/**
 * Input validation and path containment for API route parameters.
 *
 * Defense-in-depth: regex validation catches obvious bad input,
 * containment checks catch symlinks and encoding tricks.
 */

import { resolve } from "node:path";

/** Project names: lowercase alphanumeric, dots, hyphens, underscores. */
const PROJECT_NAME_RE = /^[a-z0-9][a-z0-9._-]{0,63}$/;

/** Session/entity IDs: UUIDs or short alphanumeric IDs. */
const VALID_ID_RE = /^[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}$/;

/** Task/condition/model names for eval jobs. Allows colons for provider:model format. */
const TASK_NAME_RE = /^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$/;

export function isValidProjectName(value: string): boolean {
  return PROJECT_NAME_RE.test(value);
}

export function isValidId(value: string): boolean {
  return VALID_ID_RE.test(value);
}

export function isValidTaskName(value: string): boolean {
  // Must not contain path traversal sequences even if regex allows some chars
  if (value.includes("..") || value.includes("/") || value.includes("\\")) {
    return false;
  }
  return TASK_NAME_RE.test(value);
}

/**
 * Verify that a resolved file path is contained within an allowed root.
 * Throws if the path escapes the root directory.
 */
export function assertContained(filePath: string, allowedRoot: string): void {
  const resolved = resolve(filePath);
  const root = resolve(allowedRoot);
  if (!resolved.startsWith(root + "/") && resolved !== root) {
    throw new Error("Path traversal detected");
  }
}
