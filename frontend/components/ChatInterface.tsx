'use client';

import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';
import { format } from 'date-fns';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  message: Message;
}

export default function ChatInterface({ message }: ChatInterfaceProps) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`chat-message ${isUser ? 'user' : 'assistant'}`}
    >
      <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div
          className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
            isUser
              ? 'bg-gradient-to-br from-primary-600 to-secondary-600'
              : 'bg-gradient-to-br from-purple-600 to-pink-600'
          }`}
        >
          {isUser ? (
            <User className="w-6 h-6 text-white" />
          ) : (
            <Bot className="w-6 h-6 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
          <div className={`chat-bubble ${isUser ? 'user' : 'assistant'}`}>
            <div className="flex items-baseline gap-2 mb-1">
              <span className={`text-xs font-semibold ${isUser ? 'text-white/90' : 'text-gray-500'}`}>
                {isUser ? 'You' : 'Maeju AI'}
              </span>
              <span className={`text-xs ${isUser ? 'text-white/70' : 'text-gray-400'}`}>
                {format(message.timestamp, 'HH:mm')}
              </span>
            </div>
            <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
