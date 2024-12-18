import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './pages/theme';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/Login';
import SignupPage from './pages/SignupPage';
import MainPage from './pages/MainPage';
import Dashboard from './pages/DashBoarded';
import AIChatbotSection from './components/AiChatBot';
import ChatbotInterface from './pages/ChatBotInterface';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        
        {/* <Navbar /> */}
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/mainpage" element={<MainPage/>} />
          <Route path="/dashboard" element={<Dashboard/>} />
          <Route path="/SelectLanguage" element={<AIChatbotSection/>} />
          <Route path="/chatbot" element={<ChatbotInterface/>} />
        </Routes>
      </Router>
      
    </ThemeProvider>
  );
}

export default App;

