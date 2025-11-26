import { useState, useEffect } from 'react';
import apiClient, { Panel } from '../api/client';

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
        maxWidth: '600px',
        margin: '20px auto',
        padding: '20px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#fff',
        textAlign: 'center',
      }}>
        <p style={{ color: '#6c757d' }}>Loading lab panels...</p>
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

  if (panels.length === 0) {
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
        <p style={{ color: '#6c757d' }}>No lab panels available.</p>
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
      <h2 style={{ marginTop: 0 }}>Select Lab Panel</h2>
      <p style={{ 
        color: '#6c757d', 
        fontSize: '14px',
        marginBottom: '20px',
      }}>
        Choose a lab panel to view your test results and history.
      </p>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}>
        {panels.map((panel) => (
          <button
            key={panel.id}
            onClick={() => handlePanelClick(panel)}
            style={{
              padding: '16px 20px',
              fontSize: '16px',
              fontWeight: selectedPanelId === panel.id ? 'bold' : 'normal',
              backgroundColor: selectedPanelId === panel.id ? '#007bff' : '#fff',
              color: selectedPanelId === panel.id ? '#fff' : '#333',
              border: selectedPanelId === panel.id ? '2px solid #007bff' : '2px solid #ddd',
              borderRadius: '6px',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              if (selectedPanelId !== panel.id) {
                e.currentTarget.style.backgroundColor = '#f8f9fa';
                e.currentTarget.style.borderColor = '#007bff';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedPanelId !== panel.id) {
                e.currentTarget.style.backgroundColor = '#fff';
                e.currentTarget.style.borderColor = '#ddd';
              }
            }}
          >
            <div style={{ fontSize: '18px', marginBottom: '4px' }}>
              {panel.display_name}
            </div>
            <div style={{ 
              fontSize: '12px', 
              color: selectedPanelId === panel.id ? '#e3f2fd' : '#6c757d',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}>
              {panel.key}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default PanelSelector;
