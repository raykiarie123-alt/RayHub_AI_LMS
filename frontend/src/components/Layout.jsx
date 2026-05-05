import Sidebar from './Sidebar';

export default function Layout({ children, title }) {
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto p-6">
          {title && (
            <h1 className="text-2xl font-bold text-slate-900 mb-6">{title}</h1>
          )}
          {children}
        </div>
      </main>
    </div>
  );
}