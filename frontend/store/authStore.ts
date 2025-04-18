import { create } from "zustand";
import api from "@/utils/api";
import AsyncStorage from "@react-native-async-storage/async-storage";

type RegisterUserData = {
    firstname: string;
    lastname: string;
    email: string;
    password: string;
}

type LoginUserData = {
    email: string;
    password: string;
}

type UserData = {
    firstname: string;
    lastname: string;
    email: string;
}

interface AuthState {
    isLoading: boolean;
    error: string | null;
    success: boolean;
    refresh_token: string | null;
    access_token: string | null;
    user: UserData | null;
    register: (user: RegisterUserData) => Promise<void>;
    login: (user: LoginUserData) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
    isLoading: false,
    error: null,
    user: null,
    success: false,
    refresh_token: null,
    access_token: null,
    
    register: async ({firstname, lastname, email, password}) => {
        set({ isLoading: true, error: null, user: null, success: false});

        const formData = new URLSearchParams();

        formData.append("first_name", firstname);
        formData.append("last_name", lastname);
        formData.append("email", email);
        formData.append("password", password);

        try {
            const response = await api.post('/auth/register', formData.toString(), {
                headers: {
                    "Content-Type": "multipart/x-www-form-urlencoded"
                }
            });

            if (response.status !== 200) {
               throw new Error(`Registration Failed. ${response?.data}`);
            } else {
                set({
                    user: {
                        firstname: response.data.first_name,
                        lastname: response.data.last_name,
                        email: response.data.email,
                    },
                    success: true
                });
            }
        } catch (err: any) {
            set({ success: false, error: err?.response?.data?.message || "Registration failed. please try again!" });
        } finally {
            set({isLoading: false});
        }
    },

    login: async ({email, password}) => {
        set({ isLoading: true, user: null, success: false, error: null })

        const formData = new URLSearchParams();

        formData.append("username", email);
        formData.append("password", password);

        try {
            const response = await api.post("/auth/login", formData.toString(), {
                headers: {
                    "Content-Type": "multipart/x-www-form-urlencoded"
                }
            })

            if (response.status === 200) {
                const {access_token, refresh_token } = response.data;

                set({
                    success: true,
                    access_token,
                    refresh_token
                });
                await AsyncStorage.setItem("access_token", response?.data?.access_token);
                await AsyncStorage.setItem("refresh_token", response?.data?.refresh_token);
            }

        } catch (err: any) {
            set({
                success: false,
                error: err?.response?.data?.message || "Login Failed. Try again",
            })
        } finally {
            set({ isLoading: false });
        }
    }
}));
