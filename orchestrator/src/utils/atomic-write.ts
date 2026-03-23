import { writeFile, rename, mkdir } from "node:fs/promises";
import { join, dirname } from "node:path";
import { randomBytes } from "node:crypto";

/**
 * Atomic file write using write-to-temp-then-rename pattern.
 * Prevents partial writes and corruption during crashes.
 */
export async function atomicWriteFile(
  path: string,
  data: string,
  options?: { encoding?: BufferEncoding },
): Promise<void> {
  const dir = dirname(path);
  await mkdir(dir, { recursive: true });

  const tempPath = join(dir, `.${randomBytes(8).toString("hex")}.tmp`);

  try {
    await writeFile(tempPath, data, options?.encoding ?? "utf-8");
    await rename(tempPath, path);
  } catch (err) {
    // Clean up temp file on failure
    try {
      await import("node:fs/promises").then((fs) => fs.unlink(tempPath));
    } catch {
      // Already deleted or doesn't exist
    }
    throw err;
  }
}

/**
 * Atomic append to JSONL file using read-modify-write pattern.
 * Not ideal for high-throughput, but safe for low-frequency daemon writes.
 */
export async function atomicAppendJsonl(
  path: string,
  line: string,
): Promise<void> {
  const { readFile } = await import("node:fs/promises");
  const dir = dirname(path);
  await mkdir(dir, { recursive: true });

  let existing = "";
  try {
    existing = await readFile(path, "utf-8");
  } catch {
    // File doesn't exist yet
  }

  const updated = existing + (existing && !existing.endsWith("\n") ? "\n" : "") + line + "\n";
  await atomicWriteFile(path, updated);
}
