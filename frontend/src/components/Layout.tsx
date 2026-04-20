import { Outlet, Link } from "react-router";

export default function Layout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container flex h-14 items-center">
          <Link to="/" className="text-lg font-semibold">
            LLM Leaderboard
          </Link>
        </div>
      </header>
      <main className="container py-6">
        <Outlet />
      </main>
    </div>
  );
}
