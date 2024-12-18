import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Button, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  AppBar,
  Toolbar,
  IconButton,
  Avatar,
  Card,
  CardContent,
  LinearProgress,
  Drawer,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Chat as ChatIcon,
  Mic as MicIcon,
  EmojiEvents as EmojiEventsIcon,
  Translate as TranslateIcon,
  School as SchoolIcon,
  Assessment as AssessmentIcon,
  Group as GroupIcon,
  Settings as SettingsIcon,
  ExitToApp as ExitToAppIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Mock data (replace with real data from your backend)
const user = {
  name: 'John Doe',
  avatar: '/placeholder.svg?height=40&width=40',
  language: 'Spanish',
  level: 'Intermediate',
  streak: 7,
  xp: 450
};

const learningPaths = [
  { id: 1, name: 'Travel Spanish', progress: 60 },
  { id: 2, name: 'Business Spanish', progress: 30 },
  { id: 3, name: 'Casual Conversation', progress: 45 },
];

const recentActivities = [
  { id: 1, type: 'lesson', name: 'Past Tense Verbs', score: 8 },
  { id: 2, type: 'quiz', name: 'Food Vocabulary', score: 9 },
  { id: 3, type: 'conversation', name: 'Ordering at a Restaurant', score: 7 },
];

const Dashboard = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <div>
      <Toolbar />
      <List>
        {[
          { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
          { text: 'AI Chatbot', icon: <ChatIcon />, path: '/chatbot' },
          { text: 'Speech Practice', icon: <MicIcon />, path: '/speech' },
          { text: 'Gamification', icon: <EmojiEventsIcon />, path: '/games' },
          { text: 'Translation', icon: <TranslateIcon />, path: '/translate' },
          { text: 'Exercises', icon: <SchoolIcon />, path: '/exercises' },
          { text: 'Progress', icon: <AssessmentIcon />, path: '/progress' },
          { text: 'Community', icon: <GroupIcon />, path: '/community' },
        ].map((item, index) => (
          <ListItem button key={item.text} component="a" href={item.path}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            LinguaLeap Dashboard
          </Typography>
          <IconButton color="inherit">
            <SettingsIcon />
          </IconButton>
          <IconButton color="inherit">
            <ExitToAppIcon />
          </IconButton>
          <Avatar alt={user.name} src={user.avatar} sx={{ ml: 1 }} />
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: 240 }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - 240px)` } }}
      >
        <Toolbar />
        <Container maxWidth="lg">
          <Grid container spacing={3}>
            {/* User Profile Card */}
            <Grid item xs={12} md={4}>
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Paper elevation={3} sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar alt={user.name} src={user.avatar} sx={{ width: 60, height: 60, mr: 2 }} />
                    <Box>
                      <Typography variant="h6">{user.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {user.language} - {user.level}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    🔥 {user.streak} day streak
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    XP: {user.xp}
                  </Typography>
                  <Button variant="contained" color="primary" fullWidth>
                    Continue Learning
                  </Button>
                </Paper>
              </motion.div>
            </Grid>

            {/* Learning Paths */}
            <Grid item xs={12} md={8}>
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <Paper elevation={3} sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
                  <Typography variant="h6" gutterBottom>
                    Your Learning Paths
                  </Typography>
                  {learningPaths.map((path) => (
                    <Box key={path.id} sx={{ mb: 2 }}>
                      <Typography variant="body2">{path.name}</Typography>
                      <LinearProgress variant="determinate" value={path.progress} sx={{ mt: 1 }} />
                    </Box>
                  ))}
                </Paper>
              </motion.div>
            </Grid>

            {/* AI Chatbot */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Paper elevation={3} sx={{ p: 2, height: 300 }}>
                  <Typography variant="h6" gutterBottom>
                    AI Language Partner
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Practice conversations with our AI-powered language partner.
                  </Typography>
                  <Button variant="outlined" color="primary">
                    Start Conversation
                  </Button>
                </Paper>
              </motion.div>
            </Grid>

            {/* Speech Recognition */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <Paper elevation={3} sx={{ p: 2, height: 300 }}>
                  <Typography variant="h6" gutterBottom>
                    Pronunciation Practice
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Improve your accent with AI-powered speech recognition.
                  </Typography>
                  <Button variant="outlined" color="primary">
                    Start Speaking
                  </Button>
                </Paper>
              </motion.div>
            </Grid>

            {/* Recent Activities */}
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                <Paper elevation={3} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Recent Activities
                  </Typography>
                  <Grid container spacing={2}>
                    {recentActivities.map((activity) => (
                      <Grid item xs={12} sm={6} md={4} key={activity.id}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              {activity.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Type: {activity.type}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Score: {activity.score}/10
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Paper>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default Dashboard;

