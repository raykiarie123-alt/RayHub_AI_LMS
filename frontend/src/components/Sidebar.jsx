import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import {
  LayoutDashboard,
  BookOpen,
  FileText,
  Bot,
  TrendingUp,
  Trophy,
  Users,
  Menu,
  X,
  LogOut,
  Calendar,
  Shield,
} from "lucide-react";

function Sidebar() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout } = useAuth();

  const links = [
    { label: "Dashboard", path: "/", icon: LayoutDashboard },
    { label: "Courses", path: "/courses", icon: BookOpen },
    { label: "Resources", path: "/resources", icon: FileText },
    { label: "AI Tutor", path: "/ai-tutor", icon: Bot },
    { label: "Progress", path: "/progress", icon: TrendingUp },
    { label: "Leaderboard", path: "/leaderboard", icon: Trophy },
    { label: "Community", path: "/community", icon: Users },
    { label: "Study Plan", path: "/study-plan", icon: Calendar },
  ];

  const adminLinks = [
    { label: "Admin", path: "/admin", icon: Shield },
  ];

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md border border-slate-200"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 z-40 w-64 min-h-screen bg-white border-r border-slate-200 p-4 transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <h1 className="text-xl font-bold mb-6">RayHub</h1>

        <nav className="space-y-2 mb-6">
          {links.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                  active
                    ? "bg-blue-50 text-blue-700 font-semibold"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}

          {user?.role === 'admin' && (
            <>
              <div className="border-t border-slate-200 my-3"></div>
              {adminLinks.map((item) => {
                const Icon = item.icon;
                const active = location.pathname === item.path;

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                      active
                        ? "bg-purple-50 text-purple-700 font-semibold"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <Icon size={18} />
                    {item.label}
                  </Link>
                );
              })}
            </>
          )}
        </nav>

        {/* User info & logout */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="border-t border-slate-200 pt-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-semibold text-sm">
                {user?.full_name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">{user?.full_name || 'User'}</p>
                <p className="text-xs text-slate-500 truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-600 hover:bg-red-50 hover:text-red-600 rounded-lg transition-colors"
            >
              <LogOut size={16} />
              Sign out
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;