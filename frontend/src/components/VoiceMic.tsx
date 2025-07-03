import React, { useRef, useState } from 'react';
import axios from 'axios';
import { Mic, MicOff, Loader2, Radio } from 'lucide-react';

interface VoiceResponse {
  response: string;
  transcription: string;
  citations: Array<{
    citation: string;
    page: number | string;
    image?: string;
    type: "pdf" | "web" | "google_drive";
    url?: string;
    content?: string;
    name?: string;
  }>;
}

const VoiceMic = ({ onResult }: { onResult: (result: VoiceResponse) => void }) => {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          sampleSize: 16,
          channelCount: 1
        }
      });
      
      // Check for supported MIME types - prefer WAV if available
      let mimeType = 'audio/wav';
      if (!MediaRecorder.isTypeSupported('audio/wav')) {
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
          mimeType = 'audio/webm';
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          mimeType = 'audio/mp4';
        } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
          mimeType = 'audio/ogg;codecs=opus';
        } else {
          console.warn('No supported audio format found, using default');
          mimeType = 'audio/webm';
        }
      }
      
      console.log(`🎵 Using MIME type: ${mimeType}`);
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      
      const audioChunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        setRecording(false);
        setProcessing(true);
        
        try {
          const audioBlob = new Blob(audioChunks, { type: mimeType });
          console.log(`Audio recorded: ${audioBlob.size} bytes, type: ${mimeType}`);
          
          const formData = new FormData();
          // Use appropriate file extension based on MIME type
          let filename = 'recording.wav';
          if (mimeType.includes('webm')) {
            filename = 'recording.webm';
          } else if (mimeType.includes('mp4')) {
            filename = 'recording.mp4';
          } else if (mimeType.includes('ogg')) {
            filename = 'recording.ogg';
          }
          
          formData.append('audio_file', audioBlob, filename);
          console.log(`🎤 Uploading audio as: ${filename}`);
          
          const response = await axios.post('/voice-query/', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            timeout: 30000, // 30 second timeout
          });
          
          onResult(response.data);
        } catch (error) {
          console.error('Error processing voice query:', error);
          if (axios.isAxiosError(error)) {
            if (error.code === 'ECONNABORTED') {
              alert('Voice processing timed out. Please try a shorter recording.');
            } else if (error.response?.status === 500) {
              const errorMsg = error.response?.data?.detail || 'Server error processing voice query';
              if (errorMsg.includes('WebM')) {
                alert('Voice recording format not fully supported. Please try:\\n1. Using Chrome or Edge browser\\n2. Recording again\\n3. Keeping recording under 10 seconds');
              } else if (errorMsg.includes('FFmpeg') || errorMsg.includes('format')) {
                alert('Audio format issue. Please try:\\n1. Using a different browser (Chrome/Edge recommended)\\n2. Recording again\\n3. Speaking more clearly');
              } else {
                alert(`Voice processing error: ${errorMsg}`);
              }
            } else {
              alert('Network error. Please check your connection and try again.');
            }
          } else {
            alert('Error processing voice query. Please try again.');
          }
        } finally {
          setProcessing(false);
        }
      };
      
      setRecording(true);
      mediaRecorder.start();
      
      // Auto-stop after 30 seconds
      setTimeout(() => {
        if (mediaRecorderRef.current && recording) {
          stopRecording();
        }
      }, 30000);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      // Stop all tracks to free up the microphone
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  const handleClick = () => {
    if (recording) {
      stopRecording();
    } else if (!processing) {
      startRecording();
    }
  };

  return (
    <div className="flex items-center">
      <button
        onClick={handleClick}
        disabled={processing}
        className={`
          p-3 rounded-full transition-all duration-200 border-2
          ${recording 
            ? 'bg-red-500 border-red-600 hover:bg-red-600 shadow-lg scale-110' 
            : processing
            ? 'bg-gray-400 border-gray-500 cursor-not-allowed'
            : 'bg-blue-500 border-blue-600 hover:bg-blue-600 hover:scale-105 shadow-md'
          }
          disabled:opacity-50
        `}
        title={
          processing 
            ? 'Processing audio...' 
            : recording 
            ? 'Stop recording' 
            : 'Start voice recording'
        }
      >
        {processing ? (
          <Loader2 className="w-4 h-4 animate-spin text-white" />
        ) : recording ? (
          <MicOff className="w-4 h-4 text-white" />
        ) : (
          <Mic className="w-4 h-4 text-white" />
        )}
      </button>
      
      {recording && (
        <div className="ml-3 flex items-center">
          <Radio className="w-4 h-4 text-red-500 animate-pulse" />
          <span className="ml-2 text-sm text-gray-600">Recording...</span>
        </div>
      )}
      
      {processing && (
        <div className="ml-3 flex items-center">
          <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
          <span className="ml-2 text-sm text-gray-600">Processing...</span>
        </div>
      )}
    </div>
  );
};

export default VoiceMic;
