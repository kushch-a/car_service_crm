import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";

export default function InvoiceDetailsPage() {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [services, setServices] = useState([]);
  const [itemForm, setItemForm] = useState({ service_id: "", quantity: 1 });

  useEffect(() => {
    api.get(`/invoices/${id}`).then(res => setInvoice(res.data));
    api.get(`/invoice_items?invoice_id=${id}`).then(res => setItems(res.data)).finally(() => setLoading(false));
    api.get("/services").then(res => setServices(res.data));
  }, [id]);

  const handleItemChange = (e) => {
    setItemForm({ ...itemForm, [e.target.name]: e.target.value });
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    await api.post("/invoice_items", {
      invoice_id: id,
      ...itemForm,
      price: services.find(s => s.id === Number(itemForm.service_id))?.price || 0,
    });
    setItemForm({ service_id: "", quantity: 1 });
    // онови список позицій
    api.get(`/invoice_items?invoice_id=${id}`).then(res => setItems(res.data));
  };

  if (loading) return <div>Завантаження...</div>;
  if (!invoice) return <div>Інвойс не знайдено</div>;

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <MainMenu />
      <h2>Інвойс #{invoice.id}</h2>
      <div>Клієнт: {invoice.customer_id}</div>
      <div>Авто: {invoice.car_id}</div>
      <div>Сума: {invoice.total}</div>
      <div>Статус: {invoice.status}</div>
      <h3 style={{ marginTop: 24 }}>Позиції інвойсу</h3>
      {items.length === 0 ? (
        <div>Немає позицій</div>
      ) : (
        <table border="1" cellPadding={8} style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Послуга</th>
              <th>Кількість</th>
              <th>Ціна</th>
              <th>Сума</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>
                  {services.find(s => s.id === item.service_id)?.name || item.service_id}
                </td>
                <td>{item.quantity}</td>
                <td>{item.price}</td>
                <td>{item.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <form onSubmit={handleAddItem} style={{ marginBottom: 20 }}>
        <select name="service_id" value={itemForm.service_id} onChange={handleItemChange} required>
          <option value="">Оберіть послугу</option>
          {services.map(s => (
            <option key={s.id} value={s.id}>{s.name} ({s.price} грн)</option>
          ))}
        </select>
        <input name="quantity" type="number" min="1" value={itemForm.quantity} onChange={handleItemChange} required style={{ width: 60 }} />
        <button type="submit">Додати послугу</button>
      </form>
      <Link to="/invoices" style={{ display: "inline-block", marginTop: 20 }}>← Назад до списку інвойсів</Link>
    </div>
  );
}
