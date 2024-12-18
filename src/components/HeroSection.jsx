import React from 'react';
import { Typography, Button, Box, Container, useTheme, useMediaQuery } from '@mui/material';
import { motion } from 'framer-motion';

const HeroSection = () => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const heroVariants = {
    hidden: { opacity: 0, y: -50 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { 
        duration: 0.8,
        staggerChildren: 0.3
      } 
    }
  };

  return (
    <Box
      sx={{
        background: `linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(30,30,30,0.8) 100%), url('/hero-background.jpg')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <Container maxWidth="lg">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={heroVariants}
        >
          <motion.div variants={heroVariants}>
            <Typography
              variant={isSmallScreen ? 'h3' : 'h1'}
              sx={{
                fontWeight: 'bold',
                marginBottom: '1rem',
                background: 'linear-gradient(to right, #00b0ff, #f50057)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}
            >
              Unlock Your Language Potential
            </Typography>
          </motion.div>
          <motion.div variants={heroVariants}>
            <Typography
              variant={isSmallScreen ? 'body1' : 'h5'}
              sx={{
                maxWidth: '800px',
                marginBottom: '2rem',
                color: '#b0b0b0'
              }}
            >
              Revolutionize your language learning with cutting-edge AI technology, personalized learning paths, and intelligent feedback.
            </Typography>
          </motion.div>
          <motion.div variants={heroVariants}>
            <Button 
              variant="contained" 
              color="secondary" 
              size="large" 
              sx={{ 
                px: 4, 
                py: 2, 
                borderRadius: 4,
                boxShadow: '0 10px 20px rgba(245,0,87,0.3)'
              }}
            >
              Start Learning
            </Button>
          </motion.div>
        </motion.div>
      </Container>
    </Box>
  );
};

export default HeroSection;

