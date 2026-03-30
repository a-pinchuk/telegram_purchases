import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
  tg.setHeaderColor("#0f0f0f");
  tg.setBackgroundColor("#0f0f0f");
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
