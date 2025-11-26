import { useState, useEffect } from 'react';
import apiClient, { TestType } from '../api/client';
import { FaFlask, FaExclamationTriangle, FaCheck } from 'react-icons/fa';

interface TestSelectorProps {
  panelKey: string;
  onSelect: (test: TestType) => void;
}

function TestSelector({ panelKey, onSelect }: TestSelectorProps) {
  const [tests, setTests] = useState<TestType[]>([]);
  const [selectedTestId, setSelectedTestId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch tests when panel changes
  useEffect(() => {
    const fetchTests = async () => {
      setIsLoading(true);
      setError(null);
      setSelectedTestId(null); // Reset selection when panel changes

      try {
        const response = await apiClient.get<TestType[]>(`/panels/${panelKey}/tests`);
        setTests(response.data);
      } catch (err: any) {
        console.error('Error fetching tests:', err);

        let errorMessage = 'Failed to load tests. Please try again.';

        if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response?.status === 401) {
          errorMessage = 'Authentication failed. Please log in again.';
        } else if (err.response?.status === 404) {
          errorMessage = `Panel '${panelKey}' not found.`;
        }

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    if (panelKey) {
      fetchTests();
    }
  }, [panelKey]);

  const handleTestSelect = (test: TestType) => {
    setSelectedTestId(test.id);
    onSelect(test);
  };

  if (isLoading) {
    return (
      <div style={{
        maxWidth: '700px',
        margin: '0 auto 32px',
        padding: '32px',
        background: 'white',
        borderRadius: '20px',
        boxShadow: '0 4px 16px rgba(102, 126, 234, 0.08)',
        textAlign: 'center',
        animation: 'fadeIn 0.4s ease-out',
      }}>
        <div style={{
          display: 'inline-block',
          width: '48px',
          height: '48px',
          border: '4px solid #e2e8f0',
          borderTopColor: '#667eea',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }} />
        <p style={{
          color: '#718096',
          marginTop: '16px',
          fontSize: '14px',
        }}>Loading tests...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        maxWidth: '700px',
        margin: '0 auto 32px',
        padding: '32px',
        background: 'white',
        borderRadius: '20px',
        boxShadow: '0 4px 16px rgba(102, 126, 234, 0.08)',
        animation: 'fadeIn 0.4s ease-out',
      }}>
        <div style={{
          padding: '16px 20px',
          backgroundColor: '#ffebee',
          border: '1px solid #ef5350',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px',
        }}>
          <span style={{ fontSize: '20px', display: 'flex', alignItems: 'center' }}><FaExclamationTriangle /></span>
          <div>
            <strong style={{ color: '#c62828', fontSize: '14px' }}>Error:</strong>
            <div style={{ color: '#c62828', fontSize: '13px', marginTop: '4px' }}>
              {error}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (tests.length === 0) {
    return (
      <div style={{
        maxWidth: '700px',
        margin: '0 auto 32px',
        padding: '32px',
        background: 'white',
        borderRadius: '20px',
        boxShadow: '0 4px 16px rgba(102, 126, 234, 0.08)',
        textAlign: 'center',
        animation: 'fadeIn 0.4s ease-out',
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px', display: 'flex', justifyContent: 'center' }}><FaFlask /></div>
        <p style={{ color: '#718096', fontSize: '14px' }}>No tests available for this panel.</p>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '700px',
      margin: '0 auto 32px',
      padding: '32px',
      background: 'white',
      borderRadius: '20px',
      boxShadow: '0 4px 16px rgba(102, 126, 234, 0.08)',
      animation: 'fadeIn 0.4s ease-out',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <div style={{
          width: '48px',
          height: '48px',
          background: 'linear-gradient(135deg, #00d4aa 0%, #00a885 100%)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          color: 'white',
        }}><FaFlask /></div>
        <div>
          <h2 style={{
            margin: 0,
            fontSize: '22px',
            fontWeight: '700',
            color: '#1a202c',
          }}>Select Test</h2>
          <p style={{
            margin: 0,
            color: '#718096',
            fontSize: '13px',
          }}>
            Choose a test to view results and history
          </p>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gap: '10px',
      }}>
        {tests.map((test) => (
          <button
            key={test.id}
            onClick={() => handleTestSelect(test)}
            style={{
              padding: '18px 20px',
              fontSize: '15px',
              fontWeight: selectedTestId === test.id ? '700' : '600',
              background: selectedTestId === test.id
                ? 'linear-gradient(135deg, #00d4aa 0%, #00a885 100%)'
                : 'white',
              color: selectedTestId === test.id ? 'white' : '#1a202c',
              border: selectedTestId === test.id
                ? '2px solid transparent'
                : '2px solid #e2e8f0',
              borderRadius: '12px',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
              boxShadow: selectedTestId === test.id
                ? '0 4px 16px rgba(0, 212, 170, 0.3)'
                : 'none',
            }}
            onMouseEnter={(e) => {
              if (selectedTestId !== test.id) {
                e.currentTarget.style.background = '#f8f9fe';
                e.currentTarget.style.borderColor = '#00d4aa';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 212, 170, 0.1)';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedTestId !== test.id) {
                e.currentTarget.style.background = 'white';
                e.currentTarget.style.borderColor = '#e2e8f0';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }
            }}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '16px', marginBottom: '4px', fontWeight: '600' }}>
                  {test.display_name}
                </div>
                <div style={{
                  fontSize: '11px',
                  color: selectedTestId === test.id ? 'rgba(255, 255, 255, 0.8)' : '#718096',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  fontWeight: '600',
                }}>
                  {test.key}
                </div>
              </div>
              <div style={{
                textAlign: 'right',
                fontSize: '12px',
                color: selectedTestId === test.id ? 'rgba(255, 255, 255, 0.9)' : '#718096',
                fontWeight: '500',
                marginLeft: '16px',
              }}>
                <div>{test.unit}</div>
                {test.ref_low !== null && test.ref_high !== null && (
                  <div style={{
                    fontSize: '10px',
                    marginTop: '4px',
                    opacity: 0.8,
                  }}>
                    Range: {test.ref_low} - {test.ref_high}
                  </div>
                )}
              </div>
              {selectedTestId === test.id && (
                <div style={{
                  width: '24px',
                  height: '24px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  marginLeft: '12px',
                }}><FaCheck /></div>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default TestSelector;
