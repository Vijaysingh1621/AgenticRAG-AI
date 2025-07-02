import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const UploadPDF = ({ onUpload }: { onUpload: (message: string) => void }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

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

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0] && files[0].type === 'application/pdf') {
      setFile(files[0]);
    }
  };

  return (
    <div className="space-y-4">
      {/* Drag & Drop Area */}
      <div 
        className={`relative p-8 border-2 border-dashed rounded-xl transition-all duration-300 ${
          dragActive 
            ? 'border-indigo-400 bg-indigo-50' 
            : file 
              ? 'border-green-400 bg-green-50' 
              : 'border-slate-300 bg-slate-50 hover:border-slate-400 hover:bg-slate-100'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="text-center">
          <div className="mb-4">
            {file ? (
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
            ) : (
              <Upload className="w-12 h-12 text-slate-400 mx-auto" />
            )}
          </div>
          
          <input 
            type="file" 
            accept=".pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          
          <div className="space-y-2">
            <p className="text-lg font-semibold text-slate-700">
              {file ? 'PDF Ready to Upload' : 'Drop your PDF here'}
            </p>
            <p className="text-sm text-slate-500">
              {file ? 'Click upload to process' : 'or click to browse files'}
            </p>
          </div>
        </div>
      </div>

      {/* File Info */}
      {file && (
        <div className="p-4 bg-white rounded-xl border border-slate-200 animate-fade-in">
          <div className="flex items-center gap-3">
            <FileText className="w-8 h-8 text-indigo-600" />
            <div className="flex-1">
              <p className="font-semibold text-slate-800">{file.name}</p>
              <p className="text-sm text-slate-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB • PDF Document
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Upload Button */}
      <button 
        onClick={upload} 
        disabled={!file || uploading}
        className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-xl hover:from-indigo-600 hover:to-purple-600 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:scale-105 font-semibold"
      >
        {uploading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Processing PDF...
          </>
        ) : (
          <>
            <Upload className="w-5 h-5" />
            Upload & Process PDF
          </>
        )}
      </button>

      {/* Features */}
      <div className="grid grid-cols-1 gap-3 text-sm">
        {[
          { icon: <FileText className="w-4 h-4" />, text: "Automatic text extraction" },
          { icon: <AlertCircle className="w-4 h-4" />, text: "Image recognition & processing" },
          { icon: <CheckCircle className="w-4 h-4" />, text: "Smart citation tracking" }
        ].map((feature, index) => (
          <div key={index} className="flex items-center gap-2 text-slate-600">
            <div className="text-indigo-500">{feature.icon}</div>
            <span>{feature.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UploadPDF;