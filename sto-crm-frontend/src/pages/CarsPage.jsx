import React, { useEffect, useState } from "react";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";

export default function CarsPage() {
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    vin: "",
    brand: "",
    model: "",
    year: "",
    customer_id: "",
  });
  const [error, setError] = useState("");
  const [customers, setCustomers] = useState([]);
  const [editId, setEditId] = useState(null);

  useEffect(() => {
    fetchCars();
    api.get("/customers").then(res => setCustomers(res.data));
  }, []);

  const fetchCars = () => {
    setLoading(true);
    api.get("/cars")
      .then(res => setCars(res.data))
      .catch(() => setCars([]))
      .finally(() => setLoading(false));
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/cars", form);
      setForm({
        vin: "",
        brand: "",
        model: "",
        year: "",
        customer_id: "",
      });
      fetchCars();
    } catch (err) {
      setError("Помилка при додаванні авто");
    }
  };

  const handleEdit = (car) => {
    setEditId(car.id);
    setForm({
      vin: car.vin,
      brand: car.brand,
      model: car.model,
      year: car.year,
      customer_id: car.customer_id,
    });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.put(`/cars/${editId}`, form);
      setEditId(null);
      setForm({ vin: "", brand: "", model: "", year: "", customer_id: "" });
      fetchCars();
    } catch (err) {
      setError("Ошибка при обновлении авто");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Удалить авто?")) return;
    await api.delete(`/cars/${id}`);
    fetchCars();
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <MainMenu />
      <h2>Автомобілі</h2>
      <form onSubmit={editId ? handleUpdate : handleAdd} style={{ marginBottom: 20 }}>
        <input name="vin" placeholder="VIN" value={form.vin} onChange={handleChange} required />
        <input name="brand" placeholder="Марка" value={form.brand} onChange={handleChange} required />
        <input name="model" placeholder="Модель" value={form.model} onChange={handleChange} required />
        <input name="year" placeholder="Рік" value={form.year} onChange={handleChange} required />
        <select
          name="customer_id"
          value={form.customer_id}
          onChange={handleChange}
          required
        >
          <option value="">Виберіть клієнта</option>
          {customers.map(c => (
            <option key={c.id} value={c.id}>
              {c.first_name} {c.last_name}
            </option>
          ))}
        </select>
        <button type="submit">{editId ? "Сохранить" : "Добавить"}</button>
        {editId && <button type="button" onClick={() => setEditId(null)}>Отмена</button>}
        {error && <span style={{ color: "red", marginLeft: 10 }}>{error}</span>}
      </form>
      {loading ? (
        <div>Завантаження...</div>
      ) : (
        <table border="1" cellPadding={8} style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>VIN</th>
              <th>Марка</th>
              <th>Модель</th>
              <th>Рік</th>
              <th>ID Клієнта</th>
              <th>Дії</th>
            </tr>
          </thead>
          <tbody>
            {cars.map(car => (
              <tr key={car.id}>
                <td>{car.id}</td>
                <td>{car.vin}</td>
                <td>{car.brand}</td>
                <td>{car.model}</td>
                <td>{car.year}</td>
                <td>{car.customer_id}</td>
                <td>
                  <button onClick={() => handleEdit(car)}>Редактировать</button>
                  <button onClick={() => handleDelete(car.id)}>Удалить</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
