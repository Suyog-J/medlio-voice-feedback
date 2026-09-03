import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import FeedbackUploadPage from './pages/user/FeedbackUploadPage';
import MyFeedbackListPage from './pages/user/MyFeedbackListPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminFeedbackDetail from './pages/admin/AdminFeedbackDetail';

const HomeRedirect = () => {
    const { user, loading } = React.useContext(AuthContext);
    if (loading) return <div>Loading...</div>;
    if (!user) return <Navigate to="/auth/login" />;
    return user.role === 'ADMIN' ? <Navigate to="/admin/dashboard" replace /> : <Navigate to="/user/upload" replace />;
};

const ProtectedRoute = ({ children, role }) => {
    const { user, loading } = React.useContext(AuthContext);
    if (loading) return <div>Loading...</div>;
    if (!user) return <Navigate to="/auth/login" />;
    if (role && user.role !== role) return <Navigate to="/" replace />;
    return children;
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/auth/login" element={<LoginPage />} />
                    <Route path="/auth/register" element={<RegisterPage />} />

                    <Route path="/" element={<Layout />}>
                        <Route index element={<HomeRedirect />} />
                        <Route path="user/upload" element={
                            <ProtectedRoute role="USER">
                                <FeedbackUploadPage />
                            </ProtectedRoute>
                        } />
                        <Route path="user/my-feedback" element={
                            <ProtectedRoute role="USER">
                                <MyFeedbackListPage />
                            </ProtectedRoute>
                        } />
                        <Route path="admin/dashboard" element={
                            <ProtectedRoute role="ADMIN">
                                <AdminDashboard />
                            </ProtectedRoute>
                        } />
                        <Route path="admin/feedback/:id" element={
                            <ProtectedRoute role="ADMIN">
                                <AdminFeedbackDetail />
                            </ProtectedRoute>
                        } />
                        <Route path="*" element={<Navigate to="/auth/login" />} />
                    </Route>
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
