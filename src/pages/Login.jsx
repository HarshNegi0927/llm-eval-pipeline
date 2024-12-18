import React, { useState } from "react";
import { motion } from "framer-motion";
import { Button, TextField, Checkbox, FormControlLabel, IconButton, InputAdornment } from "@mui/material";
import GoogleIcon from "@mui/icons-material/Google";
import GitHubIcon from "@mui/icons-material/GitHub";
import FacebookIcon from "@mui/icons-material/Facebook";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import Navbar from "../components/Navbar";

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);

  return (
     <div className="h-full">
      
    <div className="flex flex-col md:flex-row h-screen">
      {/* Left Section - Image */}
      <div className="md:flex-1 flex justify-center items-center p-4 bg-gray-900">
        <motion.img
          src="/Image3.webp" // Replace with your actual image path
          alt="Login Illustration"
          className="w-full h-auto"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
          whileHover={{ scale: 1.05 }}
        />
      </div>

      {/* Right Section - Login Form */}
      <div className="md:flex-1 bg-gray-900 flex justify-center items-center p-6">
        <motion.div
          className="w-full max-w-md p-8 rounded-lg text-white"
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1 }}
        >
          {/* Welcome Back */}
          <h1 className="text-3xl md:text-5xl font-extrabold mb-4 text-center">
            Welcome&nbsp;Back
          </h1>
          <p className="text-gray-400 mb-6 text-center">
            Sign in to continue and explore amazing features.
          </p>

          <form>
            {/* Email Input */}
            <TextField
              label="Email"
              variant="filled"
              fullWidth
              margin="normal"
              InputProps={{ style: { color: "white" } }}
              InputLabelProps={{ style: { color: "gray" } }}
            />

            {/* Password Input with Eye Icon */}
            <TextField
              label="Password"
              variant="filled"
              type={showPassword ? "text" : "password"}
              fullWidth
              margin="normal"
              InputProps={{
                style: { color: "white" },
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      sx={{ color: "white" }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              InputLabelProps={{ style: { color: "gray" } }}
            />

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between mt-2">
              <FormControlLabel
                control={<Checkbox sx={{ color: "white" }} />}
                label={<span className="text-gray-400">Remember Me</span>}
              />
              <a
                href="#"
                className="text-sm text-blue-400 hover:underline"
              >
                Forgot Password?
              </a>
            </div>

            {/* Sign In Button */}
            <Button
              variant="contained"
              color="success"
              fullWidth
              className="mt-6 bg-green-500 hover:bg-green-600"
            >
              Sign In
            </Button>

            {/* Social Login */}
            <div className="mt-8 text-center">
              <p className="text-gray-400 mb-4">Or sign in with</p>
              <div className="flex justify-center space-x-4">
                {/* Google */}
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  className="p-3 rounded-full shadow-md border border-gray-600"
                >
                  <GoogleIcon className="text-red-600" />
                </motion.button>
                {/* GitHub */}
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  className="p-3 rounded-full shadow-md border border-gray-600"
                >
                  <GitHubIcon className="text-white" />
                </motion.button>
                {/* Facebook */}
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  className="p-3 rounded-full shadow-md border border-gray-600"
                >
                  <FacebookIcon className="text-blue-600" />
                </motion.button>
              </div>
            </div>

            {/* Footer */}
            <div className="text-center mt-8">
              <p className="text-gray-400">
                New here?{" "}
                <a href="#" className="text-blue-400 hover:underline">
                  Create an account
                </a>
              </p>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
    </div>
  );
};

export default LoginPage;
