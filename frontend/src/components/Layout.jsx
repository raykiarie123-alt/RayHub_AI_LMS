import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  BookOpen,
  Brain,
  Users,
  FileText,
  Medal,
} from "lucide-react";

export default function Layout({ children }) {
  const location = useLocation();

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Courses", path: "/courses", icon: BookOpen },
    { name: "AI Tutor", path: "/ai-tutor", icon: Brain },
    { name: "Resources", path: "/resources", icon: FileText },
    { name: "Leaderboard", path: "/leaderboard", icon: Medal },
    { name: "Community", path: "/community", icon: Users },
  ];

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="px-6 py-5 border-b border-slate-200">
          <h1 className="text-2xl font-bold text-indigo-600">RayHub</h1>
          <p className="text-xs text-slate-500 mt-1">
            AI-powered CPA LMS
          </p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition ${
                  active
                    ? "bg-indigo-600 text-white"
                    : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon size={18} />
                <span className="text-sm font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <header className="h-16 px-6 flex items-center justify-between bg-white border-b border-slate-200">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Welcome to RayHub
            </h2>
            <p className="text-xs text-slate-500">
              Your AI-powered CPA learning platform
            </p>
          </div>
        </header>

        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}