import { readFile, writeFile, readdir, mkdir } from "node:fs/promises";
import { join } from "node:path";

export interface DailyDigest {
  date: string;
  digest: string;
  key_events: string[];
  filed_by: string;
  created_at: string;
}

const RETENTION_DAYS = 30;

export class DigestStore {
  private readonly digestsDir: string;
  private dirCreated = false;

  constructor(rootDir: string) {
    this.digestsDir = join(rootDir, ".logs", "digests");
  }

  async save(digest: Omit<DailyDigest, "created_at">): Promise<DailyDigest> {
    await this.ensureDir();
    const entry: DailyDigest = {
      ...digest,
      created_at: new Date().toISOString(),
    };
    const filePath = join(this.digestsDir, `${digest.date}.json`);
    await writeFile(filePath, JSON.stringify(entry, null, 2), "utf-8");
    await this.pruneOld();
    return entry;
  }

  async getLatest(): Promise<DailyDigest | null> {
    await this.ensureDir();
    try {
      const files = await readdir(this.digestsDir);
      const jsonFiles = files.filter((f) => f.endsWith(".json")).sort().reverse();
      if (jsonFiles.length === 0) return null;
      const content = await readFile(join(this.digestsDir, jsonFiles[0]), "utf-8");
      return JSON.parse(content) as DailyDigest;
    } catch {
      return null;
    }
  }

  async getByDate(date: string): Promise<DailyDigest | null> {
    try {
      const content = await readFile(join(this.digestsDir, `${date}.json`), "utf-8");
      return JSON.parse(content) as DailyDigest;
    } catch {
      return null;
    }
  }

  async listDates(): Promise<string[]> {
    await this.ensureDir();
    try {
      const files = await readdir(this.digestsDir);
      return files
        .filter((f) => f.endsWith(".json"))
        .map((f) => f.replace(".json", ""))
        .sort()
        .reverse();
    } catch {
      return [];
    }
  }

  private async pruneOld(): Promise<void> {
    try {
      const files = await readdir(this.digestsDir);
      const jsonFiles = files.filter((f) => f.endsWith(".json")).sort();
      if (jsonFiles.length <= RETENTION_DAYS) return;

      const { unlink } = await import("node:fs/promises");
      const toRemove = jsonFiles.slice(0, jsonFiles.length - RETENTION_DAYS);
      for (const f of toRemove) {
        await unlink(join(this.digestsDir, f));
      }
    } catch {
      // Best-effort cleanup
    }
  }

  private async ensureDir(): Promise<void> {
    if (this.dirCreated) return;
    await mkdir(this.digestsDir, { recursive: true });
    this.dirCreated = true;
  }
}
