import React, { useEffect, useState } from "react";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";

export default function ServicesPage() {
  const [services, setServices] = useState([]);
  const [form, setForm] = useState({
    name: "",
    description: "",
    price: "",
    duration: "",
  });
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const role = localStorage.getItem("role") || "";

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    setLoading(true);
    try {
      const res = await api.get("/services");
      setServices(res.data);
    } catch {
      setServices([]);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setError("");
    if (!form.duration || Number(form.duration) < 1) {
      setError("Вкажіть тривалість (хвилини)");
      return;
    }
    try {
      await api.post("/services", {
        ...form,
        price: Number(form.price),
        duration: Number(form.duration),
      });
      setForm({ name: "", description: "", price: "", duration: "" });
      fetchServices();
    } catch (err) {
      setError("Помилка при додаванні послуги");
    }
  };

  const handleEdit = (service) => {
    setEditId(service.id);
    setForm({
      name: service.name,
      description: service.description,
      price: service.price,
      duration: service.duration ?? 1,
    });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError("");
    if (!form.duration || Number(form.duration) < 1) {
      setError("Вкажіть тривалість (хвилини)");
      return;
    }
    try {
      await api.patch(`/services/${editId}`, {
        ...form,
        price: Number(form.price),
        duration: Number(form.duration),
      });
      setEditId(null);
      setForm({ name: "", description: "", price: "", duration: "" });
      fetchServices();
    } catch (err) {
      setError("Помилка при оновленні послуги");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Видалити послугу?")) return;
    try {
      await api.delete(`/services/${id}`);
      fetchServices();
    } catch (err) {
      setError("Помилка при видаленні послуги");
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <MainMenu />
      <h2>Послуги</h2>
      <form onSubmit={editId ? handleUpdate : handleAdd} style={{ marginBottom: 20 }}>
        <input name="name" placeholder="Назва" value={form.name} onChange={handleChange} required />
        <input name="description" placeholder="Опис" value={form.description} onChange={handleChange} />
        <input name="price" placeholder="Ціна" value={form.price} onChange={handleChange} required />
        <input
          name="duration"
          placeholder="Тривалість (хв)"
          type="number"
          min={1}
          value={form.duration}
          onChange={handleChange}
          required
        />
        <button type="submit">{editId ? "Зберегти" : "Додати"}</button>
        {editId && <button type="button" onClick={() => { setEditId(null); setForm({ name: "", description: "", price: "", duration: "" }); }}>Відміна</button>}
        {error && <span style={{ color: "red", marginLeft: 10 }}>{error}</span>}
      </form>
      {loading ? (
        <div>Завантаження...</div>
      ) : (
        <table border="1" cellPadding={8} style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Назва</th>
              <th>Опис</th>
              <th>Ціна</th>
              <th>Тривалість</th>
              <th>Дії</th>
            </tr>
          </thead>
          <tbody>
            {services.map(s => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{s.description}</td>
                <td>{s.price}</td>
                <td>{s.duration}</td>
                <td>
                  {(role === "admin" || role === "manager") && (
                    <>
                      <button onClick={() => handleEdit(s)}>Редагувати</button>
                      <button onClick={() => handleDelete(s.id)}>Видалити</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
