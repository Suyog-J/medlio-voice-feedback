import React, { useState, useContext } from 'react';
import { TextField, Button, Container, Typography, Box, Alert, MenuItem, Link as MuiLink } from '@mui/material';
import { AuthContext } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const RegisterPage = () => {
    const [formData, setFormData] = useState({ name: '', email: '', password: '', role: 'USER' });
    const [error, setError] = useState('');
    const { register } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await register(formData.name, formData.email, formData.password, formData.role);
            navigate('/auth/login');
        } catch (err) {
            setError(err.response?.data?.msg || 'Registration failed. Email might already be in use.');
        }
    };

    return (
        <Container maxWidth="xs">
            <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Typography variant="h4" gutterBottom>Register</Typography>
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1, width: '100%' }}>
                    <TextField margin="normal" required fullWidth label="Full Name" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} />
                    <TextField margin="normal" required fullWidth label="Email Address" type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} />
                    <TextField margin="normal" required fullWidth label="Password" type="password" value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} />
                    <TextField margin="normal" select fullWidth label="Role" value={formData.role} onChange={(e) => setFormData({...formData, role: e.target.value})}>
                        <MenuItem value="USER">User (Customer)</MenuItem>
                        <MenuItem value="ADMIN">Admin</MenuItem>
                    </TextField>
                    {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}
                    <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>Sign Up</Button>
                    <Box sx={{ textAlign: 'center' }}>
                        <MuiLink component={Link} to="/auth/login" variant="body2">
                            Already have an account? Sign In
                        </MuiLink>
                    </Box>
                </Box>
            </Box>
        </Container>
    );
};

export default RegisterPage;
