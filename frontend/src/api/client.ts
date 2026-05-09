import axios, { AxiosInstance } from "axios";

const baseURL = import.meta.env.VITE_API_URL || "/api";

export const http: AxiosInstance = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
  timeout: 15000,
});

http.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error?.response?.data?.detail) {
      error.message = error.response.data.detail;
    }
    return Promise.reject(error);
  }
);
