import Link from 'next/link';
import { TuiBox } from '@/components/tui';

interface Post {
  date: string;
  title: string;
  href: string;
}

export function ActivityLog({ posts }: { posts: Post[] }) {
  return (
    <TuiBox title="LOG">
      <div className="space-y-2 font-mono text-xs">
        {posts.map((post) => (
          <div key={post.href} className="flex items-baseline gap-4">
            <span className="text-text-muted shrink-0 tabular-nums">{post.date}</span>
            <Link
              href={post.href}
              className="text-text-secondary hover:text-text-bright"
            >
              {post.title} {'\u2192'}
            </Link>
          </div>
        ))}
      </div>
    </TuiBox>
  );
}
