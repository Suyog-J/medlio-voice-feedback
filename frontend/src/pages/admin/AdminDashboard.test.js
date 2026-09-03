import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import AdminDashboard from './AdminDashboard';
import apiClient from '../../services/api';

jest.mock('../../services/api');

describe('AdminDashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );
  };

  test('fetches and displays feedback items in table', async () => {
    apiClient.get.mockResolvedValueOnce({
      data: [
        { id: 'fb-001', user_name: 'Alice', status: 'COMPLETED', date: '2026-09-04T00:00:00Z' },
        { id: 'fb-002', user_name: 'Bob', status: 'PROCESSING', date: '2026-09-04T00:05:00Z' },
      ],
    });

    renderComponent();

    expect(screen.getByText(/Admin Feedback Dashboard/i)).toBeInTheDocument();
    expect(await screen.findByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
    expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    expect(screen.getByText('PROCESSING')).toBeInTheDocument();
  });
});
