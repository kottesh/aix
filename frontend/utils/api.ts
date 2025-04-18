import axios from "axios";

const api = axios.create({
    baseURL: process.env.EXPO_API_BASE_URL || "http://localhost:8000/api/v1",
    headers: {
        "Content-Type": "application/json",
    },
})

export default api;
