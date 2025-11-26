import { useState, useEffect } from 'react';
import apiClient, { Panel } from '../api/client';
import { FaClipboardList, FaMicroscope, FaExclamationTriangle, FaCheck } from 'react-icons/fa';

interface PanelSelectorProps {
  onSelect: (panel: Panel) => void;
}

function PanelSelector({ onSelect }: PanelSelectorProps) {
  const [panels, setPanels] = useState<Panel[]>([]);
  const [selectedPanelId, setSelectedPanelId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch panels on component mount
  useEffect(() => {
    const fetchPanels = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.get<Panel[]>('/panels');
        setPanels(response.data);
      } catch (err: any) {
        console.error('Error fetching panels:', err);

        let errorMessage = 'Failed to load lab panels. Please try again.';

        if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response?.status === 401) {
          errorMessage = 'Authentication failed. Please log in again.';
        }

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPanels();
  }, []);

  const handlePanelClick = (panel: Panel) => {
    setSelectedPanelId(panel.id);
    onSelect(panel);
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
        }}>Loading lab panels...</p>
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

  if (panels.length === 0) {
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
        <div style={{ fontSize: '48px', marginBottom: '16px', display: 'flex', justifyContent: 'center' }}><FaClipboardList /></div>
        <p style={{ color: '#718096', fontSize: '14px' }}>No lab panels available.</p>
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
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          color: 'white',
        }}><FaMicroscope /></div>
        <div>
          <h2 style={{
            margin: 0,
            fontSize: '22px',
            fontWeight: '700',
            color: '#1a202c',
          }}>Select Lab Panel</h2>
          <p style={{
            margin: 0,
            color: '#718096',
            fontSize: '13px',
          }}>
            Choose a panel to view your test results
          </p>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gap: '12px',
      }}>
        {panels.map((panel) => (
          <button
            key={panel.id}
            onClick={() => handlePanelClick(panel)}
            style={{
              padding: '20px 24px',
              fontSize: '16px',
              fontWeight: selectedPanelId === panel.id ? '700' : '600',
              background: selectedPanelId === panel.id
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'white',
              color: selectedPanelId === panel.id ? 'white' : '#1a202c',
              border: selectedPanelId === panel.id
                ? '2px solid transparent'
                : '2px solid #e2e8f0',
              borderRadius: '14px',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
              boxShadow: selectedPanelId === panel.id
                ? '0 4px 16px rgba(102, 126, 234, 0.3)'
                : 'none',
            }}
            onMouseEnter={(e) => {
              if (selectedPanelId !== panel.id) {
                e.currentTarget.style.background = '#f8f9fe';
                e.currentTarget.style.borderColor = '#667eea';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.1)';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedPanelId !== panel.id) {
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
              <div>
                <div style={{ fontSize: '18px', marginBottom: '4px' }}>
                  {panel.display_name}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: selectedPanelId === panel.id ? 'rgba(255, 255, 255, 0.8)' : '#718096',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  fontWeight: '600',
                }}>
                  {panel.key}
                </div>
              </div>
              {selectedPanelId === panel.id && (
                <div style={{
                  width: '24px',
                  height: '24px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                }}><FaCheck /></div>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default PanelSelector;
