import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import TestHistoryChart from './TestHistoryChart';
import apiClient from '../api/client';

// Mock the API client
vi.mock('../api/client');

/**
 * Property-Based Tests for TestHistoryChart Component
 * 
 * Feature: lab-report-companion, Property 39: Charts render all data points
 * Feature: lab-report-companion, Property 40: Charts display reference ranges when available
 * Validates: Requirements 16.2, 16.3
 */

describe('TestHistoryChart - Property-Based Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Property 39: Charts render all data points', () => {
    /**
     * Property: For any test history data provided to the chart component, 
     * all data points should be included in the rendered chart.
     * 
     * Feature: lab-report-companion, Property 39: Charts render all data points
     * Validates: Requirements 16.2
     */
    
    it('should render all data points when given a single data point', async () => {
      // Arrange: Single data point
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: 4.5,
            ref_high: 11.0,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 7.2,
              unit: '10^3/µL',
              status: 'NORMAL',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Wait for data to load and verify count
      await waitFor(() => {
        expect(screen.getByText(/White Blood Cells History/i)).toBeInTheDocument();
      });

      // Verify data points count is displayed - use more specific matcher
      expect(screen.getByText(/Data Points:/i)).toBeInTheDocument();
      expect(screen.getByText((_content, element) => {
        return element?.textContent === 'Data Points: 1';
      })).toBeInTheDocument();
    });

    it('should render all data points when given multiple data points', async () => {
      // Arrange: Multiple data points (3)
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: 4.5,
            ref_high: 11.0,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 7.2,
              unit: '10^3/µL',
              status: 'NORMAL',
            },
            {
              timestamp: '2024-01-15T10:00:00Z',
              value: 8.5,
              unit: '10^3/µL',
              status: 'NORMAL',
            },
            {
              timestamp: '2024-02-01T10:00:00Z',
              value: 6.8,
              unit: '10^3/µL',
              status: 'NORMAL',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Verify all 3 data points are counted
      await waitFor(() => {
        expect(screen.getByText(/Data Points:/i)).toBeInTheDocument();
      });

      expect(screen.getByText((_content, element) => {
        return element?.textContent === 'Data Points: 3';
      })).toBeInTheDocument();
    });

    it('should render all data points when given many data points', async () => {
      // Arrange: Many data points (10)
      const dataPoints = Array.from({ length: 10 }, (_, i) => ({
        timestamp: `2024-01-${String(i + 1).padStart(2, '0')}T10:00:00Z`,
        value: 7.0 + Math.random() * 2,
        unit: '10^3/µL',
        status: 'NORMAL',
      }));

      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: 4.5,
            ref_high: 11.0,
          },
          data: dataPoints,
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Verify all 10 data points are counted
      await waitFor(() => {
        expect(screen.getByText(/Data Points:/i)).toBeInTheDocument();
      });

      expect(screen.getByText((_content, element) => {
        return element?.textContent === 'Data Points: 10';
      })).toBeInTheDocument();
    });

    it('should render all data points with varying statuses', async () => {
      // Arrange: Data points with different statuses
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: 4.5,
            ref_high: 11.0,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 3.5,
              unit: '10^3/µL',
              status: 'LOW',
            },
            {
              timestamp: '2024-01-15T10:00:00Z',
              value: 7.2,
              unit: '10^3/µL',
              status: 'NORMAL',
            },
            {
              timestamp: '2024-02-01T10:00:00Z',
              value: 12.5,
              unit: '10^3/µL',
              status: 'HIGH',
            },
            {
              timestamp: '2024-02-15T10:00:00Z',
              value: 15.0,
              unit: '10^3/µL',
              status: 'CRITICAL_HIGH',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Verify all 4 data points are counted regardless of status
      await waitFor(() => {
        expect(screen.getByText(/Data Points:/i)).toBeInTheDocument();
      });

      expect(screen.getByText((_content, element) => {
        return element?.textContent === 'Data Points: 4';
      })).toBeInTheDocument();
    });

    it('should handle empty data array correctly', async () => {
      // Arrange: Empty data array
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: 4.5,
            ref_high: 11.0,
          },
          data: [],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Should show "no data" message
      await waitFor(() => {
        expect(screen.getByText(/No historical data available/i)).toBeInTheDocument();
      });
    });
  });

  describe('Property 40: Charts display reference ranges when available', () => {
    /**
     * Property: For any test with defined reference ranges, when rendering the 
     * history chart, the normal range band should be displayed.
     * 
     * Feature: lab-report-companion, Property 40: Charts display reference ranges when available
     * Validates: Requirements 16.3
     */

    it('should display reference range when both ref_low and ref_high are provided', async () => {
      // Arrange: Data with valid reference ranges
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: 4.5,
            ref_high: 11.0,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 7.2,
              unit: '10^3/µL',
              status: 'NORMAL',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Verify reference range is displayed
      await waitFor(() => {
        expect(screen.getByText(/Normal Range:/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/4\.5 - 11/)).toBeInTheDocument();
    });

    it('should display reference range for different test types', async () => {
      // Arrange: Lipid panel test with different reference ranges
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'LIPID',
            test_key: 'LDL',
            display_name: 'LDL Cholesterol',
            unit: 'mg/dL',
            ref_low: 0,
            ref_high: 100,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 85,
              unit: 'mg/dL',
              status: 'NORMAL',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="LDL" />);

      // Assert: Verify reference range is displayed
      await waitFor(() => {
        expect(screen.getByText(/Normal Range:/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/0 - 100/)).toBeInTheDocument();
    });

    it('should NOT display reference range when ref_low is null', async () => {
      // Arrange: Data with null ref_low
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: null,
            ref_high: 11.0,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 7.2,
              unit: '10^3/µL',
              status: 'UNKNOWN',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Verify reference range is NOT displayed
      await waitFor(() => {
        expect(screen.getByText(/White Blood Cells History/i)).toBeInTheDocument();
      });

      expect(screen.queryByText(/Normal Range:/i)).not.toBeInTheDocument();
    });

    it('should NOT display reference range when ref_high is null', async () => {
      // Arrange: Data with null ref_high
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: 4.5,
            ref_high: null,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 7.2,
              unit: '10^3/µL',
              status: 'UNKNOWN',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Verify reference range is NOT displayed
      await waitFor(() => {
        expect(screen.getByText(/White Blood Cells History/i)).toBeInTheDocument();
      });

      expect(screen.queryByText(/Normal Range:/i)).not.toBeInTheDocument();
    });

    it('should NOT display reference range when both ref_low and ref_high are null', async () => {
      // Arrange: Data with both null
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: null,
            ref_high: null,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 7.2,
              unit: '10^3/µL',
              status: 'UNKNOWN',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Verify reference range is NOT displayed
      await waitFor(() => {
        expect(screen.getByText(/White Blood Cells History/i)).toBeInTheDocument();
      });

      expect(screen.queryByText(/Normal Range:/i)).not.toBeInTheDocument();
    });

    it('should display reference range with zero as valid value', async () => {
      // Arrange: Data with ref_low = 0 (valid for some tests like LDL)
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'LIPID',
            test_key: 'LDL',
            display_name: 'LDL Cholesterol',
            unit: 'mg/dL',
            ref_low: 0,
            ref_high: 100,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 85,
              unit: 'mg/dL',
              status: 'NORMAL',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="LDL" />);

      // Assert: Verify reference range is displayed (0 is valid, not null)
      await waitFor(() => {
        expect(screen.getByText(/Normal Range:/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/0 - 100/)).toBeInTheDocument();
    });
  });

  describe('Additional Property Validations', () => {
    it('should display disclaimer on all charts', async () => {
      // Arrange
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'CBC',
            test_key: 'WBC',
            display_name: 'White Blood Cells',
            unit: '10^3/µL',
            ref_low: 4.5,
            ref_high: 11.0,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 7.2,
              unit: '10^3/µL',
              status: 'NORMAL',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="WBC" />);

      // Assert: Verify disclaimer is present (Property 38)
      await waitFor(() => {
        expect(screen.getByText(/Disclaimer:/i)).toBeInTheDocument();
      });

      expect(
        screen.getByText(/This is general educational information and NOT a medical diagnosis/i)
      ).toBeInTheDocument();
    });

    it('should display all metadata fields', async () => {
      // Arrange
      const mockResponse = {
        data: {
          metadata: {
            panel_key: 'METABOLIC',
            test_key: 'GLUCOSE',
            display_name: 'Glucose',
            unit: 'mg/dL',
            ref_low: 70,
            ref_high: 100,
          },
          data: [
            {
              timestamp: '2024-01-01T10:00:00Z',
              value: 95,
              unit: 'mg/dL',
              status: 'NORMAL',
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

      // Act
      render(<TestHistoryChart testKey="GLUCOSE" />);

      // Assert: Verify all metadata is displayed
      await waitFor(() => {
        expect(screen.getByText(/Glucose History/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/Panel:/i)).toBeInTheDocument();
      expect(screen.getByText(/METABOLIC/i)).toBeInTheDocument();
      expect(screen.getByText(/Test:/i)).toBeInTheDocument();
      // Use more specific matcher for GLUCOSE to avoid matching the heading
      expect(screen.getByText((_content, element) => {
        return element?.tagName === 'SPAN' && element?.textContent?.includes('Test:') && element?.textContent?.includes('GLUCOSE');
      })).toBeInTheDocument();
      expect(screen.getByText(/Unit:/i)).toBeInTheDocument();
      expect(screen.getByText(/mg\/dL/i)).toBeInTheDocument();
    });
  });
});
