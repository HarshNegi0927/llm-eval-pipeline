import React, { useState } from "react";
import { motion } from "framer-motion";
import { Button, TextField, Checkbox, FormControlLabel, IconButton, InputAdornment } from "@mui/material";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";

const SignupPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  return (
    <div className="flex flex-col md:flex-row h-screen">
      {/* Right Section - Signup Form */}
      <div className="md:w-[45%] bg-gray-900 flex justify-center items-center">
        <motion.div
          className="w-full max-w-md  rounded-lg text-white"
          initial={{ opacity: 0, x: -100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1 }}
        >
          {/* Create Account */}
          <h1 className="text-3xl md:text-5xl font-extrabold mb-4 text-center">
            Create&nbsp;Account
          </h1>
          <p className="text-gray-400 mb-6 text-center">
            Sign up to start your journey and explore amazing features.
          </p>

          <form>
            {/* Username Input */}
            <TextField
              label="Username"
              variant="filled"
              fullWidth
              margin="normal"
              InputProps={{ style: { color: "white" } }}
              InputLabelProps={{ style: { color: "gray" } }}
            />

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

            {/* Confirm Password Input with Eye Icon */}
            <TextField
              label="Confirm Password"
              variant="filled"
              type={showConfirmPassword ? "text" : "password"}
              fullWidth
              margin="normal"
              InputProps={{
                style: { color: "white" },
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      sx={{ color: "white" }}
                    >
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              InputLabelProps={{ style: { color: "gray" } }}
            />

            {/* Remember Me & Terms */}
            <div className="flex items-center justify-between mt-2">
              <FormControlLabel
                control={<Checkbox sx={{ color: "white" }} />}
                label={<span className="text-gray-400">I agree to the terms and conditions</span>}
              />
            </div>

            {/* Sign Up Button */}
            <Button
              variant="contained"
              color="success"
              fullWidth
              className="mt-6 bg-green-500 hover:bg-green-600"
            >
              Sign Up
            </Button>

            {/* Footer */}
            <div className="text-center mt-8">
              <p className="text-gray-400">
                Already have an account?{" "}
                <a href="#" className="text-blue-400 hover:underline">
                  Login
                </a>
              </p>
            </div>
          </form>
        </motion.div>
      </div>

      {/* Left Section - Image */}
      <div className="md:w-[55%] flex justify-center items-center p-20 bg-gray-900">
        <motion.img
          src="/image6.png" // Replace with your actual image path
          alt="Signup Illustration"
          className="max-w-full h-auto rounded-lg"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
          whileHover={{ scale: 1.05 }}
        />
      </div>
    </div>
  );
};

export default SignupPage;
