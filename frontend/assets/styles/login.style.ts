import { StyleSheet, TextStyle, ViewStyle } from "react-native";
import COLORS from "@/constants/colors";

type Styles = {
  safeArea: ViewStyle;
  container: ViewStyle;
  header: ViewStyle;
  title: TextStyle;
  subtitle: TextStyle;
  form: ViewStyle;
  inputContainer: ViewStyle;
  inputIcon: ViewStyle;
  input: TextStyle;
  authButton: ViewStyle;
  authButtonText: TextStyle;
  forgotPassword: TextStyle;
  footerText: TextStyle;
  footerLink: TextStyle;
  errorText: TextStyle;
};


const styles = StyleSheet.create<Styles>({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
    backgroundColor: COLORS.background,
  },
  header: {
    marginBottom: 40,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: COLORS.white,
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.textSecondary,
    textAlign: 'center',
  },
  form: {
    width: '100%',
    maxWidth: 380,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.inputBackground,
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginBottom: 20,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 8,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    color: COLORS.white,
    fontSize: 16,
  },
  authButton: {
    backgroundColor: COLORS.primary,
    paddingVertical: 15,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
    shadowColor: COLORS.primary,
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
  },
  authButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: COLORS.white,
  },
  forgotPassword: {
    color: COLORS.primary,
    marginTop: 8,
    alignSelf: 'flex-end',
    fontSize: 14,
    textDecorationLine: 'underline',
  },
  footerText: {
    color: COLORS.textSecondary,
    textAlign: 'center',
    marginTop: 30,
  },
  footerLink: {
    color: COLORS.primary,
    fontWeight: 'bold',
  },
  errorText: {
    color: COLORS.error,
    textAlign: "center"
  },
});

export default styles;
