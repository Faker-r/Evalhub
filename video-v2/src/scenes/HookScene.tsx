import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";

// Playful color palette
const COLORS = {
  coral: "#FF6B6B",
  mint: "#10B981",
  purple: "#8B5CF6",
  yellow: "#FBBF24",
  blue: "#3B82F6",
  pink: "#EC4899",
  dark: "#1F2937",
  light: "#F9FAFB",
};

export const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Phase 1: "You use AI every day" with icons (0-5s)
  const phase1Opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const phase1Exit = interpolate(frame, [140, 160], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Phase 2: "Same model, different results" (5-12s)
  const phase2Start = 160;
  const phase2Opacity = interpolate(frame, [phase2Start, phase2Start + 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const phase2Exit = interpolate(frame, [380, 400], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Phase 3: "How do you know which one to trust?" (12-18s)
  const phase3Start = 400;
  const phase3Opacity = interpolate(frame, [phase3Start, phase3Start + 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 30, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Floating animation for icons
  const float = (offset: number) => Math.sin((frame + offset) * 0.05) * 8;

  // Bounce animation
  const bounce = spring({
    frame: frame - 30,
    fps,
    config: { damping: 8, stiffness: 150 },
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${COLORS.light} 0%, #EEF2FF 100%)`,
        opacity: fadeOut,
      }}
    >
      {/* Decorative background shapes */}
      <div
        style={{
          position: "absolute",
          top: 100,
          right: 150,
          width: 200,
          height: 200,
          borderRadius: "50%",
          background: `${COLORS.purple}15`,
          transform: `translateY(${float(0)}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 150,
          left: 100,
          width: 150,
          height: 150,
          borderRadius: "30%",
          background: `${COLORS.coral}15`,
          transform: `translateY(${float(50)}px) rotate(${frame * 0.2}deg)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "40%",
          left: 80,
          width: 80,
          height: 80,
          borderRadius: "20%",
          background: `${COLORS.mint}20`,
          transform: `translateY(${float(100)}px)`,
        }}
      />

      {/* Phase 1: "You use AI every day" */}
      {frame < 180 && (
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
              fontSize: 72,
              fontWeight: 800,
              color: COLORS.dark,
              fontFamily: "system-ui, -apple-system, sans-serif",
              textAlign: "center",
              margin: 0,
              transform: `scale(${bounce})`,
            }}
          >
            You use{" "}
            <span
              style={{
                background: `linear-gradient(135deg, ${COLORS.purple} 0%, ${COLORS.blue} 100%)`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              AI
            </span>{" "}
            every day
          </h1>

          {/* AI use case icons */}
          <div
            style={{
              display: "flex",
              gap: 60,
              marginTop: 60,
              opacity: interpolate(frame, [40, 70], [0, 1], { extrapolateRight: "clamp" }),
            }}
          >
            {[
              { icon: "💬", label: "Chatbots", color: COLORS.blue, delay: 0 },
              { icon: "🔍", label: "Search", color: COLORS.purple, delay: 10 },
              { icon: "✍️", label: "Writing", color: COLORS.coral, delay: 20 },
              { icon: "🎨", label: "Images", color: COLORS.pink, delay: 30 },
            ].map((item, i) => {
              const itemBounce = spring({
                frame: frame - 50 - item.delay,
                fps,
                config: { damping: 10, stiffness: 200 },
              });
              return (
                <div
                  key={item.label}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 16,
                    transform: `scale(${itemBounce}) translateY(${float(i * 30)}px)`,
                  }}
                >
                  <div
                    style={{
                      width: 100,
                      height: 100,
                      borderRadius: 24,
                      background: `${item.color}15`,
                      border: `3px solid ${item.color}30`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 48,
                    }}
                  >
                    {item.icon}
                  </div>
                  <span
                    style={{
                      fontSize: 20,
                      fontWeight: 600,
                      color: COLORS.dark,
                      fontFamily: "system-ui, sans-serif",
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

      {/* Phase 2: "Same model, different results" */}
      {frame >= 160 && frame < 420 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            opacity: phase2Opacity * phase2Exit,
            padding: 80,
          }}
        >
          <h2
            style={{
              fontSize: 56,
              fontWeight: 700,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
              textAlign: "center",
              marginBottom: 60,
            }}
          >
            But did you know...
          </h2>

          {/* Visual: Same model → Different providers → Different outputs */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 40,
            }}
          >
            {/* Input */}
            <div
              style={{
                opacity: interpolate(frame, [phase2Start + 20, phase2Start + 40], [0, 1], {
                  extrapolateRight: "clamp",
                }),
                transform: `translateX(${interpolate(frame, [phase2Start + 20, phase2Start + 40], [-30, 0], { extrapolateRight: "clamp" })}px)`,
              }}
            >
              <div
                style={{
                  padding: "24px 32px",
                  background: "#fff",
                  borderRadius: 16,
                  boxShadow: "0 8px 32px rgba(0,0,0,0.08)",
                  border: `2px solid ${COLORS.blue}30`,
                }}
              >
                <div style={{ fontSize: 16, color: "#6B7280", marginBottom: 8, fontFamily: "system-ui, sans-serif" }}>
                  Same AI Model
                </div>
                <div style={{ fontSize: 28, fontWeight: 700, color: COLORS.blue, fontFamily: "system-ui, sans-serif" }}>
                  🤖 GPT-4
                </div>
              </div>
            </div>

            {/* Arrow */}
            <div
              style={{
                opacity: interpolate(frame, [phase2Start + 40, phase2Start + 60], [0, 1], {
                  extrapolateRight: "clamp",
                }),
              }}
            >
              <svg width="60" height="40" viewBox="0 0 60 40">
                <path
                  d="M5 20 L45 20 M35 10 L45 20 L35 30"
                  stroke={COLORS.dark}
                  strokeWidth="4"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>

            {/* Different providers with different outputs */}
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              {[
                { provider: "Provider A", quality: "Great answer! ✓", color: COLORS.mint },
                { provider: "Provider B", quality: "Okay answer ~", color: COLORS.yellow },
                { provider: "Provider C", quality: "Wrong answer ✗", color: COLORS.coral },
              ].map((item, i) => {
                const itemOpacity = interpolate(
                  frame,
                  [phase2Start + 60 + i * 25, phase2Start + 80 + i * 25],
                  [0, 1],
                  { extrapolateRight: "clamp" }
                );
                const itemX = interpolate(
                  frame,
                  [phase2Start + 60 + i * 25, phase2Start + 80 + i * 25],
                  [30, 0],
                  { extrapolateRight: "clamp" }
                );
                return (
                  <div
                    key={item.provider}
                    style={{
                      opacity: itemOpacity,
                      transform: `translateX(${itemX}px)`,
                      display: "flex",
                      alignItems: "center",
                      gap: 16,
                      padding: "16px 24px",
                      background: "#fff",
                      borderRadius: 12,
                      boxShadow: "0 4px 16px rgba(0,0,0,0.06)",
                      border: `2px solid ${item.color}40`,
                    }}
                  >
                    <div
                      style={{
                        width: 12,
                        height: 12,
                        borderRadius: "50%",
                        background: item.color,
                      }}
                    />
                    <span
                      style={{
                        fontSize: 18,
                        fontWeight: 600,
                        color: COLORS.dark,
                        fontFamily: "system-ui, sans-serif",
                        minWidth: 100,
                      }}
                    >
                      {item.provider}
                    </span>
                    <span
                      style={{
                        fontSize: 16,
                        color: item.color,
                        fontFamily: "system-ui, sans-serif",
                        fontWeight: 600,
                      }}
                    >
                      {item.quality}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Explanation text */}
          <p
            style={{
              marginTop: 50,
              fontSize: 24,
              color: "#6B7280",
              fontFamily: "system-ui, sans-serif",
              textAlign: "center",
              opacity: interpolate(frame, [phase2Start + 140, phase2Start + 160], [0, 1], {
                extrapolateRight: "clamp",
              }),
            }}
          >
            The same AI model can give{" "}
            <span style={{ color: COLORS.coral, fontWeight: 700 }}>different results</span>
            {" "}depending on who runs it
          </p>
        </div>
      )}

      {/* Phase 3: "How do you know which one to trust?" */}
      {frame >= 400 && (
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
          <h2
            style={{
              fontSize: 64,
              fontWeight: 800,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
              textAlign: "center",
              lineHeight: 1.3,
            }}
          >
            How do you know{" "}
            <span
              style={{
                background: `linear-gradient(135deg, ${COLORS.coral} 0%, ${COLORS.purple} 100%)`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              which one
            </span>
            <br />
            to trust?
          </h2>

          {/* Animated question marks */}
          <div
            style={{
              display: "flex",
              gap: 30,
              marginTop: 40,
              opacity: interpolate(frame, [phase3Start + 30, phase3Start + 50], [0, 1], {
                extrapolateRight: "clamp",
              }),
            }}
          >
            {["🤔", "❓", "🤷"].map((emoji, i) => (
              <span
                key={i}
                style={{
                  fontSize: 60,
                  transform: `translateY(${float(i * 40)}px)`,
                }}
              >
                {emoji}
              </span>
            ))}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
