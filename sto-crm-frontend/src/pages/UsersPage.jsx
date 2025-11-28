import React, { useEffect, useState, useRef } from "react";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";
import { fetchWithResilience } from "../lib/http";
import { getOrReuseKey } from "../lib/idempotency";

const MAX_FAILURES = 3; // Кількість помилок для переходу в degraded mode

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    username: "",
    password: "",
    email: "",
    role: "manager",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [editId, setEditId] = useState(null);

  // --- State для Degraded Mode ---
  const [degradedMode, setDegradedMode] = useState(false);
  const failureCount = useRef(0);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = () => {
    setLoading(true);
    api.get("/users")
      .then(res => {
        setUsers(res.data);
        // Скидаємо лічильник помилок при успішному запиті
        failureCount.current = 0;
        setDegradedMode(false);
      })
      .catch(() => {
        setUsers([]);
        failureCount.current += 1;
        if (failureCount.current >= MAX_FAILURES) {
          setDegradedMode(true);
        }
      })
      .finally(() => setLoading(false));
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setError("");
    
    const payload = { ...form };
    if (!payload.password) {
        setError("Пароль є обов'язковим");
        return;
    }

    try {
      const idemKey = await getOrReuseKey(payload);
      const res = await fetchWithResilience("http://localhost:8000/users/", {
        method: "POST",
        body: JSON.stringify(payload),
        idempotencyKey: idemKey,
        retry: { retries: 3, baseDelayMs: 300, timeoutMs: 4000 },
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.details || "Невідома помилка сервера");
      }

      setForm({ username: "", password: "", email: "", role: "manager" });
      fetchUsers();

    } catch (err) {
      setError(`Помилка при додаванні: ${err.message}`);
      failureCount.current += 1;
      if (failureCount.current >= MAX_FAILURES) {
        setDegradedMode(true);
      }
    }
  };

  const handleEdit = (user) => {
    setEditId(user.id);
    setForm({
      username: user.username,
      email: user.email,
      role: user.role,
      password: "", // Пароль не редагуємо, але поле має бути в формі
    });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    // Логіка оновлення залишається без змін, але можна додати ретраї
    try {
      await api.patch(`/users/${editId}`, form);
      setEditId(null);
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || "Помилка при оновленні");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Видалити користувача?")) return;
    try {
      await api.delete(`/users/${id}`);
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || "Помилка при видаленні");
    }
  };

  const isSubmitDisabled = degradedMode || (editId ? false : !form.password);

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <MainMenu />
      <h2>Користувачі</h2>

      {degradedMode && (
        <div style={{ padding: 10, backgroundColor: "orange", color: "white", marginBottom: 15 }}>
          Система перевантажена. Деякі функції можуть бути недоступні. Спробуйте пізніше.
        </div>
      )}

      <form onSubmit={editId ? handleUpdate : handleAdd} style={{ marginBottom: 20 }}>
        <input name="username" placeholder="Логін" value={form.username} onChange={handleChange} required />
        <input name="password" placeholder="Пароль" type="password" value={form.password} onChange={handleChange} />
        <input name="email" placeholder="Email" value={form.email} onChange={handleChange} required />
        <select name="role" value={form.role} onChange={handleChange} required>
          <option value="manager">Менеджер</option>
          <option value="master">Майстер</option>
          <option value="admin">Адмін</option>
        </select>
        <button type="submit" disabled={isSubmitDisabled}>
          {editId ? "Зберегти" : "Додати"}
        </button>
        {editId && <button type="button" onClick={() => setEditId(null)}>Відміна</button>}
        {error && <span style={{ color: "red", marginLeft: 10 }}>{error}</span>}
      </form>

      {loading ? (
        <div>Завантаження...</div>
      ) : (
        <table border="1" cellPadding={8} style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Логін</th>
              <th>Email</th>
              <th>Роль</th>
              <th>Дії</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>
                  <button onClick={() => handleEdit(user)} disabled={degradedMode}>Редагувати</button>
                  <button onClick={() => handleDelete(user.id)} disabled={degradedMode}>Видалити</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
