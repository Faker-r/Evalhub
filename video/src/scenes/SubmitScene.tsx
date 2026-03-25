import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  spring,
} from "remotion";

const STEPS = [
  { id: 1, title: "Select Source", icon: "database" },
  { id: 2, title: "Dataset Configuration", icon: "file" },
  { id: 3, title: "Model & Judge", icon: "server" },
  { id: 4, title: "Submit", icon: "play" },
];

export const SubmitScene: React.FC = () => {
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

  // Step progression
  const currentStep = Math.min(
    4,
    Math.floor(interpolate(frame, [60, 600], [1, 5], { extrapolateRight: "clamp" }))
  );

  // Card animations
  const cardScale = spring({
    frame: frame - 30,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(180deg, #fafafa 0%, #f4f4f5 100%)",
        opacity: fadeOut,
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

      {/* Layout */}
      <div style={{ display: "flex", height: "100%", paddingTop: 100 }}>
        {/* Sidebar */}
        <div
          style={{
            width: 280,
            padding: "40px 30px",
            background: "#ffffff",
            borderRight: "1px solid #e4e4e7",
            opacity: interpolate(frame, [20, 40], [0, 1], { extrapolateRight: "clamp" }),
          }}
        >
          <h3 style={{ color: "#09090b", fontSize: 18, fontWeight: 700, marginBottom: 32, fontFamily: "system-ui, sans-serif" }}>
            New Evaluation
          </h3>

          {STEPS.map((step, index) => {
            const isActive = step.id === currentStep;
            const isCompleted = step.id < currentStep;

            return (
              <div
                key={step.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  padding: "12px 16px",
                  marginBottom: 8,
                  borderRadius: 8,
                  background: isActive ? "rgba(16, 185, 129, 0.1)" : "transparent",
                }}
              >
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: "50%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 12,
                    fontWeight: 700,
                    fontFamily: "system-ui, sans-serif",
                    background: isActive ? "#10b981" : isCompleted ? "#09090b" : "#ffffff",
                    color: isActive || isCompleted ? "#ffffff" : "#a1a1aa",
                    border: isActive || isCompleted ? "none" : "2px solid #e4e4e7",
                  }}
                >
                  {isCompleted ? (
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="white" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : (
                    step.id
                  )}
                </div>
                <span
                  style={{
                    color: isActive ? "#10b981" : isCompleted ? "#09090b" : "#a1a1aa",
                    fontSize: 14,
                    fontWeight: isActive ? 600 : 500,
                    fontFamily: "system-ui, sans-serif",
                  }}
                >
                  {step.title}
                </span>
              </div>
            );
          })}
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: 60 }}>
          <div
            style={{
              transform: `scale(${cardScale})`,
              background: "#ffffff",
              borderRadius: 16,
              border: "1px solid #e4e4e7",
              boxShadow: "0 4px 20px rgba(0, 0, 0, 0.05)",
              padding: 40,
              minHeight: 500,
            }}
          >
            {/* Step header */}
            <div style={{ marginBottom: 32 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  color: "#10b981",
                  marginBottom: 8,
                }}
              >
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                  <ellipse cx="12" cy="5" rx="9" ry="3" />
                  <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                  <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
                </svg>
                <span style={{ fontSize: 12, fontWeight: 700, letterSpacing: 1, fontFamily: "system-ui, sans-serif" }}>
                  STEP {currentStep}
                </span>
              </div>
              <h2 style={{ color: "#09090b", fontSize: 28, fontWeight: 700, margin: 0, fontFamily: "system-ui, sans-serif" }}>
                {STEPS[currentStep - 1]?.title || "Submit"}
              </h2>
            </div>

            {/* Step 1: Select Source */}
            {currentStep === 1 && (
              <div>
                <h3 style={{ color: "#09090b", fontSize: 18, fontWeight: 600, marginBottom: 20, fontFamily: "system-ui, sans-serif" }}>
                  Select a Dataset
                </h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  {["Custom QA Dataset", "Test Dataset"].map((name, i) => (
                    <div
                      key={name}
                      style={{
                        padding: 20,
                        border: i === 0 ? "2px solid #10b981" : "1px solid #e4e4e7",
                        borderRadius: 12,
                        background: i === 0 ? "rgba(16, 185, 129, 0.05)" : "#fff",
                        opacity: interpolate(frame, [80 + i * 20, 100 + i * 20], [0, 1], { extrapolateRight: "clamp" }),
                      }}
                    >
                      <div style={{ color: "#09090b", fontSize: 16, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
                        {name}
                      </div>
                      <div style={{ color: "#71717a", fontSize: 14, marginTop: 4, fontFamily: "system-ui, sans-serif" }}>
                        General • {i === 0 ? "250" : "100"} samples
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ margin: "30px 0", borderTop: "1px solid #e4e4e7", position: "relative" }}>
                  <span
                    style={{
                      position: "absolute",
                      top: -10,
                      left: "50%",
                      transform: "translateX(-50%)",
                      background: "#fff",
                      padding: "0 16px",
                      color: "#71717a",
                      fontSize: 12,
                      fontFamily: "system-ui, sans-serif",
                    }}
                  >
                    Or
                  </span>
                </div>

                <h3 style={{ color: "#09090b", fontSize: 18, fontWeight: 600, marginBottom: 20, fontFamily: "system-ui, sans-serif" }}>
                  Select a Benchmark
                </h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  {["MMLU-Pro", "HumanEval+"].map((name, i) => (
                    <div
                      key={name}
                      style={{
                        padding: 20,
                        border: "1px solid #e4e4e7",
                        borderRadius: 12,
                        opacity: interpolate(frame, [120 + i * 20, 140 + i * 20], [0, 1], { extrapolateRight: "clamp" }),
                      }}
                    >
                      <div style={{ color: "#09090b", fontSize: 16, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
                        {name}
                      </div>
                      <div style={{ color: "#71717a", fontSize: 14, marginTop: 4, fontFamily: "system-ui, sans-serif" }}>
                        {i === 0 ? "57 tasks available" : "12 tasks available"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Step 2: Configuration */}
            {currentStep === 2 && (
              <div>
                <div style={{ marginBottom: 24 }}>
                  <label style={{ color: "#09090b", fontSize: 14, fontWeight: 600, display: "block", marginBottom: 8, fontFamily: "system-ui, sans-serif" }}>
                    Input Field
                  </label>
                  <div
                    style={{
                      padding: "12px 16px",
                      border: "1px solid #e4e4e7",
                      borderRadius: 8,
                      color: "#09090b",
                      fontSize: 14,
                      fontFamily: "system-ui, sans-serif",
                    }}
                  >
                    question
                  </div>
                </div>

                <div style={{ marginBottom: 24 }}>
                  <label style={{ color: "#09090b", fontSize: 14, fontWeight: 600, display: "block", marginBottom: 8, fontFamily: "system-ui, sans-serif" }}>
                    Output Type
                  </label>
                  <div style={{ display: "flex", gap: 16 }}>
                    {["Text", "Multiple Choice"].map((type, i) => (
                      <div
                        key={type}
                        style={{
                          flex: 1,
                          padding: 16,
                          border: i === 0 ? "2px solid #10b981" : "1px solid #e4e4e7",
                          borderRadius: 8,
                          background: i === 0 ? "rgba(16, 185, 129, 0.05)" : "#fff",
                        }}
                      >
                        <div style={{ color: "#09090b", fontSize: 14, fontWeight: 600, fontFamily: "system-ui, sans-serif" }}>
                          {type}
                        </div>
                        <div style={{ color: "#71717a", fontSize: 12, marginTop: 4, fontFamily: "system-ui, sans-serif" }}>
                          {i === 0 ? "Free-form text response" : "Select from options"}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label style={{ color: "#09090b", fontSize: 14, fontWeight: 600, display: "block", marginBottom: 8, fontFamily: "system-ui, sans-serif" }}>
                    Judge Type
                  </label>
                  <div style={{ display: "flex", gap: 12 }}>
                    {["LLM as Judge", "Exact Match", "F1 Score"].map((type, i) => (
                      <div
                        key={type}
                        style={{
                          flex: 1,
                          padding: 16,
                          border: i === 0 ? "2px solid #10b981" : "1px solid #e4e4e7",
                          borderRadius: 8,
                          background: i === 0 ? "rgba(16, 185, 129, 0.05)" : "#fff",
                        }}
                      >
                        <div style={{ color: "#09090b", fontSize: 14, fontWeight: 600, fontFamily: "system-ui, sans-serif" }}>
                          {type}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Model Selection */}
            {currentStep === 3 && (
              <div>
                <div style={{ marginBottom: 32 }}>
                  <div style={{ color: "#71717a", fontSize: 12, fontWeight: 600, letterSpacing: 1, marginBottom: 16, fontFamily: "system-ui, sans-serif" }}>
                    STEP 3.1
                  </div>
                  <h3 style={{ color: "#09090b", fontSize: 18, fontWeight: 600, marginBottom: 20, fontFamily: "system-ui, sans-serif" }}>
                    Completion Model
                  </h3>
                  <div
                    style={{
                      padding: 20,
                      border: "2px solid #10b981",
                      borderRadius: 12,
                      background: "rgba(16, 185, 129, 0.05)",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <div style={{ color: "#09090b", fontSize: 16, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
                        GPT-4o
                      </div>
                      <div style={{ color: "#71717a", fontSize: 14, marginTop: 4, fontFamily: "system-ui, sans-serif" }}>
                        OpenAI via OpenRouter
                      </div>
                    </div>
                    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#10b981" strokeWidth="2">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </div>
                </div>

                <div>
                  <div style={{ color: "#71717a", fontSize: 12, fontWeight: 600, letterSpacing: 1, marginBottom: 16, fontFamily: "system-ui, sans-serif" }}>
                    STEP 3.2
                  </div>
                  <h3 style={{ color: "#09090b", fontSize: 18, fontWeight: 600, marginBottom: 20, fontFamily: "system-ui, sans-serif" }}>
                    Judge Model
                  </h3>
                  <div
                    style={{
                      padding: 20,
                      border: "2px solid #10b981",
                      borderRadius: 12,
                      background: "rgba(16, 185, 129, 0.05)",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <div>
                      <div style={{ color: "#09090b", fontSize: 16, fontWeight: 700, fontFamily: "system-ui, sans-serif" }}>
                        Claude 3.5 Sonnet
                      </div>
                      <div style={{ color: "#71717a", fontSize: 14, marginTop: 4, fontFamily: "system-ui, sans-serif" }}>
                        Anthropic via OpenRouter
                      </div>
                    </div>
                    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#10b981" strokeWidth="2">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Submit */}
            {currentStep === 4 && (
              <div>
                <h3 style={{ color: "#09090b", fontSize: 18, fontWeight: 600, marginBottom: 20, fontFamily: "system-ui, sans-serif" }}>
                  Review Your Evaluation
                </h3>
                <div
                  style={{
                    background: "#fafafa",
                    borderRadius: 12,
                    padding: 24,
                  }}
                >
                  {[
                    { label: "Dataset", value: "Custom QA Dataset" },
                    { label: "Input Field", value: "question" },
                    { label: "Output Type", value: "Text" },
                    { label: "Judge Type", value: "LLM as Judge" },
                    { label: "Completion Model", value: "GPT-4o" },
                    { label: "Judge Model", value: "Claude 3.5 Sonnet" },
                  ].map((item) => (
                    <div
                      key={item.label}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        padding: "10px 0",
                        borderBottom: "1px solid #e4e4e7",
                      }}
                    >
                      <span style={{ color: "#71717a", fontSize: 14, fontFamily: "system-ui, sans-serif" }}>
                        {item.label}:
                      </span>
                      <span style={{ color: "#09090b", fontSize: 14, fontWeight: 600, fontFamily: "system-ui, sans-serif" }}>
                        {item.value}
                      </span>
                    </div>
                  ))}
                </div>

                <button
                  style={{
                    marginTop: 24,
                    width: "100%",
                    padding: "16px 32px",
                    background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                    border: "none",
                    borderRadius: 8,
                    color: "#fff",
                    fontSize: 16,
                    fontWeight: 700,
                    fontFamily: "system-ui, sans-serif",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 8,
                    cursor: "pointer",
                    boxShadow: "0 4px 20px rgba(16, 185, 129, 0.3)",
                  }}
                >
                  Start Evaluation
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
