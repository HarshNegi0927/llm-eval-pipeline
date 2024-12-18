import React from 'react';
import { 
  Typography, 
  Button, 
  Container, 
  Grid, 
  Card, 
  CardContent, 
  Box, 
  Avatar,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  School as SchoolIcon, 
  Support as SupportIcon, 
  Favorite as FavoriteIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import Footer from '../components/Footer';
import Navbar from '../components/Navbar';

const pricingOptions = [
  { 
    plan: 'Basic', 
    price: '$19/month', 
    features: ['Access to all courses', 'Community support', 'Progress tracking'],
    icon: <SchoolIcon color="primary" fontSize="large" />
  },
  { 
    plan: 'Pro', 
    price: '$39/month', 
    features: ['Everything in Basic', '1-on-1 tutoring', 'Personalized feedback', 'Priority support'],
    icon: <SupportIcon color="primary" fontSize="large" />
  },
  { 
    plan: 'Premium', 
    price: '$59/month', 
    features: ['Everything in Pro', 'Personalized learning plan', 'Unlimited tutoring sessions', 'Certification'],
    icon: <FavoriteIcon color="primary" fontSize="large" />
  },
];

const testimonials = [
  { 
    name: 'John Doe', 
    feedback: 'This platform has transformed my language learning experience!', 
    avatar: 'https://randomuser.me/api/portraits/men/1.jpg',
    profession: 'Software Engineer'
  },
  { 
    name: 'Jane Smith', 
    feedback: 'The personalized feedback is incredibly helpful.', 
    avatar: 'https://randomuser.me/api/portraits/women/2.jpg',
    profession: 'Marketing Specialist'
  },
  { 
    name: 'Robert Brown', 
    feedback: 'I love the flexibility to learn at my own pace!', 
    avatar: 'https://randomuser.me/api/portraits/men/3.jpg',
    profession: 'Entrepreneur'
  },
];

const LandingPage = () => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const sectionVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { 
        duration: 0.8, 
        ease: "easeOut" 
      } 
    }
  };

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
    <Box sx={{ backgroundColor: 'background.default', color: 'text.primary' }}>
      <Navbar/>
      {/* Hero Section */}
      <Box
        sx={{
          background: `linear-gradient(160deg, rgba(0,0,0,0.9) 50%, rgba(0,20,10,0.7) 50%), url('/image.webp')`,
          backgroundSize: 'cover',
          backgroundPosition:'center',
          minHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
          padding: '0 20px'
        }}
      >
        <motion.div
          initial="hidden"
          animate="visible"
          variants={heroVariants}
        >
          <motion.h1
            variants={heroVariants}
            style={{
              fontSize: isSmallScreen ? '3rem' : '4rem',
              fontWeight: 'bold',
              marginBottom: '1rem',
              background: 'linear-gradient(to right, #00b0ff, #f50057)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Unlock Your Language Potential
          </motion.h1>
          <motion.p
            variants={heroVariants}
            style={{
              fontSize: isSmallScreen ? '1rem' : '1.5rem',
              maxWidth: '800px',
              marginBottom: '2rem',
              color: '#b0b0b0'
            }}
          >
            Revolutionize your language learning with cutting-edge AI technology, personalized learning paths, and intelligent feedback.
          </motion.p>
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
      </Box>

      {/* About Section */}
      <Container maxWidth="lg" sx={{ py: 10 }} id="about">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={sectionVariants}
        >
          <Typography 
            variant="h4" 
            align="center" 
            sx={{ 
              mb: 8, 
              fontWeight: 'bold',
              background: 'linear-gradient(to right, #00b0ff, #f50057)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            About LinguaLeap
          </Typography>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h5" gutterBottom>
                Empowering Language Learners Worldwide
              </Typography>
              <Typography variant="body1" paragraph>
                At LinguaLeap, we believe that language is the key to understanding and connecting with the world. Our innovative platform combines cutting-edge AI technology with proven language learning methodologies to create a personalized and effective learning experience.
              </Typography>
              <Typography variant="body1">
                Whether you're a beginner or looking to polish your skills, LinguaLeap offers tailored courses, real-time feedback, and interactive lessons to help you achieve your language goals faster and more efficiently than ever before.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                component="img"
                src="/image5.png"
                alt="About LinguaLeap"
                sx={{
                  width: '100%',
                  // borderRadius: 4,
                  // boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
                }}
              />
            </Grid>
          </Grid>
        </motion.div>
      </Container>

      {/* Testimonials Section */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={sectionVariants}
        >
          <Typography 
            variant="h4" 
            align="center" 
            sx={{ 
              mb: 8, 
              fontWeight: 'bold',
              background: 'linear-gradient(to right, #00b0ff, #f50057)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Voices of Success
          </Typography>
          <Grid container spacing={4}>
            {testimonials.map((testimonial, index) => (
              <Grid item xs={12} md={4} key={index}>
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
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>

      {/* Pricing Section */}
      <Container maxWidth="lg" sx={{ py: 10 }} id="pricing">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={sectionVariants}
        >
          <Typography 
            variant="h4" 
            align="center" 
            sx={{ 
              mb: 8, 
              fontWeight: 'bold',
              background: 'linear-gradient(to right, #00b0ff, #f50057)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            Choose Your Learning Path
          </Typography>
          <Grid container spacing={4} sx={{ alignItems: 'stretch' }}>
            {pricingOptions.map((option, index) => (
              <Grid item xs={12} sm={4} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: index * 0.2 }}
                  style={{ height: '100%' }}
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
                    <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center' }}>
                        {option.icon}
                      </Box>
                      <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 2, textAlign: 'center' }}>
                        {option.plan}
                      </Typography>
                      <Typography variant="h6" color="primary" sx={{ mb: 2, textAlign: 'center' }}>
                        {option.price}
                      </Typography>
                      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                          {option.features.map((feature, i) => (
                            <li 
                              key={i} 
                              style={{ 
                                marginBottom: 8, 
                                display: 'flex', 
                                alignItems: 'center',
                                color: '#b0b0b0'
                              }}
                            >
                              <LanguageIcon 
                                fontSize="small" 
                                color="primary" 
                                sx={{ mr: 1, flexShrink: 0 }} 
                              />
                              <span>{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </Box>
                    </CardContent>
                    <Button 
                      variant="contained" 
                      color="primary" 
                      fullWidth 
                      sx={{ 
                        mt: 2, 
                        py: 1.5, 
                        borderRadius: 4 
                      }}
                    >
                      Choose Plan
                    </Button>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>
      <Footer/>
    </Box>
    
  );
};

export default LandingPage;

