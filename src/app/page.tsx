export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white px-6 font-sans">
      <main className="flex w-full max-w-lg flex-col items-center gap-8 text-center">
        <div className="flex flex-col gap-3">
          <span className="text-sm font-medium uppercase tracking-widest text-[#ff6b4a]">
            Profit Drive
          </span>
          <h1 className="text-3xl font-semibold tracking-tight text-zinc-900">
            Your field partner, riding shotgun.
          </h1>
          <p className="text-lg leading-7 text-zinc-600">
            Voice-first property scouting for Drive-for-Dollars agents. Pre-scanned zips,
            distress grades, and hands-free lead capture.
          </p>
        </div>
        <a
          href="/design-system/index.html"
          className="inline-flex h-12 items-center justify-center rounded-full bg-[#ff6b4a] px-6 text-base font-medium text-white transition-colors hover:bg-[#e85a3b]"
        >
          View design system
        </a>
      </main>
    </div>
  );
}
