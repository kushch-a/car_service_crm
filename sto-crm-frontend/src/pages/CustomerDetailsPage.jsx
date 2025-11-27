import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";

export default function CustomerDetailsPage() {
  const { id } = useParams();
  const [customer, setCustomer] = useState(null);
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/customers/${id}`).then(res => setCustomer(res.data));
    api.get(`/cars?customer_id=${id}`).then(res => setCars(res.data)).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div>Завантаження...</div>;
  if (!customer) return <div>Клієнта не знайдено</div>;

  return (
    <div style={{ maxWidth: 800, margin: "40px auto" }}>
      <MainMenu />
      <h2>Клієнт: {customer.first_name} {customer.last_name}</h2>
      <div>Телефон: {customer.phone}</div>
      <div>Email: {customer.email}</div>
      <div>Адреса: {customer.address}</div>
      <h3 style={{ marginTop: 24 }}>Автомобілі клієнта</h3>
      {cars.length === 0 ? (
        <div>Немає авто</div>
      ) : (
        <table border="1" cellPadding={8} style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>VIN</th>
              <th>Марка</th>
              <th>Модель</th>
              <th>Рік</th>
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
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <Link to="/customers" style={{ display: "inline-block", marginTop: 20 }}>← Назад до списку клієнтів</Link>
    </div>
  );
}
