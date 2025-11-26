import { useState, ChangeEvent, FormEvent } from 'react';
import apiClient, { UploadReportResponse, ParsedTest } from '../api/client';

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
        return '#28a745';
      case 'LOW':
        return '#ffc107';
      case 'HIGH':
        return '#fd7e14';
      case 'CRITICAL_LOW':
      case 'CRITICAL_HIGH':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  return (
    <div style={{ 
      maxWidth: '600px', 
      margin: '20px auto', 
      padding: '20px',
      border: '1px solid #ddd',
      borderRadius: '8px',
      backgroundColor: '#fff',
    }}>
      <h2 style={{ marginTop: 0 }}>Upload Lab Report</h2>
      
      <form onSubmit={handleUpload}>
        <div style={{ marginBottom: '15px' }}>
          <label 
            htmlFor="file-input" 
            style={{ 
              display: 'block', 
              marginBottom: '8px',
              fontWeight: 'bold',
            }}
          >
            Select Lab Report (JPEG, PNG, or PDF)
          </label>
          <input
            type="file"
            id="file-input"
            accept=".jpg,.jpeg,.png,.pdf"
            onChange={handleFileChange}
            disabled={uploadState.isUploading}
            style={{
              width: '100%',
              padding: '8px',
              fontSize: '14px',
              border: '1px solid #ccc',
              borderRadius: '4px',
            }}
          />
          <small style={{ color: '#6c757d', fontSize: '12px' }}>
            Maximum file size: 10MB
          </small>
        </div>

        {uploadState.file && !uploadState.success && (
          <div style={{ 
            marginBottom: '15px',
            padding: '10px',
            backgroundColor: '#e7f3ff',
            borderRadius: '4px',
          }}>
            <strong>Selected file:</strong> {uploadState.file.name} 
            ({(uploadState.file.size / 1024 / 1024).toFixed(2)} MB)
          </div>
        )}

        {uploadState.isUploading && (
          <div style={{ marginBottom: '15px' }}>
            <div style={{ 
              marginBottom: '5px',
              fontSize: '14px',
              color: '#007bff',
            }}>
              Uploading... {uploadState.uploadProgress}%
            </div>
            <div style={{
              width: '100%',
              height: '20px',
              backgroundColor: '#e9ecef',
              borderRadius: '4px',
              overflow: 'hidden',
            }}>
              <div style={{
                width: `${uploadState.uploadProgress}%`,
                height: '100%',
                backgroundColor: '#007bff',
                transition: 'width 0.3s ease',
              }} />
            </div>
          </div>
        )}

        {uploadState.error && (
          <div style={{
            marginBottom: '15px',
            padding: '12px',
            backgroundColor: '#f8d7da',
            border: '1px solid #f5c6cb',
            borderRadius: '4px',
            color: '#721c24',
          }}>
            <strong>Error:</strong> {uploadState.error}
          </div>
        )}

        {uploadState.success && (
          <div style={{
            marginBottom: '15px',
            padding: '12px',
            backgroundColor: '#d4edda',
            border: '1px solid #c3e6cb',
            borderRadius: '4px',
            color: '#155724',
          }}>
            <strong>Success!</strong> Lab report uploaded successfully.
            {uploadState.parsedTests.length > 0 && (
              <span> {uploadState.parsedTests.length} test(s) extracted.</span>
            )}
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            type="submit"
            disabled={!uploadState.file || uploadState.isUploading}
            style={{
              flex: 1,
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: (!uploadState.file || uploadState.isUploading) ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: (!uploadState.file || uploadState.isUploading) ? 'not-allowed' : 'pointer',
            }}
          >
            {uploadState.isUploading ? 'Uploading...' : 'Upload'}
          </button>

          {(uploadState.success || uploadState.error) && (
            <button
              type="button"
              onClick={resetUpload}
              style={{
                padding: '10px 20px',
                fontSize: '16px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Upload Another
            </button>
          )}
        </div>
      </form>

      {uploadState.success && uploadState.parsedTests.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Parsed Test Results</h3>
          <div style={{ 
            maxHeight: '300px',
            overflowY: 'auto',
            border: '1px solid #ddd',
            borderRadius: '4px',
          }}>
            <table style={{ 
              width: '100%',
              borderCollapse: 'collapse',
            }}>
              <thead>
                <tr style={{ backgroundColor: '#f8f9fa' }}>
                  <th style={{ 
                    padding: '10px',
                    textAlign: 'left',
                    borderBottom: '2px solid #dee2e6',
                  }}>
                    Test Name
                  </th>
                  <th style={{ 
                    padding: '10px',
                    textAlign: 'right',
                    borderBottom: '2px solid #dee2e6',
                  }}>
                    Value
                  </th>
                  <th style={{ 
                    padding: '10px',
                    textAlign: 'center',
                    borderBottom: '2px solid #dee2e6',
                  }}>
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {uploadState.parsedTests.map((test, index) => (
                  <tr key={index} style={{ 
                    borderBottom: '1px solid #dee2e6',
                  }}>
                    <td style={{ padding: '10px' }}>
                      {test.test_name}
                    </td>
                    <td style={{ 
                      padding: '10px',
                      textAlign: 'right',
                    }}>
                      {test.value} {test.unit}
                    </td>
                    <td style={{ 
                      padding: '10px',
                      textAlign: 'center',
                    }}>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        color: 'white',
                        backgroundColor: getStatusColor(test.status),
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
