import { signIn } from '@/lib/auth';
import { Github } from 'lucide-react';

export default function SignInPage() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-sm border border-border bg-bg-elevated p-8">
        <h1 className="font-mono text-2xl font-bold text-text-bright">deepwork</h1>
        <p className="mt-2 text-sm text-text-secondary">
          Sign in to access the research dashboard
        </p>
        <form
          action={async () => {
            'use server';
            await signIn('github', { redirectTo: '/dashboard' });
          }}
          className="mt-8"
        >
          <button
            type="submit"
            className="flex w-full items-center justify-center gap-3 bg-white px-4 py-3 font-mono text-sm font-medium text-black transition-colors hover:bg-neutral-200"
          >
            <Github className="h-5 w-5" />
            Continue with GitHub
          </button>
        </form>
      </div>
    </main>
  );
}
