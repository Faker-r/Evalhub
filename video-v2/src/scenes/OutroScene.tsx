import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT, popIn } from "../theme";

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Animations
  const ctaScale = popIn(frame, fps, 0);
  const elementsOpacity = interpolate(frame, [15, 30], [0, 1], {
    extrapolateRight: "clamp",
  });
  
  // Button pulse animation
  const buttonPulse = 1 + Math.sin(frame * 0.1) * 0.05;

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
        backgroundColor: C.black,
        opacity: fadeOut,
      }}
    >
      {/* Noise background */}
      <svg
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.1, pointerEvents: "none" }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <filter id="outro-noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#outro-noise)" />
      </svg>
      
      {/* Abstract Grid Background */}
      <div
        style={{
          position: "absolute",
          top: -200,
          right: -200,
          width: 800,
          height: 800,
          background: `radial-gradient(circle, ${C.green}30 0%, transparent 60%)`,
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
          background: `radial-gradient(circle, ${C.pink}30 0%, transparent 60%)`,
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          gap: 60,
        }}
      >
        {/* Main CTA */}
        <div
          style={{
            transform: `scale(${ctaScale})`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 24,
          }}
        >
          <div
            style={{
              width: 140,
              height: 140,
              background: C.white,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: `12px 12px 0px ${C.green}`,
              border: `4px solid ${C.black}`,
            }}
          >
            <svg viewBox="0 0 24 24" width="80" height="80" fill="none" stroke={C.black} strokeWidth="3" strokeLinecap="square">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          
          <h1
            style={{
              fontSize: 100,
              color: C.white,
              fontFamily: FONT.display,
              textAlign: "center",
              lineHeight: 1.1,
              margin: 0,
              textShadow: `4px 4px 0px ${C.pink}`,
            }}
          >
            READY TO FIND<br/>
            YOUR <span style={{ color: C.green }}>BEST AI</span>?
          </h1>
        </div>

        {/* Benefits list */}
        <div
          style={{
            opacity: elementsOpacity,
            display: "flex",
            gap: 40,
            justifyContent: "center",
          }}
        >
          {[
            { text: "100% Free", icon: (
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={C.green} strokeWidth="3"><circle cx="12" cy="12" r="10"/><path d="M12 8v8"/><path d="M8 12h8"/></svg>
            )},
            { text: "No Lock-in", icon: (
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={C.white} strokeWidth="3"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            )},
            { text: "Instant Setup", icon: (
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={C.pink} strokeWidth="3"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            )},
          ].map((item, i) => (
            <div
              key={item.text}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                transform: `translateY(${interpolate(frame, [15 + i * 5, 30 + i * 5], [20, 0], { extrapolateRight: "clamp" }) }px)`,
                opacity: interpolate(frame, [15 + i * 5, 30 + i * 5], [0, 1], { extrapolateRight: "clamp" }),
              }}
            >
              <div
                style={{
                  padding: 12,
                  background: `${C.white}10`,
                  border: `2px solid ${item.icon.props.stroke}`,
                }}
              >
                {item.icon}
              </div>
              <span
                style={{
                  fontSize: 24,
                  fontWeight: 800,
                  color: C.white,
                  fontFamily: FONT.body,
                  textTransform: "uppercase",
                  letterSpacing: 1,
                }}
              >
                {item.text}
              </span>
            </div>
          ))}
        </div>

        {/* Call to action button */}
        <div
          style={{
            opacity: elementsOpacity,
            marginTop: 20,
          }}
        >
          <div
            style={{
              padding: "24px 64px",
              background: C.green,
              color: C.black,
              fontSize: 32,
              fontWeight: 800,
              fontFamily: FONT.display,
              textTransform: "uppercase",
              letterSpacing: 3,
              boxShadow: `12px 12px 0px ${C.white}`,
              display: "flex",
              alignItems: "center",
              gap: 16,
              transform: `scale(${buttonPulse})`,
              border: `4px solid ${C.black}`,
            }}
          >
            START EVALUATING TODAY
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </div>
          <div
            style={{
              fontSize: 20,
              color: C.white,
              fontFamily: FONT.body,
              fontWeight: 700,
              textAlign: "center",
              marginTop: 32,
              letterSpacing: 4,
            }}
          >
            WWW.EVALHUB.IO
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
