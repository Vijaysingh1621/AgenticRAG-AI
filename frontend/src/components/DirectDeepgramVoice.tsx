import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2, Radio, AlertCircle } from 'lucide-react';
import { DEEPGRAM_CONFIG } from '../config/deepgram';

interface DirectDeepgramVoiceProps {
  onTranscript: (text: string) => void;
  onAutoSend: (text: string) => void;
}

const DirectDeepgramVoice: React.FC<DirectDeepgramVoiceProps> = ({ onTranscript, onAutoSend }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [permissionDenied, setPermissionDenied] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const accumulatedTranscript = useRef('');
  const silenceTimer = useRef<NodeJS.Timeout | null>(null);
  const isProcessingRef = useRef(false);

  // Check if API key is configured
  const isApiKeyConfigured = () => {
    return DEEPGRAM_CONFIG.API_KEY && 
           DEEPGRAM_CONFIG.API_KEY !== 'YOUR_DEEPGRAM_API_KEY_HERE' &&
           DEEPGRAM_CONFIG.API_KEY.length > 10; // Basic validation for API key length
  };

  // Connect to Deepgram WebSocket
  const connectToDeepgram = (): Promise<boolean> => {
    return new Promise((resolve) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        resolve(true);
        return;
      }

      if (!isApiKeyConfigured()) {
        setError('Please configure your Deepgram API key in frontend/src/config/deepgram.ts');
        resolve(false);
        return;
      }

      setIsConnecting(true);
      setError(null);

      try {
        // Correct Deepgram WebSocket connection - token in header, params in query
        const wsUrl = `${DEEPGRAM_CONFIG.WS_URL}?model=${DEEPGRAM_CONFIG.MODEL}&language=${DEEPGRAM_CONFIG.LANGUAGE}&interim_results=true&punctuate=true&smart_format=true&utterance_end_ms=1500&vad_events=true`;
        
        const ws = new WebSocket(wsUrl, ['token', DEEPGRAM_CONFIG.API_KEY]);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('🔗 Connected to Deepgram WebSocket');
          setIsConnected(true);
          setIsConnecting(false);
          resolve(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'Results' && data.channel?.alternatives?.[0]?.transcript) {
              const newTranscript = data.channel.alternatives[0].transcript;
              const isFinal = data.is_final;
              
              if (newTranscript.trim()) {
                if (isFinal) {
                  // Final transcript - add to accumulated
                  accumulatedTranscript.current += ' ' + newTranscript.trim();
                  const fullTranscript = accumulatedTranscript.current.trim();
                  
                  console.log('📝 Final transcript:', fullTranscript);
                  setTranscript(fullTranscript);
                  onTranscript(fullTranscript);
                  
                  // Reset silence timer
                  if (silenceTimer.current) {
                    clearTimeout(silenceTimer.current);
                  }
                  
                  // Auto-send after 2 seconds of silence
                  silenceTimer.current = setTimeout(() => {
                    if (fullTranscript.trim() && !isProcessingRef.current) {
                      isProcessingRef.current = true;
                      console.log('🚀 Auto-sending transcript after silence:', fullTranscript);
                      onAutoSend(fullTranscript.trim());
                      
                      // Reset state
                      accumulatedTranscript.current = '';
                      setTranscript('');
                      setTimeout(() => {
                        isProcessingRef.current = false;
                      }, 1000);
                    }
                  }, 2000);
                  
                } else {
                  // Interim result - show live transcript
                  const liveTranscript = (accumulatedTranscript.current + ' ' + newTranscript).trim();
                  setTranscript(liveTranscript);
                  onTranscript(liveTranscript);
                }
              }
            } else if (data.type === 'SpeechStarted') {
              console.log('🎤 Speech started detected');
            } else if (data.type === 'UtteranceEnd') {
              console.log('🔚 Utterance ended');
            }
          } catch (err) {
            console.error('Error parsing Deepgram response:', err);
          }
        };

        ws.onerror = (error) => {
          console.error('❌ Deepgram WebSocket error:', error);
          setError('Failed to connect to Deepgram. Please check your API key and internet connection.');
          setIsConnecting(false);
          setIsConnected(false);
          resolve(false);
        };

        ws.onclose = (event) => {
          console.log('🔌 Deepgram connection closed:', event.code, event.reason);
          setIsConnected(false);
          setIsConnecting(false);
          
          // Only show errors if it's not a normal closure (1000) and not intentionally closed
          if (event.code === 4001) {
            setError('Invalid API key. Please check your Deepgram API key.');
          } else if (event.code === 4008) {
            setError('Rate limit exceeded. Please try again later.');
          } else if (event.code === 4009) {
            setError('Insufficient credits. Please check your Deepgram account.');
          } else if (event.code !== 1000 && event.code !== 1001) {
            // Don't show error for normal closures (1000) or going away (1001)
            console.warn(`Connection closed with code ${event.code}, but not showing error to user`);
          }
        };

      } catch (error) {
        console.error('Error creating WebSocket:', error);
        setError('Failed to connect to Deepgram');
        setIsConnecting(false);
        resolve(false);
      }
    });
  };

  // Request microphone permission and start recording
  const startRecording = async () => {
    try {
      setError(null);
      setPermissionDenied(false);
      setTranscript('');
      accumulatedTranscript.current = '';
      isProcessingRef.current = false;

      // Clear any existing silence timer
      if (silenceTimer.current) {
        clearTimeout(silenceTimer.current);
        silenceTimer.current = null;
      }

      // Connect to Deepgram first
      const connected = await connectToDeepgram();
      if (!connected) {
        return;
      }

      // Request microphone access with specific constraints
      console.log('🎤 Requesting microphone access...');
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });

      console.log('✅ Microphone access granted');
      streamRef.current = stream;

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 16000,
      });

      mediaRecorderRef.current = mediaRecorder;

      // Handle audio data
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(event.data);
        }
      };

      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
        setError('Recording error occurred');
        stopRecording();
      };

      // Start recording with small chunks for real-time processing
      mediaRecorder.start(250); // Send audio every 250ms
      setIsRecording(true);

      console.log('🎙️ Recording started successfully');

    } catch (error) {
      console.error('Error starting recording:', error);
      
      if (error instanceof DOMException) {
        switch (error.name) {
          case 'NotAllowedError':
            setPermissionDenied(true);
            setError('Microphone access denied. Please allow microphone permissions in your browser.');
            break;
          case 'NotFoundError':
            setError('No microphone found. Please connect a microphone and try again.');
            break;
          case 'NotReadableError':
            setError('Microphone is already in use by another application.');
            break;
          default:
            setError('Could not access microphone. Please check your browser settings.');
        }
      } else {
        setError('Failed to start recording. Please try again.');
      }
    }
  };

  // Stop recording and cleanup
  const stopRecording = () => {
    console.log('🛑 Stopping recording...');
    
    // Stop MediaRecorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
        console.log('🔇 Audio track stopped');
      });
      streamRef.current = null;
    }

    setIsRecording(false);

    // Send any remaining transcript immediately
    const finalText = accumulatedTranscript.current.trim();
    if (finalText && !isProcessingRef.current) {
      isProcessingRef.current = true;
      console.log('🚀 Sending final transcript on stop:', finalText);
      onAutoSend(finalText);
      
      // Reset state
      accumulatedTranscript.current = '';
      setTranscript('');
      setTimeout(() => {
        isProcessingRef.current = false;
      }, 1000);
    }

    // Clear silence timer
    if (silenceTimer.current) {
      clearTimeout(silenceTimer.current);
      silenceTimer.current = null;
    }

    // Close WebSocket connection gracefully after a short delay
    setTimeout(() => {
      if (wsRef.current) {
        wsRef.current.close(1000, 'Recording stopped');
        wsRef.current = null;
      }
      setIsConnected(false);
    }, 500);

    console.log('✅ Recording stopped and cleanup completed');
  };

  // Handle main button click
  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else if (!isConnecting) {
      startRecording();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (silenceTimer.current) {
        clearTimeout(silenceTimer.current);
      }
    };
  }, []);

  // Get button styling based on state
  const getButtonStyle = () => {
    if (isRecording) {
      return 'bg-red-500 hover:bg-red-600 border-red-600 animate-pulse shadow-lg shadow-red-500/50';
    }
    if (isConnecting) {
      return 'bg-gray-500 cursor-not-allowed border-gray-600';
    }
    if (error) {
      return 'bg-orange-500 hover:bg-orange-600 border-orange-600';
    }
    return 'bg-blue-500 hover:bg-blue-600 border-blue-600 hover:shadow-lg hover:shadow-blue-500/50';
  };

  // Get button icon
  const getButtonIcon = () => {
    if (isConnecting) return <Loader2 className="w-5 h-5 animate-spin" />;
    if (isRecording) return <MicOff className="w-5 h-5" />;
    if (error) return <AlertCircle className="w-5 h-5" />;
    return <Mic className="w-5 h-5" />;
  };

  // Get status text
  const getStatusText = () => {
    if (error) return 'Error - Click to retry';
    if (isConnecting) return 'Connecting to Deepgram...';
    if (isRecording) return 'Recording... Click to stop';
    return 'Click to start voice input';
  };

  return (
    <div className="flex flex-col items-center space-y-3">
      {/* Main Recording Button */}
      <button
        onClick={handleClick}
        disabled={isConnecting}
        className={`
          relative w-14 h-14 rounded-full flex items-center justify-center
          text-white transition-all duration-200 border-2 transform
          ${getButtonStyle()}
          ${isRecording ? 'scale-110' : 'hover:scale-105'}
          disabled:opacity-50 disabled:transform-none
        `}
        title={getStatusText()}
      >
        {getButtonIcon()}
      </button>

      {/* Status Indicators */}
      <div className="flex flex-col items-center space-y-2">
        <div className="flex items-center space-x-3 text-sm">
          {isConnected && (
            <div className="flex items-center text-green-500">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
              <span>Connected</span>
            </div>
          )}
          
          {isRecording && (
            <div className="flex items-center text-red-500">
              <Radio className="w-4 h-4 animate-pulse mr-1" />
              <span>Listening...</span>
            </div>
          )}
          
          {isConnecting && (
            <div className="flex items-center text-blue-500">
              <Loader2 className="w-4 h-4 animate-spin mr-1" />
              <span>Connecting...</span>
            </div>
          )}
        </div>

        {/* Status Text */}
        <div className="text-xs text-gray-500 text-center">
          {getStatusText()}
        </div>
      </div>

      {/* Live Transcript Display */}
      {transcript && (
        <div className="max-w-sm p-3 bg-blue-50 border border-blue-200 rounded-lg shadow-sm">
          <p className="text-sm text-blue-800">
            <span className="font-medium">Live:</span> {transcript}
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="max-w-sm p-3 bg-red-50 border border-red-200 rounded-lg shadow-sm">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm text-red-700">{error}</p>
              {permissionDenied && (
                <p className="text-xs text-red-600 mt-1">
                  Please click the microphone icon in your browser's address bar and allow access.
                </p>
              )}
              {error.includes('API key') && (
                <p className="text-xs text-red-600 mt-1">
                  Get your free API key at{' '}
                  <a 
                    href="https://deepgram.com" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="underline hover:text-red-800"
                  >
                    deepgram.com
                  </a>
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="text-xs text-gray-400 text-center max-w-xs">
        <div>Direct Deepgram Integration</div>
        <div className="text-gray-500 mt-1">Auto-sends after 2 seconds of silence</div>
      </div>
    </div>
  );
};

export default DirectDeepgramVoice;
