import React, { useState } from 'react';
import axios from 'axios';

const UploadPDF = ({ onUpload }: { onUpload: (message: string) => void }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const upload = async () => {
    if (!file) return;
    
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const response = await axios.post("/upload-pdf/", formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const message = `✅ ${response.data.message} (${response.data.pages_processed} pages processed, ${response.data.images_extracted} images extracted)`;
      onUpload(message);
      setFile(null);
    } catch (error) {
      console.error('Upload error:', error);
      onUpload("❌ Error uploading PDF. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-gray-400 transition-colors">
      <div className="text-center">
        <input 
          type="file" 
          accept=".pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mb-3 block w-full text-sm text-gray-500
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-full file:border-0
                     file:text-sm file:font-semibold
                     file:bg-blue-50 file:text-blue-700
                     hover:file:bg-blue-100"
        />
        
        {file && (
          <p className="text-sm text-gray-600 mb-3">
            Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
        
        <button 
          onClick={upload} 
          disabled={!file || uploading}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {uploading ? "🔄 Uploading..." : "📄 Upload PDF"}
        </button>
      </div>
    </div>
  );
};

export default UploadPDF;
