import { useState } from 'react';
import UploadReport from '../components/UploadReport';
import PanelSelector from '../components/PanelSelector';
import TestSelector from '../components/TestSelector';
import TestSummaryCard from '../components/TestSummaryCard';
import TestHistoryChart from '../components/TestHistoryChart';
import { Panel, TestType } from '../api/client';

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
      padding: '20px', 
      minHeight: '100vh', 
      backgroundColor: '#f5f5f5' 
    }}>
      {/* Header */}
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        padding: '0 20px',
      }}>
        <h1 style={{ 
          margin: 0, 
          color: '#333',
          fontSize: '28px',
        }}>
          Lab Report Companion
        </h1>
        <button
          onClick={handleLogout}
          style={{
            padding: '10px 20px',
            fontSize: '14px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: '500',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#c82333';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#dc3545';
          }}
        >
          Logout
        </button>
      </div>
      
      {/* Main Content */}
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto',
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
          <div>
            {/* Test Summary Card */}
            <TestSummaryCard testKey={selectedTest.key} />
            
            {/* Test History Chart */}
            <TestHistoryChart testKey={selectedTest.key} />
          </div>
        )}
        
        {/* Prominent Disclaimer - always visible on page */}
        <div style={{
          maxWidth: '900px',
          margin: '30px auto',
          padding: '20px',
          backgroundColor: '#fff3cd',
          border: '2px solid #ffc107',
          borderRadius: '8px',
          fontSize: '14px',
          color: '#856404',
          lineHeight: '1.6',
          textAlign: 'center',
        }}>
          <div style={{ 
            fontWeight: 'bold', 
            marginBottom: '12px', 
            fontSize: '16px',
            color: '#664d03',
          }}>
            ⚠️ Important Medical Disclaimer
          </div>
          <p style={{ margin: 0 }}>
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
            margin: '20px auto',
            padding: '20px',
            border: '1px solid #ddd',
            borderRadius: '8px',
            backgroundColor: '#fff',
            textAlign: 'center',
          }}>
            <h3 style={{ 
              marginTop: 0, 
              marginBottom: '16px',
              color: '#333',
            }}>
              Getting Started
            </h3>
            <div style={{ 
              fontSize: '14px', 
              color: '#6c757d',
              lineHeight: '1.6',
            }}>
              <p style={{ marginBottom: '12px' }}>
                1. <strong>Upload</strong> your lab report (JPEG, PNG, or PDF) using the form above
              </p>
              <p style={{ marginBottom: '12px' }}>
                2. <strong>Select a lab panel</strong> below to explore your test results
              </p>
              <p style={{ marginBottom: '12px' }}>
                3. <strong>Choose a specific test</strong> to view detailed insights and history
              </p>
              <p style={{ margin: 0 }}>
                We support <strong>CBC</strong>, <strong>Metabolic Panel</strong>, and <strong>Lipid Panel</strong> tests only.
              </p>
            </div>
          </div>
        )}
        
        {selectedPanel && !selectedTest && (
          <div style={{
            maxWidth: '600px',
            margin: '20px auto',
            padding: '16px',
            backgroundColor: '#e7f3ff',
            border: '1px solid #b3d9ff',
            borderRadius: '6px',
            textAlign: 'center',
            fontSize: '14px',
            color: '#0c5460',
          }}>
            <strong>Panel Selected:</strong> {selectedPanel.display_name}
            <br />
            Now choose a specific test above to view your results and history.
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardPage;