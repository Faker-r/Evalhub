import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Mock leaderboard data
const LEADERBOARD_DATA = [
  { rank: 1, model: "GPT-4o", provider: "OpenAI", score: 92.4, std: 1.2 },
  { rank: 2, model: "Claude 3.5 Sonnet", provider: "Anthropic", score: 91.8, std: 1.4 },
  { rank: 3, model: "Gemini 1.5 Pro", provider: "Google", score: 89.7, std: 1.8 },
  { rank: 4, model: "Llama 3.1 405B", provider: "Meta", score: 88.2, std: 2.1 },
  { rank: 5, model: "Mistral Large", provider: "Mistral", score: 85.6, std: 2.4 },
  { rank: 6, model: "Command R+", provider: "Cohere", score: 84.3, std: 2.6 },
];

export const LeaderboardScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Scene title animation
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 20], [-30, 0], {
    extrapolateRight: "clamp",
  });

  // Table header animation
  const headerOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateRight: "clamp",
  });

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
        background: "linear-gradient(180deg, #09090b 0%, #18181b 100%)",
        padding: 80,
        opacity: fadeOut,
      }}
    >
      {/* Scene label */}
      <div
        style={{
          position: "absolute",
          top: 40,
          left: 80,
          display: "flex",
          alignItems: "center",
          gap: 12,
          opacity: titleOpacity,
        }}
      >
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: 10,
            background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <svg
            viewBox="0 0 24 24"
            width="24"
            height="24"
            fill="none"
            stroke="white"
            strokeWidth="2"
          >
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </div>
        <span
          style={{
            fontSize: 24,
            fontWeight: 700,
            fontFamily: "system-ui, sans-serif",
          }}
        >
          <span style={{ color: "#10b981" }}>Eval</span>
          <span style={{ color: "#fff" }}>Hub</span>
        </span>
      </div>

      {/* Title */}
      <div
        style={{
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
          marginTop: 60,
        }}
      >
        <h2
          style={{
            fontSize: 56,
            fontWeight: 800,
            color: "#ffffff",
            fontFamily: "system-ui, sans-serif",
            margin: 0,
          }}
        >
          Top Models
        </h2>
        <p
          style={{
            fontSize: 24,
            color: "#71717a",
            fontFamily: "system-ui, sans-serif",
            margin: "12px 0 0 0",
          }}
        >
          Ranked by aggregate performance across key benchmarks
        </p>
      </div>

      {/* Filter bar */}
      <div
        style={{
          opacity: headerOpacity,
          display: "flex",
          gap: 20,
          marginTop: 40,
          padding: 20,
          background: "rgba(255, 255, 255, 0.03)",
          borderRadius: 12,
          border: "1px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#10b981" strokeWidth="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
            <polyline points="17 6 23 6 23 12" />
          </svg>
          <span style={{ color: "#fff", fontSize: 16, fontFamily: "system-ui, sans-serif", fontWeight: 600 }}>
            Filters:
          </span>
        </div>
        <div
          style={{
            padding: "10px 20px",
            background: "rgba(255, 255, 255, 0.05)",
            borderRadius: 8,
            color: "#fff",
            fontSize: 14,
            fontFamily: "system-ui, sans-serif",
            border: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          Dataset: All Datasets
        </div>
        <div
          style={{
            padding: "10px 20px",
            background: "rgba(255, 255, 255, 0.05)",
            borderRadius: 8,
            color: "#fff",
            fontSize: 14,
            fontFamily: "system-ui, sans-serif",
            border: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          Metric: Helpfulness
        </div>
      </div>

      {/* Table */}
      <div
        style={{
          marginTop: 30,
          background: "rgba(255, 255, 255, 0.02)",
          borderRadius: 16,
          border: "1px solid rgba(255, 255, 255, 0.1)",
          overflow: "hidden",
        }}
      >
        {/* Table header */}
        <div
          style={{
            opacity: headerOpacity,
            display: "grid",
            gridTemplateColumns: "80px 1fr 1fr 200px",
            padding: "20px 30px",
            background: "rgba(255, 255, 255, 0.03)",
            borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          <span style={{ color: "#71717a", fontSize: 14, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
            Rank
          </span>
          <span style={{ color: "#71717a", fontSize: 14, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
            Model
          </span>
          <span style={{ color: "#71717a", fontSize: 14, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
            Provider
          </span>
          <span
            style={{
              color: "#71717a",
              fontSize: 14,
              fontWeight: 700,
              fontFamily: "system-ui, sans-serif",
              textAlign: "right",
            }}
          >
            Score (mean ± std)
          </span>
        </div>

        {/* Table rows */}
        {LEADERBOARD_DATA.map((entry, index) => {
          const rowDelay = 50 + index * 15;
          const rowOpacity = interpolate(frame, [rowDelay, rowDelay + 20], [0, 1], {
            extrapolateRight: "clamp",
          });
          const rowX = interpolate(frame, [rowDelay, rowDelay + 20], [30, 0], {
            extrapolateRight: "clamp",
          });

          const isTopThree = entry.rank <= 3;

          return (
            <div
              key={entry.rank}
              style={{
                opacity: rowOpacity,
                transform: `translateX(${rowX}px)`,
                display: "grid",
                gridTemplateColumns: "80px 1fr 1fr 200px",
                padding: "24px 30px",
                borderBottom: "1px solid rgba(255, 255, 255, 0.05)",
                background: isTopThree ? "rgba(16, 185, 129, 0.05)" : "transparent",
              }}
            >
              <span
                style={{
                  color: isTopThree ? "#10b981" : "#71717a",
                  fontSize: 18,
                  fontWeight: 700,
                  fontFamily: "monospace",
                }}
              >
                #{entry.rank}
              </span>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span
                  style={{
                    color: "#ffffff",
                    fontSize: 18,
                    fontWeight: 700,
                    fontFamily: "system-ui, sans-serif",
                  }}
                >
                  {entry.model}
                </span>
                {isTopThree && (
                  <svg
                    viewBox="0 0 24 24"
                    width="16"
                    height="16"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="2"
                  >
                    <line x1="7" y1="17" x2="17" y2="7" />
                    <polyline points="7 7 17 7 17 17" />
                  </svg>
                )}
              </div>
              <span
                style={{
                  color: "#a1a1aa",
                  fontSize: 16,
                  fontFamily: "system-ui, sans-serif",
                }}
              >
                {entry.provider}
              </span>
              <div style={{ textAlign: "right" }}>
                <span
                  style={{
                    color: isTopThree ? "#10b981" : "#ffffff",
                    fontSize: 20,
                    fontWeight: 700,
                    fontFamily: "monospace",
                  }}
                >
                  {entry.score.toFixed(1)}
                </span>
                <span
                  style={{
                    color: "#71717a",
                    fontSize: 14,
                    fontFamily: "monospace",
                    marginLeft: 8,
                  }}
                >
                  ± {entry.std.toFixed(1)}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer text */}
      <div
        style={{
          opacity: interpolate(frame, [150, 170], [0, 1], { extrapolateRight: "clamp" }),
          marginTop: 30,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span
          style={{
            color: "#71717a",
            fontSize: 16,
            fontFamily: "system-ui, sans-serif",
          }}
        >
          Compare models across different providers
        </span>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            color: "#10b981",
            fontSize: 16,
            fontWeight: 600,
            fontFamily: "system-ui, sans-serif",
          }}
        >
          View Full Rankings
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </div>
      </div>
    </AbsoluteFill>
  );
};
