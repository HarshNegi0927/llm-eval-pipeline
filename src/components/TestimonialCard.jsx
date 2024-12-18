import React from 'react';
import { Card, CardContent, Typography, Avatar, Box } from '@mui/material';
import { motion } from 'framer-motion';

const TestimonialCard = ({ testimonial, index }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: index * 0.2 }}
    >
      <Card 
        sx={{ 
          height: '100%', 
          display: 'flex', 
          flexDirection: 'column', 
          p: 3,
          background: 'linear-gradient(145deg, #1e1e1e 0%, #121212 100%)',
          border: '1px solid rgba(255,255,255,0.1)'
        }}
      >
        <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
          <Avatar 
            src={testimonial.avatar} 
            sx={{ 
              width: 80, 
              height: 80, 
              mb: 2, 
              mx: 'auto',
              border: '3px solid',
              borderColor: 'primary.main'
            }} 
          />
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 'bold', 
              mb: 1,
              color: 'primary.light'
            }}
          >
            {testimonial.name}
          </Typography>
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ mb: 2 }}
          >
            {testimonial.profession}
          </Typography>
          <Typography 
            variant="body1" 
            sx={{ 
              fontStyle: 'italic',
              color: 'text.primary',
              opacity: 0.8
            }}
          >
            "{testimonial.feedback}"
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default TestimonialCard;

