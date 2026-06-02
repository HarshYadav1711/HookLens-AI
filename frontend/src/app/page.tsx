export default function Home() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-[var(--border)]">
        <div className="max-w-3xl mx-auto px-6 py-8">
          <h1 className="text-2xl font-bold tracking-tight">
            Hook<span className="text-accent">Lens</span> AI
          </h1>
          <p className="text-sm text-[var(--muted)] mt-2">
            Compare a YouTube video and an Instagram Reel with evidence-backed analysis.
          </p>
        </div>
      </header>

      <section className="max-w-3xl mx-auto px-6 py-10 space-y-6">
        <div className="space-y-4">
          <label className="block space-y-2">
            <span className="text-sm text-[var(--muted)]">YouTube URL</span>
            <input
              type="url"
              name="youtube_url"
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40"
              readOnly={false}
            />
          </label>
          <label className="block space-y-2">
            <span className="text-sm text-[var(--muted)]">Instagram Reel URL</span>
            <input
              type="url"
              name="instagram_url"
              placeholder="https://www.instagram.com/reel/..."
              className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40"
            />
          </label>
        </div>

        <button
          type="button"
          disabled
          className="rounded-lg bg-accent px-6 py-3 text-sm font-medium text-white opacity-50 cursor-not-allowed"
        >
          Analyze
        </button>
        <p className="text-xs text-[var(--muted)]">Analysis will be enabled in a future release.</p>
      </section>
    </main>
  );
}
