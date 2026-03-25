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

export const ResultsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Section title animation
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Card entrance
  const cardScale = spring({
    frame: frame - 20,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Progress animation (0% to 100%)
  const progressValue = interpolate(frame, [60, 240], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Results reveal (after progress completes)
  const resultsOpacity = interpolate(frame, [260, 290], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Score counter animation
  const scoreCounter = interpolate(frame, [290, 380], [0, 87.5], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 30, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Floating animation
  const float = (offset: number) => Math.sin((frame + offset) * 0.05) * 5;

  // Celebration particles (after results)
  const showCelebration = frame > 350;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(180deg, #F0FDF4 0%, ${COLORS.light} 100%)`,
        padding: 60,
        opacity: fadeOut,
      }}
    >
      {/* Celebration particles */}
      {showCelebration && (
        <>
          {[...Array(12)].map((_, i) => {
            const angle = (i / 12) * Math.PI * 2;
            const distance = 100 + Math.sin(frame * 0.1 + i) * 50;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;
            const colors = [COLORS.mint, COLORS.purple, COLORS.yellow, COLORS.coral, COLORS.blue];
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  top: "50%",
                  left: "50%",
                  width: 12,
                  height: 12,
                  borderRadius: i % 2 === 0 ? "50%" : "3px",
                  background: colors[i % colors.length],
                  transform: `translate(${x}px, ${y}px) rotate(${frame * 2 + i * 30}deg)`,
                  opacity: interpolate(frame, [350, 380], [0, 0.8], { extrapolateRight: "clamp" }),
                }}
              />
            );
          })}
        </>
      )}

      {/* Section Title */}
      <div
        style={{
          opacity: titleOpacity,
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
            background: `linear-gradient(135deg, ${COLORS.mint} 0%, ${COLORS.blue} 100%)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span style={{ fontSize: 24 }}>📊</span>
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
            Watch Results in Real-Time
          </h2>
          <p
            style={{
              fontSize: 18,
              color: COLORS.gray,
              fontFamily: "system-ui, sans-serif",
              margin: 0,
            }}
          >
            See exactly how your AI performs
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div
        style={{
          display: "flex",
          gap: 40,
          transform: `scale(${cardScale})`,
        }}
      >
        {/* Left: Progress Card */}
        <div
          style={{
            flex: 1,
            background: "#fff",
            borderRadius: 24,
            padding: 40,
            boxShadow: "0 15px 50px rgba(0,0,0,0.1)",
          }}
        >
          {/* Header */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 32,
            }}
          >
            <div>
              <div
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: COLORS.gray,
                  fontFamily: "system-ui, sans-serif",
                  marginBottom: 4,
                }}
              >
                EVALUATION #42
              </div>
              <div
                style={{
                  fontSize: 24,
                  fontWeight: 700,
                  color: COLORS.dark,
                  fontFamily: "system-ui, sans-serif",
                }}
              >
                My Custom QA Dataset
              </div>
            </div>
            <div
              style={{
                padding: "8px 16px",
                borderRadius: 20,
                background: progressValue < 100 ? `${COLORS.blue}15` : `${COLORS.mint}15`,
                border: `2px solid ${progressValue < 100 ? COLORS.blue : COLORS.mint}`,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              {progressValue < 100 ? (
                <>
                  <div
                    style={{
                      width: 12,
                      height: 12,
                      borderRadius: "50%",
                      border: `2px solid ${COLORS.blue}`,
                      borderTopColor: "transparent",
                      animation: "spin 1s linear infinite",
                      transform: `rotate(${frame * 6}deg)`,
                    }}
                  />
                  <span
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: COLORS.blue,
                      fontFamily: "system-ui, sans-serif",
                    }}
                  >
                    Running
                  </span>
                </>
              ) : (
                <>
                  <span style={{ fontSize: 14 }}>✅</span>
                  <span
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: COLORS.mint,
                      fontFamily: "system-ui, sans-serif",
                    }}
                  >
                    Completed
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          <div style={{ marginBottom: 32 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: 12,
              }}
            >
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 600,
                  color: COLORS.gray,
                  fontFamily: "system-ui, sans-serif",
                }}
              >
                Processing samples...
              </span>
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 700,
                  color: COLORS.dark,
                  fontFamily: "monospace",
                }}
              >
                {Math.round(progressValue)}%
              </span>
            </div>
            <div
              style={{
                height: 12,
                background: "#E5E7EB",
                borderRadius: 6,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${progressValue}%`,
                  background: `linear-gradient(90deg, ${COLORS.mint} 0%, ${COLORS.blue} 100%)`,
                  borderRadius: 6,
                  transition: "width 0.1s ease",
                }}
              />
            </div>
            <div
              style={{
                marginTop: 12,
                fontSize: 13,
                color: COLORS.gray,
                fontFamily: "system-ui, sans-serif",
              }}
            >
              {Math.round((progressValue / 100) * 250)} / 250 samples evaluated
            </div>
          </div>

          {/* Results (revealed after completion) */}
          <div
            style={{
              opacity: resultsOpacity,
              transform: `translateY(${interpolate(frame, [260, 290], [20, 0], { extrapolateRight: "clamp" })}px)`,
            }}
          >
            <h3
              style={{
                fontSize: 18,
                fontWeight: 700,
                color: COLORS.dark,
                fontFamily: "system-ui, sans-serif",
                marginBottom: 20,
              }}
            >
              Results
            </h3>

            <div style={{ display: "flex", gap: 20 }}>
              {[
                { metric: "Helpfulness", score: scoreCounter, color: COLORS.mint },
                { metric: "Factuality", score: scoreCounter * 1.02, color: COLORS.blue },
                { metric: "Clarity", score: scoreCounter * 0.95, color: COLORS.purple },
              ].map((item, i) => (
                <div
                  key={item.metric}
                  style={{
                    flex: 1,
                    padding: 20,
                    background: `${item.color}08`,
                    borderRadius: 16,
                    border: `2px solid ${item.color}30`,
                    textAlign: "center",
                    transform: `translateY(${float(i * 30)}px)`,
                  }}
                >
                  <div
                    style={{
                      fontSize: 36,
                      fontWeight: 800,
                      color: item.color,
                      fontFamily: "system-ui, sans-serif",
                    }}
                  >
                    {item.score.toFixed(1)}
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: COLORS.gray,
                      fontFamily: "system-ui, sans-serif",
                      marginTop: 4,
                    }}
                  >
                    {item.metric}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Sample Preview */}
        <div
          style={{
            width: 400,
            background: "#fff",
            borderRadius: 24,
            padding: 32,
            boxShadow: "0 15px 50px rgba(0,0,0,0.1)",
            opacity: resultsOpacity,
          }}
        >
          <h3
            style={{
              fontSize: 18,
              fontWeight: 700,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
              marginBottom: 20,
            }}
          >
            Sample Preview
          </h3>

          <div
            style={{
              padding: 16,
              background: "#F9FAFB",
              borderRadius: 12,
              marginBottom: 16,
            }}
          >
            <div
              style={{
                fontSize: 12,
                fontWeight: 600,
                color: COLORS.gray,
                fontFamily: "system-ui, sans-serif",
                marginBottom: 8,
              }}
            >
              INPUT
            </div>
            <div
              style={{
                fontSize: 14,
                color: COLORS.dark,
                fontFamily: "system-ui, sans-serif",
                lineHeight: 1.5,
              }}
            >
              "What are the key benefits of renewable energy?"
            </div>
          </div>

          <div
            style={{
              padding: 16,
              background: `${COLORS.blue}08`,
              borderRadius: 12,
              border: `1px solid ${COLORS.blue}30`,
              marginBottom: 16,
            }}
          >
            <div
              style={{
                fontSize: 12,
                fontWeight: 600,
                color: COLORS.blue,
                fontFamily: "system-ui, sans-serif",
                marginBottom: 8,
              }}
            >
              MODEL OUTPUT
            </div>
            <div
              style={{
                fontSize: 14,
                color: COLORS.dark,
                fontFamily: "system-ui, sans-serif",
                lineHeight: 1.5,
              }}
            >
              "Renewable energy offers several key benefits: reduced carbon emissions, lower long-term costs..."
            </div>
          </div>

          <div
            style={{
              display: "flex",
              gap: 12,
            }}
          >
            <div
              style={{
                flex: 1,
                padding: "10px 14px",
                background: `${COLORS.mint}15`,
                borderRadius: 8,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: COLORS.mint,
                  fontFamily: "system-ui, sans-serif",
                }}
              >
                9.2
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: COLORS.gray,
                  fontFamily: "system-ui, sans-serif",
                }}
              >
                Helpfulness
              </div>
            </div>
            <div
              style={{
                flex: 1,
                padding: "10px 14px",
                background: `${COLORS.blue}15`,
                borderRadius: 8,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  color: COLORS.blue,
                  fontFamily: "system-ui, sans-serif",
                }}
              >
                8.8
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: COLORS.gray,
                  fontFamily: "system-ui, sans-serif",
                }}
              >
                Factuality
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Callout */}
      <div
        style={{
          position: "absolute",
          bottom: 60,
          left: "50%",
          transform: `translateX(-50%)`,
          opacity: interpolate(frame, [400, 430], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        <div
          style={{
            padding: "16px 32px",
            background: "#fff",
            borderRadius: 50,
            boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span style={{ fontSize: 24 }}>🎯</span>
          <span
            style={{
              fontSize: 18,
              fontWeight: 600,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
            }}
          >
            Now you know exactly how your AI performs
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
