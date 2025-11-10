import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '../packages/auth/src/components/LoginForm.jsx';

describe('LoginForm', () => {
  it('submits credentials on login', async () => {
    const onLogin = jest.fn(() => Promise.resolve());
    const onSwitchToRegister = jest.fn();

    render(<LoginForm onLogin={onLogin} onSwitchToRegister={onSwitchToRegister} />);

    fireEvent.change(screen.getByLabelText('Email Address'), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    // Wait for async handler
    await Promise.resolve();
    expect(onLogin).toHaveBeenCalledWith({ email: 'user@example.com', password: 'password123' });
  });
});