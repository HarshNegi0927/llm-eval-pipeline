import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  IconButton, 
  Paper, 
  Typography, 
  Avatar 
} from '@mui/material';
import { 
  Send as SendIcon, 
  SmartToy as RobotIcon,
  Mic as MicIcon,
  Clear as ClearIcon 
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

const ChatbotInterface = ({ selectedLanguage = 'English' }) => {
  const [messages, setMessages] = useState([
    {
      id: 0,
      text: `Hello! I'm your AI Language Learning Assistant for ${selectedLanguage}. How can I help you improve your language skills today?`,
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);

  // Advanced language-specific response generator
  const generateLanguageResponse = (userInput) => {
    const responses = [
      "That's an interesting point!",
      "Could you elaborate on that?",
      "Let me help you understand better.",
      "Great question! Here's some insight..."
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  };

  // Speech recognition simulation
  const startVoiceInput = () => {
    setIsListening(true);
    setTimeout(() => {
      setIsListening(false);
      handleSendMessage("Voice input: Hello, how are you?");
    }, 3000);
  };

  // Message sending handler
  const handleSendMessage = (message) => {
    const userInput = message || inputMessage;
    if (userInput.trim() === '') return;

    const userMessage = {
      id: Date.now(),
      text: userInput,
      sender: 'user',
      timestamp: new Date()
    };

    const botResponse = {
      id: Date.now() + 1,
      text: generateLanguageResponse(userInput),
      sender: 'bot',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage, botResponse]);
    setInputMessage('');
  };

  // Clear chat history
  const clearChat = () => {
    setMessages([
      {
        id: 0,
        text: `Hello! I'm your AI Language Learning Assistant for ${selectedLanguage}. How can I help you improve your language skills today?`,
        sender: 'bot',
        timestamp: new Date()
      }
    ]);
  };

  // Scroll to bottom effect
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-4">
      <Paper 
        elevation={12} 
        className="w-full max-w-4xl h-[90vh] flex flex-col bg-gray-800 rounded-2xl shadow-2xl overflow-hidden"
      >
        {/* Chat Header */}
        <Box 
          className="bg-gray-700 p-4 flex items-center justify-between text-white"
        >
          <Box className="flex items-center">
            <Avatar className="mr-3 bg-green-500">
              <RobotIcon className="text-white" />
            </Avatar>
            <Typography variant="h6" className="text-green-300">
              AI {selectedLanguage.charAt(0).toUpperCase() + selectedLanguage.slice(1)} Tutor
            </Typography>
          </Box>
          <IconButton onClick={clearChat} className="text-red-400">
            <ClearIcon />
          </IconButton>
        </Box>

        {/* Messages Container */}
        <Box 
          className="flex-grow overflow-y-auto p-4 space-y-4"
          sx={{
            backgroundColor: 'rgb(17,24,39)',
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: 'rgb(31,41,55)',
            },
            '&::-webkit-scrollbar-thumb': {
              background: 'rgb(16,185,129)',
              borderRadius: '4px',
            }
          }}
        >
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3 }}
                className={`flex ${
                  message.sender === 'user' 
                    ? 'justify-end' 
                    : 'justify-start'
                }`}
              >
                <Box
                  className={`
                    max-w-[70%] p-3 rounded-lg relative
                    ${
                      message.sender === 'user'
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 text-green-300'
                    }
                  `}
                >
                  {message.text}
                  <Typography 
                    variant="caption" 
                    className="block text-right text-xs opacity-50 mt-1"
                  >
                    {message.timestamp.toLocaleTimeString()}
                  </Typography>
                </Box>
              </motion.div>
            ))}
            <div ref={messagesEndRef} />
          </AnimatePresence>
        </Box>

        {/* Input Area */}
        <Box 
          className="bg-gray-800 p-4 flex items-center space-x-2"
        >
          <TextField
            fullWidth
            variant="outlined"
            placeholder={`Type in ${selectedLanguage}...`}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            className="mr-2"
            InputProps={{
              className: 'text-green-300 border-green-700',
              style: { 
                backgroundColor: 'rgb(31,41,55)', 
                borderColor: 'rgb(16,185,129)' 
              }
            }}
          />
          <IconButton 
            color="primary" 
            onClick={startVoiceInput}
            className={`
              ${isListening 
                ? 'bg-red-500 animate-pulse' 
                : 'bg-green-600 hover:bg-green-700'
              } text-white`}
          >
            <MicIcon />
          </IconButton>
          <IconButton 
            color="primary" 
            onClick={() => handleSendMessage()}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </div>
  );
};

export default ChatbotInterface;