import { BrowserRouter, Routes, Route } from "react-router-dom";
import BottomNav from "./components/BottomNav";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import History from "./pages/History";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-bg-primary pb-16">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/history" element={<History />} />
        </Routes>
        <BottomNav />
      </div>
    </BrowserRouter>
  );
}
