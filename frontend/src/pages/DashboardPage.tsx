import { useState } from 'react';
import UploadReport from '../components/UploadReport';
import PanelSelector from '../components/PanelSelector';
import TestSelector from '../components/TestSelector';
import TestSummaryCard from '../components/TestSummaryCard';
import TestHistoryChart from '../components/TestHistoryChart';
import { Panel, TestType } from '../api/client';
import {
  FaHospital,
  FaSignOutAlt,
  FaExclamationTriangle,
  FaClipboardList,
  FaUpload,
  FaMicroscope,
  FaChartBar,
  FaCheckCircle
} from 'react-icons/fa';

function DashboardPage() {
  const [selectedPanel, setSelectedPanel] = useState<Panel | null>(null);
  const [selectedTest, setSelectedTest] = useState<TestType | null>(null);

  const handlePanelSelect = (panel: Panel) => {
    setSelectedPanel(panel);
    // Reset test selection when panel changes
    setSelectedTest(null);
  };

  const handleTestSelect = (test: TestType) => {
    setSelectedTest(test);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(to bottom, #f8f9fe 0%, #ffffff 100%)',
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        boxShadow: '0 4px 16px rgba(102, 126, 234, 0.2)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '20px 32px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              color: 'white',
            }}>
              <FaHospital />
            </div>
            <div>
              <h1 style={{
                margin: 0,
                color: 'white',
                fontSize: '24px',
                fontWeight: '700',
                letterSpacing: '-0.5px',
              }}>
                Health Monitor
              </h1>
              <p style={{
                margin: 0,
                color: 'rgba(255, 255, 255, 0.9)',
                fontSize: '13px',
                fontWeight: '400',
              }}>Lab Report Companion</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              padding: '12px 24px',
              fontSize: '14px',
              fontWeight: '600',
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '10px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              backdropFilter: 'blur(10px)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <FaSignOutAlt /> Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '32px 20px',
      }}>
        {/* Upload Report Component */}
        <UploadReport />

        {/* Panel Selector */}
        <PanelSelector onSelect={handlePanelSelect} />

        {/* Test Selector - shown when panel is selected */}
        {selectedPanel && (
          <TestSelector
            panelKey={selectedPanel.key}
            onSelect={handleTestSelect}
          />
        )}

        {/* Test Results Section - shown when test is selected */}
        {selectedTest && (
          <div style={{ animation: 'fadeIn 0.4s ease-out' }}>
            {/* Test Summary Card */}
            <TestSummaryCard testKey={selectedTest.key} />

            {/* Test History Chart */}
            <TestHistoryChart testKey={selectedTest.key} />
          </div>
        )}

        {/* Prominent Disclaimer - always visible on page */}
        <div style={{
          maxWidth: '900px',
          margin: '40px auto',
          padding: '24px 28px',
          background: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)',
          border: '2px solid #ffa726',
          borderRadius: '16px',
          fontSize: '14px',
          color: '#e65100',
          lineHeight: '1.7',
          textAlign: 'center',
          boxShadow: '0 4px 16px rgba(255, 167, 38, 0.15)',
          animation: 'fadeIn 0.5s ease-out',
        }}>
          <div style={{
            fontWeight: '700',
            marginBottom: '12px',
            fontSize: '18px',
            color: '#e65100',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
          }}>
            <FaExclamationTriangle size={24} />
            Important Medical Disclaimer
          </div>
          <p style={{ margin: 0, fontWeight: '500' }}>
            This application provides general educational information about laboratory test results
            and is NOT intended for medical diagnosis, treatment, or clinical decision-making.
            All information displayed is for educational purposes only. Please consult a qualified
            healthcare professional or your doctor for proper medical advice, diagnosis, and
            interpretation of your laboratory results.
          </p>
        </div>

        {/* Instructions Section */}
        {!selectedPanel && (
          <div style={{
            maxWidth: '900px',
            margin: '32px auto',
            padding: '32px',
            background: 'white',
            borderRadius: '20px',
            boxShadow: '0 4px 16px rgba(102, 126, 234, 0.08)',
            textAlign: 'center',
            animation: 'fadeIn 0.5s ease-out',
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px',
              fontSize: '32px',
              color: 'white',
            }}>
              <FaClipboardList />
            </div>
            <h3 style={{
              marginTop: 0,
              marginBottom: '20px',
              color: '#1a202c',
              fontSize: '24px',
              fontWeight: '700',
            }}>
              Getting Started
            </h3>
            <div style={{
              fontSize: '15px',
              color: '#4a5568',
              lineHeight: '1.8',
              maxWidth: '600px',
              margin: '0 auto',
            }}>
              <div style={{
                display: 'grid',
                gap: '16px',
                textAlign: 'left',
                marginTop: '24px',
              }}>
                <div style={{
                  display: 'flex',
                  gap: '16px',
                  padding: '16px',
                  background: '#f8f9fe',
                  borderRadius: '12px',
                  alignItems: 'flex-start',
                }}>
                  <span style={{
                    fontSize: '24px',
                    minWidth: '32px',
                    color: '#667eea',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <FaUpload />
                  </span>
                  <div>
                    <strong style={{ color: '#1a202c' }}>Upload</strong> your lab report (JPEG, PNG, or PDF) using the form above
                  </div>
                </div>
                <div style={{
                  display: 'flex',
                  gap: '16px',
                  padding: '16px',
                  background: '#f8f9fe',
                  borderRadius: '12px',
                  alignItems: 'flex-start',
                }}>
                  <span style={{
                    fontSize: '24px',
                    minWidth: '32px',
                    color: '#667eea',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <FaMicroscope />
                  </span>
                  <div>
                    <strong style={{ color: '#1a202c' }}>Select a lab panel</strong> below to explore your test results
                  </div>
                </div>
                <div style={{
                  display: 'flex',
                  gap: '16px',
                  padding: '16px',
                  background: '#f8f9fe',
                  borderRadius: '12px',
                  alignItems: 'flex-start',
                }}>
                  <span style={{
                    fontSize: '24px',
                    minWidth: '32px',
                    color: '#667eea',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <FaChartBar />
                  </span>
                  <div>
                    <strong style={{ color: '#1a202c' }}>Choose a specific test</strong> to view detailed insights and history
                  </div>
                </div>
              </div>
              <p style={{
                marginTop: '24px',
                padding: '16px',
                background: 'linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%)',
                borderRadius: '12px',
                fontSize: '14px',
                color: '#5568d3',
                fontWeight: '600',
              }}>
                We support CBC, Metabolic Panel, and Lipid Panel tests
              </p>
            </div>
          </div>
        )}

        {selectedPanel && !selectedTest && (
          <div style={{
            maxWidth: '700px',
            margin: '24px auto',
            padding: '20px 24px',
            background: 'linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%)',
            border: '2px solid #60a5fa',
            borderRadius: '16px',
            textAlign: 'center',
            fontSize: '15px',
            color: '#1e40af',
            fontWeight: '500',
            boxShadow: '0 4px 16px rgba(96, 165, 250, 0.15)',
            animation: 'fadeIn 0.3s ease-out',
          }}>
            <div style={{ fontSize: '20px', marginBottom: '8px', display: 'flex', justifyContent: 'center' }}>
              <FaCheckCircle />
            </div>
            <strong>Panel Selected:</strong> {selectedPanel.display_name}
            <br />
            <span style={{ fontSize: '14px', opacity: 0.9 }}>
              Now choose a specific test above to view your results and history
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardPage;