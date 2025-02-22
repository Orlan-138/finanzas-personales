import axios from "axios";
import { ElMessage } from "element-plus";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para token
api.interceptors.request.use(
  (config) => {
    console.log("Enviando petición:", config);
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error("Error en petición:", error);
    return Promise.reject(error);
  }
);

// Interceptor para respuestas
api.interceptors.response.use(
  (response) => {
    console.log("Respuesta recibida:", response);
    return response;
  },
  (error) => {
    console.error("Error en respuesta:", error);
    console.log("Detalles del error:", error.response?.data);
    ElMessage.error(error.response?.data?.detail || "Error en la petición");
    return Promise.reject(error);
  }
);

export default api;
