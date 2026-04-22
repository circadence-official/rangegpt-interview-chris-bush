import { Outlet, Link, NavLink } from "react-router";
import { cn } from "@/lib/utils";

export default function Layout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container flex h-14 items-center gap-6">
          <Link to="/" className="text-lg font-semibold">
            LLM Leaderboard
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <NavItem to="/">Models</NavItem>
            <NavItem to="/leaderboard">Leaderboard</NavItem>
            <NavItem to="/compare">Compare</NavItem>
          </nav>
        </div>
      </header>
      <main className="container py-6">
        <Outlet />
      </main>
    </div>
  );
}

function NavItem({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <NavLink
      to={to}
      end={to === "/"}
      className={({ isActive }) =>
        cn(
          "transition-colors hover:text-foreground",
          isActive ? "text-foreground font-medium" : "text-muted-foreground",
        )
      }
    >
      {children}
    </NavLink>
  );
}
