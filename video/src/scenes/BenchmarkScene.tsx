import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Mock benchmark data
const BENCHMARKS = [
  {
    name: "MMLU-Pro",
    description: "Massive Multitask Language Understanding",
    tags: ["knowledge", "reasoning", "multiple-choice"],
    downloads: 128000,
    tasks: 57,
    samples: 12000,
  },
  {
    name: "HumanEval+",
    description: "Enhanced code generation benchmark",
    tags: ["coding", "generation"],
    downloads: 95000,
    tasks: 12,
    samples: 164,
  },
  {
    name: "GSM8K-Hard",
    description: "Grade School Math with increased difficulty",
    tags: ["math", "reasoning"],
    downloads: 87000,
    tasks: 8,
    samples: 8500,
  },
  {
    name: "IFEval",
    description: "Instruction Following Evaluation",
    tags: ["instruction-following", "general"],
    downloads: 72000,
    tasks: 15,
    samples: 5000,
  },
];

const LANGUAGE_FILTERS = [
  { code: "en", label: "English", color: "#3b82f6" },
  { code: "zh", label: "Chinese", color: "#ef4444" },
  { code: "fr", label: "French", color: "#8b5cf6" },
  { code: "de", label: "German", color: "#6366f1" },
];

export const BenchmarkScene: React.FC = () => {
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

  // Cursor animation for search
  const cursorBlink = Math.floor(frame / 15) % 2 === 0;
  const searchProgress = interpolate(frame, [40, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const searchText = "mmlu".slice(0, Math.floor(searchProgress * 4));

  // Filter click animation
  const filterHighlight = interpolate(frame, [120, 150], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(180deg, #09090b 0%, #18181b 100%)",
        opacity: fadeOut,
      }}
    >
      {/* Header */}
      <div
        style={{
          position: "absolute",
          top: 40,
          left: 80,
          right: 80,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          opacity: titleOpacity,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
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
            <span style={{ color: "#fff" }}>Hub</span>
          </span>
        </div>

        {/* Navigation */}
        <div style={{ display: "flex", gap: 32 }}>
          {["Leaderboard", "Benchmarks", "Models", "Providers"].map((item, i) => (
            <span
              key={item}
              style={{
                color: i === 1 ? "#10b981" : "#a1a1aa",
                fontSize: 16,
                fontWeight: i === 1 ? 700 : 500,
                fontFamily: "system-ui, sans-serif",
                borderBottom: i === 1 ? "2px solid #10b981" : "none",
                paddingBottom: 4,
              }}
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Main content */}
      <div style={{ padding: "120px 80px 80px", display: "flex", gap: 40 }}>
        {/* Sidebar filters */}
        <div
          style={{
            width: 280,
            opacity: interpolate(frame, [20, 40], [0, 1], { extrapolateRight: "clamp" }),
          }}
        >
          <div style={{ marginBottom: 30 }}>
            <h3 style={{ color: "#fff", fontSize: 14, fontWeight: 700, marginBottom: 16, fontFamily: "system-ui, sans-serif" }}>
              Search
            </h3>
            <div
              style={{
                background: "rgba(255, 255, 255, 0.05)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                borderRadius: 8,
                padding: "12px 16px",
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}
            >
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#71717a" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <span style={{ color: "#fff", fontSize: 14, fontFamily: "system-ui, sans-serif" }}>
                {searchText}
                {cursorBlink && <span style={{ color: "#10b981" }}>|</span>}
              </span>
            </div>
          </div>

          <div style={{ marginBottom: 30 }}>
            <h3 style={{ color: "#fff", fontSize: 14, fontWeight: 700, marginBottom: 16, fontFamily: "system-ui, sans-serif" }}>
              Languages
            </h3>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {LANGUAGE_FILTERS.map((lang, i) => (
                <div
                  key={lang.code}
                  style={{
                    padding: "6px 12px",
                    borderRadius: 6,
                    fontSize: 12,
                    fontFamily: "system-ui, sans-serif",
                    fontWeight: 500,
                    background: i === 0 && filterHighlight > 0.5 ? lang.color : "rgba(255, 255, 255, 0.05)",
                    color: i === 0 && filterHighlight > 0.5 ? "#fff" : "#a1a1aa",
                    border: `1px solid ${i === 0 && filterHighlight > 0.5 ? lang.color : "rgba(255, 255, 255, 0.1)"}`,
                    transform: i === 0 && filterHighlight > 0 ? `scale(${1 + filterHighlight * 0.05})` : "scale(1)",
                  }}
                >
                  {lang.label}
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 style={{ color: "#fff", fontSize: 14, fontWeight: 700, marginBottom: 16, fontFamily: "system-ui, sans-serif" }}>
              Benchmark type
            </h3>
            {["reasoning", "coding", "math", "knowledge", "instruction-following"].map((tag, i) => (
              <div
                key={tag}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  marginBottom: 12,
                }}
              >
                <div
                  style={{
                    width: 18,
                    height: 18,
                    borderRadius: 4,
                    border: "2px solid rgba(255, 255, 255, 0.3)",
                    background: i < 2 ? "#10b981" : "transparent",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {i < 2 && (
                    <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="white" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </div>
                <span style={{ color: "#a1a1aa", fontSize: 14, fontFamily: "system-ui, sans-serif" }}>
                  {tag}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Benchmark cards */}
        <div style={{ flex: 1 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 24,
              opacity: titleOpacity,
            }}
          >
            <div>
              <h2 style={{ color: "#fff", fontSize: 40, fontWeight: 800, margin: 0, fontFamily: "system-ui, sans-serif" }}>
                <span style={{ color: "#10b981" }}>Lighteval</span> Tasks Explorer
              </h2>
              <p style={{ color: "#71717a", fontSize: 16, margin: "8px 0 0", fontFamily: "system-ui, sans-serif" }}>
                Browse tasks by language, tags and search
              </p>
            </div>
            <span style={{ color: "#71717a", fontSize: 14, fontFamily: "system-ui, sans-serif" }}>
              {BENCHMARKS.length * 25} tasks
            </span>
          </div>

          {/* Cards grid */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
            {BENCHMARKS.map((benchmark, index) => {
              const cardDelay = 60 + index * 20;
              const cardOpacity = interpolate(frame, [cardDelay, cardDelay + 30], [0, 1], {
                extrapolateRight: "clamp",
              });
              const cardY = interpolate(frame, [cardDelay, cardDelay + 30], [20, 0], {
                extrapolateRight: "clamp",
              });

              return (
                <div
                  key={benchmark.name}
                  style={{
                    opacity: cardOpacity,
                    transform: `translateY(${cardY}px)`,
                    background: "rgba(255, 255, 255, 0.02)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    borderRadius: 16,
                    padding: 24,
                    transition: "all 0.2s",
                  }}
                >
                  <h3 style={{ color: "#fff", fontSize: 20, fontWeight: 700, margin: 0, fontFamily: "system-ui, sans-serif" }}>
                    {benchmark.name}
                  </h3>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6, margin: "12px 0" }}>
                    {benchmark.tags.map((tag) => (
                      <span
                        key={tag}
                        style={{
                          padding: "4px 10px",
                          background: "rgba(234, 179, 8, 0.15)",
                          color: "#eab308",
                          borderRadius: 4,
                          fontSize: 11,
                          fontFamily: "system-ui, sans-serif",
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <p style={{ color: "#71717a", fontSize: 14, margin: "12px 0", fontFamily: "system-ui, sans-serif", lineHeight: 1.5 }}>
                    {benchmark.description}
                  </p>
                  <div style={{ display: "flex", gap: 16, marginTop: 16 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#71717a" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="7 10 12 15 17 10" />
                        <line x1="12" y1="15" x2="12" y2="3" />
                      </svg>
                      <span style={{ color: "#71717a", fontSize: 12, fontFamily: "system-ui, sans-serif" }}>
                        {(benchmark.downloads / 1000).toFixed(0)}K
                      </span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#71717a" strokeWidth="2">
                        <ellipse cx="12" cy="5" rx="9" ry="3" />
                        <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                        <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
                      </svg>
                      <span style={{ color: "#71717a", fontSize: 12, fontFamily: "system-ui, sans-serif" }}>
                        {benchmark.samples.toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid rgba(255, 255, 255, 0.1)" }}>
                    <span style={{ color: "#71717a", fontSize: 10, fontWeight: 600, letterSpacing: 1, fontFamily: "system-ui, sans-serif" }}>
                      RUN USING LIGHTEVAL:
                    </span>
                    <div style={{ display: "flex", gap: 8, marginTop: 8, flexWrap: "wrap" }}>
                      {[`${benchmark.name.toLowerCase()}|0|0`, `${benchmark.name.toLowerCase()}|5|0`].map((task) => (
                        <code
                          key={task}
                          style={{
                            padding: "4px 8px",
                            background: "rgba(16, 185, 129, 0.1)",
                            border: "1px solid rgba(16, 185, 129, 0.2)",
                            borderRadius: 4,
                            color: "#10b981",
                            fontSize: 11,
                            fontFamily: "monospace",
                          }}
                        >
                          {task}
                        </code>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
