import { useState, ChangeEvent, FormEvent } from 'react';
import apiClient, { UploadReportResponse, ParsedTest } from '../api/client';
import { FaUpload, FaFileAlt, FaSpinner, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';

interface UploadState {
  file: File | null;
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
  success: boolean;
  parsedTests: ParsedTest[];
  reportId: number | null;
}

function UploadReport() {
  const [uploadState, setUploadState] = useState<UploadState>({
    file: null,
    isUploading: false,
    uploadProgress: 0,
    error: null,
    success: false,
    parsedTests: [],
    reportId: null,
  });

  // Supported file types
  const SUPPORTED_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!SUPPORTED_TYPES.includes(file.type)) {
      return 'Unsupported file format. Please upload a JPEG, PNG, or PDF file.';
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return 'File size exceeds 10MB limit. Please upload a smaller file.';
    }

    return null;
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    // Validate file
    const validationError = validateFile(selectedFile);

    if (validationError) {
      setUploadState({
        file: null,
        isUploading: false,
        uploadProgress: 0,
        error: validationError,
        success: false,
        parsedTests: [],
        reportId: null,
      });
      return;
    }

    // Clear previous state and set new file
    setUploadState({
      file: selectedFile,
      isUploading: false,
      uploadProgress: 0,
      error: null,
      success: false,
      parsedTests: [],
      reportId: null,
    });
  };

  const handleUpload = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!uploadState.file) {
      setUploadState(prev => ({
        ...prev,
        error: 'Please select a file to upload',
      }));
      return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('file', uploadState.file);

    setUploadState(prev => ({
      ...prev,
      isUploading: true,
      uploadProgress: 0,
      error: null,
      success: false,
    }));

    try {
      // Upload file with progress tracking
      const response = await apiClient.post<UploadReportResponse>(
        '/reports/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setUploadState(prev => ({
                ...prev,
                uploadProgress: percentCompleted,
              }));
            }
          },
        }
      );

      // Handle successful upload
      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        success: true,
        parsedTests: response.data.parsed_tests || [],
        reportId: response.data.report_id,
        error: response.data.parsed_success
          ? null
          : 'Upload successful, but parsing failed. Please try a clearer image.',
      }));
    } catch (error: any) {
      console.error('Upload error:', error);

      let errorMessage = 'An error occurred during upload. Please try again.';

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 413) {
        errorMessage = 'File is too large. Please upload a file smaller than 10MB.';
      } else if (error.response?.status === 401) {
        errorMessage = 'Authentication failed. Please log in again.';
      }

      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        error: errorMessage,
        success: false,
      }));
    }
  };

  const resetUpload = () => {
    setUploadState({
      file: null,
      isUploading: false,
      uploadProgress: 0,
      error: null,
      success: false,
      parsedTests: [],
      reportId: null,
    });

    // Reset file input
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status.toUpperCase()) {
      case 'NORMAL':
        return '#00d4aa';
      case 'LOW':
        return '#ffa726';
      case 'HIGH':
        return '#ff8a65';
      case 'CRITICAL_LOW':
      case 'CRITICAL_HIGH':
        return '#ef5350';
      default:
        return '#718096';
    }
  };

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
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <div style={{
          width: '48px',
          height: '48px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
        }}>
          <FaUpload />
        </div>
        <h2 style={{
          margin: 0,
          fontSize: '22px',
          fontWeight: '700',
          color: '#1a202c',
        }}>Upload Lab Report</h2>
      </div>

      <form onSubmit={handleUpload}>
        <div style={{ marginBottom: '20px' }}>
          <label
            htmlFor="file-input"
            style={{
              display: 'block',
              marginBottom: '10px',
              fontWeight: '600',
              fontSize: '14px',
              color: '#1a202c',
            }}
          >
            Select Lab Report
          </label>
          <input
            type="file"
            id="file-input"
            accept=".jpg,.jpeg,.png,.pdf"
            onChange={handleFileChange}
            disabled={uploadState.isUploading}
            style={{
              width: '100%',
              padding: '14px 16px',
              fontSize: '14px',
              border: '2px solid #e2e8f0',
              borderRadius: '12px',
              outline: 'none',
              transition: 'all 0.2s',
              backgroundColor: '#f8f9fe',
              cursor: uploadState.isUploading ? 'not-allowed' : 'pointer',
            }}
          />
          <small style={{
            color: '#718096',
            fontSize: '12px',
            display: 'block',
            marginTop: '8px',
          }}>
            Supported formats: JPEG, PNG, PDF • Maximum size: 10MB
          </small>
        </div>

        {uploadState.file && !uploadState.success && (
          <div style={{
            marginBottom: '20px',
            padding: '14px 16px',
            background: 'linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%)',
            borderRadius: '12px',
            border: '1px solid #60a5fa',
            animation: 'fadeIn 0.3s ease-out',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '16px', display: 'flex', alignItems: 'center' }}><FaFileAlt /></span>
              <strong style={{ fontSize: '14px', color: '#1e40af' }}>Selected file:</strong>
            </div>
            <div style={{ fontSize: '13px', color: '#1e3a8a', marginLeft: '24px' }}>
              {uploadState.file.name} ({(uploadState.file.size / 1024 / 1024).toFixed(2)} MB)
            </div>
          </div>
        )}

        {uploadState.isUploading && (
          <div style={{ marginBottom: '20px', animation: 'fadeIn 0.3s ease-out' }}>
            <div style={{
              marginBottom: '8px',
              fontSize: '14px',
              color: '#667eea',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <span style={{ animation: 'spin 1s linear infinite', display: 'flex' }}><FaSpinner /></span>
              Uploading... {uploadState.uploadProgress}%
            </div>
            <div style={{
              width: '100%',
              height: '8px',
              backgroundColor: '#e2e8f0',
              borderRadius: '999px',
              overflow: 'hidden',
            }}>
              <div style={{
                width: `${uploadState.uploadProgress}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                transition: 'width 0.3s ease',
                borderRadius: '999px',
              }} />
            </div>
          </div>
        )}

        {uploadState.error && (
          <div style={{
            marginBottom: '20px',
            padding: '14px 16px',
            backgroundColor: '#ffebee',
            border: '1px solid #ef5350',
            borderRadius: '12px',
            animation: 'fadeIn 0.3s ease-out',
          }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
              <span style={{ fontSize: '16px', marginTop: '2px', display: 'flex' }}><FaExclamationTriangle /></span>
              <div>
                <strong style={{ color: '#c62828', fontSize: '14px' }}>Error:</strong>
                <div style={{ color: '#c62828', fontSize: '13px', marginTop: '4px' }}>
                  {uploadState.error}
                </div>
              </div>
            </div>
          </div>
        )}

        {uploadState.success && (
          <div style={{
            marginBottom: '20px',
            padding: '14px 16px',
            background: 'linear-gradient(135deg, #d4f8f0 0%, #c8f5ea 100%)',
            border: '1px solid #00d4aa',
            borderRadius: '12px',
            animation: 'fadeIn 0.3s ease-out',
          }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
              <span style={{ fontSize: '16px', marginTop: '2px', display: 'flex' }}><FaCheckCircle /></span>
              <div>
                <strong style={{ color: '#00a885', fontSize: '14px' }}>Success!</strong>
                <div style={{ color: '#00a885', fontSize: '13px', marginTop: '4px' }}>
                  Lab report uploaded successfully.
                  {uploadState.parsedTests.length > 0 && (
                    <span> {uploadState.parsedTests.length} test(s) extracted.</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            type="submit"
            disabled={!uploadState.file || uploadState.isUploading}
            style={{
              flex: 1,
              padding: '14px 24px',
              fontSize: '15px',
              fontWeight: '600',
              background: (!uploadState.file || uploadState.isUploading)
                ? '#cbd5e0'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: (!uploadState.file || uploadState.isUploading) ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              boxShadow: (!uploadState.file || uploadState.isUploading)
                ? 'none'
                : '0 4px 12px rgba(102, 126, 234, 0.3)',
            }}
            onMouseEnter={(e) => {
              if (uploadState.file && !uploadState.isUploading) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (uploadState.file && !uploadState.isUploading) {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
              }
            }}
          >
            {uploadState.isUploading ? 'Uploading...' : 'Upload Report'}
          </button>

          {(uploadState.success || uploadState.error) && (
            <button
              type="button"
              onClick={resetUpload}
              style={{
                padding: '14px 24px',
                fontSize: '15px',
                fontWeight: '600',
                backgroundColor: '#718096',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#4a5568';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#718096';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              Upload Another
            </button>
          )}
        </div>
      </form>

      {uploadState.success && uploadState.parsedTests.length > 0 && (
        <div style={{ marginTop: '28px', animation: 'fadeIn 0.4s ease-out' }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#1a202c',
            marginBottom: '16px',
          }}>Parsed Test Results</h3>
          <div style={{
            maxHeight: '350px',
            overflowY: 'auto',
            border: '2px solid #e2e8f0',
            borderRadius: '12px',
          }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
            }}>
              <thead>
                <tr style={{ background: 'linear-gradient(135deg, #f8f9fe 0%, #f0f2f8 100%)' }}>
                  <th style={{
                    padding: '14px 16px',
                    textAlign: 'left',
                    borderBottom: '2px solid #e2e8f0',
                    fontSize: '13px',
                    fontWeight: '700',
                    color: '#4a5568',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    Test Name
                  </th>
                  <th style={{
                    padding: '14px 16px',
                    textAlign: 'right',
                    borderBottom: '2px solid #e2e8f0',
                    fontSize: '13px',
                    fontWeight: '700',
                    color: '#4a5568',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    Value
                  </th>
                  <th style={{
                    padding: '14px 16px',
                    textAlign: 'center',
                    borderBottom: '2px solid #e2e8f0',
                    fontSize: '13px',
                    fontWeight: '700',
                    color: '#4a5568',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}>
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {uploadState.parsedTests.map((test, index) => (
                  <tr key={index} style={{
                    borderBottom: '1px solid #e2e8f0',
                    transition: 'background 0.2s',
                  }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#f8f9fe'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <td style={{
                      padding: '14px 16px',
                      fontSize: '14px',
                      color: '#1a202c',
                      fontWeight: '500',
                    }}>
                      {test.test_name}
                    </td>
                    <td style={{
                      padding: '14px 16px',
                      textAlign: 'right',
                      fontSize: '14px',
                      color: '#4a5568',
                      fontWeight: '600',
                    }}>
                      {test.value} {test.unit}
                    </td>
                    <td style={{
                      padding: '14px 16px',
                      textAlign: 'center',
                    }}>
                      <span style={{
                        padding: '6px 12px',
                        borderRadius: '8px',
                        fontSize: '12px',
                        fontWeight: '700',
                        color: 'white',
                        backgroundColor: getStatusColor(test.status),
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px',
                      }}>
                        {test.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default UploadReport;
