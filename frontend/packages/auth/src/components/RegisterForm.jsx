import React, { useState, useEffect, useRef } from 'react';
import { Button, Input, Card, ErrorMessage } from '@genai-med-chat/shared';
import { validateEmail, validatePassword, validateName } from '@genai-med-chat/shared';
import gsap from 'gsap';

const RegisterForm = ({ onRegister, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const formRef = useRef(null);

  useEffect(() => {
    gsap.fromTo(
      formRef.current,
      { opacity: 0, y: 40 },
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
    setErrors({});

    const validationErrors = {};
    const nameError = validateName(formData.name);
    if (nameError) validationErrors.name = nameError;

    if (!validateEmail(formData.email)) {
      validationErrors.email = 'Invalid email address';
    }

    const passwordError = validatePassword(formData.password);
    if (passwordError) validationErrors.password = passwordError;

    if (formData.password !== formData.confirmPassword) {
      validationErrors.confirmPassword = 'Passwords do not match';
    }

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);
    try {
      await onRegister({
        full_name: formData.name,
        email: formData.email,
        password: formData.password
      });
    } catch (err) {
      setErrors({ form: err.message || 'Registration failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <form
        ref={formRef}
        onSubmit={handleSubmit}
        className="space-y-5 animate-fadeIn"
      >
        <div className="text-center mb-4">
          <h2 className="text-2xl font-semibold text-teal-300">Create Account ✨</h2>
          <p className="text-gray-400 text-sm mt-1">Join GenAI Medical Chat for smarter insights</p>
        </div>

        {errors.form && <ErrorMessage message={errors.form} />}

        <Input
          type="text"
          name="name"
          placeholder="Dr. John Doe"
          value={formData.name}
          onChange={handleChange}
          label="Full Name"
          error={errors.name}
          required
        />

        <Input
          type="email"
          name="email"
          placeholder="yourname@example.com"
          value={formData.email}
          onChange={handleChange}
          label="Email Address"
          error={errors.email}
          required
        />

        <Input
          type="password"
          name="password"
          placeholder="••••••••"
          value={formData.password}
          onChange={handleChange}
          label="Password"
          error={errors.password}
          required
        />

        <Input
          type="password"
          name="confirmPassword"
          placeholder="Re-enter your password"
          value={formData.confirmPassword}
          onChange={handleChange}
          label="Confirm Password"
          error={errors.confirmPassword}
          required
        />

        <div className="flex gap-3 items-center mt-6">
          <Button type="submit" disabled={loading} className="flex-1">
            {loading ? 'Registering...' : 'Register'}
          </Button>

          <Button
            type="button"
            variant="secondary"
            onClick={onSwitchToLogin}
            disabled={loading}
            className="flex-1"
          >
            Login
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default RegisterForm;
