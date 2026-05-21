import { useEffect, useState } from "react";

export default function ThemeSelector() {
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");

  useEffect(() => {
    const root = document.documentElement;

    root.classList.remove("light", "dark");

    if (theme === "system") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

      if (prefersDark) {
        root.classList.add("dark");
      }
    } else {
      root.classList.add(theme);
    }

    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <select
      value={theme}
      onChange={(e) => setTheme(e.target.value)}
      className="px-3 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 text-sm focus:outline-none"
    >
      <option value="light">Light Theme</option>
      <option value="dark">Dark Theme</option>
      <option value="system">System Theme</option>
    </select>
  );
}