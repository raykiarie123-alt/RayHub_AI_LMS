import Sidebar from "./components/Sidebar";
import DashboardPage from "./pages/DashboardPage";

function App() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <DashboardPage />
      </div>
    </div>
  );
}

export default App;