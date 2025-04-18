import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, SafeAreaView, KeyboardAvoidingView, Platform, ActivityIndicator } from 'react-native';
import { EnvelopeIcon, EyeIcon, EyeSlashIcon, KeyIcon, RectangleGroupIcon, UserIcon } from 'react-native-heroicons/outline';
import { Link } from 'expo-router';
import styles from '@/assets/styles/signup.style';
import COLORS from '@/constants/colors';
import { useAuthStore } from '@/store/authStore';

const Signup: React.FC = () => {
  const [firstName, setFirstName] = useState<string>('');
  const [lastName, setLastName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [isVisible, setIsVisible] = useState<boolean>(false)

  const { success, error, isLoading, register } = useAuthStore();

  const validateForm = (): boolean => {
    if (!firstName.trim() || !lastName.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()) {
      Alert.alert('Validation Error', 'Please fill in all fields.');
      return false;
    }
    if (password !== confirmPassword) {
      Alert.alert('Password Error', 'Passwords do not match.');
      return false;
    }
    return true;
  };

  const handleSignup = async () => {
    if (!validateForm()) return;
    await register(
      {
        firstname: firstName,
        lastname: lastName,
        email,
        password
      }
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.header}>
          <Text style={styles.title}>Sign Up</Text>
          <Text style={styles.subtitle}>Create your account</Text>
        </View>

        <View style={styles.form}>
          <View style={styles.nameContainer}>
            <View style={{ flex: 1, marginRight: 10 }}>
              <View style={styles.inputContainer}>
                <UserIcon style={styles.inputIcon} size={24} color={COLORS.white} />
                <TextInput
                  style={styles.input}
                  placeholder="First Name"
                  placeholderTextColor={COLORS.textSecondary}
                  value={firstName}
                  onChangeText={setFirstName}
                />
              </View>
            </View>
            <View style={{ flex: 1 }}>
              <View style={styles.inputContainer}>
                <UserIcon style={styles.inputIcon} size={24} color={COLORS.white} />
                <TextInput
                  style={styles.input}
                  placeholder="Last Name"
                  placeholderTextColor={COLORS.textSecondary}
                  value={lastName}
                  onChangeText={setLastName}
                />
              </View>
            </View>
          </View>

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
          </View>

          <View style={styles.inputContainer}>
            <KeyIcon style={styles.inputIcon} size={24} color={COLORS.white} />
            <TextInput
              style={styles.input}
              placeholder="Confirm Password"
              placeholderTextColor={COLORS.textSecondary}
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              secureTextEntry={isVisible}
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
            !success && error && <Text style={styles.errorText}>{error}</Text>
          }

          <TouchableOpacity style={styles.authButton} onPress={handleSignup} disabled={isLoading}>
            { 
              isLoading
              ? <ActivityIndicator size="small" color={COLORS.white} />
              : <Text style={styles.authButtonText}>Sign Up</Text>
            }
          </TouchableOpacity>

          <Text style={styles.footerText}>
            Already have an account? <Link href="/(auth)" style={styles.footerLink}>Login</Link>
          </Text>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default Signup;
