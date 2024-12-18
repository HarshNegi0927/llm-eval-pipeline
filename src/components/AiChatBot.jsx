import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  MenuItem, 
  Select, 
  FormControl, 
  InputLabel 
} from '@mui/material';
import { motion } from 'framer-motion';

const AIChatbotFullPage = () => {
  const [selectedLanguage, setSelectedLanguage] = useState('');

  const languages = [
    { value: 'spanish', label: 'Spanish' },
    { value: 'french', label: 'French' },
    { value: 'german', label: 'German' },
    { value: 'mandarin', label: 'Mandarin' },
    { value: 'italian', label: 'Italian' }
  ];

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-0 m-0 w-full">
      <Container 
        maxWidth="full" 
        className="h-screen flex items-center justify-center bg-gray-900"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ 
            duration: 0.6, 
            ease: "easeInOut" 
          }}
          className="w-full h-full flex flex-col items-center justify-center bg-gray-900 text-center p-8"
        >
          {/* AI Chatbot Header */}
          <Typography 
            variant="h2" 
            className="text-6xl font-extrabold text-green-400 mb-12 drop-shadow-lg"
          >
            Learn with AI Companion
          </Typography>

          {/* AI Robot Image */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
            className="flex justify-center mb-16"
          >
            <img 
              src="/Image3.webp"  // Replace with your AI robot image
              alt="AI Language Learning Robot" 
              className="w-96 h-96 object-contain transform hover:scale-105 transition-transform duration-300"
            />
          </motion.div>

          {/* Language Selection Container */}
          <div className="w-full max-w-xl space-y-8">
            {/* Language Selection */}
            <FormControl fullWidth variant="outlined" className="mb-8">
              <InputLabel 
                className="text-green-300 border-green-300"
                sx={{
                  '&.Mui-focused': {
                    color: 'rgb(134 239 172)' // Green color when focused
                  }
                }}
              >
                Select Language
              </InputLabel>
              <Select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                label="Select Language"
                className="bg-gray-800 text-green-300 border-green-700"
                sx={{
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgb(22 163 74)', // Green border
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgb(34 197 94)', // Lighter green on hover
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgb(74 222 128)', // Even lighter green when focused
                  }
                }}
              >
                {languages.map((lang) => (
                  <MenuItem 
                    key={lang.value} 
                    value={lang.value}
                    className="hover:bg-green-800 focus:bg-green-900"
                  >
                    {lang.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Learn Language Button */}
            <motion.div
              whileTap={{ scale: 0.95 }}
              whileHover={{ 
                scale: 1.05,
                boxShadow: "0px 10px 20px rgba(0,0,0,0.2)"
              }}
            >
              <Button
                variant="contained"
                disabled={!selectedLanguage}
                className="w-full py-4 text-xl bg-green-600 hover:bg-green-700 text-white"
                sx={{
                  backgroundColor: selectedLanguage ? 'rgb(22 163 74)' : 'rgba(22, 163, 74, 0.5)'
                }}
              >
                Start Your Language Journey
              </Button>
            </motion.div>
          </div>

          {/* Additional Information */}
          <Typography 
            variant="body1" 
            className="text-green-300 mt-8 text-lg italic max-w-2xl"
          >
            Unlock the world of languages with our AI-powered personalized learning experience. 
            Adaptive, intelligent, and tailored just for you.
          </Typography>
        </motion.div>
      </Container>
    </div>
  );
};

export default AIChatbotFullPage;