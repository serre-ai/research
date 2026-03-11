import { appendFile, mkdir } from "node:fs/promises";
import { join, dirname } from "node:path";

const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024; // 50MB safety cap

export class TranscriptWriter {
  private readonly filePath: string;
  private dirCreated = false;
  private sizeLimitReached = false;
  private currentSize = 0;

  constructor(rootDir: string, projectName: string, sessionId: string) {
    const month = new Date().toISOString().slice(0, 7);
    const dir = join(rootDir, ".sessions", projectName, month);
    this.filePath = join(dir, `${sessionId}.jsonl`);
  }

  async write(message: unknown): Promise<void> {
    if (this.sizeLimitReached) return;

    try {
      await this.ensureDir();
      const line = JSON.stringify({ t: Date.now(), ...message as Record<string, unknown> }) + "\n";
      this.currentSize += Buffer.byteLength(line);

      if (this.currentSize > MAX_FILE_SIZE_BYTES) {
        this.sizeLimitReached = true;
        await appendFile(this.filePath, JSON.stringify({ t: Date.now(), type: "_transcript_truncated" }) + "\n", "utf-8");
        return;
      }

      await appendFile(this.filePath, line, "utf-8");
    } catch {
      // Never let transcript failure crash the session
    }
  }

  getFilePath(): string {
    return this.filePath;
  }

  private async ensureDir(): Promise<void> {
    if (this.dirCreated) return;
    await mkdir(dirname(this.filePath), { recursive: true });
    this.dirCreated = true;
  }
}
