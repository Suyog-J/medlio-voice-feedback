import React, { useState, useRef } from 'react';
import { Button, Container, Typography, Box, Alert, Card, CardContent, Divider, Stack } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import apiClient from '../../services/api';

const getSupportedMimeType = () => {
    if (typeof MediaRecorder === 'undefined') return { mimeType: '', ext: 'webm', type: 'audio/webm' };
    if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) return { mimeType: 'audio/webm;codecs=opus', ext: 'webm', type: 'audio/webm' };
    if (MediaRecorder.isTypeSupported('audio/webm')) return { mimeType: 'audio/webm', ext: 'webm', type: 'audio/webm' };
    if (MediaRecorder.isTypeSupported('audio/mp4')) return { mimeType: 'audio/mp4', ext: 'mp4', type: 'audio/mp4' };
    if (MediaRecorder.isTypeSupported('audio/wav')) return { mimeType: 'audio/wav', ext: 'wav', type: 'audio/wav' };
    return { mimeType: '', ext: 'webm', type: 'audio/webm' };
};

const FeedbackUploadPage = () => {
    const [recording, setRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [audioUrl, setAudioUrl] = useState(null);
    const [recordedFormat, setRecordedFormat] = useState({ ext: 'webm', type: 'audio/webm' });
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const startRecording = async () => {
        setError('');
        setStatus('');
        setAudioBlob(null);
        setAudioUrl(null);
        audioChunksRef.current = [];

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const format = getSupportedMimeType();
            setRecordedFormat(format);

            const options = format.mimeType ? { mimeType: format.mimeType } : {};
            mediaRecorderRef.current = new MediaRecorder(stream, options);

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorderRef.current.onstop = () => {
                const blob = new Blob(audioChunksRef.current, { type: format.type });
                setAudioBlob(blob);
                setAudioUrl(URL.createObjectURL(blob));
                // Stop all track streams
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorderRef.current.start();
            setRecording(true);
        } catch (err) {
            setError('Microphone access denied or not supported in this browser.');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && recording) {
            mediaRecorderRef.current.stop();
            setRecording(false);
        }
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        if (selectedFile) {
            setAudioBlob(null);
            setAudioUrl(URL.createObjectURL(selectedFile));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const payloadFile = file || (audioBlob ? new File([audioBlob], `feedback_recording.${recordedFormat.ext}`, { type: recordedFormat.type }) : null);

        if (!payloadFile) {
            setError('Please record audio or select a file to upload.');
            return;
        }

        setStatus('Uploading...');
        setError('');

        const formData = new FormData();
        formData.append('file', payloadFile);

        try {
            const response = await apiClient.post('/user/feedback', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setStatus(`Success! Feedback ID: ${response.data.id}. Your voice feedback is processing.`);
            setFile(null);
            setAudioBlob(null);
            setAudioUrl(null);
        } catch (err) {
            setError(err.response?.data?.msg || 'Upload failed. Please try again.');
            setStatus('');
        }
    };

    return (
        <Container maxWidth="sm">
            <Box sx={{ mt: 6, textAlign: 'center' }}>
                <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
                    Submit Voice Feedback
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
                    Record your feedback directly using your microphone or upload an existing audio file.
                </Typography>

                <Card variant="outlined" sx={{ mt: 3, p: 2 }}>
                    <CardContent>
                        <Typography variant="h6" gutterBottom>
                            Voice Recorder
                        </Typography>
                        <Box sx={{ my: 3 }}>
                            {!recording ? (
                                <Button
                                    variant="contained"
                                    color="error"
                                    size="large"
                                    startIcon={<MicIcon />}
                                    onClick={startRecording}
                                    sx={{ borderRadius: 8, px: 4, py: 1.5 }}
                                >
                                    Press to Record
                                </Button>
                            ) : (
                                <Button
                                    variant="contained"
                                    color="secondary"
                                    size="large"
                                    startIcon={<StopIcon />}
                                    onClick={stopRecording}
                                    sx={{ borderRadius: 8, px: 4, py: 1.5 }}
                                >
                                    Stop Recording
                                </Button>
                            )}
                        </Box>

                        <Divider sx={{ my: 3 }}>OR UPLOAD FILE</Divider>

                        <Stack direction="row" spacing={2} justifyContent="center" alignItems="center">
                            <Button
                                variant="outlined"
                                component="label"
                                startIcon={<UploadFileIcon />}
                            >
                                Choose Audio File
                                <input type="file" hidden accept="audio/*" onChange={handleFileChange} />
                            </Button>
                            {file && <Typography variant="body2">{file.name}</Typography>}
                        </Stack>

                        {audioUrl && (
                            <Box sx={{ mt: 3 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Audio Preview:
                                </Typography>
                                <audio src={audioUrl} controls style={{ width: '100%' }} />
                            </Box>
                        )}

                        <Box sx={{ mt: 4 }}>
                            <Button
                                variant="contained"
                                color="primary"
                                fullWidth
                                size="large"
                                disabled={!audioUrl && !file}
                                onClick={handleSubmit}
                            >
                                Submit Feedback
                            </Button>
                        </Box>
                    </CardContent>
                </Card>

                {status && <Alert severity="success" sx={{ mt: 3 }}>{status}</Alert>}
                {error && <Alert severity="error" sx={{ mt: 3 }}>{error}</Alert>}
            </Box>
        </Container>
    );
};

export default FeedbackUploadPage;
