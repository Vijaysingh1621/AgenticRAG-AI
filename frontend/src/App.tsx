
import { useState } from 'react';
import UploadPDF from './components/UploadPDF';
import ChatBox from './components/ChatBox';

function App() {
  const [uploadStatus, setUploadStatus] = useState<string>("");

  const handleUploadSuccess = (message: string) => {
    setUploadStatus(message);
    setTimeout(() => setUploadStatus(""), 5000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🧠 Agentic RAG Chatbot
          </h1>
          <p className="text-gray-600 text-lg">
            Advanced AI with Speech-to-Text, MultiModal PDF Processing, Web Search & Google Drive Integration
          </p>
          
          {/* Features List */}
          <div className="mt-6 flex flex-wrap justify-center gap-4 text-sm">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">🎙️ Voice Queries</span>
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full">📄 MultiModal PDFs</span>
            <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full">🌐 Web Search</span>
            <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full">☁️ Google Drive</span>
            <span className="px-3 py-1 bg-pink-100 text-pink-800 rounded-full">📊 Smart Citations</span>
          </div>
        </div>

        {/* Upload Section */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">📄 Upload Documents</h2>
            <UploadPDF onUpload={handleUploadSuccess} />
            
            {uploadStatus && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-700">{uploadStatus}</p>
              </div>
            )}
          </div>
        </div>

        {/* Chat Section */}
        <ChatBox />

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>Powered by LangChain, FastAPI, Whisper STT, and Google Gemini</p>
        </div>
      </div>
    </div>
  );
}

export default App;
