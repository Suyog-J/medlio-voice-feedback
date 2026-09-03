import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Paper, Grid, Chip, Button } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../../services/api';

const AdminFeedbackDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [detail, setDetail] = useState(null);

    useEffect(() => {
        const fetchDetail = async () => {
            try {
                const response = await apiClient.get(`/admin/feedback/${id}`);
                setDetail(response.data);
            } catch (err) {
                console.error('Failed to fetch detail');
            }
        };
        fetchDetail();
    }, [id]);

    const handleDelete = async () => {
        if (window.confirm('Are you sure you want to delete this feedback?')) {
            try {
                await apiClient.delete(`/admin/feedback/${id}`);
                navigate('/admin/dashboard');
            } catch (err) {
                alert('Deletion failed');
            }
        }
    };

    if (!detail) return <Typography>Loading...</Typography>;

    return (
        <Container maxWidth="md">
            <Box sx={{ mt: 8 }}>
                <Typography variant="h4" gutterBottom>Feedback Detail</Typography>
                <Paper sx={{ p: 3, mb: 3 }}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <Typography variant="subtitle1">User ID: {detail.feedback.user_id}</Typography>
                            <Typography variant="subtitle1">Status: <Chip label={detail.feedback.status} color="primary" /></Typography>
                            <Typography variant="subtitle1">Date: {new Date(detail.feedback.date).toLocaleString()}</Typography>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <Typography variant="subtitle1" gutterBottom>Audio Playback:</Typography>
                            {detail.feedback.audio_url ? (
                                <audio controls src={detail.feedback.audio_url} style={{ width: '100%', marginTop: 8 }} />
                            ) : (
                                <Typography variant="body2" color="text.secondary">No audio recording available.</Typography>
                            )}
                        </Grid>
                    </Grid>
                </Paper>

                <Paper sx={{ p: 3, mb: 3 }}>
                    <Typography variant="h6" gutterBottom>Transcription</Typography>
                    <Typography variant="body1">{detail.transcription?.text || 'No transcription available.'}</Typography>
                    <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
                        Language: {detail.transcription?.language || 'Unknown'}
                    </Typography>
                </Paper>

                <Paper sx={{ p: 3, mb: 3 }}>
                    <Typography variant="h6" gutterBottom>Sentiment Analysis</Typography>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                        <Chip label={detail.sentiment?.sentiment} color={detail.sentiment?.sentiment === 'POSITIVE' ? 'success' : detail.sentiment?.sentiment === 'NEGATIVE' ? 'error' : 'default'} />
                        <Chip label={`Confidence: ${detail.sentiment?.confidence}`} />
                        <Chip label={`Urgency: ${detail.sentiment?.urgency}`} />
                    </Box>
                    <Typography variant="body1"><strong>Summary:</strong> {detail.sentiment?.summary}</Typography>
                    <Typography variant="body1" sx={{ mt: 1 }}><strong>Key Topics:</strong> {detail.sentiment?.key_topics?.join(', ') || 'None'}</Typography>
                </Paper>

                <Button variant="contained" color="error" onClick={handleDelete}>Delete Feedback</Button>
                <Button variant="outlined" sx={{ ml: 2 }} onClick={() => navigate('/admin/dashboard')}>Back to Dashboard</Button>
            </Box>
        </Container>
    );
};

export default AdminFeedbackDetail;
