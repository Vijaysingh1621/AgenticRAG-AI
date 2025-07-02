import { useState } from 'react';
import axios from 'axios';
import VoiceMic from './VoiceMic';

type Citation = {
  citation: string;
  page: number | string;
  image?: string;
  type?: "pdf" | "web" | "google_drive";
  url?: string;
  content?: string;
  name?: string;
};

interface QueryResponse {
  response: string;
  citations: Citation[];
  sources_used?: {
    pdf_documents: number;
    google_drive_docs: number;
    web_search: number;
  };
  transcription?: string;
}

const ChatBox = () => {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [sourcesUsed, setSourcesUsed] = useState<any>(null);
  const [transcription, setTranscription] = useState("");
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const sendQuery = async (q: string) => {
    setLoading(true);
    try {
      const res = await axios.post("/query/", new URLSearchParams({ query: q }));
      handleQueryResponse(res.data);
    } catch (error) {
      console.error('Error sending query:', error);
      setAnswer("Sorry, there was an error processing your query. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleQueryResponse = (data: QueryResponse) => {
    setAnswer(data.response);
    setCitations(data.citations || []);
    setSourcesUsed(data.sources_used || null);
    if (data.transcription) {
      setTranscription(data.transcription);
    }
  };

  const handleVoiceResult = (result: QueryResponse) => {
    if (result.transcription) {
      setQuery(result.transcription);
      setTranscription(result.transcription);
    }
    handleQueryResponse(result);
  };

  const openImageModal = (imagePath: string) => {
    setSelectedImage(imagePath);
  };

  const closeImageModal = () => {
    setSelectedImage(null);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">🤖 Agentic RAG Chatbot</h1>
        
        {/* Query Input */}
        <div className="mb-4">
          <textarea 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
            placeholder="Ask me anything about your documents..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
            rows={3} 
          />
          
          {transcription && (
            <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-sm">
              <strong>Voice Input:</strong> {transcription}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mb-6">
          <button 
            onClick={() => sendQuery(query)} 
            disabled={loading || !query.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? "🔄 Processing..." : "💬 Ask"}
          </button>
          
          <VoiceMic onResult={handleVoiceResult} />
        </div>

        {/* Sources Used Summary */}
        {sourcesUsed && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-sm text-gray-700 mb-2">Sources Consulted:</h3>
            <div className="flex gap-4 text-sm">
              {sourcesUsed.pdf_documents > 0 && (
                <span className="flex items-center gap-1">
                  📄 {sourcesUsed.pdf_documents} PDF documents
                </span>
              )}
              {sourcesUsed.google_drive_docs > 0 && (
                <span className="flex items-center gap-1">
                  ☁️ {sourcesUsed.google_drive_docs} Google Drive docs
                </span>
              )}
              {sourcesUsed.web_search > 0 && (
                <span className="flex items-center gap-1">
                  🌐 Web search results
                </span>
              )}
            </div>
          </div>
        )}

        {/* Answer */}
        {answer && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-3 text-gray-800">Answer:</h2>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">{answer}</p>
            </div>
          </div>
        )}

        {/* Citations */}
        {citations.length > 0 && (
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Citations & Sources:</h3>
            <div className="space-y-3">
              {citations.map((c, i) => (
                <div key={i} className="border border-gray-200 rounded-lg p-4 bg-white">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-bold text-blue-600">{c.citation}</span>
                        <span className="text-xs px-2 py-1 rounded-full bg-gray-100">
                          {c.type === "pdf" ? "📄 PDF" : 
                           c.type === "google_drive" ? "☁️ Google Drive" : 
                           "🌐 Web Search"}
                        </span>
                        {c.type === "pdf" && (
                          <span className="text-xs text-gray-500">Page {c.page}</span>
                        )}
                      </div>
                      
                      {c.name && (
                        <p className="font-medium text-gray-700 mb-1">{c.name}</p>
                      )}
                      
                      {c.content && (
                        <p className="text-sm text-gray-600 mb-2">{c.content}</p>
                      )}
                      
                      {c.url && (
                        <a 
                          href={c.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 underline text-sm hover:text-blue-800"
                        >
                          🔗 Open Source
                        </a>
                      )}
                    </div>
                    
                    {c.image && (
                      <button
                        onClick={() => openImageModal(c.image!)}
                        className="ml-4 flex-shrink-0"
                      >
                        <img 
                          src={`/images/${c.image.split('/').pop()}`} 
                          alt={`Page ${c.page} preview`}
                          className="w-20 h-20 object-cover rounded border hover:shadow-lg transition-shadow cursor-pointer"
                        />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
          onClick={closeImageModal}
        >
          <div className="max-w-4xl max-h-4xl p-4">
            <img 
              src={`/images/${selectedImage.split('/').pop()}`}
              alt="Full size view"
              className="max-w-full max-h-full object-contain rounded"
            />
            <button
              onClick={closeImageModal}
              className="absolute top-4 right-4 text-white text-2xl bg-black bg-opacity-50 rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-75"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBox;
