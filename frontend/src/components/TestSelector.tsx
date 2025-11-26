import { useState, useEffect } from 'react';
import apiClient, { TestType } from '../api/client';

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
        maxWidth: '600px',
        margin: '20px auto',
        padding: '20px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#fff',
        textAlign: 'center',
      }}>
        <p style={{ color: '#6c757d' }}>Loading tests...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        maxWidth: '600px',
        margin: '20px auto',
        padding: '20px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#fff',
      }}>
        <div style={{
          padding: '12px',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          color: '#721c24',
        }}>
          <strong>Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (tests.length === 0) {
    return (
      <div style={{
        maxWidth: '600px',
        margin: '20px auto',
        padding: '20px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#fff',
        textAlign: 'center',
      }}>
        <p style={{ color: '#6c757d' }}>No tests available for this panel.</p>
      </div>
    );
  }

  return (
    <div style={{
      maxWidth: '600px',
      margin: '20px auto',
      padding: '20px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      backgroundColor: '#fff',
    }}>
      <h2 style={{ marginTop: 0 }}>Select Test</h2>
      <p style={{ 
        color: '#6c757d', 
        fontSize: '14px',
        marginBottom: '20px',
      }}>
        Choose a specific test to view your results and history.
      </p>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
      }}>
        {tests.map((test) => (
          <button
            key={test.id}
            onClick={() => handleTestSelect(test)}
            style={{
              padding: '14px 18px',
              fontSize: '15px',
              fontWeight: selectedTestId === test.id ? 'bold' : 'normal',
              backgroundColor: selectedTestId === test.id ? '#28a745' : '#fff',
              color: selectedTestId === test.id ? '#fff' : '#333',
              border: selectedTestId === test.id ? '2px solid #28a745' : '2px solid #ddd',
              borderRadius: '6px',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              if (selectedTestId !== test.id) {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
                e.currentTarget.style.borderColor = '#28a745';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedTestId !== test.id) {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.borderColor = '#ddd';
              }
            }}
          >
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <div>
                <div style={{ fontSize: '16px', marginBottom: '2px' }}>
                  {test.display_name}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: selectedTestId === test.id ? '#d4edda' : '#6c757d',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}>
                  {test.key}
                </div>
              </div>
              <div style={{
                fontSize: '12px',
                color: selectedTestId === test.id ? '#d4edda' : '#6c757d',
                fontWeight: 'normal',
              }}>
                {test.unit}
                {test.ref_low !== null && test.ref_high !== null && (
                  <div style={{ fontSize: '10px', marginTop: '2px' }}>
                    Range: {test.ref_low} - {test.ref_high}
                  </div>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default TestSelector;
