import { useState } from 'react';
import axios from 'axios';
import { 
  Send, 
  Loader2, 
  FileText, 
  Globe, 
  Cloud, 
  ExternalLink, 
  ZoomIn,
  Bot,
  User,
  Sparkles,
  BookOpen,
  Activity
} from 'lucide-react';
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

const ChatUI = () => {
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

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'pdf': return <FileText className="w-4 h-4" />;
      case 'google_drive': return <Cloud className="w-4 h-4" />;
      case 'web': return <Globe className="w-4 h-4" />;
      default: return <BookOpen className="w-4 h-4" />;
    }
  };

  const getSourceColor = (type: string) => {
    switch (type) {
      case 'pdf': return 'from-blue-500 to-cyan-500';
      case 'google_drive': return 'from-green-500 to-emerald-500';
      case 'web': return 'from-purple-500 to-violet-500';
      default: return 'from-gray-500 to-slate-500';
    }
  };

  return (
    <div className="p-6">
      {/* Query Input Section */}
      <div className="mb-6">
        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <User className="w-5 h-5 text-gray-400" />
            <span className="font-medium text-gray-300">Your Question</span>
          </div>
          <textarea 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
            placeholder="Ask me anything about your documents... I can search through PDFs, web content, and Google Drive files!"
            className="w-full p-4 bg-gray-800/50 border border-gray-700 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200 resize-none backdrop-blur-sm text-white placeholder-gray-400" 
            rows={3} 
          />
          
          {transcription && (
            <div className="mt-3 p-3 bg-gradient-to-r from-purple-500/20 to-cyan-500/20 border border-purple-500/30 rounded-xl animate-fade-in">
              <div className="flex items-center gap-2 mb-1">
                <Activity className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-purple-300">Voice Input Detected:</span>
              </div>
              <p className="text-gray-300">{transcription}</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mt-4">
          <button 
            onClick={() => sendQuery(query)} 
            disabled={loading || !query.trim()}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-cyan-500 text-white rounded-xl hover:from-purple-600 hover:to-cyan-600 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-lg hover:scale-105 font-medium"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Send
              </>
            )}
          </button>
          
          <VoiceMic onResult={handleVoiceResult} />
        </div>
      </div>

      {/* Sources Used Summary */}
      {sourcesUsed && (
        <div className="mb-6 p-4 bg-gradient-to-r from-gray-800/50 to-gray-900/50 rounded-xl border border-gray-700/50 animate-fade-in">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <h3 className="font-semibold text-gray-200">Sources Consulted</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {sourcesUsed.pdf_documents > 0 && (
              <div className="flex items-center gap-2 p-3 bg-gray-800/70 rounded-lg border border-blue-500/30">
                <FileText className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-medium text-gray-300">
                  {sourcesUsed.pdf_documents} PDF documents
                </span>
              </div>
            )}
            {sourcesUsed.google_drive_docs > 0 && (
              <div className="flex items-center gap-2 p-3 bg-gray-800/70 rounded-lg border border-green-500/30">
                <Cloud className="w-4 h-4 text-green-400" />
                <span className="text-sm font-medium text-gray-300">
                  {sourcesUsed.google_drive_docs} Google Drive docs
                </span>
              </div>
            )}
            {sourcesUsed.web_search > 0 && (
              <div className="flex items-center gap-2 p-3 bg-gray-800/70 rounded-lg border border-purple-500/30">
                <Globe className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-gray-300">
                  Web search results
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Answer Section */}
      {answer && (
        <div className="mb-6 animate-fade-in">
          <div className="flex items-center gap-2 mb-4">
            <Bot className="w-5 h-5 text-cyan-400" />
            <span className="font-semibold text-gray-200 text-lg">AI Response</span>
          </div>
          <div className="bg-gradient-to-r from-gray-800/60 via-gray-900/60 to-gray-800/60 p-6 rounded-xl border border-gray-700/50 backdrop-blur-sm">
            <p className="text-gray-200 whitespace-pre-wrap leading-relaxed text-lg">{answer}</p>
          </div>
        </div>
      )}

      {/* Citations Section */}
      {citations.length > 0 && (
        <div className="animate-fade-in">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-200">Citations & Sources</h3>
            <span className="px-2 py-1 bg-gray-800/70 text-gray-400 rounded-full text-xs font-medium">
              {citations.length} sources
            </span>
          </div>
          <div className="space-y-4">
            {citations.map((c, i) => (
              <div key={i} className="group bg-gray-800/50 border border-gray-700/50 rounded-xl p-5 hover:shadow-lg hover:border-gray-600/50 transition-all duration-300 backdrop-blur-sm">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`p-2 bg-gradient-to-r ${getSourceColor(c.type || 'pdf')} text-white rounded-lg`}>
                        {getSourceIcon(c.type || 'pdf')}
                      </div>
                      <div>
                        <span className="font-bold text-cyan-400 text-lg">{c.citation}</span>
                        {c.type === "pdf" && (
                          <span className="ml-2 text-sm text-gray-400 bg-gray-800/70 px-2 py-1 rounded-full">
                            Page {c.page}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    {c.name && (
                      <h4 className="font-semibold text-gray-200 mb-2">{c.name}</h4>
                    )}
                    
                    {c.content && (
                      <p className="text-gray-300 mb-3 leading-relaxed">{c.content}</p>
                    )}
                    
                    {c.url && (
                      <a 
                        href={c.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-cyan-400 hover:text-cyan-300 font-medium transition-colors duration-200"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Open Source
                      </a>
                    )}
                  </div>
                  
                  {c.image && (
                    <button
                      onClick={() => openImageModal(c.image!)}
                      className="ml-4 flex-shrink-0 group-hover:scale-105 transition-transform duration-200"
                    >
                      <div className="relative">
                        <img 
                          src={`/images/${c.image.split('/').pop()}`} 
                          alt={`Page ${c.page} preview`}
                          className="w-24 h-24 object-cover rounded-lg border-2 border-gray-600 hover:border-cyan-400 transition-all duration-200"
                        />
                        <div className="absolute inset-0 bg-black/0 hover:bg-black/20 rounded-lg flex items-center justify-center transition-all duration-200">
                          <ZoomIn className="w-5 h-5 text-white opacity-0 hover:opacity-100 transition-opacity duration-200" />
                        </div>
                      </div>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in"
          onClick={closeImageModal}
        >
          <div className="max-w-5xl max-h-[90vh] relative animate-scale-in">
            <img 
              src={`/images/${selectedImage.split('/').pop()}`}
              alt="Full size view"
              className="max-w-full max-h-full object-contain rounded-xl shadow-2xl"
            />
            <button
              onClick={closeImageModal}
              className="absolute -top-4 -right-4 text-white bg-black/50 hover:bg-black/70 rounded-full w-10 h-10 flex items-center justify-center transition-all duration-200 hover:scale-110"
            >
              ×
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatUI;