import React, { useEffect, useState } from "react";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";

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

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = () => {
    setLoading(true);
    api.get("/users")
      .then(res => setUsers(res.data))
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/users", form);
      setForm({ username: "", password: "", email: "", role: "manager" });
      fetchUsers();
    } catch (err) {
      setError("Помилка при додаванні користувача");
    }
  };

  const handleEdit = (user) => {
    setEditId(user.id);
    setForm({
      username: user.username,
      email: user.email,
      role: user.role,
      password: "",
    });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/users/${editId}`, form);
      setEditId(null);
      fetchUsers();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Помилка при оновленні користувача"
      );
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Видалити користувача?")) return;
    try {
      await api.delete(`/users/${id}`);
      fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || "Помилка при видаленні користувача");
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <MainMenu />
      <h2>Користувачі</h2>
      <form onSubmit={editId ? handleUpdate : handleAdd} style={{ marginBottom: 20 }}>
        <input name="username" placeholder="Логін" value={form.username} onChange={handleChange} required />
        <input name="password" placeholder="Пароль" type="password" value={form.password} onChange={handleChange} required />
        <input name="email" placeholder="Email" value={form.email} onChange={handleChange} required />
        <select name="role" value={form.role} onChange={handleChange} required>
          <option value="manager">Менеджер</option>
          <option value="master">Майстер</option>
          <option value="admin">Адмін</option>
        </select>
        <button type="submit">{editId ? "Зберегти" : "Додати"}</button>
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
                  <button onClick={() => handleEdit(user)}>Редагувати</button>
                  <button onClick={() => handleDelete(user.id)}>Видалити</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
