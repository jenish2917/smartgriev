import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, Image as ImageIcon, Video, Loader2, Bot, User as UserIcon, X, FileImage } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Button, Input } from '@/components/atoms';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { useAuthStore } from '@/store/authStore';
import { chatbotApi } from '@/api/chatbot';
import { handleApiError } from '@/lib/axios';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  media?: {
    type: 'image' | 'video';
    url: string;
    name: string;
  };
}

export const ChatbotPage = () => {
  const { user } = useAuthStore();
  const { i18n, t } = useTranslation();
  const [sessionId] = useState<string>(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language);

  // Re-initialize welcome message when language changes
  useEffect(() => {
    if (i18n.language !== currentLanguage) {
      setMessages([{
        id: '1',
        role: 'assistant',
        content: `${t('common.welcome')}, ${user?.first_name || 'there'}! 👋 ${t('chatbot.greeting')}`,
        timestamp: new Date(),
      }]);
      setCurrentLanguage(i18n.language);
    } else if (!isInitialized) {
      setMessages([{
        id: '1',
        role: 'assistant',
        content: `${t('common.welcome')}, ${user?.first_name || 'there'}! 👋 ${t('chatbot.greeting')}`,
        timestamp: new Date(),
      }]);
      setIsInitialized(true);
    }
  }, [t, user?.first_name, i18n.language, isInitialized, currentLanguage]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [isRequestingLocation, setIsRequestingLocation] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Cleanup preview URL on unmount
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileSelect = (file: File) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      alert('File size must be less than 10MB');
      return;
    }

    const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    const validVideoTypes = ['video/mp4', 'video/webm', 'video/ogg'];
    
    if (!validImageTypes.includes(file.type) && !validVideoTypes.includes(file.type)) {
      alert('Please select a valid image (JPEG, PNG, GIF, WebP) or video (MP4, WebM, OGG) file');
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleRemoveFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (videoInputRef.current) videoInputRef.current.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        const audioFile = new File([audioBlob], 'voice-message.webm', { type: 'audio/webm' });
        
        // Send voice message
        await sendVoiceMessage(audioFile);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      setMediaRecorder(recorder);
      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check your permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      setIsRecording(false);
      setMediaRecorder(null);
    }
  };

  const requestLocation = () => {
    setIsRequestingLocation(true);
    
    if (!navigator.geolocation) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: t('chatbot.gpsNotAvailable'),
          timestamp: new Date(),
        },
      ]);
      setIsRequestingLocation(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ latitude, longitude });
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: `${t('chatbot.locationCaptured')} (${latitude.toFixed(4)}, ${longitude.toFixed(4)}). ${t('chatbot.describeIssue')}`,
            timestamp: new Date(),
          },
        ]);
        setIsRequestingLocation(false);
      },
      (error) => {
        console.error('Location error:', error);
        let errorMessage = '';
        
        if (error.code === error.PERMISSION_DENIED) {
          errorMessage += t('chatbot.locationDenied');
        } else if (error.code === error.POSITION_UNAVAILABLE) {
          errorMessage += t('chatbot.locationUnavailable');
        } else {
          errorMessage += t('chatbot.locationUnavailable');
        }
        
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: errorMessage,
            timestamp: new Date(),
          },
        ]);
        setIsRequestingLocation(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  };

  const sendVoiceMessage = async (audioFile: File) => {
    setIsLoading(true);

    // Add loading message
    const loadingMessage: Message = {
      id: `${Date.now()}-loading`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    };
    setMessages((prev) => [...prev, loadingMessage]);

    try {
      const response = await chatbotApi.sendVoiceMessage(audioFile, i18n.language);
      
      // Add user message showing voice was sent
      setMessages((prev) => [
        ...prev.filter((msg) => msg.id !== loadingMessage.id),
        {
          id: Date.now().toString(),
          role: 'user',
          content: `🎤 Voice message: "${response.transcription || 'Audio recorded'}"`,
          timestamp: new Date(),
        },
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.response || 'I heard your message. How can I help you?',
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      // Remove loading message and add error
      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== loadingMessage.id)
          .concat({
            id: Date.now().toString(),
            role: 'assistant',
            content: `Sorry, I couldn't process your voice message: ${handleApiError(error)}. Please try again.`,
            timestamp: new Date(),
          })
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if ((!inputValue.trim() && !selectedFile) || isLoading) return;

    const messageContent = inputValue.trim() || (selectedFile ? `[${selectedFile.type.startsWith('image') ? 'Image' : 'Video'} uploaded]` : '');
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent,
      timestamp: new Date(),
      media: selectedFile && previewUrl ? {
        type: selectedFile.type.startsWith('image') ? 'image' : 'video',
        url: previewUrl,
        name: selectedFile.name,
      } : undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageText = inputValue;
    const fileToSend = selectedFile;
    const currentLocation = userLocation;
    setInputValue('');
    setSelectedFile(null);
    setPreviewUrl(null);
    setIsLoading(true);

    // Add loading message
    const loadingMessage: Message = {
      id: `${Date.now()}-loading`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    };
    setMessages((prev) => [...prev, loadingMessage]);

    try {
      let response;
      
      if (fileToSend) {
        // Send image or video to chatbot with location if available - use current language
        response = await chatbotApi.sendImage(fileToSend, messageText, currentLocation, i18n.language);
      } else {
        // Send text message with location if available - use current language and session ID
        response = await chatbotApi.sendMessage(messageText, i18n.language, currentLocation, sessionId);
      }

      // Remove loading message and add real response
      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== loadingMessage.id)
          .concat({
            id: Date.now().toString(),
            role: 'assistant',
            content: response.response || 'I analyzed your message. How can I help you further?',
            timestamp: new Date(),
          })
      );
    } catch (error) {
      console.error('Chatbot error:', error);
      // Remove loading message and add error
      setMessages((prev) =>
        prev
          .filter((msg) => msg.id !== loadingMessage.id)
          .concat({
            id: Date.now().toString(),
            role: 'assistant',
            content: `Sorry, I encountered an error: ${handleApiError(error)}. Please try again.`,
            timestamp: new Date(),
          })
      );
    } finally {
      setIsLoading(false);
      handleRemoveFile();
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickReplies = [
    t('chatbot.fileComplaint'),
    t('chatbot.reportPothole'),
    t('chatbot.garbageIssue'),
    t('chatbot.streetLight'),
  ];

  const handleQuickReply = (reply: string) => {
    if (reply === t('chatbot.fileComplaint')) {
      // Trigger location request flow
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'user',
          content: reply,
          timestamp: new Date(),
        },
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: t('chatbot.locationPrompt'),
          timestamp: new Date(),
        },
      ]);
      
      // Add location buttons as quick replies
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 2).toString(),
            role: 'assistant',
            content: t('chatbot.chooseOption'),
            timestamp: new Date(),
          },
        ]);
      }, 500);
    } else {
      setInputValue(reply);
    }
  };

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-120px)] flex flex-col bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        {/* Chat Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {t('chatbot.aiAssistant')}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {t('chatbot.alwaysHelp')}
            </p>
          </div>
          <div className="ml-auto">
            <span className="flex items-center gap-2 text-xs text-success-600 dark:text-success-400">
              <span className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></span>
              {t('chatbot.online')}
            </span>
          </div>
        </div>

        {/* Messages Area */}
        <div 
          className="flex-1 overflow-y-auto p-4 space-y-4"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {isDragging && (
            <div className="absolute inset-0 bg-primary-500/10 backdrop-blur-sm border-2 border-dashed border-primary-500 rounded-xl flex items-center justify-center z-10">
              <div className="text-center">
                <FileImage className="w-16 h-16 text-primary-500 mx-auto mb-2" />
                <p className="text-lg font-semibold text-primary-600 dark:text-primary-400">
                  {t('chatbot.dropImage')}
                </p>
              </div>
            </div>
          )}
          
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`flex gap-3 max-w-[80%] ${
                    message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.role === 'user'
                        ? 'bg-primary-100 dark:bg-primary-900/20'
                        : 'bg-gradient-to-br from-primary-500 to-secondary-500'
                    }`}
                  >
                    {message.role === 'user' ? (
                      <UserIcon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>

                  {/* Message Bubble */}
                  <div
                    className={`rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    }`}
                  >
                    {message.isLoading ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm">Analyzing...</span>
                      </div>
                    ) : (
                      <>
                        {/* Media Preview */}
                        {message.media && (
                          <div className="mb-2">
                            {message.media.type === 'image' ? (
                              <img
                                src={message.media.url}
                                alt={message.media.name}
                                className="max-w-full rounded-lg max-h-64 object-cover"
                              />
                            ) : (
                              <video
                                src={message.media.url}
                                controls
                                className="max-w-full rounded-lg max-h-64"
                              >
                                Your browser does not support the video tag.
                              </video>
                            )}
                            <p className="text-xs mt-1 opacity-75">
                              {message.media.name}
                            </p>
                          </div>
                        )}
                        
                        {/* Text Content */}
                        <p className="text-sm whitespace-pre-wrap">
                          {message.content}
                        </p>
                        <p
                          className={`text-xs mt-1 ${
                            message.role === 'user'
                              ? 'text-primary-100'
                              : 'text-gray-500 dark:text-gray-400'
                          }`}
                        >
                          {message.timestamp.toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Replies */}
        {messages.length <= 2 && (
          <div className="px-4 pb-2">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
              {t('chatbot.quickActions')}
            </p>
            <div className="flex flex-wrap gap-2">
              {quickReplies.map((reply) => (
                <button
                  key={reply}
                  onClick={() => handleQuickReply(reply)}
                  className="px-3 py-1.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  {reply}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Location Request Buttons */}
        {!isRequestingLocation && messages.length > 0 && messages[messages.length - 1]?.content.includes('📍') && (
          <div className="px-4 pb-2">
            <div className="flex gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={requestLocation}
                leftIcon={<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>}
              >
                {t('chatbot.enableGPS')}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setMessages((prev) => [
                    ...prev,
                    {
                      id: Date.now().toString(),
                      role: 'assistant',
                      content: t('chatbot.enterAddressManually'),
                      timestamp: new Date(),
                    },
                  ]);
                }}
              >
                {t('chatbot.enterManually')}
              </Button>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          {/* Recording Indicator */}
          {isRecording && (
            <div className="mb-3 flex items-center gap-2 px-4 py-2 bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-lg">
              <div className="w-3 h-3 bg-error-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-error-700 dark:text-error-400">
                {t('chatbot.recording')}
              </span>
            </div>
          )}

          {/* File Preview */}
          {selectedFile && previewUrl && (
            <div className="mb-3 relative inline-block">
              <div className="relative rounded-lg overflow-hidden border-2 border-primary-500">
                {selectedFile.type.startsWith('image') ? (
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="max-h-32 max-w-xs object-cover"
                  />
                ) : (
                  <video
                    src={previewUrl}
                    className="max-h-32 max-w-xs"
                    controls
                  />
                )}
                <button
                  onClick={handleRemoveFile}
                  className="absolute top-1 right-1 p-1 bg-error-500 text-white rounded-full hover:bg-error-600 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
              </p>
            </div>
          )}

          <div className="flex items-end gap-2">
            {/* Image Upload */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileSelect(file);
              }}
              className="hidden"
              title="Upload image file"
              placeholder="Upload image"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Upload image"
              aria-label="Upload image"
            >
              <ImageIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>

            {/* Video Upload */}
            <input
              ref={videoInputRef}
              type="file"
              accept="video/mp4,video/webm,video/ogg"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileSelect(file);
              }}
              className="hidden"
              title="Upload video file"
              placeholder="Upload video"
            />
            <button
              onClick={() => videoInputRef.current?.click()}
              disabled={isLoading}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Upload video"
              aria-label="Upload video"
            >
              <Video className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>

            {/* Voice Recording */}
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              className={`p-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                isRecording
                  ? 'bg-error-500 text-white hover:bg-error-600 animate-pulse'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
              title={isRecording ? 'Stop recording' : 'Start voice recording'}
            >
              <Mic className={`w-5 h-5 ${isRecording ? 'text-white' : 'text-gray-500 dark:text-gray-400'}`} />
            </button>

            {/* Text Input */}
            <div className="flex-1">
              <Input
                ref={inputRef}
                type="text"
                placeholder={t('chatbot.typeMessage')}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                wrapperClassName="mb-0"
              />
            </div>

            {/* Send Button */}
            <Button
              variant="primary"
              size="md"
              onClick={handleSendMessage}
              disabled={(!inputValue.trim() && !selectedFile) || isLoading}
              className="h-10"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};
