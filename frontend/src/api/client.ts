import axios from 'axios';

// В Docker VITE_API_URL=""  → baseURL пустой → axios ходит same-origin на
// nginx (`/api/...`), который проксирует на backend. В локальном dev
// переменная не задана (undefined) → фолбэк на http://localhost:8000.
// Важно использовать `??`, а не `||`: пустая строка — валидное значение
// «same-origin», её нельзя заменять фолбэком.
const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL,
  timeout: 180_000,
});
