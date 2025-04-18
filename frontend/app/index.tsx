import React, { useCallback } from "react";
import { Text, View, TouchableOpacity, ImageBackground } from "react-native";
import { Link } from "expo-router";
import styles from "@/assets/styles/landing.style";

export default function Index() {
  return (
    <View style={styles.container}>
      <ImageBackground
        source={{
          uri: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="8" height="8" viewBox="0 0 8 8"%3E%3Ccircle cx="4" cy="4" r="1" fill="%23FFFFFF" opacity="0.4" /%3E%3C/svg%3E',
        }}
        resizeMode="repeat"
        style={styles.dottedBackground}
      />
      <Text style={[styles.title, { fontFamily: 'brico' }]}>AIX</Text>
      <Text style={[styles.subtitle, { fontFamily: 'poppins' }]}>The Expense Tracker</Text>

      <View style={styles.buttonContainer}>
        <Link href="/(auth)" asChild>
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>Login</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/(auth)/signup" asChild>
          <TouchableOpacity style={styles.button}>
            <Text style={styles.buttonText}>Create Account</Text>
          </TouchableOpacity>
        </Link>
      </View>
    </View>
  );
}
