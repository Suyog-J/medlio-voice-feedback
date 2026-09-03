import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import FeedbackUploadPage from './FeedbackUploadPage';
import apiClient from '../../services/api';

jest.mock('../../services/api');

describe('FeedbackUploadPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    if (!global.URL.createObjectURL) {
      global.URL.createObjectURL = jest.fn(() => 'mock-url');
    } else {
      jest.spyOn(global.URL, 'createObjectURL').mockImplementation(() => 'mock-url');
    }
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <FeedbackUploadPage />
      </BrowserRouter>
    );
  };

  test('renders upload page headers, record button and file upload input', () => {
    renderComponent();
    expect(screen.getByText(/Submit Voice Feedback/i)).toBeInTheDocument();
    expect(screen.getByText(/Press to Record/i)).toBeInTheDocument();
    expect(screen.getByText(/Choose Audio File/i)).toBeInTheDocument();
  });

  test('handles audio file upload submission successfully', async () => {
    apiClient.post.mockResolvedValueOnce({
      data: { id: 'fb-12345', status: 'UPLOADED' },
    });

    renderComponent();

    const file = new File(['dummy audio content'], 'my_voice.wav', { type: 'audio/wav' });
    const fileInput = screen.getByLabelText(/Choose Audio File/i);

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(screen.getByText('my_voice.wav')).toBeInTheDocument();

    const submitBtn = screen.getByRole('button', { name: /Submit Feedback/i });
    expect(submitBtn).not.toBeDisabled();

    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith('/user/feedback', expect.any(FormData), {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    });
    expect(await screen.findByText(/Success! Feedback ID: fb-12345/i)).toBeInTheDocument();
  });
});
