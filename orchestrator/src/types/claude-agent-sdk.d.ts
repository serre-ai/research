declare module "@anthropic-ai/claude-agent-sdk" {
  export interface QueryOptions {
    prompt: string;
    options: {
      cwd: string;
      allowedTools: string[];
      permissionMode: string;
      maxTurns: number;
      abortController: AbortController;
      systemPrompt: {
        type: string;
        preset: string;
        append: string;
      };
    };
  }

  export function query(options: QueryOptions): AsyncIterable<any>;
}
