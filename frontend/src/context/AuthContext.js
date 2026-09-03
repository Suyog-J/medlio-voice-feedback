import React, { createContext, useState, useEffect } from 'react';
import apiClient from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        const role = localStorage.getItem('role');
        if (token && role) {
            setUser({ token, role });
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const response = await apiClient.post('/auth/login', { email, password });
        const { access_token, token, role } = response.data;
        const jwtToken = access_token || token;
        localStorage.setItem('token', jwtToken);
        localStorage.setItem('role', role);
        setUser({ token: jwtToken, role });
        return role;
    };

    const register = async (name, email, password, role = 'USER') => {
        await apiClient.post('/auth/register', { name, email, password, role });
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
