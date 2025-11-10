import React, { useState, useEffect, useRef } from 'react';
import { Button, Input, Card, ErrorMessage } from '@genai-med-chat/shared';
import gsap from 'gsap';

const LoginForm = ({ onLogin, onSwitchToRegister }) => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const formRef = useRef(null);

  useEffect(() => {
    gsap.fromTo(
      formRef.current,
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out' }
    );
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await onLogin(formData);
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="shadow-2xl rounded-2xl bg-white/80 backdrop-blur-md border border-blue-100">
      <form
        ref={formRef}
        onSubmit={handleSubmit}
        className="space-y-5 animate-fadeIn"
      >
        <div className="text-center mb-4">
          <h2 className="text-2xl font-semibold text-blue-700">Welcome Back 👋</h2>
          <p className="text-gray-500 text-sm mt-1">Sign in to continue your medical insights</p>
        </div>

        <ErrorMessage message={error} />

        <Input
          type="email"
          name="email"
          placeholder="yourname@example.com"
          value={formData.email}
          onChange={handleChange}
          label="Email Address"
          required
        />

        <Input
          type="password"
          name="password"
          placeholder="••••••••"
          value={formData.password}
          onChange={handleChange}
          label="Password"
          required
        />

        <div className="flex justify-between items-center mt-6">
          <Button type="submit" disabled={loading} className="w-1/2">
            {loading ? 'Logging in...' : 'Login'}
          </Button>

          <Button
            type="button"
            variant="secondary"
            onClick={onSwitchToRegister}
            disabled={loading}
            className="w-1/2"
          >
            Register
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default LoginForm;
