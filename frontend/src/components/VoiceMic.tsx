import React, { useRef, useState } from 'react';
import axios from 'axios';

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
      
      // Check for supported MIME types
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/wav')) {
        mimeType = 'audio/wav';
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
      }
      
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
          formData.append('audio_file', audioBlob, 'recording.wav');
          
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
              alert('Server error processing voice query. Please try again.');
            } else {
              alert('Error processing voice query. Please check your connection and try again.');
            }
          } else {
            alert('Error processing voice query. Please try again.');
          }
        } finally {
          setProcessing(false);
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start(1000); // Collect data every second
      setRecording(true);
      
      // Auto-stop after 10 seconds
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
        }
      }, 10000);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Error accessing microphone. Please check permissions and try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div className="flex gap-2">
      <button 
        onClick={recording ? stopRecording : startRecording}
        disabled={processing}
        className={`p-3 rounded-lg text-white font-semibold ${
          recording 
            ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
            : processing
              ? 'bg-gray-500 cursor-not-allowed'
              : 'bg-green-500 hover:bg-green-600'
        }`}
      >
        {processing ? (
          <>🔄 Processing...</>
        ) : recording ? (
          <>🔴 Stop Recording</>
        ) : (
          <>🎙️ Voice Query</>
        )}
      </button>
      
      {recording && (
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          Recording... (auto-stop in 10s)
        </div>
      )}
    </div>
  );
};

export default VoiceMic;
