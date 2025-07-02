import { useState, useEffect } from 'react';
import { 
  Brain, 
  Sparkles, 
  Upload, 
  MessageCircle, 
  Zap, 
  Rocket,
  Shield,
  Globe2,
  Database,
  Code2,
  Layers3,
  Star,
  ArrowRight,
  Bot
} from 'lucide-react';
import UploadPDF from './components/UploadPDF';
import ChatUI from './components/ChatUI';
import { Skeleton } from '@/components/ui/Skeleton';

function App() {
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);

  const handleUploadSuccess = (message: string) => {
    setUploadStatus(message);
    setTimeout(() => setUploadStatus(""), 5000);
  };

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setIsLoading(false), 2000);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="text-center mb-12">
            <Skeleton className="h-16 w-96 mx-auto mb-4 bg-gray-800" />
            <Skeleton className="h-6 w-[600px] mx-auto mb-8 bg-gray-800" />
            
            <div className="flex justify-center gap-4 mb-8">
              {[1,2,3,4,5].map((i) => (
                <Skeleton key={i} className="h-20 w-32 bg-gray-800" />
              ))}
            </div>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1">
              <Skeleton className="h-[500px] w-full bg-gray-800" />
            </div>
            <div className="lg:col-span-2">
              <Skeleton className="h-[500px] w-full bg-gray-800" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-blue-900/20 to-teal-900/20"></div>
        <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-4000"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-7xl">
        {/* Hero Section */}
        <div className="text-center mb-16 animate-fade-in">
          <div className="flex items-center justify-center gap-4 mb-10">
            {/* <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-cyan-600 rounded-2xl blur opacity-75 animate-pulse"></div>
              <div className="relative bg-black p-4 rounded-2xl border border-gray-800">
                <Bot className="w-12 h-12 text-transparent bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text" style={{WebkitBackgroundClip: 'text'}} />
              </div>
            </div> */}
            <h1 className="text-6xl md:text-7xl font-black bg-gradient-to-r from-white via-gray-300 to-gray-500 bg-clip-text text-transparent">
              Agentic
            </h1>
            <div className="flex items-center gap-2">
              <Sparkles className="w-8 h-8 text-yellow-400 animate-spin" />
              <span className="text-6xl md:text-7xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
                RAG
              </span>
            </div>
          </div>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto leading-relaxed font-light">
            Experience the future of AI interaction with{' '}
            <span className="text-transparent bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text font-semibold">
              multimodal intelligence
            </span>
            , voice recognition, and semantic search
          </p>
          
          {/* Feature Pills */}
          <div className="flex flex-wrap justify-center gap-3 mb-12">
            {[
              { icon: Rocket, label: "Voice Queries", gradient: "from-red-400 to-pink-400" },
              { icon: Shield, label: "Secure PDFs", gradient: "from-blue-400 to-indigo-400" },
              { icon: Globe2, label: "Web Intelligence", gradient: "from-green-400 to-teal-400" },
              { icon: Database, label: "Cloud Storage", gradient: "from-purple-400 to-violet-400" },
              { icon: Code2, label: "Smart Citations", gradient: "from-yellow-400 to-orange-400" }
            ].map((feature, index) => (
              <div 
                key={index}
                className={`group relative px-6 py-3 rounded-full bg-gradient-to-r ${feature.gradient} opacity-80 hover:opacity-100 transform hover:scale-110 transition-all duration-300 cursor-pointer animate-fade-in`}
                style={{ animationDelay: `${index * 200}ms` }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative flex items-center gap-2 text-white font-medium">
                  <feature.icon className="w-4 h-4" />
                  <span>{feature.label}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto mb-16">
            {[
              { icon: Zap, value: "99.9%", label: "Uptime", color: "text-yellow-400" },
              { icon: Layers3, value: "10ms", label: "Response", color: "text-green-400" },
              { icon: Star, value: "4.9★", label: "Rating", color: "text-purple-400" },
              { icon: Shield, value: "256-bit", label: "Security", color: "text-cyan-400" }
            ].map((stat, index) => (
              <div key={index} className="text-center group animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                <stat.icon className={`w-6 h-6 ${stat.color} mx-auto mb-2 group-hover:scale-110 transition-transform`} />
                <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-5 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-2">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600/50 to-cyan-600/50 rounded-3xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative bg-gray-900/50 backdrop-blur-xl rounded-3xl border border-gray-800/50 p-8 hover:border-gray-700/50 transition-all duration-500">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-2xl">
                    <Upload className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">Document Hub</h2>
                    <p className="text-gray-400">Intelligent document processing</p>
                  </div>
                </div>
                
                <UploadPDF onUpload={handleUploadSuccess} />
                
                {uploadStatus && (
                  <div className="mt-6 p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-2xl animate-fade-in">
                    <p className="text-green-300 font-medium">{uploadStatus}</p>
                  </div>
                )}

                {/* Pro Tips */}
                <div className="mt-8 p-6 bg-gradient-to-r from-gray-800/50 to-gray-900/50 rounded-2xl border border-gray-700/30">
                  <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-5 h-5 text-yellow-400" />
                    <h3 className="font-semibold text-white">AI Features</h3>
                  </div>
                  <ul className="space-y-3 text-sm text-gray-300">
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3 h-3 text-purple-400" />
                      Advanced multimodal analysis
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3 h-3 text-cyan-400" />
                      Real-time image understanding
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="w-3 h-3 text-pink-400" />
                      Intelligent citation mapping
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Section */}
          <div className="lg:col-span-3">
            <div className="relative group h-full">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-600/50 to-purple-600/50 rounded-3xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="relative bg-gray-900/50 backdrop-blur-xl rounded-3xl border border-gray-800/50 hover:border-gray-700/50 transition-all duration-500 h-full flex flex-col">
                <div className="flex items-center gap-4 p-8 border-b border-gray-800/50">
                  <div className="p-3 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-2xl">
                    <MessageCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">AI Assistant</h2>
                    <p className="text-gray-400">Powered by advanced AI models</p>
                  </div>
                </div>
                <div className="flex-1">
                  <ChatUI />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-20 text-center">
          <div className="inline-flex items-center gap-3 px-8 py-4 bg-gray-900/60 backdrop-blur-xl rounded-full border border-gray-800/50">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-gray-300 text-sm font-medium">System Online</span>
            </div>
            <div className="w-px h-4 bg-gray-700"></div>
            <span className="text-gray-400 text-sm">
              Powered by LangChain • FastAPI • Whisper • Gemini
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;