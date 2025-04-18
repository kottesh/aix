import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, SafeAreaView, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { EnvelopeIcon, KeyIcon, EyeSlashIcon, EyeIcon } from 'react-native-heroicons/outline';
import { Link } from 'expo-router';
import styles from '@/assets/styles/login.style';
import COLORS from '@/constants/colors';
import { useAuthStore } from '@/store/authStore';

const Login: React.FC = () => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [isVisible, setIsVisible] = useState<boolean>(false);

  const { isLoading, error, login, success } = useAuthStore();

  const validateForm = (): boolean => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Validation Error', 'Please fill in all fields.');
      return false;
    }
    return true;
  };

  const handleLogin = async () => {
    if (!validateForm()) return;
    await login({email, password});
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.header}>
          <Text style={styles.title}>Login</Text>
          <Text style={styles.subtitle}>Welcome back! Let's get you logged in.</Text>
        </View>

        <View style={styles.form}>
          <View style={styles.inputContainer}>
            <EnvelopeIcon style={styles.inputIcon} size={24} color={COLORS.white} />
            <TextInput
              style={styles.input}
              placeholder="Email"
              placeholderTextColor={COLORS.textSecondary}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
            />
          </View>
          <View style={styles.inputContainer}>
            <KeyIcon style={styles.inputIcon} size={24} color={COLORS.white} />
            <TextInput
              style={styles.input}
              placeholder="Password"
              placeholderTextColor={COLORS.textSecondary}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />
            <TouchableOpacity onPress={() => setIsVisible(!isVisible)}>
              { 
              isVisible
              ? <EyeSlashIcon style={styles.inputIcon} size={24} color={COLORS.white} />
              : <EyeIcon style={styles.inputIcon} size={24} color={COLORS.white} />
              }
            </TouchableOpacity>
          </View>

          {
            !success && <Text style={styles.errorText}>{error}</Text>
          }

          <TouchableOpacity style={styles.authButton} onPress={handleLogin}>
            { 
              isLoading
              ? <ActivityIndicator size="small" color={COLORS.white} />
              : <Text style={styles.authButtonText}>Login</Text>
            }
          </TouchableOpacity>

          <TouchableOpacity>
            <Text style={styles.forgotPassword}>Forgot Password?</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.footerText}>
          Don't have an account? <Link href='/(auth)/signup' style={styles.footerLink}>Sign Up</Link>
        </Text>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default Login;
