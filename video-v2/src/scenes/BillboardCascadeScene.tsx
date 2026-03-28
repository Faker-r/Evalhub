import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  staticFile,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import { C, popIn } from "../theme";

// All billboard images from public/capstone-assets/ai-billboards
// Index 4 = center cell of the 3x3 grid (row 1, col 1) — Baseten goes here
const BILLBOARD_FILES = [
  "capstone-assets/ai-billboards/-FWEBP.webp",
  "capstone-assets/ai-billboards/00tech-billboard-top-cvmh-facebookJumbo.jpg",
  "capstone-assets/ai-billboards/5363038b-a98a-4dfd-b47b-5ef8e9c8e0ce_2110x1582.jpg",
  "capstone-assets/ai-billboards/5ab41160-61cb-4c57-99bb-c7ed98c4a72d_2102x1582.jpg",
  "capstone-assets/ai-billboards/Screenshot 2026-03-26 at 1.58.28 PM.png", // Baseten — center
  "capstone-assets/ai-billboards/68f818cecc993f9955d0a27f.webp",
  "capstone-assets/ai-billboards/download.jpeg",
  "capstone-assets/ai-billboards/rawImage (1).jpg",
  "capstone-assets/ai-billboards/rawImage.jpg",
];

// Deterministic pseudo-random (seeded by index — no Math.random() at render time)
const seededFloat = (seed: number, min: number, max: number): number => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return min + (x - Math.floor(x)) * (max - min);
};

const CANVAS_W = 1920;
const CANVAS_H = 1080;

// Large images to aggressively cover the screen
const BASE_W = 800;
const BASE_H = 520;

// 3x3 grid of cells, one image per cell
// Grid is taller than canvas so bottom row hangs off the bottom edge
const GRID_COLS = 3;
const GRID_ROWS = 3;
const CELL_W = CANVAS_W / GRID_COLS;       // 640
const CELL_H = (CANVAS_H * 1.15) / GRID_ROWS; // ~414 — stretches grid below frame

interface BillboardConfig {
  file: string;
  startFrame: number;
  x: number;       // top-left x of image
  y: number;       // top-left y of image
  rotation: number;
  scale: number;
  zIndex: number;
  color: string;   // shadow color
}

const buildConfigs = (fps: number): BillboardConfig[] => {
  const n = BILLBOARD_FILES.length;
  const colors = [C.green, C.pink, C.black];

  const configs = BILLBOARD_FILES.map((file, i) => {
    const col = i % GRID_COLS;
    const row = Math.floor(i / GRID_COLS);

    // Center of this grid cell — top row offset slightly up, bottom row pushed down
    const cellCenterX = col * CELL_W + CELL_W / 2;
    const cellCenterY = row * CELL_H + CELL_H / 2 - CANVAS_H * 0.05;

    // Scale: 1.0–1.2
    const scale = seededFloat(i * 13 + 4, 1.0, 1.2);
    const imgW = BASE_W * scale;
    const imgH = BASE_H * scale;

    // Jitter within cell — wider range so images spread more organically
    const xJitter = seededFloat(i * 5 + 1, -CELL_W * 0.28, CELL_W * 0.28);
    const yJitter = seededFloat(i * 7 + 2, -CELL_H * 0.28, CELL_H * 0.28);

    // Top-left position from center
    const x = cellCenterX - imgW / 2 + xJitter;
    const y = cellCenterY - imgH / 2 + yJitter;

    // Rotation: ±12–28 deg, direction alternates per cell for variety
    const rotMag = seededFloat(i * 11 + 3, 12, 28);
    const rotSign = ((col + row) % 2 === 0 ? 1 : -1) * (seededFloat(i * 17, 0, 1) > 0.5 ? 1 : -1);
    const rotation = rotMag * rotSign;

    // Stagger: 9 images spread over first ~5.5s (165 frames), tightly packed
    const baseInterval = 165 / (n - 1);
    const jitter = seededFloat(i * 23 + 6, -0.3, 0.3) * baseInterval;
    const startFrame = Math.round(Math.max(0, baseInterval * i + jitter));

    // Assign a theme color for the shadow drops
    const color = colors[i % colors.length];

    return { file, startFrame, x, y, rotation, scale, zIndex: 0, color };
  });

  // Sort ascending by startFrame — render order IS the stacking order.
  // Later in the DOM = naturally on top, so the newest billboard always covers older ones.
  configs.sort((a, b) => a.startFrame - b.startFrame);
  configs.forEach((cfg, order) => { cfg.zIndex = order + 1; });

  return configs;
};

export const BillboardCascadeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const configs = buildConfigs(fps);

  // Fade-out for transition to HookScene
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 18, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.white,
        overflow: "hidden",
        opacity: fadeOut,
      }}
    >
      {/* Subtle radial noise texture */}
      <svg
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.05, pointerEvents: "none" }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <filter id="cascade-noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#cascade-noise)" />
      </svg>

      {/* Billboard images — snap into existence */}
      {configs.map((cfg, i) => {
        const localFrame = frame - cfg.startFrame;

        // Hidden before its time
        if (localFrame < 0) return null;

        // Snap scale: slams in from 3.0 → 1.0 (popIn helper)
        const snapScale = popIn(frame, fps, cfg.startFrame, { damping: 14, stiffness: 180 });

        // Very brief opacity flash: appears at full opacity immediately, no fade
        const opacity = interpolate(localFrame, [0, 2], [0, 1], {
          extrapolateRight: "clamp",
        });

        const imgW = BASE_W * cfg.scale;
        const imgH = BASE_H * cfg.scale;

        return (
          <Img
            key={i}
            src={staticFile(cfg.file)}
            style={{
              position: "absolute",
              left: cfg.x,
              top: cfg.y,
              width: imgW,
              height: imgH,
              objectFit: "cover",
              border: `4px solid ${C.black}`,
              transform: `rotate(${cfg.rotation}deg) scale(${snapScale})`,
              transformOrigin: "center center",
              zIndex: cfg.zIndex,
              opacity,
              boxShadow: `16px 16px 0px ${cfg.color}`,
            }}
          />
        );
      })}

      {/* Camera click sounds — one per billboard, synced to appearance frame */}
      {configs.map((cfg, i) => (
        <Sequence key={`click-${i}`} from={cfg.startFrame} durationInFrames={30}>
          <Audio src={staticFile("audio/sfx/click.mp3")} volume={0.65} />
        </Sequence>
      ))}

      {/* Vignette - Inverted for white theme (white center to light gray edge) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.15) 100%)`,
          pointerEvents: "none",
          zIndex: 200,
        }}
      />
    </AbsoluteFill>
  );
};
