import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";

export default function CarsPage() {
  const { customerId } = useParams(); // Отримуємо ID клієнта, якщо він є
  
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // State для форми, потрібен тільки на загальній сторінці /cars
  const [form, setForm] = useState({ vin: "", brand: "", model: "", year: "", customer_id: "" });
  const [customers, setCustomers] = useState([]);
  const [editId, setEditId] = useState(null);
  const [customer, setCustomer] = useState(null); // Для імені клієнта на сторінці деталей

  useEffect(() => {
    // Визначаємо, який запит робити
    const url = customerId ? `/cars?customer_id=${customerId}` : "/cars";
    
    setLoading(true);
    api.get(url)
      .then(res => setCars(res.data))
      .catch(() => {
        setError("Помилка при завантаженні автомобілів");
        setCars([]);
      })
      .finally(() => setLoading(false));

    // Якщо ми на сторінці /cars, завантажуємо список клієнтів для форми
    if (!customerId) {
      api.get("/customers").then(res => setCustomers(res.data));
    } else {
      // Якщо ми на сторінці клієнта, завантажуємо його дані для заголовка
      api.get(`/customers/${customerId}`).then(res => setCustomer(res.data));
    }
  }, [customerId]);

  // --- Функції для форми (працюють тільки на /cars) ---
  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleAdd = async (e) => {
    e.preventDefault();
    await api.post("/cars", form);
    setForm({ vin: "", brand: "", model: "", year: "", customer_id: "" });
    // Перезавантажуємо список всіх авто
    api.get("/cars").then(res => setCars(res.data));
  };

  const handleEdit = (car) => {
    setEditId(car.id);
    setForm({ vin: car.vin, brand: car.brand, model: car.model, year: car.year, customer_id: car.customer_id });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    await api.put(`/cars/${editId}`, form);
    setEditId(null);
    setForm({ vin: "", brand: "", model: "", year: "", customer_id: "" });
    api.get("/cars").then(res => setCars(res.data));
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Видалити авто?")) return;
    await api.delete(`/cars/${id}`);
    const url = customerId ? `/cars?customer_id=${customerId}` : "/cars";
    api.get(url).then(res => setCars(res.data));
  };

  // Визначаємо заголовок сторінки
  const pageTitle = customerId && customer 
    ? `Автомобілі клієнта: ${customer.first_name} ${customer.last_name}`
    : "Всі автомобілі";

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <MainMenu />
      <h2>{pageTitle}</h2>
      
      {/* Показуємо форму тільки на загальній сторінці /cars */}
      {!customerId && (
        <form onSubmit={editId ? handleUpdate : handleAdd} style={{ marginBottom: 20 }}>
          <input name="vin" placeholder="VIN" value={form.vin} onChange={handleChange} required />
          <input name="brand" placeholder="Марка" value={form.brand} onChange={handleChange} required />
          <input name="model" placeholder="Модель" value={form.model} onChange={handleChange} required />
          <input name="year" placeholder="Рік" value={form.year} onChange={handleChange} required />
          <select name="customer_id" value={form.customer_id} onChange={handleChange} required>
            <option value="">Виберіть клієнта</option>
            {customers.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}
          </select>
          <button type="submit">{editId ? "Зберегти" : "Додати"}</button>
          {editId && <button type="button" onClick={() => setEditId(null)}>Відміна</button>}
        </form>
      )}

      {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
      
      {loading ? (
        <div>Завантаження...</div>
      ) : (
        <table border="1" cellPadding={8} style={{ width: "100%", marginTop: 20 }}>
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
            {cars.length > 0 ? (
              cars.map(car => (
                <tr key={car.id}>
                  <td>{car.id}</td>
                  <td>{car.vin}</td>
                  <td>{car.brand}</td>
                  <td>{car.model}</td>
                  <td>{car.year}</td>
                  <td>{car.customer_id}</td>
                  <td>
                    {!customerId && <button onClick={() => handleEdit(car)}>Редагувати</button>}
                    <button onClick={() => handleDelete(car.id)}>Видалити</button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" style={{ textAlign: "center" }}>
                  {customerId ? "У цього клієнта немає автомобілів." : "Автомобілі не знайдено."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
