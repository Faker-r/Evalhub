import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT, popIn } from "../theme";

export const TeamInfoScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Entrance animations
  const cardScale = popIn(frame, fps, 0, { damping: 14, stiffness: 100 });
  const contentOpacity = interpolate(frame, [10, 25], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.white,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: fadeOut,
      }}
    >
      {/* Noise background */}
      <svg
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.05, pointerEvents: "none" }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <filter id="team-noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#team-noise)" />
      </svg>
      
      {/* Diagonal scanlines */}
      <svg width="100%" height="100%" style={{ position: "absolute", opacity: 0.05, pointerEvents: "none" }}>
        <pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="8" height="8">
          <path d="M-2,2 l4,-4 M0,8 l8,-8 M6,10 l4,-4" style={{ stroke: C.black, strokeWidth: 1 }} />
        </pattern>
        <rect x="0" y="0" width="100%" height="100%" fill="url(#diagonalHatch)" />
      </svg>

      {/* Main Info Card */}
      <div
        style={{
          transform: `scale(${cardScale})`,
          width: 1200,
          background: C.black,
          border: `4px solid ${C.black}`,
          boxShadow: `24px 24px 0px ${C.green}`,
          padding: "60px 80px",
          display: "flex",
          flexDirection: "column",
          gap: 60,
        }}
      >
        <div style={{ opacity: contentOpacity, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          
          {/* Team Section */}
          <div style={{ flex: 1, borderRight: `4px solid ${C.white}30`, paddingRight: 60 }}>
            <h2
              style={{
                fontSize: 32,
                color: C.green,
                fontFamily: FONT.display,
                margin: "0 0 32px 0",
                letterSpacing: 2,
              }}
            >
              TEAM &quot;CAP THE STONE&quot;
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {[
                { role: "Developer", name: "Parshan Javanrood" },
                { role: "Developer", name: "Ray Ho" },
                { role: "Developer", name: "Ricky Lin" },
                { role: "Developer", name: "Anthony Ji" },
                { role: "Developer", name: "Andrew Wang" },
              ].map((member, i) => (
                <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 18, color: C.pink, fontFamily: FONT.mono, fontWeight: 800, textTransform: "uppercase" }}>{member.role}</span>
                  <span style={{ fontSize: 24, color: C.white, fontFamily: FONT.body, fontWeight: 700 }}>{member.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Project Info Section */}
          <div style={{ flex: 1, paddingLeft: 60 }}>
            <div style={{ marginBottom: 48 }}>
              <h2
                style={{
                  fontSize: 32,
                  color: C.green,
                  fontFamily: FONT.display,
                  margin: "0 0 24px 0",
                  letterSpacing: 2,
                }}
              >
                PROJECT
              </h2>
              <div style={{ fontSize: 40, color: C.white, fontFamily: FONT.display, lineHeight: 1.2 }}>
                Eval<span style={{ color: C.green }}>Hub</span>
                <br />
                <span style={{ fontSize: 20, color: C.grayMid, fontFamily: FONT.mono, fontWeight: 700, textTransform: "uppercase", letterSpacing: 2 }}>CPEN 491 • 2026</span>
              </div>
            </div>

            <div>
              <h2
                style={{
                  fontSize: 32,
                  color: C.green,
                  fontFamily: FONT.display,
                  margin: "0 0 24px 0",
                  letterSpacing: 2,
                }}
              >
                SPONSOR
              </h2>
              <div style={{ fontSize: 28, color: C.white, fontFamily: FONT.body, fontWeight: 800 }}>
                Baseten
              </div>
            </div>
          </div>

        </div>

        {/* Footer Bar */}
        <div
          style={{
            opacity: contentOpacity,
            height: 8,
            background: `linear-gradient(90deg, ${C.green} 0%, ${C.pink} 100%)`,
            width: "100%",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
