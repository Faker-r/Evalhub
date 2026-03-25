import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  spring,
} from "remotion";

// Mock results data
const MOCK_RESULTS = [
  {
    id: 1,
    dataset: "Custom QA Dataset",
    model: "GPT-4o",
    provider: "OpenAI",
    status: "completed",
    scores: { Helpfulness: { mean: 8.7, std: 1.2 }, Factuality: { mean: 9.1, std: 0.8 } },
  },
  {
    id: 2,
    dataset: "MMLU-Pro",
    model: "Claude 3.5 Sonnet",
    provider: "Anthropic",
    status: "completed",
    scores: { Accuracy: { mean: 91.2, std: 2.1 } },
  },
  {
    id: 3,
    dataset: "HumanEval+",
    model: "Llama 3.1 405B",
    provider: "Meta",
    status: "running",
    progress: 67,
  },
];

export const ResultsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  const fadeOut = interpolate(
    frame,
    [durationInFrames - 30, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Stats card animation
  const statsDelay = 30;
  const statsOpacity = interpolate(frame, [statsDelay, statsDelay + 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Running progress animation
  const runningProgress = interpolate(
    frame,
    [100, 500],
    [67, 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(180deg, #fafafa 0%, #f4f4f5 100%)",
        opacity: fadeOut,
        padding: 80,
      }}
    >
      {/* Header */}
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
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" strokeWidth="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </div>
        <span style={{ fontSize: 24, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
          <span style={{ color: "#10b981" }}>Eval</span>
          <span style={{ color: "#09090b" }}>Hub</span>
        </span>
      </div>

      {/* Title */}
      <div
        style={{
          opacity: titleOpacity,
          marginTop: 60,
        }}
      >
        <h1 style={{ color: "#09090b", fontSize: 48, fontWeight: 800, margin: 0, fontFamily: "system-ui, sans-serif" }}>
          Evaluation Results
        </h1>
        <p style={{ color: "#71717a", fontSize: 18, margin: "8px 0 0", fontFamily: "system-ui, sans-serif" }}>
          View your evaluation history and results
        </p>
      </div>

      {/* Stats cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 24,
          marginTop: 40,
          opacity: statsOpacity,
        }}
      >
        {[
          { label: "Total Evaluations", value: "24", icon: "check", color: "#09090b" },
          { label: "Completed", value: "21", icon: "check-circle", color: "#10b981" },
          { label: "Running", value: "2", icon: "loader", color: "#3b82f6" },
          { label: "Failed", value: "1", icon: "x", color: "#ef4444" },
        ].map((stat, i) => (
          <div
            key={stat.label}
            style={{
              background: "#ffffff",
              border: "1px solid #e4e4e7",
              borderRadius: 12,
              padding: 24,
              opacity: interpolate(frame, [statsDelay + i * 10, statsDelay + i * 10 + 20], [0, 1], {
                extrapolateRight: "clamp",
              }),
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <p style={{ color: "#71717a", fontSize: 14, margin: 0, fontFamily: "system-ui, sans-serif" }}>
                  {stat.label}
                </p>
                <p
                  style={{
                    color: stat.color,
                    fontSize: 36,
                    fontWeight: 800,
                    margin: "8px 0 0",
                    fontFamily: "system-ui, sans-serif",
                  }}
                >
                  {stat.value}
                </p>
              </div>
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: 12,
                  background: `${stat.color}15`,
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
                  stroke={stat.color}
                  strokeWidth="2"
                >
                  {stat.icon === "check" && <polyline points="20 6 9 17 4 12" />}
                  {stat.icon === "check-circle" && (
                    <>
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </>
                  )}
                  {stat.icon === "loader" && (
                    <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
                  )}
                  {stat.icon === "x" && (
                    <>
                      <circle cx="12" cy="12" r="10" />
                      <line x1="15" y1="9" x2="9" y2="15" />
                      <line x1="9" y1="9" x2="15" y2="15" />
                    </>
                  )}
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Results table */}
      <div
        style={{
          marginTop: 40,
          background: "#ffffff",
          border: "1px solid #e4e4e7",
          borderRadius: 16,
          overflow: "hidden",
          opacity: interpolate(frame, [80, 100], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        <div
          style={{
            padding: "20px 24px",
            borderBottom: "1px solid #e4e4e7",
          }}
        >
          <h3 style={{ color: "#09090b", fontSize: 18, fontWeight: 700, margin: 0, fontFamily: "system-ui, sans-serif" }}>
            Evaluation History
          </h3>
        </div>

        {/* Table header */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "60px 1.5fr 1fr 1fr 120px 200px",
            padding: "16px 24px",
            background: "#fafafa",
            borderBottom: "1px solid #e4e4e7",
          }}
        >
          {["ID", "Dataset", "Model", "Provider", "Status", "Scores"].map((header) => (
            <span
              key={header}
              style={{
                color: "#71717a",
                fontSize: 12,
                fontWeight: 700,
                fontFamily: "system-ui, sans-serif",
              }}
            >
              {header}
            </span>
          ))}
        </div>

        {/* Table rows */}
        {MOCK_RESULTS.map((result, index) => {
          const rowDelay = 100 + index * 20;
          const rowOpacity = interpolate(frame, [rowDelay, rowDelay + 20], [0, 1], {
            extrapolateRight: "clamp",
          });

          return (
            <div
              key={result.id}
              style={{
                display: "grid",
                gridTemplateColumns: "60px 1.5fr 1fr 1fr 120px 200px",
                padding: "20px 24px",
                borderBottom: "1px solid #f4f4f5",
                opacity: rowOpacity,
                alignItems: "center",
              }}
            >
              <span style={{ color: "#71717a", fontSize: 14, fontFamily: "monospace" }}>
                #{result.id}
              </span>
              <span style={{ color: "#09090b", fontSize: 14, fontWeight: 600, fontFamily: "system-ui, sans-serif" }}>
                {result.dataset}
              </span>
              <span style={{ color: "#09090b", fontSize: 14, fontFamily: "system-ui, sans-serif" }}>
                {result.model}
              </span>
              <span style={{ color: "#71717a", fontSize: 14, fontFamily: "system-ui, sans-serif" }}>
                {result.provider}
              </span>
              <div>
                {result.status === "completed" ? (
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      padding: "4px 12px",
                      background: "rgba(16, 185, 129, 0.1)",
                      color: "#10b981",
                      borderRadius: 20,
                      fontSize: 12,
                      fontWeight: 600,
                      fontFamily: "system-ui, sans-serif",
                    }}
                  >
                    <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                    Completed
                  </span>
                ) : (
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 6,
                      padding: "4px 12px",
                      background: "rgba(59, 130, 246, 0.1)",
                      color: "#3b82f6",
                      borderRadius: 20,
                      fontSize: 12,
                      fontWeight: 600,
                      fontFamily: "system-ui, sans-serif",
                    }}
                  >
                    <svg
                      viewBox="0 0 24 24"
                      width="12"
                      height="12"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      style={{
                        animation: "spin 1s linear infinite",
                        transformOrigin: "center",
                      }}
                    >
                      <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
                    </svg>
                    Running
                  </span>
                )}
              </div>
              <div>
                {result.scores ? (
                  <div style={{ display: "flex", gap: 8 }}>
                    {Object.entries(result.scores).map(([name, score]) => (
                      <span
                        key={name}
                        style={{
                          padding: "4px 8px",
                          background: "#f4f4f5",
                          borderRadius: 4,
                          fontSize: 11,
                          fontFamily: "monospace",
                          color: "#09090b",
                        }}
                      >
                        {name}: {score.mean.toFixed(1)}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div style={{ width: 120 }}>
                    <div
                      style={{
                        height: 8,
                        background: "#e4e4e7",
                        borderRadius: 4,
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          height: "100%",
                          width: `${runningProgress}%`,
                          background: "linear-gradient(90deg, #3b82f6, #60a5fa)",
                          borderRadius: 4,
                        }}
                      />
                    </div>
                    <span style={{ color: "#71717a", fontSize: 10, fontFamily: "system-ui, sans-serif" }}>
                      {Math.round(runningProgress)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Auto-refresh notice */}
      <div
        style={{
          marginTop: 24,
          padding: 16,
          background: "rgba(59, 130, 246, 0.1)",
          border: "1px solid rgba(59, 130, 246, 0.2)",
          borderRadius: 8,
          display: "flex",
          alignItems: "center",
          gap: 12,
          opacity: interpolate(frame, [200, 220], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        <span style={{ fontSize: 18 }}>🔄</span>
        <span style={{ color: "#1e40af", fontSize: 14, fontFamily: "system-ui, sans-serif" }}>
          <strong>Auto-refreshing:</strong> This page automatically refreshes every 5 seconds to show the latest evaluation status.
        </span>
      </div>
    </AbsoluteFill>
  );
};
