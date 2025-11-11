import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import RegisterForm from '../packages/auth/src/components/RegisterForm.jsx';

describe('RegisterForm', () => {
  it('submits user data on register', async () => {
    const onRegister = jest.fn(() => Promise.resolve());
    const onSwitchToLogin = jest.fn();

    render(<RegisterForm onRegister={onRegister} onSwitchToLogin={onSwitchToLogin} />);

    fireEvent.change(screen.getByLabelText('Full Name'), { target: { value: 'Jane Doe' } });
    fireEvent.change(screen.getByLabelText('Email Address'), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } });
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'password123' } });

    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await Promise.resolve();
    expect(onRegister).toHaveBeenCalledWith({ name: 'Jane Doe', email: 'jane@example.com', password: 'password123' });
  });
});