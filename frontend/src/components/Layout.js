import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, Outlet, Link } from 'react-router-dom';

const Layout = () => {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/auth/login');
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                        Medlio Feedback Portal
                    </Typography>
                    {user?.role === 'USER' && (
                        <>
                            <Button color="inherit" component={Link} to="/user/upload">Upload</Button>
                            <Button color="inherit" component={Link} to="/user/my-feedback">My Feedback</Button>
                        </>
                    )}
                    {user?.role === 'ADMIN' && (
                        <Button color="inherit" component={Link} to="/admin/dashboard">Admin Dashboard</Button>
                    )}
                    <Button color="inherit" onClick={handleLogout}>Logout</Button>
                </Toolbar>
            </AppBar>
            <Box component="main" sx={{ p: 3, flexGrow: 1 }}>
                <Outlet />
            </Box>
        </Box>
    );
};

export default Layout;
