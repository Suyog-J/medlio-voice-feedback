import React, { useState, useContext } from 'react';
import { TextField, Button, Container, Typography, Box, Alert, Link as MuiLink } from '@mui/material';
import { AuthContext } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const role = await login(email, password);
            if (role === 'ADMIN') {
                navigate('/admin/dashboard');
            } else {
                navigate('/user/upload');
            }
        } catch (err) {
            setError(err.response?.data?.msg || 'Invalid email or password');
        }
    };

    return (
        <Container maxWidth="xs">
            <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography variant="h4" gutterBottom>Login</Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
                    <TextField margin="normal" required fullWidth label="Email Address" autoFocus value={email} onChange={(e) => setEmail(e.target.value)} />
                    <TextField margin="normal" required fullWidth label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                    {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}
                    <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>Sign In</Button>
                    <Box sx={{ textAlign: 'center' }}>
                        <MuiLink component={Link} to="/auth/register" variant="body2">
                            Don't have an account? Register here
                        </MuiLink>
                    </Box>
                </Box>
            </Box>
        </Container>
    );
};

export default LoginPage;
