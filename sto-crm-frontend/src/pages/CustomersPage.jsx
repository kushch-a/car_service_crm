import React, { useEffect, useState, useContext } from "react";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";
import { Link } from "react-router-dom";


export default function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    phone: "",
    email: "",
    address: "",
  });
  const [error, setError] = useState("");
  const [editId, setEditId] = useState(null);
  const role = localStorage.getItem("role") || "";

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = () => {
    setLoading(true);
    api.get("/customers")
      .then(res => setCustomers(res.data))
      .catch(() => setCustomers([]))
      .finally(() => setLoading(false));
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/customers", form);
      setForm({
        first_name: "",
        last_name: "",
        phone: "",
        email: "",
        address: "",
      });
      fetchCustomers();
    } catch (err) {
      setError("Помилка при додаванні клієнта");
    }
  };

  const handleEdit = (customer) => {
    setEditId(customer.id);
    setForm({
      first_name: customer.first_name,
      last_name: customer.last_name,
      phone: customer.phone,
      email: customer.email,
      address: customer.address,
    });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.patch(`/customers/${editId}`, form);
      setEditId(null);
      setForm({
        first_name: "",
        last_name: "",
        phone: "",
        email: "",
        address: "",
      });
      fetchCustomers();
    } catch (err) {
      setError("Помилка при оновленні клієнта");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Видалити клієнта?")) return;
    try {
      await api.delete(`/customers/${id}`);
      fetchCustomers();
    } catch (err) {
      setError("Помилка при видаленні клієнта");
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <MainMenu />
      <h2>Клієнти</h2>
      <form onSubmit={editId ? handleUpdate : handleAdd} style={{ marginBottom: 20 }}>
        <input name="first_name" placeholder="Ім'я" value={form.first_name} onChange={handleChange} required />
        <input name="last_name" placeholder="Прізвище" value={form.last_name} onChange={handleChange} required />
        <input name="phone" placeholder="Телефон" value={form.phone} onChange={handleChange} required />
        <input name="email" placeholder="Email" value={form.email} onChange={handleChange} />
        <input name="address" placeholder="Адреса" value={form.address} onChange={handleChange} />
        <button type="submit">{editId ? "Зберегти" : "Додати"}</button>
        {editId && (
          <button type="button" onClick={() => {
            setEditId(null);
            setForm({
              first_name: "",
              last_name: "",
              phone: "",
              email: "",
              address: "",
            });
          }}>Відміна</button>
        )}
        {error && <span style={{ color: "red", marginLeft: 10 }}>{error}</span>}
      </form>
      {loading ? (
        <div>Завантаження...</div>
      ) : (
        <table border="1" cellPadding={8} style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Ім'я</th>
              <th>Прізвище</th>
              <th>Телефон</th>
              <th>Email</th>
              <th>Адреса</th>
              <th>Дії</th>
            </tr>
          </thead>
          <tbody>
            {customers.map(c => (
              <tr key={c.id}>
                <td>{c.id}</td>
                <td>
                  <Link to={`/customers/${c.id}`}>{c.first_name}</Link>
                </td>
                <td>{c.last_name}</td>
                <td>{c.phone}</td>
                <td>{c.email}</td>
                <td>{c.address}</td>
                <td>
                  {(role === "admin" || role === "manager") && (
                    <>
                      <button onClick={() => handleEdit(c)}>Редагувати</button>
                      <button onClick={() => handleDelete(c.id)}>Видалити</button>
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