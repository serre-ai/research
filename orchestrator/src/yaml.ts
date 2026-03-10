import { parse as yamlParse, stringify as yamlStringify } from "yaml";

export function parse(content: string): Record<string, unknown> {
  return yamlParse(content) as Record<string, unknown>;
}

export function stringify(data: Record<string, unknown>): string {
  return yamlStringify(data);
}
