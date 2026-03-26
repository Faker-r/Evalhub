import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT, popIn } from "../theme";

// Leaderboard data
const LEADERBOARD = [
  { rank: 1, model: "GPT-4o", provider: "OpenAI", score: 92.4, change: "+2.1" },
  { rank: 2, model: "Claude 3.5 Sonnet", provider: "Anthropic", score: 91.8, change: "+1.4" },
  { rank: 3, model: "Gemini 1.5 Pro", provider: "Google", score: 89.7, change: "-0.3" },
  { rank: 4, model: "Llama 3.1 405B", provider: "Meta", score: 88.2, change: "+3.2" },
  { rank: 5, model: "Mistral Large", provider: "Mistral", score: 85.6, change: "+0.8" },
];

export const LeaderboardDemoScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Section title animation
  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 15], [-20, 0], {
    extrapolateRight: "clamp",
  });

  // Filter interaction animation (simulated click at frame 130 instead of 180)
  const filterClickFrame = 130;
  const filterHighlight = interpolate(
    frame,
    [filterClickFrame, filterClickFrame + 10, filterClickFrame + 20],
    [1, 1.05, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Cursor animation (compressed)
  const cursorX = interpolate(
    frame,
    [40, 80, 130, 180],
    [300, 500, 350, 600],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const cursorY = interpolate(
    frame,
    [40, 80, 130, 180],
    [400, 300, 250, 350],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const cursorVisible = interpolate(frame, [40, 60], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Score highlight animation (starts earlier)
  const scoreHighlightStart = 220;
  const scoreHighlight = Math.floor(Math.max(0, frame - scoreHighlightStart) / 30) % 5;

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
        padding: 60,
        opacity: fadeOut,
      }}
    >
      {/* Subtle radial noise texture */}
      <svg
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.05, pointerEvents: "none" }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <filter id="leaderboard-noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#leaderboard-noise)" />
      </svg>

      {/* Decorative Grid Lines */}
      <div style={{ position: "absolute", top: "20%", left: 0, right: 0, height: 1, background: C.black, opacity: 0.05 }} />
      <div style={{ position: "absolute", top: "80%", left: 0, right: 0, height: 1, background: C.black, opacity: 0.05 }} />
      <div style={{ position: "absolute", left: "20%", top: 0, bottom: 0, width: 1, background: C.black, opacity: 0.05 }} />
      <div style={{ position: "absolute", right: "20%", top: 0, bottom: 0, width: 1, background: C.black, opacity: 0.05 }} />

      {/* Section Title */}
      <div
        style={{
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          marginBottom: 30,
          display: "flex",
          alignItems: "center",
          gap: 16,
        }}
      >
        <div
          style={{
            width: 56,
            height: 56,
            background: C.black,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: `4px 4px 0px ${C.green}`,
          }}
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={C.green} strokeWidth="2.5" strokeLinecap="square">
            <path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 4h10v6a5 5 0 0 1-10 0V4z"/><path d="M7 6H4v3a4 4 0 0 0 4 4"/><path d="M17 6h3v3a4 4 0 0 1-4 4"/>
          </svg>
        </div>
        <div>
          <h2
            style={{
              fontSize: 48,
              color: C.black,
              fontFamily: FONT.display,
              margin: 0,
              textTransform: "uppercase",
            }}
          >
            Compare Models
          </h2>
          <p
            style={{
              fontSize: 20,
              fontWeight: 700,
              color: C.grayMid,
              fontFamily: FONT.body,
              margin: 0,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            See who's really the best
          </p>
        </div>
      </div>

      {/* Browser Mockup */}
      <div
        style={{
          transform: `scale(${popIn(frame, fps, 0, { damping: 16, stiffness: 100 })})`,
          background: C.white,
          border: `4px solid ${C.black}`,
          boxShadow: `16px 16px 0px ${C.pink}`,
          overflow: "hidden",
        }}
      >
        {/* Browser Header */}
        <div
          style={{
            padding: "16px 24px",
            background: C.grayLight,
            borderBottom: `4px solid ${C.black}`,
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          {/* Traffic lights */}
          <div style={{ display: "flex", gap: 8 }}>
            <div style={{ width: 14, height: 14, borderRadius: "50%", background: C.black }} />
            <div style={{ width: 14, height: 14, borderRadius: "50%", border: `2px solid ${C.black}` }} />
            <div style={{ width: 14, height: 14, borderRadius: "50%", border: `2px solid ${C.black}` }} />
          </div>

          {/* URL bar */}
          <div
            style={{
              flex: 1,
              padding: "8px 16px",
              background: C.white,
              border: `2px solid ${C.black}`,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={C.black} strokeWidth="2.5">
              <circle cx="12" cy="12" r="10" />
              <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
            <span style={{ fontSize: 16, fontWeight: 700, color: C.black, fontFamily: FONT.body }}>
              evalhub.io/leaderboard
            </span>
          </div>
        </div>

        {/* App Content */}
        <div style={{ padding: 32 }}>
          {/* App Header */}
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
            <div
              style={{
                width: 36,
                height: 36,
                background: C.black,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: `4px 4px 0px ${C.green}`,
              }}
            >
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke={C.green} strokeWidth="3" strokeLinecap="square">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
            </div>
            <span style={{ fontSize: 28, color: C.black, fontFamily: FONT.display }}>
              EVAL<span style={{ color: C.green }}>HUB</span>
            </span>
          </div>

          {/* Filters */}
          <div
            style={{
              display: "flex",
              gap: 16,
              marginBottom: 24,
              padding: 16,
              background: C.grayLight,
              border: `2px solid ${C.black}`,
            }}
          >
            <div
              style={{
                transform: `scale(${frame >= filterClickFrame && frame < filterClickFrame + 20 ? filterHighlight : 1})`,
                padding: "8px 16px",
                background: C.white,
                border: `2px solid ${frame >= filterClickFrame ? C.green : C.black}`,
                boxShadow: frame >= filterClickFrame ? `4px 4px 0px ${C.green}` : `4px 4px 0px ${C.black}`,
                fontSize: 14,
                fontWeight: 800,
                color: C.black,
                fontFamily: FONT.mono,
                display: "flex",
                alignItems: "center",
                gap: 8,
                transition: "all 0.1s",
              }}
            >
              <span>DATASET:</span>
              <span style={{ color: C.green }}>MMLU-PRO</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </div>

            <div
              style={{
                padding: "8px 16px",
                background: C.white,
                border: `2px solid ${C.black}`,
                boxShadow: `4px 4px 0px ${C.black}`,
                fontSize: 14,
                fontWeight: 800,
                color: C.black,
                fontFamily: FONT.mono,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <span>METRIC:</span>
              <span style={{ color: C.pink }}>HELPFULNESS</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </div>
          </div>

          {/* Leaderboard Table */}
          <div style={{ border: `2px solid ${C.black}`, alignSelf: "stretch" }}>
            {/* Header */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "80px 1.2fr 1fr 100px 80px",
                padding: "16px 20px",
                background: C.black,
              }}
            >
              <span style={{ fontSize: 12, fontWeight: 800, color: C.white, fontFamily: FONT.body, letterSpacing: 1 }}>RANK</span>
              <span style={{ fontSize: 12, fontWeight: 800, color: C.white, fontFamily: FONT.body, letterSpacing: 1 }}>MODEL</span>
              <span style={{ fontSize: 12, fontWeight: 800, color: C.white, fontFamily: FONT.body, letterSpacing: 1 }}>PROVIDER</span>
              <span style={{ fontSize: 12, fontWeight: 800, color: C.white, fontFamily: FONT.body, letterSpacing: 1, textAlign: "right" }}>SCORE</span>
              <span style={{ fontSize: 12, fontWeight: 800, color: C.white, fontFamily: FONT.body, letterSpacing: 1, textAlign: "right" }}>CHANGE</span>
            </div>

            {/* Rows */}
            {LEADERBOARD.map((row, i) => {
              const rowDelay = 60 + i * 15; // compressed stagger
              const rowOpacity = interpolate(frame, [rowDelay, rowDelay + 15], [0, 1], {
                extrapolateRight: "clamp",
              });
              const rowX = interpolate(frame, [rowDelay, rowDelay + 15], [20, 0], {
                extrapolateRight: "clamp",
              });

              const isHighlighted = frame > scoreHighlightStart && i === scoreHighlight;

              return (
                <div
                  key={row.rank}
                  style={{
                    opacity: rowOpacity,
                    transform: `translateX(${rowX}px)`,
                    display: "grid",
                    gridTemplateColumns: "80px 1.2fr 1fr 100px 80px",
                    padding: "16px 20px",
                    background: isHighlighted ? C.green : row.rank % 2 === 0 ? C.grayLight : C.white,
                    borderBottom: i < LEADERBOARD.length - 1 ? `2px solid ${C.black}` : "none",
                    alignItems: "center",
                    transition: "background 0.1s",
                  }}
                >
                  <span
                    style={{
                      fontSize: 18,
                      fontWeight: 800,
                      color: isHighlighted ? C.black : row.rank <= 3 ? C.pink : C.grayMid,
                      fontFamily: FONT.display,
                    }}
                  >
                    #{row.rank}
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span
                      style={{
                        fontSize: 16,
                        fontWeight: 800,
                        color: C.black,
                        fontFamily: FONT.body,
                      }}
                    >
                      {row.model}
                    </span>
                    {row.rank === 1 && (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill={isHighlighted ? C.white : C.pink} stroke="none">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                      </svg>
                    )}
                  </div>
                  <span
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: isHighlighted ? C.black : C.grayMid,
                      fontFamily: FONT.body,
                      textTransform: "uppercase",
                    }}
                  >
                    {row.provider}
                  </span>
                  <span
                    style={{
                      fontSize: 20,
                      fontWeight: 800,
                      color: isHighlighted ? C.white : C.black,
                      fontFamily: FONT.body,
                      textAlign: "right",
                      transform: isHighlighted ? "scale(1.2)" : "scale(1)",
                      transition: "all 0.1s",
                    }}
                  >
                    {row.score}
                  </span>
                  <span
                    style={{
                      fontSize: 14,
                      fontWeight: 800,
                      color: isHighlighted ? C.black : row.change.startsWith("+") ? C.green : C.pink,
                      fontFamily: FONT.body,
                      textAlign: "right",
                    }}
                  >
                    {row.change}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Animated cursor (black stroke, white fill) */}
      <div
        style={{
          position: "absolute",
          left: cursorX,
          top: cursorY,
          opacity: cursorVisible,
          zIndex: 100,
          pointerEvents: "none",
        }}
      >
        <svg width="32" height="32" viewBox="0 0 24 24" fill={C.white} stroke={C.black} strokeWidth="2">
          <path d="M5 3l14 9-6.5 1.5L11 20z" />
        </svg>
        {/* Click indicator */}
        {frame >= filterClickFrame && frame < filterClickFrame + 15 && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: 40,
              height: 40,
              borderRadius: "50%",
              background: C.pink,
              transform: `translate(-50%, -50%) scale(${interpolate(
                frame,
                [filterClickFrame, filterClickFrame + 15],
                [0.5, 2],
                { extrapolateRight: "clamp" }
              )})`,
              opacity: interpolate(
                frame,
                [filterClickFrame, filterClickFrame + 15],
                [1, 0],
                { extrapolateRight: "clamp" }
              ),
            }}
          />
        )}
      </div>

      {/* Callout bubble */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          right: 80,
          opacity: interpolate(frame, [200, 220], [0, 1], { extrapolateRight: "clamp" }),
          transform: `translateY(${interpolate(frame, [200, 220], [20, 0], { extrapolateRight: "clamp" })}) scale(${popIn(frame, fps, 200)})`,
        }}
      >
        <div
          style={{
            padding: "20px 28px",
            background: C.white,
            border: `4px solid ${C.black}`,
            boxShadow: `8px 8px 0px ${C.pink}`,
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={C.pink} strokeWidth="3" strokeLinecap="square">
            <path d="M12 2v2"/><path d="M12 20v2"/><path d="M4.22 4.22l1.42 1.42"/><path d="M18.36 18.36l1.42 1.42"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="M4.22 19.78l1.42-1.42"/><path d="M18.36 5.64l1.42-1.42"/><circle cx="12" cy="12" r="4"/>
          </svg>
          <span
            style={{
              fontSize: 20,
              fontWeight: 800,
              color: C.black,
              fontFamily: FONT.body,
              textTransform: "uppercase",
            }}
          >
            Filter by dataset, metric, or provider
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
