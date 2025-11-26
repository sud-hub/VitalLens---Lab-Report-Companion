import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { FaArrowUp, FaArrowDown, FaArrowRight, FaExclamationTriangle } from 'react-icons/fa';

interface TestSummaryCardProps {
  testKey: string;
}

interface LatestTestResult {
  timestamp: string;
  value: number;
  unit: string;
  status: string;
}

interface GuidanceData {
  message: string;
  trend: string | null;
  suggestions: string[];
  disclaimer: string;
}

interface LatestInsightResponse {
  latest: LatestTestResult;
  previous: LatestTestResult | null;
  guidance: GuidanceData;
}

function TestSummaryCard({ testKey }: TestSummaryCardProps) {
  const [insightData, setInsightData] = useState<LatestInsightResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLatestInsight = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.get<LatestInsightResponse>(
          `/tests/${testKey}/latest-insight`
        );
        setInsightData(response.data);
      } catch (err: any) {
        console.error('Error fetching latest insight:', err);

        let errorMessage = 'Failed to load test insight. Please try again.';

        if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response?.status === 401) {
          errorMessage = 'Authentication failed. Please log in again.';
        } else if (err.response?.status === 404) {
          errorMessage = `No test results found for '${testKey}'.`;
        }

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    if (testKey) {
      fetchLatestInsight();
    }
  }, [testKey]);

  // Status color mapping
  const getStatusColor = (status: string): string => {
    const statusColors: Record<string, string> = {
      LOW: '#ffc107',
      NORMAL: '#28a745',
      HIGH: '#dc3545',
      CRITICAL_LOW: '#dc3545',
      CRITICAL_HIGH: '#dc3545',
      UNKNOWN: '#6c757d',
    };
    return statusColors[status] || '#6c757d';
  };

  // Status background color mapping
  const getStatusBackgroundColor = (status: string): string => {
    const statusBgColors: Record<string, string> = {
      LOW: '#fff3cd',
      NORMAL: '#d4edda',
      HIGH: '#f8d7da',
      CRITICAL_LOW: '#f8d7da',
      CRITICAL_HIGH: '#f8d7da',
      UNKNOWN: '#e9ecef',
    };
    return statusBgColors[status] || '#e9ecef';
  };

  // Trend icon mapping
  const getTrendIcon = (trend: string | null) => {
    if (!trend) return null;
    const trendIcons: Record<string, JSX.Element> = {
      improving: <FaArrowUp />,
      worsening: <FaArrowDown />,
      stable: <FaArrowRight />,
    };
    return trendIcons[trend] || null;
  };

  // Trend color mapping
  const getTrendColor = (trend: string | null): string => {
    if (!trend) return '#6c757d';
    const trendColors: Record<string, string> = {
      improving: '#28a745',
      worsening: '#dc3545',
      stable: '#007bff',
    };
    return trendColors[trend] || '#6c757d';
  };

  if (isLoading) {
    return (
      <div
        style={{
          maxWidth: '900px',
          margin: '20px auto',
          padding: '20px',
          border: '1px solid #ddd',
          borderRadius: '8px',
          backgroundColor: '#fff',
          textAlign: 'center',
        }}
      >
        <p style={{ color: '#6c757d' }}>Loading test insight...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          maxWidth: '900px',
          margin: '20px auto',
          padding: '20px',
          border: '1px solid #ddd',
          borderRadius: '8px',
          backgroundColor: '#fff',
        }}
      >
        <div
          style={{
            padding: '12px',
            backgroundColor: '#f8d7da',
            border: '1px solid #f5c6cb',
            borderRadius: '4px',
            color: '#721c24',
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (!insightData) {
    return null;
  }

  const { latest, previous, guidance } = insightData;
  const latestDate = new Date(latest.timestamp).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <div
      style={{
        maxWidth: '900px',
        margin: '20px auto',
        padding: '24px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#fff',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
      }}
    >
      {/* Header */}
      <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#333' }}>
        Latest Test Result
      </h3>

      {/* Latest Value Section */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          marginBottom: '20px',
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '6px',
        }}
      >
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '14px', color: '#6c757d', marginBottom: '4px' }}>
            {latestDate}
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#333' }}>
            {latest.value} <span style={{ fontSize: '18px', color: '#6c757d' }}>{latest.unit}</span>
          </div>
        </div>
        <div
          style={{
            padding: '8px 16px',
            backgroundColor: getStatusBackgroundColor(latest.status),
            border: `2px solid ${getStatusColor(latest.status)}`,
            borderRadius: '6px',
            fontWeight: 'bold',
            fontSize: '14px',
            color: getStatusColor(latest.status),
          }}
        >
          {latest.status}
        </div>
      </div>

      {/* Trend Indicator */}
      {guidance.trend && previous && (
        <div
          style={{
            marginBottom: '20px',
            padding: '12px',
            backgroundColor: '#f8f9fa',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <span style={{ fontSize: '24px', display: 'flex', alignItems: 'center' }}>{getTrendIcon(guidance.trend)}</span>
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontSize: '14px',
                fontWeight: 'bold',
                color: getTrendColor(guidance.trend),
                textTransform: 'capitalize',
              }}
            >
              Trend: {guidance.trend}
            </div>
            <div style={{ fontSize: '13px', color: '#6c757d', marginTop: '4px' }}>
              Previous: {previous.value} {previous.unit} on{' '}
              {new Date(previous.timestamp).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              })}
            </div>
          </div>
        </div>
      )}

      {/* Guidance Message */}
      <div style={{ marginBottom: '20px' }}>
        <h4 style={{ marginTop: 0, marginBottom: '12px', color: '#333', fontSize: '16px' }}>
          What This Means
        </h4>
        <p style={{ margin: 0, fontSize: '14px', color: '#495057', lineHeight: '1.6' }}>
          {guidance.message}
        </p>
      </div>

      {/* Suggestions */}
      {guidance.suggestions && guidance.suggestions.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ marginTop: 0, marginBottom: '12px', color: '#333', fontSize: '16px' }}>
            General Suggestions
          </h4>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px', color: '#495057' }}>
            {guidance.suggestions.map((suggestion, index) => (
              <li key={index} style={{ marginBottom: '8px', lineHeight: '1.6' }}>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Prominent Disclaimer */}
      <div
        style={{
          marginTop: '24px',
          padding: '16px',
          backgroundColor: '#fff3cd',
          border: '2px solid #ffc107',
          borderRadius: '6px',
          fontSize: '13px',
          color: '#856404',
          lineHeight: '1.6',
        }}
      >
        <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FaExclamationTriangle /> Important Medical Disclaimer
        </div>
        <p style={{ margin: 0 }}>{guidance.disclaimer}</p>
      </div>
    </div>
  );
}

export default TestSummaryCard;
