// Minimal YAML handling for the orchestrator.
// The orchestrator operates on status.yaml files using simple serialization.
// For full YAML parsing, the CLI uses the `yaml` npm package.

export function parse(content: string): Record<string, unknown> {
  // Try JSON first (for programmatically-written files)
  try {
    return JSON.parse(content);
  } catch {
    // Fall through to basic YAML parsing
  }

  // Basic YAML parser for simple key-value structures.
  // Handles flat keys, arrays (- item), and nested objects (indented keys).
  // For complex YAML, use the `yaml` npm package in @deepwork/cli.
  const result: Record<string, unknown> = {};
  const lines = content.split("\n");
  let currentKey = "";
  let currentArray: string[] | null = null;

  for (const line of lines) {
    // Skip comments and empty lines
    if (line.trim().startsWith("#") || line.trim() === "") {
      if (currentArray && currentKey) {
        result[currentKey] = currentArray;
        currentArray = null;
        currentKey = "";
      }
      continue;
    }

    // Array item
    if (line.match(/^\s+-\s+/) && currentKey) {
      if (!currentArray) currentArray = [];
      currentArray.push(line.replace(/^\s+-\s+/, "").trim());
      continue;
    }

    // Save pending array
    if (currentArray && currentKey) {
      result[currentKey] = currentArray;
      currentArray = null;
    }

    // Key-value pair
    const match = line.match(/^(\w[\w_]*)\s*:\s*(.*)$/);
    if (match) {
      currentKey = match[1];
      const value = match[2].trim().replace(/^["']|["']$/g, "");
      if (value === "") {
        // Could be start of array or nested object
        continue;
      }
      // Type coercion
      if (value === "true") result[currentKey] = true;
      else if (value === "false") result[currentKey] = false;
      else if (/^\d+$/.test(value)) result[currentKey] = parseInt(value, 10);
      else if (/^\d+\.\d+$/.test(value))
        result[currentKey] = parseFloat(value);
      else result[currentKey] = value;
      currentKey = "";
    }
  }

  // Save any trailing array
  if (currentArray && currentKey) {
    result[currentKey] = currentArray;
  }

  return result;
}

export function stringify(data: Record<string, unknown>): string {
  return JSON.stringify(data, null, 2) + "\n";
}
