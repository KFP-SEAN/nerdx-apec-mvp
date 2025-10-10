'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Send,
  Sparkles,
  ShoppingBag,
  Video,
  MessageCircle,
  Loader2,
  Bot,
} from 'lucide-react';
import ChatInterface from '@/components/ChatInterface';
import ProductCard from '@/components/ProductCard';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  products?: Array<{
    id: string;
    name: string;
    price: number;
    image_url: string;
    description: string;
  }>;
  videos?: Array<{
    id: string;
    title: string;
    thumbnail_url: string;
    video_url: string;
  }>;
}

interface SessionInfo {
  session_id: string;
  context: string;
  total_messages: number;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initializeChat();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeChat = async () => {
    try {
      const response = await api.post('/chat/init', {
        user_preferences: {
          language: 'en',
          currency: 'USD',
        },
      });

      setSessionInfo(response.data);

      // Add welcome message
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content:
            "Hello! I'm Maeju, your AI shopping assistant. I can help you discover amazing products from our video catalog, answer questions, and provide personalized recommendations. What are you looking for today?",
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error('Failed to initialize chat:', error);
      toast.error('Failed to start chat session');
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await api.post('/chat/message', {
        session_id: sessionInfo?.session_id,
        message: inputMessage,
        context: {
          previous_products: messages
            .filter((m) => m.products)
            .flatMap((m) => m.products?.map((p) => p.id)),
        },
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date(),
        products: response.data.products,
        videos: response.data.videos,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Update session info
      if (response.data.session_info) {
        setSessionInfo(response.data.session_info);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content:
          "I'm sorry, I encountered an error. Please try again or rephrase your question.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const suggestedQuestions = [
    'Show me products featured in Sam Altman videos',
    'What are the trending electronics?',
    'I need a gift for a tech enthusiast',
    'Find products under $100',
    'Show me the latest fashion items',
  ];

  const handleSuggestedQuestion = (question: string) => {
    setInputMessage(question);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center">
              <Bot className="w-9 h-9 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-3xl font-bold">
                Chat with <span className="text-gradient">Maeju AI</span>
              </h1>
              <p className="text-gray-600">Your personal shopping assistant</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4 text-sm">
            <div className="flex items-center gap-2 text-gray-600">
              <Sparkles className="w-4 h-4 text-primary-600" />
              <span>AI-Powered Recommendations</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <Video className="w-4 h-4 text-primary-600" />
              <span>Video Product Discovery</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <ShoppingBag className="w-4 h-4 text-primary-600" />
              <span>Instant Shopping Help</span>
            </div>
          </div>
        </motion.div>

        {/* Chat Container */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Chat Area */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="card h-[700px] flex flex-col"
            >
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((message) => (
                  <div key={message.id}>
                    <ChatInterface message={message} />

                    {/* Product Recommendations */}
                    {message.products && message.products.length > 0 && (
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                        {message.products.map((product) => (
                          <ProductCard
                            key={product.id}
                            product={product}
                            viewMode="grid"
                          />
                        ))}
                      </div>
                    )}

                    {/* Video Recommendations */}
                    {message.videos && message.videos.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <h4 className="font-semibold text-sm text-gray-700">
                          Related Videos
                        </h4>
                        <div className="grid grid-cols-2 gap-3">
                          {message.videos.map((video) => (
                            <a
                              key={video.id}
                              href={`/videos/${video.id}`}
                              className="group"
                            >
                              <div className="relative aspect-video rounded-lg overflow-hidden">
                                <img
                                  src={video.thumbnail_url}
                                  alt={video.title}
                                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                />
                                <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                  <Video className="w-8 h-8 text-white" />
                                </div>
                              </div>
                              <p className="text-sm font-medium mt-2 line-clamp-2">
                                {video.title}
                              </p>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-2xl rounded-bl-none px-6 py-4 flex items-center gap-3">
                      <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                      <span className="text-gray-600">Maeju is thinking...</span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 p-6">
                <form onSubmit={handleSendMessage} className="flex gap-3">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Ask me anything about products..."
                    disabled={isLoading}
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <button
                    type="submit"
                    disabled={!inputMessage.trim() || isLoading}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Send className="w-5 h-5" />
                    <span className="hidden sm:inline">Send</span>
                  </button>
                </form>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Suggested Questions */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="card"
            >
              <div className="flex items-center gap-2 mb-4">
                <MessageCircle className="w-5 h-5 text-primary-600" />
                <h3 className="font-semibold">Suggested Questions</h3>
              </div>
              <div className="space-y-2">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestedQuestion(question)}
                    className="w-full text-left px-4 py-3 rounded-lg bg-gray-50 hover:bg-primary-50 hover:text-primary-700 transition-colors text-sm"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </motion.div>

            {/* Session Info */}
            {sessionInfo && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="card bg-gradient-to-br from-primary-50 to-secondary-50"
              >
                <h3 className="font-semibold mb-3">Session Info</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Messages:</span>
                    <span className="font-semibold">
                      {sessionInfo.total_messages}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Context:</span>
                    <span className="font-semibold">{sessionInfo.context}</span>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Tips */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="card bg-primary-600 text-white"
            >
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5" />
                <h3 className="font-semibold">Pro Tips</h3>
              </div>
              <ul className="space-y-2 text-sm opacity-90">
                <li>Ask about products in specific price ranges</li>
                <li>Request recommendations based on occasions</li>
                <li>Inquire about product features and comparisons</li>
                <li>Ask for video content related to your interests</li>
              </ul>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
