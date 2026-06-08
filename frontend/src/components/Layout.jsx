import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTheme } from "../contexts/ThemeContext";
import {
  LayoutDashboard,
  BookOpen,
  Brain,
  Users,
  FileText,
  Medal,
  TrendingUp,
  Calendar,
  CreditCard,
  History,
  Shield,
  LogOut,
  Menu,
  X,
  Zap,
  ChevronDown,
  ChevronUp,
  Sun,
  Moon,
} from "lucide-react";

export default function Layout({ children, title }) {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const navItems = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Courses", path: "/courses", icon: BookOpen },
    { name: "AI Tutor", path: "/ai-tutor", icon: Brain },
    { name: "Flashcards", path: "/flashcards", icon: CreditCard },
    { name: "Quiz History", path: "/quiz-history", icon: History },
    { name: "Resources", path: "/resources", icon: FileText },
    { name: "Study Plan", path: "/study-plan", icon: Calendar },
    { name: "Progress", path: "/progress", icon: TrendingUp },
    { name: "Leaderboard", path: "/leaderboard", icon: Medal },
    { name: "Community", path: "/community", icon: Users },
  ];

  if (user?.role === "admin" || user?.role === "tutor") {
    navItems.push({ name: "Admin", path: "/admin", icon: Shield });
  }

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : "??";

  const levelBadgeColor = {
    foundation: "bg-emerald-100 text-emerald-700",
    intermediate: "bg-amber-100 text-amber-700",
    advanced: "bg-rose-100 text-rose-700",
    "post-qualification": "bg-purple-100 text-purple-700",
  };

  const NavLinks = () => (
    <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
      {navItems.map((item) => {
        const Icon = item.icon;
        const active = location.pathname === item.path || location.pathname.startsWith(item.path + "/");

        return (
          <Link
            key={item.path}
            to={item.path}
            onClick={() => setSidebarOpen(false)}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-medium ${
              active
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            }`}
          >
            <Icon size={17} />
            <span>{item.name}</span>
          </Link>
        );
      })}
    </nav>
  );

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-30 w-64 bg-white border-r border-slate-200 flex flex-col transition-transform duration-200 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        {/* Logo */}
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Zap size={16} className="text-white" />
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 leading-none">RayHub</h1>
              <p className="text-xs text-slate-400 mt-0.5">AI CPA LMS</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded-lg hover:bg-slate-100"
          >
            <X size={16} className="text-slate-500" />
          </button>
        </div>

        <NavLinks />

        {/* User Section */}
        <div className="p-3 border-t border-slate-100">
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors"
            >
              <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                {initials}
              </div>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-medium text-slate-900 truncate">
                  {user?.full_name || "User"}
                </p>
                <span
                  className={`inline-block text-xs px-1.5 py-0.5 rounded-md font-medium ${
                    levelBadgeColor[user?.student_level] || "bg-slate-100 text-slate-600"
                  }`}
                >
                  {user?.student_level || "foundation"}
                </span>
              </div>
              {userMenuOpen ? (
                <ChevronUp size={14} className="text-slate-400 flex-shrink-0" />
              ) : (
                <ChevronDown size={14} className="text-slate-400 flex-shrink-0" />
              )}
            </button>

            {userMenuOpen && (
              <div className="absolute bottom-full left-0 right-0 mb-1 bg-white border border-slate-200 rounded-xl shadow-lg p-2 z-10">
                <div className="px-3 py-2 border-b border-slate-100 mb-1">
                  <p className="text-xs text-slate-500">Signed in as</p>
                  <p className="text-sm font-medium text-slate-900 truncate">{user?.email}</p>
                  <p className="text-xs text-indigo-600 capitalize">{user?.role}</p>
                </div>
                <button
                  onClick={() => { setUserMenuOpen(false); logout(); }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <LogOut size={14} />
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top header */}
        <header className="h-14 px-4 lg:px-6 flex items-center justify-between bg-white border-b border-slate-200 sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100"
            >
              <Menu size={18} className="text-slate-600" />
            </button>
            {title && (
              <h2 className="text-base font-semibold text-slate-900">{title}</h2>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              title={theme === "dark" ? "Switch to light" : "Switch to dark"}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
            >
              {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <div className="hidden sm:flex items-center gap-2">
              <div className="w-7 h-7 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                {initials}
              </div>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {user?.full_name?.split(" ")[0] || "User"}
              </span>
            </div>
            <button
              onClick={logout}
              title="Sign out"
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            >
              <LogOut size={15} />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
