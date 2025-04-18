import { TextStyle } from "react-native";
import COLORS from "@/constants/colors";

type Typography = {
  h1: TextStyle;
  h2: TextStyle;
  h3: TextStyle;
  h4: TextStyle;
  h5: TextStyle;
  body1: TextStyle;
  body1Bold: TextStyle;
  body2: TextStyle;
  caption: TextStyle;
  button: TextStyle;
};

export const typography: Typography = {
  h1: {
    fontSize: 34,
    fontWeight: 'bold',
  },
  h2: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  h3: {
    fontSize: 18,
    fontWeight: '600',
  },
  h4: {
    fontSize: 16,
    fontWeight: '600',
  },
  h5: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  body1: {
    fontSize: 16,
  },
  body1Bold: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  body2: {
    fontSize: 14,
  },
  caption: {
    fontSize: 12,
    color: COLORS.textSecondary,
  },
  button: {
    fontSize: 16,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
};
