import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { getRole } from "../utils/auth";

export default function MainMenu() {
  const navigate = useNavigate();
  const role = getRole();

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  // Якщо не авторизований
  if (!role) return null;

  return (
    <nav style={{
      display: "flex",
      gap: 20,
      padding: 16,
      background: "#f0f0f0",
      marginBottom: 24,
      alignItems: "center"
    }}>
      {/* Для всіх ролей */}
      <Link to="/customers">Клієнти</Link>
      <Link to="/cars">Автомобілі</Link>
      <Link to="/services">Послуги</Link>
      <Link to="/invoices">Інвойси</Link>

      {/* Тільки для адміна */}
      {role === "admin" && <Link to="/users">Користувачі</Link>}

      {/* Тільки для менеджера */}
      {role === "manager" && <span style={{ color: "#888" }}>Менеджер</span>}

      {/* Тільки для майстра */}
      {role === "worker" && <span style={{ color: "#888" }}>Майстер</span>}

      <button onClick={handleLogout}>Вийти</button>
    </nav>
  );
}
