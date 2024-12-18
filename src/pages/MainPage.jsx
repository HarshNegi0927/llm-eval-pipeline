import React from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia,
  Avatar,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  Language as LanguageIcon,
  Chat as ChatIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
  EmojiEvents as EmojiEventsIcon,
  Translate as TranslateIcon,
  School as SchoolIcon,
  Assessment as AssessmentIcon,
  Mic as MicIcon,
  AutoStories as AutoStoriesIcon,
  Public as PublicIcon,
  Forum as ForumIcon,
  Group as GroupIcon,
  Share as ShareIcon
} from '@mui/icons-material';

const features = [
  { 
    title: 'Personalized Learning Paths', 
    description: 'AI-powered customized lesson plans tailored to your goals and progress.',
    icon: <LanguageIcon fontSize="large" />
  },
  { 
    title: 'Interactive AI Chatbot', 
    description: 'Practice real-time conversations with our intelligent language partner.',
    icon: <ChatIcon fontSize="large" />
  },
  { 
    title: 'Speech Recognition', 
    description: 'Get instant feedback on your pronunciation and improve your speaking skills.',
    icon: <RecordVoiceOverIcon fontSize="large" />
  },
  { 
    title: 'Gamified Experience', 
    description: 'Learn through fun activities, earn points, and climb the leaderboards.',
    icon: <EmojiEventsIcon fontSize="large" />
  },
  { 
    title: 'AI-Powered Translation', 
    description: 'Understand context and cultural nuances with smart translations.',
    icon: <TranslateIcon fontSize="large" />
  },
  { 
    title: 'Adaptive Exercises', 
    description: 'Grammar and vocabulary exercises that evolve with your skills.',
    icon: <SchoolIcon fontSize="large" />
  },
  { 
    title: 'Real-Time Feedback', 
    description: 'Receive immediate assessments and track your progress with detailed analytics.',
    icon: <AssessmentIcon fontSize="large" />
  },
  { 
    title: 'Voice-Based Conversations', 
    description: 'Immerse yourself in realistic speaking scenarios and situations.',
    icon: <MicIcon fontSize="large" />
  },
  { 
    title: 'AI-Generated Stories', 
    description: 'Enjoy personalized reading materials tailored to your interests and level.',
    icon: <AutoStoriesIcon fontSize="large" />
  },
  { 
    title: 'Cultural Integration', 
    description: 'Learn about traditions, idioms, and regional language differences.',
    icon: <PublicIcon fontSize="large" />
  },
  { 
    title: 'Community Learning', 
    description: 'Connect with fellow learners in moderated forums and chat rooms.',
    icon: <ForumIcon fontSize="large" />
  },
  { 
    title: 'Language Exchange', 
    description: 'Practice with native speakers and help others learn your language.',
    icon: <GroupIcon fontSize="large" />
  }
];

const testimonials = [
  {
    name: 'Sarah Johnson',
    avatar: 'https://randomuser.me/api/portraits/women/1.jpg',
    text: 'LinguaLeap has transformed my language learning journey. The AI-powered lessons are incredibly effective!',
    language: 'Spanish'
  },
  {
    name: 'Michael Chen',
    avatar: 'https://randomuser.me/api/portraits/men/2.jpg',
    text: 'I love the interactive chatbot feature. Its like having a native speaker to practice with anytime!',
    language: 'French'
  },
  {
    name: 'Emily Rodriguez',
    avatar: 'https://randomuser.me/api/portraits/women/3.jpg',
    text: 'The personalized learning path helped me achieve fluency much faster than I expected. Highly recommended!',
    language: 'German'
  }
];

const MainPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box sx={{ backgroundColor: 'background.default', color: 'text.primary' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: `linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(30,30,30,0.8) 100%), url('/hero-background.jpg')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          py: 8
        }}
      >
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Typography variant={isMobile ? 'h3' : 'h1'} component="h1" gutterBottom
              sx={{
                fontWeight: 'bold',
                background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Master Any Language with AI
            </Typography>
            <Typography variant={isMobile ? 'h6' : 'h5'} gutterBottom sx={{ color: 'text.secondary', mb: 4 }}>
              Experience the future of language learning with LinguaLeap's AI-powered platform
            </Typography>
            <Button
              variant="contained"
              color="primary"
              size="large"
              sx={{
                py: 2,
                px: 4,
                fontSize: '1.2rem',
                borderRadius: '50px',
                boxShadow: '0 4px 20px 0 rgba(61, 71, 82, 0.1), 0 0 0 0 rgba(0, 127, 255, 0)',
                transition: 'all 0.2s ease-out',
                '&:hover': {
                  transform: 'scale(1.05)',
                  boxShadow: '0 6px 30px 0 rgba(61, 71, 82, 0.2), 0 0 0 2px rgba(0, 127, 255, 0.5)',
                }
              }}
            >
              Start Learning Now
            </Button>
          </motion.div>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h2" align="center" gutterBottom sx={{ mb: 6, fontWeight: 'bold' }}>
          Powerful Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                    <Box sx={{ color: 'primary.main', mb: 2 }}>
                      {feature.icon}
                    </Box>
                    <Typography gutterBottom variant="h5" component="h2">
                      {feature.title}
                    </Typography>
                    <Typography>
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Testimonials Section */}
      <Box sx={{ backgroundColor: 'background.paper', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h2" align="center" gutterBottom sx={{ mb: 6, fontWeight: 'bold' }}>
            Success Stories
          </Typography>
          <Grid container spacing={4}>
            {testimonials.map((testimonial, index) => (
              <Grid item xs={12} md={4} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <Avatar
                        src={testimonial.avatar}
                        sx={{ width: 80, height: 80, mb: 2 }}
                      />
                      <Typography gutterBottom variant="h6" component="h3">
                        {testimonial.name}
                      </Typography>
                      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                        Learning {testimonial.language}
                      </Typography>
                      <Typography variant="body1" sx={{ fontStyle: 'italic', textAlign: 'center' }}>
                        "{testimonial.text}"
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Call to Action */}
      <Box
        sx={{
          backgroundColor: 'primary.main',
          color: 'primary.contrastText',
          py: 8,
          textAlign: 'center'
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h3" gutterBottom>
            Ready to Start Your Language Journey?
          </Typography>
          <Typography variant="h6" sx={{ mb: 4 }}>
            Join thousands of learners and experience the power of AI-driven language learning.
          </Typography>
          <Button
            variant="contained"
            color="secondary"
            size="large"
            sx={{
              py: 2,
              px: 4,
              fontSize: '1.2rem',
              borderRadius: '50px',
            }}
          >
            Sign Up Now
          </Button>
        </Container>
      </Box>
    </Box>
  );
};

export default MainPage;

