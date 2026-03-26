import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";
import { spring } from "remotion";

// Load fonts
const inter = loadInter("normal", { weights: ["400", "600", "700", "800"], subsets: ["latin"] });
const jetBrainsMono = loadJetBrainsMono("normal", { weights: ["400", "600", "700", "800"], subsets: ["latin"] });

export const FONT = {
  display: `${inter.fontFamily}, -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif`,
  body: `${inter.fontFamily}, -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif`,
  mono: `${jetBrainsMono.fontFamily}, "JetBrains Mono", "Roboto Mono", monospace`,
};

// Color palette
export const C = {
  green: "#18E76F",
  black: "#000000",
  white: "#FFFFFF",
  pink: "#FFA9FD",
  grayDark: "#1A1A1A",
  grayMid: "#666666",
  grayLight: "#F5F5F5",
};

// Pop-in animation: scale from 3x → 1x
export const popIn = (
  frame: number,
  fps: number,
  startFrame: number = 0,
  config?: { damping?: number; stiffness?: number }
) => {
  const s = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: config?.damping ?? 14, stiffness: config?.stiffness ?? 120 },
  });
  // Map spring 0→1 to scale 3→1
  return 3 - 2 * s;
};
