import React, { useEffect, useState } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../services/api';

const AdminDashboard = () => {
    const [feedbacks, setFeedbacks] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchFeedback = async () => {
            try {
                const response = await apiClient.get('/admin/feedback');
                setFeedbacks(response.data);
            } catch (err) {
                console.error('Failed to fetch feedback');
            }
        };
        fetchFeedback();
    }, []);

    return (
        <Container maxWidth="lg">
            <Box sx={{ mt: 8 }}>
                <Typography variant="h4" gutterBottom>Admin Feedback Dashboard</Typography>
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>User</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Date</TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {feedbacks.map((f) => (
                                <TableRow key={f.id}>
                                    <TableCell>{f.id}</TableCell>
                                    <TableCell>{f.user_name}</TableCell>
                                    <TableCell>{f.status}</TableCell>
                                    <TableCell>{new Date(f.date).toLocaleDateString()}</TableCell>
                                    <TableCell>
                                        <Button variant="outlined" onClick={() => navigate(`/admin/feedback/${f.id}`)}>View Detail</Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Box>
        </Container>
    );
};

export default AdminDashboard;
