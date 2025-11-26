import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient, { LoginRequest, TokenResponse } from '../api/client';
import { MdLocalHospital } from 'react-icons/md';
import { FaSpinner, FaExclamationTriangle } from 'react-icons/fa';

interface LoginForm {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<LoginForm>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // FastAPI OAuth2PasswordRequestForm expects 'username' field
      const loginData: LoginRequest = {
        username: formData.email,
        password: formData.password,
      };

      // Make login request using form-urlencoded format
      const response = await apiClient.post<TokenResponse>(
        '/auth/login',
        new URLSearchParams({
          username: loginData.username,
          password: loginData.password,
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      // Store JWT token in localStorage
      localStorage.setItem('access_token', response.data.access_token);

      // Navigate to dashboard
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Login error:', error);

      if (error.response?.data?.detail) {
        setErrors({ general: error.response.data.detail });
      } else if (error.response?.status === 401) {
        setErrors({ general: 'Invalid email or password' });
      } else {
        setErrors({ general: 'An error occurred during login. Please try again.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Decorative Background Elements */}
      <div style={{
        position: 'absolute',
        top: '-10%',
        right: '-5%',
        width: '400px',
        height: '400px',
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '50%',
        filter: 'blur(60px)',
      }} />
      <div style={{
        position: 'absolute',
        bottom: '-10%',
        left: '-5%',
        width: '350px',
        height: '350px',
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '50%',
        filter: 'blur(60px)',
      }} />

      <div style={{
        maxWidth: '440px',
        width: '100%',
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(20px)',
        borderRadius: '24px',
        padding: '48px 40px',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        position: 'relative',
        zIndex: 1,
        animation: 'fadeIn 0.5s ease-out',
      }}>
        {/* Logo/Icon */}
        <div style={{
          width: '80px',
          height: '80px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 24px',
          boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)',
        }}>
          <MdLocalHospital style={{
            fontSize: '40px',
            color: 'white',
          }} />
        </div>

        <h1 style={{
          fontSize: '32px',
          fontWeight: '700',
          textAlign: 'center',
          marginBottom: '8px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}>Welcome Back</h1>

        <p style={{
          textAlign: 'center',
          color: '#718096',
          fontSize: '14px',
          marginBottom: '32px',
        }}>Sign in to access your health dashboard</p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label htmlFor="email" style={{
              display: 'block',
              marginBottom: '8px',
              fontSize: '14px',
              fontWeight: '600',
              color: '#1a202c',
            }}>
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              style={{
                width: '100%',
                padding: '14px 16px',
                fontSize: '15px',
                border: errors.email ? '2px solid #ef5350' : '2px solid #e2e8f0',
                borderRadius: '12px',
                outline: 'none',
                transition: 'all 0.2s',
                backgroundColor: '#f8f9fe',
                color: '#1a202c',
              }}
              onFocus={(e) => {
                if (!errors.email) e.target.style.borderColor = '#667eea';
                e.target.style.backgroundColor = '#ffffff';
              }}
              onBlur={(e) => {
                if (!errors.email) e.target.style.borderColor = '#e2e8f0';
                e.target.style.backgroundColor = '#f8f9fe';
              }}
              disabled={isLoading}
            />
            {errors.email && (
              <span style={{
                color: '#ef5350',
                fontSize: '13px',
                marginTop: '6px',
                animation: 'fadeIn 0.2s ease-out',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}><FaExclamationTriangle /> {errors.email}</span>
            )}
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label htmlFor="password" style={{
              display: 'block',
              marginBottom: '8px',
              fontSize: '14px',
              fontWeight: '600',
              color: '#1a202c',
            }}>
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              style={{
                width: '100%',
                padding: '14px 16px',
                fontSize: '15px',
                border: errors.password ? '2px solid #ef5350' : '2px solid #e2e8f0',
                borderRadius: '12px',
                outline: 'none',
                transition: 'all 0.2s',
                backgroundColor: '#f8f9fe',
                color: '#1a202c',
              }}
              onFocus={(e) => {
                if (!errors.password) e.target.style.borderColor = '#667eea';
                e.target.style.backgroundColor = '#ffffff';
              }}
              onBlur={(e) => {
                if (!errors.password) e.target.style.borderColor = '#e2e8f0';
                e.target.style.backgroundColor = '#f8f9fe';
              }}
              disabled={isLoading}
            />
            {errors.password && (
              <span style={{
                color: '#ef5350',
                fontSize: '13px',
                marginTop: '6px',
                animation: 'fadeIn 0.2s ease-out',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}><FaExclamationTriangle /> {errors.password}</span>
            )}
          </div>

          {errors.general && (
            <div style={{
              marginBottom: '20px',
              padding: '14px 16px',
              backgroundColor: '#ffebee',
              border: '1px solid #ef5350',
              borderRadius: '12px',
              animation: 'fadeIn 0.3s ease-out',
            }}>
              <span style={{
                color: '#c62828',
                fontSize: '14px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}><FaExclamationTriangle /> {errors.general}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '16px',
              fontSize: '16px',
              fontWeight: '600',
              background: isLoading ? '#cbd5e0' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              boxShadow: isLoading ? 'none' : '0 4px 16px rgba(102, 126, 234, 0.4)',
              transform: isLoading ? 'scale(1)' : 'scale(1)',
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 24px rgba(102, 126, 234, 0.5)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(102, 126, 234, 0.4)';
              }
            }}
          >
            {isLoading ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <span style={{ animation: 'spin 1s linear infinite', display: 'flex' }}><FaSpinner /></span>
                Logging in...
              </span>
            ) : 'Sign In'}
          </button>
        </form>

        <div style={{
          marginTop: '28px',
          textAlign: 'center',
          paddingTop: '24px',
          borderTop: '1px solid #e2e8f0',
        }}>
          <p style={{
            fontSize: '14px',
            color: '#4a5568',
          }}>
            Don't have an account?{' '}
            <a
              href="/register"
              onClick={(e) => {
                e.preventDefault();
                navigate('/register');
              }}
              style={{
                color: '#667eea',
                textDecoration: 'none',
                fontWeight: '600',
                transition: 'color 0.2s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#764ba2'}
              onMouseLeave={(e) => e.currentTarget.style.color = '#667eea'}
            >
              Create Account
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
