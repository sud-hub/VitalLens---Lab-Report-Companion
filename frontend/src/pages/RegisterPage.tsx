import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient, { RegisterRequest } from '../api/client';

interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

function RegisterPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<RegisterForm>({
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation (Requirement 1.4)
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    // Password validation (Requirement 1.5)
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // Clear previous errors and success message
    setErrors({});
    setSuccessMessage('');

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const registerData: RegisterRequest = {
        email: formData.email,
        password: formData.password,
      };

      // Make registration request
      await apiClient.post('/auth/register', registerData);

      // Show success message
      setSuccessMessage('Registration successful! Redirecting to login...');

      // Navigate to login page after a short delay
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error: any) {
      console.error('Registration error:', error);
      
      if (error.response?.data?.detail) {
        // Handle specific error messages from backend
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          if (detail.toLowerCase().includes('email') && detail.toLowerCase().includes('exists')) {
            setErrors({ email: 'This email is already registered' });
          } else {
            setErrors({ general: detail });
          }
        } else {
          setErrors({ general: 'Registration failed. Please try again.' });
        }
      } else if (error.response?.status === 400) {
        setErrors({ general: 'Invalid registration data. Please check your inputs.' });
      } else {
        setErrors({ general: 'An error occurred during registration. Please try again.' });
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
      <h1>Register</h1>
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
          <small style={{ display: 'block', marginTop: '5px', color: '#666' }}>
            Must be at least 8 characters long
          </small>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="confirmPassword" style={{ display: 'block', marginBottom: '5px' }}>
            Confirm Password
          </label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '8px',
              fontSize: '14px',
              border: errors.confirmPassword ? '1px solid red' : '1px solid #ccc',
              borderRadius: '4px',
            }}
            disabled={isLoading}
          />
          {errors.confirmPassword && (
            <span style={{ color: 'red', fontSize: '12px' }}>{errors.confirmPassword}</span>
          )}
        </div>

        {errors.general && (
          <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#fee', borderRadius: '4px' }}>
            <span style={{ color: 'red', fontSize: '14px' }}>{errors.general}</span>
          </div>
        )}

        {successMessage && (
          <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#d4edda', borderRadius: '4px' }}>
            <span style={{ color: '#155724', fontSize: '14px' }}>{successMessage}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '10px',
            fontSize: '16px',
            backgroundColor: isLoading ? '#ccc' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Registering...' : 'Register'}
        </button>
      </form>

      <div style={{ marginTop: '20px', textAlign: 'center' }}>
        <p>
          Already have an account?{' '}
          <a
            href="/login"
            onClick={(e) => {
              e.preventDefault();
              navigate('/login');
            }}
            style={{ color: '#007bff', textDecoration: 'none' }}
          >
            Login here
          </a>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;
