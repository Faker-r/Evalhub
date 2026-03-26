import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT, popIn } from "../theme";
import { IsometricDiagram } from "./IsometricDiagram";

export const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Phase 1: "You use AI every day" (0-5s)
  const phase1Opacity = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });
  const phase1Exit = interpolate(frame, [140, 150], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Phase 2: "Same model, different results" (5-12s)
  const phase2Start = 150;
  const phase2Opacity = interpolate(frame, [phase2Start, phase2Start + 15], [0, 1], {
    extrapolateRight: "clamp",
  });
  const phase2Exit = interpolate(frame, [380, 400], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Phase 3: "How do you know which one to trust?" (12-18s)
  const phase3Start = 400;
  const phase3Opacity = interpolate(frame, [phase3Start, phase3Start + 15], [0, 1], {
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
        opacity: fadeOut,
      }}
    >
      {/* Subtle radial noise texture */}
      <svg
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.05, pointerEvents: "none" }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <filter id="hook-noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#hook-noise)" />
      </svg>
      {/* Distorted background grid elements */}
      <div
        style={{
          position: "absolute",
          top: -200,
          right: -200,
          width: 800,
          height: 800,
          background: `radial-gradient(circle, ${C.green}10 0%, transparent 60%)`,
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: -300,
          left: -100,
          width: 600,
          height: 600,
          background: `radial-gradient(circle, ${C.pink}10 0%, transparent 60%)`,
          pointerEvents: "none",
        }}
      />

      {/* Phase 1: "You use AI every day" */}
      {frame < 160 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            opacity: phase1Opacity * phase1Exit,
          }}
        >
          <h1
            style={{
              fontSize: 84,
              color: C.black,
              fontFamily: FONT.display,
              textAlign: "center",
              margin: 0,
              letterSpacing: 2,
              transform: `scale(${popIn(frame, fps, 0)})`,
            }}
          >
            YOU USE <span style={{ color: C.green }}>AI</span> EVERY DAY
          </h1>

          {/* AI use case icons */}
          <div
            style={{
              display: "flex",
              gap: 80,
              marginTop: 80,
            }}
          >
            {[
              {
                icon: (
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke={C.white} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                ),
                label: "Chatbots", delay: 20
              },
              {
                icon: (
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke={C.white} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                  </svg>
                ),
                label: "Search", delay: 35
              },
              {
                icon: (
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke={C.white} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/>
                  </svg>
                ),
                label: "Writing", delay: 50
              },
              {
                icon: (
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke={C.white} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
                  </svg>
                ),
                label: "Images", delay: 65
              },
            ].map((item, i) => {
              const itemScale = popIn(frame, fps, item.delay, { damping: 12, stiffness: 150 });
              return (
                <div
                  key={item.label}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 20,
                    opacity: frame >= item.delay ? 1 : 0,
                    transform: `scale(${frame >= item.delay ? itemScale : 0})`,
                  }}
                >
                  <div
                    style={{
                      width: 120,
                      height: 120,
                      background: C.black,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: `8px 8px 0px ${C.green}`,
                      border: `2px solid ${C.black}`,
                    }}
                  >
                    {item.icon}
                  </div>
                  <span
                    style={{
                      fontSize: 24,
                      fontWeight: 800,
                      color: C.black,
                      fontFamily: FONT.body,
                      textTransform: "uppercase",
                      letterSpacing: 2,
                    }}
                  >
                    {item.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Phase 2: Isometric 3D Diagram */}
      {frame >= phase2Start && frame < 410 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: phase2Opacity * phase2Exit,
          }}
        >
          <IsometricDiagram localFrame={frame - phase2Start} />
        </div>
      )}

      {/* Phase 3: "How do you know which one to trust?" */}
      {frame >= phase3Start && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            opacity: phase3Opacity,
          }}
        >
          <div
            style={{
              padding: "40px 80px",
              background: C.black,
              transform: `scale(${popIn(frame, fps, phase3Start)}) rotate(-2deg)`,
              boxShadow: `16px 16px 0px ${C.green}`,
            }}
          >
            <h2
              style={{
                fontSize: 80,
                color: C.white,
                fontFamily: FONT.display,
                textAlign: "center",
                lineHeight: 1.2,
                margin: 0,
                letterSpacing: 2,
              }}
            >
              HOW DO YOU KNOW<br/>
              <span style={{ color: C.pink }}>WHICH ONE</span> TO TRUST?
            </h2>
          </div>

          <div
            style={{
              display: "flex",
              gap: 40,
              marginTop: 80,
            }}
          >
            {[1, 2, 3].map((_, i) => (
              <div
                key={i}
                style={{
                  opacity: frame >= phase3Start + 20 + i * 15 ? 1 : 0,
                  transform: `scale(${popIn(frame, fps, phase3Start + 20 + i * 15)})`,
                }}
              >
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke={i === 1 ? C.pink : C.black} strokeWidth="3" strokeLinecap="square" strokeLinejoin="miter">
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </div>
            ))}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};

