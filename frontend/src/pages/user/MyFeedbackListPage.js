import React, { useEffect, useState } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Box } from '@mui/material';
import apiClient from '../../services/api';

const MyFeedbackListPage = () => {
    const [feedbacks, setFeedbacks] = useState([]);

    useEffect(() => {
        const fetchFeedback = async () => {
            try {
                const response = await apiClient.get('/user/feedback');
                setFeedbacks(response.data);
            } catch (err) {
                console.error('Failed to fetch feedback');
            }
        };
        fetchFeedback();
    }, []);

    return (
        <Container maxWidth="md">
            <Box sx={{ mt: 8 }}>
                <Typography variant="h4" gutterBottom>My Voice Feedback</Typography>
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Submitted Date</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {feedbacks.map((f) => (
                                <TableRow key={f.id}>
                                    <TableCell>{f.id}</TableCell>
                                    <TableCell>{f.status}</TableCell>
                                    <TableCell>{new Date(f.date).toLocaleDateString()}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Box>
        </Container>
    );
};

export default MyFeedbackListPage;
