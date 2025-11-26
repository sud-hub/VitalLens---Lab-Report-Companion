import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient, { LoginRequest, TokenResponse } from '../api/client';

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
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px' }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '5px' }}>
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '8px',
              fontSize: '14px',
              border: errors.email ? '1px solid red' : '1px solid #ccc',
              borderRadius: '4px',
            }}
            disabled={isLoading}
          />
          {errors.email && (
            <span style={{ color: 'red', fontSize: '12px' }}>{errors.email}</span>
          )}
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px' }}>
            Password
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '8px',
              fontSize: '14px',
              border: errors.password ? '1px solid red' : '1px solid #ccc',
              borderRadius: '4px',
            }}
            disabled={isLoading}
          />
          {errors.password && (
            <span style={{ color: 'red', fontSize: '12px' }}>{errors.password}</span>
          )}
        </div>

        {errors.general && (
          <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#fee', borderRadius: '4px' }}>
            <span style={{ color: 'red', fontSize: '14px' }}>{errors.general}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '16px',
            backgroundColor: isLoading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <p>
          Don't have an account?{' '}
          <a
            href="/register"
            onClick={(e) => {
              e.preventDefault();
              navigate('/register');
            }}
            style={{ color: '#007bff', textDecoration: 'none' }}
          >
            Register here
          </a>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
