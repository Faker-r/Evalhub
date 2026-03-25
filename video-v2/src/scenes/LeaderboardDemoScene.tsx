import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const COLORS = {
  mint: "#10B981",
  mintLight: "#D1FAE5",
  purple: "#8B5CF6",
  blue: "#3B82F6",
  coral: "#FF6B6B",
  yellow: "#FBBF24",
  dark: "#1F2937",
  light: "#F9FAFB",
  gray: "#6B7280",
};

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
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 20], [-20, 0], {
    extrapolateRight: "clamp",
  });

  // Browser mockup entrance
  const browserScale = spring({
    frame: frame - 30,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Filter interaction animation (simulated click)
  const filterClickFrame = 180;
  const filterHighlight = interpolate(
    frame,
    [filterClickFrame, filterClickFrame + 15, filterClickFrame + 30],
    [1, 1.05, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Cursor animation
  const cursorX = interpolate(
    frame,
    [60, 120, 180, 240],
    [300, 500, 350, 600],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const cursorY = interpolate(
    frame,
    [60, 120, 180, 240],
    [400, 300, 250, 350],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const cursorVisible = interpolate(frame, [60, 80], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Score highlight animation
  const scoreHighlight = Math.floor((frame - 300) / 40) % 5;

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 30, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 100%)`,
        padding: 60,
        opacity: fadeOut,
      }}
    >
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
            width: 48,
            height: 48,
            borderRadius: 12,
            background: `linear-gradient(135deg, ${COLORS.purple} 0%, ${COLORS.blue} 100%)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span style={{ fontSize: 24 }}>🏆</span>
        </div>
        <div>
          <h2
            style={{
              fontSize: 36,
              fontWeight: 800,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
              margin: 0,
            }}
          >
            Compare AI Models
          </h2>
          <p
            style={{
              fontSize: 18,
              color: COLORS.gray,
              fontFamily: "system-ui, sans-serif",
              margin: 0,
            }}
          >
            See who&apos;s really the best
          </p>
        </div>
      </div>

      {/* Browser Mockup */}
      <div
        style={{
          transform: `scale(${browserScale})`,
          background: "#fff",
          borderRadius: 20,
          boxShadow: "0 25px 80px rgba(0,0,0,0.12)",
          overflow: "hidden",
          border: "1px solid #E5E7EB",
        }}
      >
        {/* Browser Header */}
        <div
          style={{
            padding: "16px 24px",
            background: "#F9FAFB",
            borderBottom: "1px solid #E5E7EB",
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          {/* Traffic lights */}
          <div style={{ display: "flex", gap: 8 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F57" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FFBD2E" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28C840" }} />
          </div>

          {/* URL bar */}
          <div
            style={{
              flex: 1,
              padding: "10px 20px",
              background: "#fff",
              borderRadius: 8,
              border: "1px solid #E5E7EB",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
            <span style={{ fontSize: 14, color: COLORS.gray, fontFamily: "system-ui, sans-serif" }}>
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
                borderRadius: 8,
                background: `linear-gradient(135deg, ${COLORS.mint} 0%, #059669 100%)`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="white" strokeWidth="2.5">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
            </div>
            <span style={{ fontSize: 22, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
              <span style={{ color: COLORS.mint }}>Eval</span>
              <span style={{ color: COLORS.dark }}>Hub</span>
            </span>
          </div>

          {/* Filters */}
          <div
            style={{
              display: "flex",
              gap: 16,
              marginBottom: 24,
              padding: 16,
              background: "#F9FAFB",
              borderRadius: 12,
            }}
          >
            <div
              style={{
                transform: `scale(${frame >= filterClickFrame && frame < filterClickFrame + 30 ? filterHighlight : 1})`,
                padding: "10px 20px",
                background: "#fff",
                borderRadius: 8,
                border: `2px solid ${frame >= filterClickFrame ? COLORS.mint : "#E5E7EB"}`,
                fontSize: 14,
                fontWeight: 600,
                color: COLORS.dark,
                fontFamily: "system-ui, sans-serif",
                display: "flex",
                alignItems: "center",
                gap: 8,
                transition: "all 0.2s",
              }}
            >
              <span>Dataset:</span>
              <span style={{ color: COLORS.mint }}>MMLU-Pro</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </div>

            <div
              style={{
                padding: "10px 20px",
                background: "#fff",
                borderRadius: 8,
                border: "2px solid #E5E7EB",
                fontSize: 14,
                fontWeight: 600,
                color: COLORS.dark,
                fontFamily: "system-ui, sans-serif",
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <span>Metric:</span>
              <span style={{ color: COLORS.purple }}>Helpfulness</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </div>
          </div>

          {/* Leaderboard Table */}
          <div style={{ borderRadius: 12, border: "1px solid #E5E7EB", overflow: "hidden" }}>
            {/* Header */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "60px 1.2fr 1fr 100px 80px",
                padding: "14px 20px",
                background: "#F9FAFB",
                borderBottom: "1px solid #E5E7EB",
              }}
            >
              <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.gray, fontFamily: "system-ui, sans-serif" }}>
                RANK
              </span>
              <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.gray, fontFamily: "system-ui, sans-serif" }}>
                MODEL
              </span>
              <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.gray, fontFamily: "system-ui, sans-serif" }}>
                PROVIDER
              </span>
              <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.gray, fontFamily: "system-ui, sans-serif", textAlign: "right" }}>
                SCORE
              </span>
              <span style={{ fontSize: 12, fontWeight: 700, color: COLORS.gray, fontFamily: "system-ui, sans-serif", textAlign: "right" }}>
                CHANGE
              </span>
            </div>

            {/* Rows */}
            {LEADERBOARD.map((row, i) => {
              const rowDelay = 80 + i * 20;
              const rowOpacity = interpolate(frame, [rowDelay, rowDelay + 20], [0, 1], {
                extrapolateRight: "clamp",
              });
              const rowX = interpolate(frame, [rowDelay, rowDelay + 20], [20, 0], {
                extrapolateRight: "clamp",
              });

              const isHighlighted = frame > 300 && i === scoreHighlight;

              return (
                <div
                  key={row.rank}
                  style={{
                    opacity: rowOpacity,
                    transform: `translateX(${rowX}px)`,
                    display: "grid",
                    gridTemplateColumns: "60px 1.2fr 1fr 100px 80px",
                    padding: "16px 20px",
                    background: isHighlighted ? `${COLORS.mint}10` : row.rank <= 3 ? `${COLORS.mint}05` : "#fff",
                    borderBottom: i < LEADERBOARD.length - 1 ? "1px solid #F3F4F6" : "none",
                    alignItems: "center",
                    transition: "background 0.3s",
                  }}
                >
                  <span
                    style={{
                      fontSize: 16,
                      fontWeight: 700,
                      color: row.rank <= 3 ? COLORS.mint : COLORS.gray,
                      fontFamily: "monospace",
                    }}
                  >
                    #{row.rank}
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span
                      style={{
                        fontSize: 16,
                        fontWeight: 700,
                        color: COLORS.dark,
                        fontFamily: "system-ui, sans-serif",
                      }}
                    >
                      {row.model}
                    </span>
                    {row.rank === 1 && <span style={{ fontSize: 16 }}>👑</span>}
                  </div>
                  <span
                    style={{
                      fontSize: 14,
                      color: COLORS.gray,
                      fontFamily: "system-ui, sans-serif",
                    }}
                  >
                    {row.provider}
                  </span>
                  <span
                    style={{
                      fontSize: 18,
                      fontWeight: 800,
                      color: isHighlighted ? COLORS.mint : COLORS.dark,
                      fontFamily: "monospace",
                      textAlign: "right",
                      transform: isHighlighted ? "scale(1.1)" : "scale(1)",
                      transition: "all 0.2s",
                    }}
                  >
                    {row.score}
                  </span>
                  <span
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: row.change.startsWith("+") ? COLORS.mint : COLORS.coral,
                      fontFamily: "monospace",
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

      {/* Animated cursor */}
      <div
        style={{
          position: "absolute",
          left: cursorX,
          top: cursorY,
          opacity: cursorVisible,
          zIndex: 100,
          pointerEvents: "none",
          filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.2))",
        }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="#fff" stroke="#000" strokeWidth="1">
          <path d="M5 3l14 9-6.5 1.5L11 20z" />
        </svg>
        {/* Click indicator */}
        {frame >= filterClickFrame && frame < filterClickFrame + 20 && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: 40,
              height: 40,
              borderRadius: "50%",
              background: `${COLORS.mint}40`,
              transform: `translate(-50%, -50%) scale(${interpolate(
                frame,
                [filterClickFrame, filterClickFrame + 20],
                [0.5, 2],
                { extrapolateRight: "clamp" }
              )})`,
              opacity: interpolate(
                frame,
                [filterClickFrame, filterClickFrame + 20],
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
          opacity: interpolate(frame, [400, 430], [0, 1], { extrapolateRight: "clamp" }),
          transform: `translateY(${interpolate(frame, [400, 430], [20, 0], { extrapolateRight: "clamp" })}px)`,
        }}
      >
        <div
          style={{
            padding: "20px 28px",
            background: "#fff",
            borderRadius: 16,
            boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
            border: `2px solid ${COLORS.mint}`,
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span style={{ fontSize: 28 }}>💡</span>
          <span
            style={{
              fontSize: 18,
              fontWeight: 600,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
            }}
          >
            Filter by dataset, metric, or provider
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
