import { useLocation, useNavigate } from "react-router-dom";

const tabs = [
  { path: "/", label: "Обзор", icon: "\ud83d\udcca" },
  { path: "/analytics", label: "Аналитика", icon: "\ud83d\udcc8" },
  { path: "/history", label: "История", icon: "\ud83d\udccb" },
];

export default function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-bg-secondary/95 backdrop-blur-md border-t border-white/5 z-50">
      <div className="flex justify-around items-center h-14">
        {tabs.map((tab) => {
          const active = location.pathname === tab.path;
          return (
            <button
              key={tab.path}
              onClick={() => navigate(tab.path)}
              className={`flex flex-col items-center gap-0.5 px-4 py-1.5 rounded-lg transition-colors ${
                active ? "text-accent-primary" : "text-text-muted"
              }`}
            >
              <span className="text-lg">{tab.icon}</span>
              <span className="text-[10px] font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
