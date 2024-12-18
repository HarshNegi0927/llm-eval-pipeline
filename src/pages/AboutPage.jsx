import React from 'react';
import { Container, Typography, Grid, Box } from '@mui/material';
import { motion } from 'framer-motion';

const AboutPage = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 10 }}>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <Typography 
          variant="h2" 
          align="center" 
          sx={{ 
            mb: 6, 
            fontWeight: 'bold',
            background: 'linear-gradient(to right, #00b0ff, #f50057)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          About LinguaLeap
        </Typography>
      </motion.div>

      <Grid container spacing={6} alignItems="center">
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Typography variant="h4" gutterBottom>
              Our Mission
            </Typography>
            <Typography variant="body1" paragraph>
              At LinguaLeap, we believe that language is the key to understanding and connecting with the world. Our mission is to make language learning accessible, engaging, and effective for everyone.
            </Typography>
            <Typography variant="body1" paragraph>
              We combine cutting-edge AI technology with proven language learning methodologies to create a personalized and immersive learning experience that adapts to your unique needs and goals.
            </Typography>
          </motion.div>
        </Grid>
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <Box
              component="img"
              src="/about-image.jpg"
              alt="About LinguaLeap"
              sx={{
                width: '100%',
                borderRadius: 4,
                boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
              }}
            />
          </motion.div>
        </Grid>
      </Grid>

      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        <Typography variant="h4" align="center" sx={{ mt: 10, mb: 4 }}>
          Why Choose LinguaLeap?
        </Typography>
        <Grid container spacing={4}>
          {[
            { title: 'Personalized Learning', description: 'Our AI-powered platform adapts to your learning style and pace.' },
            { title: 'Interactive Lessons', description: 'Engage with native speakers and real-world content.' },
            { title: 'Progress Tracking', description: 'Monitor your improvement with detailed analytics and insights.' },
            { title: 'Community Support', description: 'Connect with fellow learners and practice your skills together.' },
          ].map((item, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Box textAlign="center">
                <Typography variant="h6" gutterBottom>
                  {item.title}
                </Typography>
                <Typography variant="body2">
                  {item.description}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </motion.div>
    </Container>
  );
};

export default AboutPage;

