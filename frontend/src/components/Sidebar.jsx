import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  BookOpen,
  FileText,
  Bot,
  TrendingUp,
  Trophy,
  Users,
} from "lucide-react";

function Sidebar() {
  const location = useLocation();

  const links = [
    { label: "Dashboard", path: "/", icon: LayoutDashboard },
    { label: "Courses", path: "/courses", icon: BookOpen },
    { label: "Resources", path: "/resources", icon: FileText },
    { label: "AI Tutor", path: "/ai-tutor", icon: Bot },
    { label: "Progress", path: "/progress", icon: TrendingUp },
    { label: "Leaderboard", path: "/leaderboard", icon: Trophy },
    { label: "Community", path: "/community", icon: Users },
  ];

  return (
    <aside className="w-64 min-h-screen bg-white border-r border-slate-200 p-4">
      <h1 className="text-xl font-bold mb-6">RayHub</h1>

      <nav className="space-y-2">
        {links.map((item) => {
          const Icon = item.icon;
          const active = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
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
      </nav>
    </aside>
  );
}

export default Sidebar;