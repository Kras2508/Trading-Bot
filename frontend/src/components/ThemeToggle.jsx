import React from "react";
import { useTheme } from "../context/ThemeContext";
import "./ThemeToggle.css";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      className="theme-toggle-btn"
      onClick={toggleTheme}
      title={`Switch to ${theme === "Sáng" ? "Tối" : "Sáng"} mode`}
      aria-label="Toggle theme"
    >
      {theme === "Sáng" ? (
        <i className="bi bi-moon-stars-fill"></i>
      ) : (
        <i className="bi bi-sun-fill"></i>
      )}
      <span className="ms-2">{theme === "Sáng" ? "Tối" : "Sáng"}</span>
    </button>
  );
}
