import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="pt-20 text-center">
      <p className="text-text-muted text-sm">404</p>
      <p className="text-sm mt-2">
        <Link href="/">Back to home</Link>
      </p>
    </div>
  );
}
