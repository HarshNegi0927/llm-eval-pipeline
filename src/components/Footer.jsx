import React from 'react';
import { Box, Container, Grid, Typography, Link, IconButton, Divider } from '@mui/material';
import { Facebook, Twitter, LinkedIn, Instagram } from '@mui/icons-material';
import { motion } from 'framer-motion';

const Footer = () => {
  const footerSections = [
    {
      title: 'Quick Links',
      links: [
        { name: 'Features', href: '#features' },
        { name: 'Pricing', href: '#pricing' },
        { name: 'Addons', href: '#addons' },
        { name: 'Changelog', href: '#changelog' },
      ],
    },
    {
      title: 'Support',
      links: [
        { name: 'Documentation', href: '#documentation' },
        { name: 'FAQ', href: '#faq' },
        { name: 'Contact Us', href: '#contact' },
        { name: 'Blog', href: '#blog' },
      ],
    },
  ];

  const socialLinks = [
    { name: 'Facebook', icon: <Facebook />, href: 'https://www.facebook.com' },
    { name: 'Twitter', icon: <Twitter />, href: 'https://www.twitter.com' },
    { name: 'LinkedIn', icon: <LinkedIn />, href: 'https://www.linkedin.com' },
    { name: 'Instagram', icon: <Instagram />, href: 'https://www.instagram.com' },
  ];

  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: '#2e7d32',
        color: '#fff',
        py: 6,
        boxShadow: '0 -4px 6px rgba(0,0,0,0.1)',
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4} alignItems="stretch">
          <Grid item xs={12} md={4}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <Typography 
                variant="h4" 
                fontWeight="bold" 
                gutterBottom 
                sx={{ 
                  mb: 2,
                  letterSpacing: '0.5px',
                  textShadow: '1px 1px 2px rgba(0,0,0,0.2)'
                }}
              >
                LinguaLeap
              </Typography>
              <Typography 
                variant="body1" 
                sx={{ 
                  mb: 2, 
                  opacity: 0.9,
                  lineHeight: 1.6
                }}
              >
                Revolutionizing language learning with AI-powered technology.
              </Typography>
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1,
                  '& .MuiIconButton-root': {
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.1)',
                      color: '#e8f5e9',
                      backgroundColor: 'rgba(255,255,255,0.1)'
                    }
                  }
                }}
              >
                {socialLinks.map((link) => (
                  <IconButton
                    key={link.name}
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    color="inherit"
                    size="medium"
                  >
                    {link.icon}
                  </IconButton>
                ))}
              </Box>
            </motion.div>
          </Grid>
          {footerSections.map((section, index) => (
            <Grid item xs={12} sm={6} md={4} key={section.title}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 * (index + 1) }}
                style={{ height: '100%' }}
              >
                <Typography 
                  variant="h6" 
                  fontWeight="bold" 
                  gutterBottom 
                  sx={{ 
                    mb: 2,
                    position: 'relative',
                    '&::after': {
                      content: '""',
                      position: 'absolute',
                      bottom: -8,
                      left: 0,
                      width: '40px',
                      height: '3px',
                      backgroundColor: '#fff',
                      opacity: 0.7
                    }
                  }}
                >
                  {section.title}
                </Typography>
                <Box>
                  {section.links.map((link) => (
                    <Link
                      key={link.name}
                      href={link.href}
                      color="inherit"
                      variant="body2"
                      display="block"
                      underline="none"  // Key change: Remove underline
                      sx={{ 
                        mb: 1, 
                        opacity: 0.8,
                        transition: 'all 0.3s ease',
                        '&:hover': { 
                          opacity: 1,
                          transform: 'translateX(5px)',
                          color: '#e8f5e9'
                        }
                      }}
                    >
                      {link.name}
                    </Link>
                  ))}
                </Box>
              </motion.div>
            </Grid>
          ))}
        </Grid>
        <Divider 
          sx={{ 
            my: 4, 
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
          }} 
        />
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'flex-start', sm: 'center' },
          }}
        >
          <Typography 
            variant="body2" 
            sx={{ 
              mb: { xs: 2, sm: 0 },
              opacity: 0.7,
              fontWeight: 300
            }}
          >
            © {new Date().getFullYear()} LinguaLeap. All rights reserved.
          </Typography>
          <Box>
            <Link 
              href="#terms" 
              color="inherit" 
              variant="body2" 
              underline="none"  // Remove underline for terms link
              sx={{ 
                mr: 2, 
                opacity: 0.7,
                transition: 'all 0.3s ease',
                '&:hover': { 
                  opacity: 1,
                  color: '#e8f5e9'
                }
              }}
            >
              Terms of Service
            </Link>
            <Link 
              href="#privacy" 
              color="inherit" 
              variant="body2"
              underline="none"  // Remove underline for privacy link
              sx={{ 
                opacity: 0.7,
                transition: 'all 0.3s ease',
                '&:hover': { 
                  opacity: 1,
                  color: '#e8f5e9'
                }
              }}
            >
              Privacy Policy
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;