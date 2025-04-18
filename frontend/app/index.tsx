import { Text, View } from "react-native";
import { Link } from "expo-router";

export default function Index() {
  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Text>AIX</Text>
      <Link href="/(auth)">Login</Link>
      <Link href="/(auth)/signup">Signup</Link>
    </View>
  );
}
