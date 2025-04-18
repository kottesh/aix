import { useSafeAreaInsets } from "react-native-safe-area-context";
import { View, StyleSheet } from "react-native";
import {COLORS} from "../constants/colors" 
import { ReactNode } from "react";

type SafeScreenProps = {
    children: ReactNode
}

export default function SafeScreen({ children }: SafeScreenProps) {
    const insets = useSafeAreaInsets()

    return (
        <View
            style={[
                styles.container, {
                    paddingTop: insets.top
                }
            ]}
        >
            { children }
        </View>
    )
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background
    }
})