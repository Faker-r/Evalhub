import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT, popIn } from "../theme";

export const SolutionIntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // "Meet" text
  const meetTextOpacity = interpolate(frame, [15, 25], [0, 1], {
    extrapolateRight: "clamp",
  });
  
  // Tagline
  const taglineOpacity = interpolate(frame, [60, 75], [0, 1], {
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
      {/* Noise background */}
      <svg
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.05, pointerEvents: "none" }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <filter id="intro-noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#intro-noise)" />
      </svg>
      
      {/* Decorative Grid Lines */}
      <div style={{ position: "absolute", top: "20%", left: 0, right: 0, height: 1, background: C.black, opacity: 0.1 }} />
      <div style={{ position: "absolute", top: "80%", left: 0, right: 0, height: 1, background: C.black, opacity: 0.1 }} />
      <div style={{ position: "absolute", left: "20%", top: 0, bottom: 0, width: 1, background: C.black, opacity: 0.1 }} />
      <div style={{ position: "absolute", right: "20%", top: 0, bottom: 0, width: 1, background: C.black, opacity: 0.1 }} />

      {/* Main content */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          gap: 32,
        }}
      >
        {/* "Meet" text */}
        <div
          style={{
            opacity: meetTextOpacity,
            fontSize: 24,
            fontWeight: 800,
            color: C.black,
            fontFamily: FONT.body,
            letterSpacing: 8,
            textTransform: "uppercase",
            background: C.green,
            padding: "8px 24px",
            transform: `rotate(-2deg)`,
            boxShadow: `4px 4px 0px ${C.black}`,
          }}
        >
          Enter
        </div>

        {/* Logo */}
        <div
          style={{
            transform: `scale(${popIn(frame, fps, 0)})`,
            display: "flex",
            alignItems: "center",
            gap: 24,
            opacity: frame >= 0 ? 1 : 0,
          }}
        >
          {/* Logo icon */}
          <div
            style={{
              width: 100,
              height: 100,
              background: C.black,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: `8px 8px 0px ${C.green}`,
              border: `2px solid ${C.black}`,
            }}
          >
            <svg
              viewBox="0 0 24 24"
              width="60"
              height="60"
              fill="none"
              stroke={C.green}
              strokeWidth="2.5"
              strokeLinecap="square"
              strokeLinejoin="miter"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>

          {/* Logo text */}
          <div
            style={{
              fontSize: 120,
              color: C.black,
              fontFamily: FONT.display,
              letterSpacing: 2,
            }}
          >
            EVAL<span style={{ color: C.green }}>HUB</span>
          </div>
        </div>

        {/* Tagline */}
        <div
          style={{
            opacity: taglineOpacity,
            marginTop: 24,
          }}
        >
          <h2
            style={{
              fontSize: 48,
              fontWeight: 800,
              color: C.black,
              fontFamily: FONT.body,
              textAlign: "center",
              margin: 0,
              textTransform: "uppercase",
            }}
          >
            Finally see how AI <span style={{ color: C.white, background: C.black, padding: "0 12px" }}>really</span> compares
          </h2>
        </div>

        {/* Feature pills */}
        <div
          style={{
            display: "flex",
            gap: 32,
            marginTop: 60,
          }}
        >
          {[
            {
              text: "Open & Transparent", delay: 90, icon: (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/>
                </svg>
              )
            },
            {
              text: "Rigorous Testing", delay: 100, icon: (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
                  <path d="M9 2v2"/><path d="M15 2v2"/><path d="M12 4v16"/><path d="M5 22h14"/><path d="M12 9a2 2 0 1 0 0 4 2 2 0 1 0 0-4z"/>
                </svg>
              )
            },
            {
              text: "Make Better Decisions", delay: 110, icon: (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
                  <path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M4.93 19.07l2.83-2.83"/><path d="M16.24 7.76l2.83-2.83"/>
                </svg>
              )
            },
          ].map((pill) => {
            const pillScale = popIn(frame, fps, pill.delay);
            return (
              <div
                key={pill.text}
                style={{
                  opacity: frame >= pill.delay ? 1 : 0,
                  transform: `scale(${pillScale})`,
                  padding: "16px 32px",
                  background: C.white,
                  border: `3px solid ${C.black}`,
                  boxShadow: `6px 6px 0px ${C.pink}`,
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                }}
              >
                <div style={{ color: C.pink }}>{pill.icon}</div>
                <span
                  style={{
                    fontSize: 20,
                    fontWeight: 800,
                    color: C.black,
                    fontFamily: FONT.body,
                    textTransform: "uppercase",
                  }}
                >
                  {pill.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
