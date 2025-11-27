import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import CustomersPage from "./pages/CustomersPage";
import CarsPage from "./pages/CarsPage";
import ServicesPage from "./pages/ServicesPage";
import InvoicesPage from "./pages/InvoicesPage";
import CustomerDetailsPage from "./pages/CustomerDetailsPage";
import UsersPage from "./pages/UsersPage";
import { getRole } from "./utils/auth";
import './App.css'

function App() {
  const isAuth = !!localStorage.getItem("token");
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/customers" element={isAuth ? <CustomersPage /> : <Navigate to="/login" />} />
        <Route path="/cars" element={isAuth ? <CarsPage /> : <Navigate to="/login" />} />
        <Route path="/services" element={isAuth ? <ServicesPage /> : <Navigate to="/login" />} />
        <Route path="/invoices" element={isAuth ? <InvoicesPage /> : <Navigate to="/login" />} />
        <Route path="/customers/:id" element={isAuth ? <CustomerDetailsPage /> : <Navigate to="/login" />} />
        <Route path="/users" element={isAuth && getRole() === "admin" ? <UsersPage /> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
