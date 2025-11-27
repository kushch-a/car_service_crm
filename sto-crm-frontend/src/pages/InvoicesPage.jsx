import React, { useEffect, useState } from "react";
import api from "../api/axios";
import MainMenu from "../components/MainMenu";
import { useNavigate } from "react-router-dom";

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    customer_id: "",
    car_id: "",
    worker_id: "",
    service_id: "",
    total_amount: "",
    payment_status: "unpaid",
    work_status: "new"
  });
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState("");
  const [customers, setCustomers] = useState([]);
  const [cars, setCars] = useState([]);
  const [filteredCars, setFilteredCars] = useState([]);
  const [services, setServices] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userRes = await api.get("/users/me");
        setUser(userRes.data);

        const invoicesRes = await api.get("/invoices");
        setInvoices(invoicesRes.data);

        const customersRes = await api.get("/customers");
        setCustomers(customersRes.data);

        const carsRes = await api.get("/cars");
        setCars(carsRes.data);

        const servicesRes = await api.get("/services");
        setServices(servicesRes.data);

        const workersRes = await api.get("/users");
        setWorkers(workersRes.data.filter(u => u.role === "master"));
      } catch (err) {
        setError("Помилка завантаження даних");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    let carsList = [];
    if (form.customer_id) {
      carsList = cars.filter(car => car.customer_id == form.customer_id);
    }
    if (
      form.car_id &&
      !carsList.find(car => car.id == form.car_id)
    ) {
      const selectedCar = cars.find(car => car.id == form.car_id);
      if (selectedCar) {
        carsList = [...carsList, selectedCar];
      }
    }
    setFilteredCars(carsList);
  }, [form.customer_id, cars, form.car_id]);

  useEffect(() => {
    if (form.service_id) {
      const selectedService = services.find(s => s.id === Number(form.service_id));
      setForm(f => ({
        ...f,
        total_amount: selectedService ? selectedService.price : ""
      }));
    }
    // eslint-disable-next-line
  }, [form.service_id, services]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const response = await api.post("/invoices", form);
      setForm({
        customer_id: "",
        car_id: "",
        worker_id: "",
        service_id: "",
        total_amount: "",
        payment_status: "unpaid",
        work_status: "new"
      });
      const invoicesRes = await api.get("/invoices");
      setInvoices(invoicesRes.data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (inv) => {
    setEditId(inv.id);
    setForm({
      customer_id: inv.customer_id,
      car_id: inv.car_id,
      worker_id: inv.worker_id,
      service_id: inv.service_id,
      total_amount: inv.total_amount,
      payment_status: inv.payment_status,
      work_status: inv.work_status
    });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.patch(`/invoices/${editId}`, form);
      setEditId(null);
      setForm({
        customer_id: "",
        car_id: "",
        worker_id: "",
        service_id: "",
        total_amount: "",
        payment_status: "unpaid",
        work_status: "new"
      });
      const invoicesRes = await api.get("/invoices");
      setInvoices(invoicesRes.data);
    } catch (err) {
      setError("Помилка при оновленні інвойсу");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Видалити інвойс?")) return;
    try {
      await api.delete(`/invoices/${id}`);
      setInvoices(invoices.filter(inv => inv.id !== id));
    } catch (err) {
      setError("Помилка при видаленні інвойсу");
    }
  };

  if (loading || !user) {
    return <div>Завантаження...</div>;
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto" }}>
      <MainMenu />
      <h2>Інвойси</h2>
      {error && <div style={{ color: "red" }}>{error}</div>}
      {loading ? (
        <div>Завантаження...</div>
      ) : (
        <>
          <form onSubmit={editId ? handleUpdate : handleAdd} style={{ marginBottom: 20 }}>
            <select
              name="customer_id"
              value={form.customer_id}
              onChange={handleChange}
              required
            >
              <option value="">Оберіть клієнта</option>
              {customers.map(c => (
                <option key={c.id} value={c.id}>
                  {c.first_name} {c.last_name}
                </option>
              ))}
            </select>
            <select
              name="car_id"
              value={form.car_id}
              onChange={handleChange}
              required
            >
              <option value="">Оберіть авто</option>
              {filteredCars.map(car => (
                <option key={car.id} value={car.id}>
                  {car.brand} {car.model}
                </option>
              ))}
            </select>
            <select
              name="worker_id"
              value={form.worker_id}
              onChange={handleChange}
              required
            >
              <option value="">Оберіть майстра</option>
              {workers.map(w => (
                <option key={w.id} value={w.id}>
                  {w.username}
                </option>
              ))}
            </select>
            <select
              name="service_id"
              value={form.service_id}
              onChange={handleChange}
              required
            >
              <option value="">Оберіть послугу</option>
              {services.map(s => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
            <input
              type="number"
              name="total_amount"
              placeholder="Сума"
              value={form.total_amount}
              readOnly
              required
              min={0}
            />
            <select
              name="payment_status"
              value={form.payment_status}
              onChange={handleChange}
              required
            >
              <option value="unpaid">Не оплачено</option>
              <option value="paid">Оплачено</option>
            </select>
            <select
              name="work_status"
              value={form.work_status}
              onChange={handleChange}
              required
            >
              <option value="new">Новий</option>
              <option value="in_progress">В роботі</option>
              <option value="done">Виконано</option>
            </select>
            {error && <div className="error">{error}</div>}
            <button type="submit">{editId ? "Зберегти" : "Додати інвойс"}</button>
            {editId && (
              <button type="button" onClick={() => {
                setEditId(null);
                setForm({
                  customer_id: "",
                  car_id: "",
                  worker_id: "",
                  service_id: "",
                  total_amount: "",
                  payment_status: "unpaid",
                  work_status: "new"
                });
              }}>Відміна</button>
            )}
          </form>

          <table border="1" cellPadding={8} style={{ width: "100%" }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Клієнт</th>
                <th>Авто</th>
                <th>Майстер</th>
                <th>Послуга</th>
                <th>Сума</th>
                <th>Статус оплати</th>
                <th>Статус виконання</th>
                <th>Дії</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map(inv => (
                <tr key={inv.id}>
                  <td>{inv.id}</td>
                  <td>
                    {customers.find(c => c.id === inv.customer_id)?.first_name}{" "}
                    {customers.find(c => c.id === inv.customer_id)?.last_name}
                  </td>
                  <td>
                    {cars.find(car => car.id === inv.car_id)?.brand}{" "}
                    {cars.find(car => car.id === inv.car_id)?.model}
                  </td>
                  <td>
                    {workers.find(w => w.id === inv.worker_id)?.username}
                  </td>
                  <td>
                    {services.find(s => s.id === inv.service_id)?.name}
                  </td>
                  <td>{inv.total_amount}</td>
                  <td>{inv.payment_status === "paid" ? "Оплачено" : "Не оплачено"}</td>
                  <td>
                    {inv.work_status === "new" && "Нове"}
                    {inv.work_status === "in_progress" && "Виконується"}
                    {inv.work_status === "done" && "Виконано"}
                  </td>
                  <td>
                    <button onClick={() => handleEdit(inv)}>Редагувати</button>
                    <button onClick={() => handleDelete(inv.id)}>Видалити</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}