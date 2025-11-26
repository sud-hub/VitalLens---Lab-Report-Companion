import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceArea,
  TooltipProps,
} from 'recharts';
import apiClient from '../api/client';
import { FaExclamationTriangle } from 'react-icons/fa';

interface TestHistoryChartProps {
  testKey: string;
}

interface TestHistoryDataPoint {
  timestamp: string;
  value: number;
  unit: string;
  status: string;
}

interface TestHistoryMetadata {
  panel_key: string;
  test_key: string;
  display_name: string;
  unit: string;
  ref_low: number | null;
  ref_high: number | null;
}

interface TestHistoryResponse {
  metadata: TestHistoryMetadata;
  data: TestHistoryDataPoint[];
}

interface ChartDataPoint {
  timestamp: string;
  displayDate: string;
  value: number;
  status: string;
}

// Custom tooltip component
const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload as ChartDataPoint;

    // Status color mapping
    const statusColors: Record<string, string> = {
      LOW: '#ffc107',
      NORMAL: '#28a745',
      HIGH: '#dc3545',
      CRITICAL_LOW: '#dc3545',
      CRITICAL_HIGH: '#dc3545',
      UNKNOWN: '#6c757d',
    };

    return (
      <div
        style={{
          backgroundColor: '#fff',
          border: '1px solid #ddd',
          borderRadius: '6px',
          padding: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <p style={{ margin: '0 0 8px 0', fontWeight: 'bold', fontSize: '14px' }}>
          {data.displayDate}
        </p>
        <p style={{ margin: '0 0 4px 0', fontSize: '13px' }}>
          <strong>Value:</strong> {data.value}
        </p>
        <p
          style={{
            margin: 0,
            fontSize: '13px',
            color: statusColors[data.status] || '#6c757d',
            fontWeight: 'bold',
          }}
        >
          <strong>Status:</strong> {data.status}
        </p>
      </div>
    );
  }

  return null;
};

function TestHistoryChart({ testKey }: TestHistoryChartProps) {
  const [historyData, setHistoryData] = useState<TestHistoryResponse | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.get<TestHistoryResponse>(
          `/tests/${testKey}/history`
        );
        setHistoryData(response.data);

        // Transform data for chart
        const transformed = response.data.data.map((result: TestHistoryDataPoint) => {
          const date = new Date(result.timestamp);
          return {
            timestamp: result.timestamp,
            displayDate: date.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            }),
            value: result.value,
            status: result.status,
          };
        });

        setChartData(transformed);
      } catch (err: any) {
        console.error('Error fetching test history:', err);

        let errorMessage = 'Failed to load test history. Please try again.';

        if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response?.status === 401) {
          errorMessage = 'Authentication failed. Please log in again.';
        } else if (err.response?.status === 404) {
          errorMessage = `Test '${testKey}' not found.`;
        }

        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    if (testKey) {
      fetchHistory();
    }
  }, [testKey]);

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
        <p style={{ color: '#6c757d' }}>Loading test history...</p>
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

  if (!historyData || chartData.length === 0) {
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
        <h3 style={{ marginTop: 0, color: '#333' }}>Test History</h3>
        <p style={{ color: '#6c757d', fontSize: '14px' }}>
          No historical data available for this test yet.
        </p>
        <p style={{ color: '#6c757d', fontSize: '13px', marginTop: '10px' }}>
          Upload lab reports to start tracking your results over time.
        </p>
      </div>
    );
  }

  // Check if we have reference ranges to display
  const hasReferenceRange =
    historyData.metadata.ref_low !== null && historyData.metadata.ref_high !== null;

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
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ marginTop: 0, marginBottom: '8px', color: '#333' }}>
          {historyData.metadata.display_name} History
        </h3>
        <div style={{ display: 'flex', gap: '16px', fontSize: '13px', color: '#6c757d', flexWrap: 'wrap' }}>
          <span>
            <strong>Panel:</strong> {historyData.metadata.panel_key}
          </span>
          <span>
            <strong>Test:</strong> {historyData.metadata.test_key}
          </span>
          <span>
            <strong>Unit:</strong> {historyData.metadata.unit}
          </span>
          {hasReferenceRange && (
            <span>
              <strong>Normal Range:</strong> {historyData.metadata.ref_low} - {historyData.metadata.ref_high}
            </span>
          )}
          <span>
            <strong>Data Points:</strong> {chartData.length}
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            dataKey="displayDate"
            tick={{ fontSize: 12 }}
            stroke="#666"
          />
          <YAxis
            label={{
              value: historyData.metadata.unit,
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12, fill: '#666' },
            }}
            tick={{ fontSize: 12 }}
            stroke="#666"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '13px' }}
            iconType="line"
          />
          {hasReferenceRange && (
            <ReferenceArea
              y1={historyData.metadata.ref_low!}
              y2={historyData.metadata.ref_high!}
              fill="#28a745"
              fillOpacity={0.1}
              label={{
                value: 'Normal Range',
                position: 'insideTopRight',
                fontSize: 11,
                fill: '#28a745',
              }}
            />
          )}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#007bff"
            strokeWidth={2}
            dot={{ fill: '#007bff', r: 4 }}
            activeDot={{ r: 6 }}
            name={historyData.metadata.display_name}
          />
        </LineChart>
      </ResponsiveContainer>

      <div
        style={{
          marginTop: '20px',
          padding: '12px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px',
          fontSize: '12px',
          color: '#856404',
        }}
      >
        <strong style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><FaExclamationTriangle /> Disclaimer:</strong> This is general educational information and
        NOT a medical diagnosis. Please consult a qualified doctor for medical advice
        and interpretation of your lab results.
      </div>
    </div>
  );
}

export default TestHistoryChart;
