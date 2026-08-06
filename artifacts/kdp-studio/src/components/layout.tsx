import { ReactNode } from "react";
import { Link, useLocation } from "wouter";
import { BookOpen, Home, Palette, CheckSquare, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export function Layout({ children }: { children: ReactNode }) {
  const [location] = useLocation();

  const navItems = [
    { href: "/", label: "Dashboard", icon: Home },
    { href: "/books", label: "Book Library", icon: BookOpen },
    { href: "/palettes", label: "Palettes", icon: Palette },
    { href: "/tasks", label: "Tasks", icon: CheckSquare },
  ];

  return (
    <div className="min-h-[100dvh] flex flex-col md:flex-row bg-background">
      {/* Sidebar */}
      <aside className="w-full md:w-64 border-r border-border bg-sidebar shrink-0 flex flex-col">
        <div className="p-6">
          <Link href="/" className="flex items-center gap-3 no-underline outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-sm">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center text-primary-foreground shadow-sm">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h1 className="font-serif font-semibold text-lg leading-tight text-sidebar-foreground">Studio</h1>
              <p className="text-[10px] uppercase tracking-widest text-sidebar-foreground/60 font-sans font-medium">Bright Mindful</p>
            </div>
          </Link>
        </div>

        <nav className="flex-1 px-4 pb-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = location === item.href || (item.href !== "/" && location.startsWith(item.href));
            const Icon = item.icon;
            
            return (
              <Link 
                key={item.href} 
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  isActive 
                    ? "bg-primary/10 text-primary" 
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                )}
              >
                <Icon className={cn("w-4 h-4", isActive ? "text-primary" : "opacity-70")} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto p-4 md:p-8 lg:p-12">
           <div className="max-w-[1440px] mx-auto w-full">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
