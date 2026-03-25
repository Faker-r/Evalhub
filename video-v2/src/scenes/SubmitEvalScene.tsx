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

const STEPS = [
  { num: 1, title: "Select Source", icon: "📊", desc: "Choose dataset or benchmark" },
  { num: 2, title: "Configure", icon: "⚙️", desc: "Set up evaluation options" },
  { num: 3, title: "Pick Models", icon: "🤖", desc: "Choose AI to evaluate" },
  { num: 4, title: "Submit", icon: "🚀", desc: "Start evaluation" },
];

export const SubmitEvalScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Section title animation
  const titleOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Browser mockup entrance
  const browserScale = spring({
    frame: frame - 20,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  // Current step (animated through the wizard)
  const currentStepRaw = interpolate(frame, [60, 180, 300, 420], [1, 2, 3, 4], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const currentStep = Math.floor(currentStepRaw);

  // Card content based on step
  const stepContentOpacity = (step: number) => {
    const stepStart = 60 + (step - 1) * 120;
    return interpolate(frame, [stepStart, stepStart + 30], [0, 1], {
      extrapolateRight: "clamp",
    });
  };

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 30, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Floating decorative elements
  const float = (offset: number) => Math.sin((frame + offset) * 0.05) * 6;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${COLORS.light} 0%, #FEF3C7 50%, ${COLORS.mintLight} 100%)`,
        padding: 60,
        opacity: fadeOut,
      }}
    >
      {/* Decorative elements */}
      <div
        style={{
          position: "absolute",
          top: 80,
          right: 100,
          width: 100,
          height: 100,
          borderRadius: "50%",
          background: `${COLORS.purple}15`,
          transform: `translateY(${float(0)}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 100,
          left: 80,
          width: 80,
          height: 80,
          borderRadius: "30%",
          background: `${COLORS.yellow}20`,
          transform: `translateY(${float(50)}px) rotate(${frame * 0.2}deg)`,
        }}
      />

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
            background: `linear-gradient(135deg, ${COLORS.yellow} 0%, ${COLORS.coral} 100%)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span style={{ fontSize: 24 }}>📝</span>
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
            Run Your Own Evaluation
          </h2>
          <p
            style={{
              fontSize: 18,
              color: COLORS.gray,
              fontFamily: "system-ui, sans-serif",
              margin: 0,
            }}
          >
            4 simple steps to test any AI
          </p>
        </div>
      </div>

      {/* Content Area */}
      <div style={{ display: "flex", gap: 40 }}>
        {/* Left: Steps Sidebar */}
        <div
          style={{
            width: 280,
            transform: `scale(${browserScale})`,
          }}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: 20,
              padding: 24,
              boxShadow: "0 8px 32px rgba(0,0,0,0.08)",
            }}
          >
            <h3
              style={{
                fontSize: 14,
                fontWeight: 700,
                color: COLORS.gray,
                fontFamily: "system-ui, sans-serif",
                margin: "0 0 20px 0",
                letterSpacing: 1,
              }}
            >
              WIZARD STEPS
            </h3>

            {STEPS.map((step, i) => {
              const isActive = step.num === currentStep;
              const isCompleted = step.num < currentStep;

              const stepBounce = spring({
                frame: frame - 40 - i * 15,
                fps,
                config: { damping: 12, stiffness: 200 },
              });

              return (
                <div
                  key={step.num}
                  style={{
                    transform: `scale(${stepBounce})`,
                    display: "flex",
                    alignItems: "center",
                    gap: 16,
                    padding: "14px 16px",
                    marginBottom: 8,
                    borderRadius: 12,
                    background: isActive ? `${COLORS.mint}15` : "transparent",
                    border: isActive ? `2px solid ${COLORS.mint}` : "2px solid transparent",
                    transition: "all 0.3s",
                  }}
                >
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: "50%",
                      background: isCompleted
                        ? COLORS.mint
                        : isActive
                        ? COLORS.mint
                        : "#E5E7EB",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: isCompleted ? 16 : 14,
                      fontWeight: 700,
                      color: isCompleted || isActive ? "#fff" : COLORS.gray,
                      fontFamily: "system-ui, sans-serif",
                      transition: "all 0.3s",
                    }}
                  >
                    {isCompleted ? "✓" : step.num}
                  </div>
                  <div>
                    <div
                      style={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: isActive ? COLORS.dark : COLORS.gray,
                        fontFamily: "system-ui, sans-serif",
                      }}
                    >
                      {step.title}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Main Card */}
        <div
          style={{
            flex: 1,
            transform: `scale(${browserScale})`,
          }}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: 20,
              padding: 40,
              boxShadow: "0 15px 50px rgba(0,0,0,0.1)",
              minHeight: 450,
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Step 1: Select Source */}
            {currentStep === 1 && (
              <div style={{ opacity: stepContentOpacity(1) }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
                  <span style={{ fontSize: 32 }}>📊</span>
                  <h3
                    style={{
                      fontSize: 28,
                      fontWeight: 700,
                      color: COLORS.dark,
                      fontFamily: "system-ui, sans-serif",
                      margin: 0,
                    }}
                  >
                    Select a Dataset
                  </h3>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  {[
                    { name: "My Custom QA", samples: 250, selected: true },
                    { name: "Product Reviews", samples: 1200, selected: false },
                  ].map((ds, i) => {
                    const cardBounce = spring({
                      frame: frame - 80 - i * 20,
                      fps,
                      config: { damping: 12, stiffness: 200 },
                    });
                    return (
                      <div
                        key={ds.name}
                        style={{
                          transform: `scale(${cardBounce})`,
                          padding: 24,
                          borderRadius: 16,
                          border: ds.selected ? `3px solid ${COLORS.mint}` : "2px solid #E5E7EB",
                          background: ds.selected ? `${COLORS.mint}08` : "#fff",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                          <div>
                            <div
                              style={{
                                fontSize: 18,
                                fontWeight: 700,
                                color: COLORS.dark,
                                fontFamily: "system-ui, sans-serif",
                              }}
                            >
                              {ds.name}
                            </div>
                            <div
                              style={{
                                fontSize: 14,
                                color: COLORS.gray,
                                fontFamily: "system-ui, sans-serif",
                                marginTop: 4,
                              }}
                            >
                              {ds.samples} samples
                            </div>
                          </div>
                          {ds.selected && (
                            <div
                              style={{
                                width: 28,
                                height: 28,
                                borderRadius: "50%",
                                background: COLORS.mint,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                              }}
                            >
                              <span style={{ color: "#fff", fontSize: 14 }}>✓</span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Step 2: Configure */}
            {currentStep === 2 && (
              <div style={{ opacity: stepContentOpacity(2) }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
                  <span style={{ fontSize: 32 }}>⚙️</span>
                  <h3
                    style={{
                      fontSize: 28,
                      fontWeight: 700,
                      color: COLORS.dark,
                      fontFamily: "system-ui, sans-serif",
                      margin: 0,
                    }}
                  >
                    Configure Options
                  </h3>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                  <div>
                    <label
                      style={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: COLORS.dark,
                        fontFamily: "system-ui, sans-serif",
                        display: "block",
                        marginBottom: 8,
                      }}
                    >
                      Input Field
                    </label>
                    <div
                      style={{
                        padding: "14px 18px",
                        borderRadius: 10,
                        border: "2px solid #E5E7EB",
                        fontSize: 16,
                        color: COLORS.dark,
                        fontFamily: "monospace",
                        background: "#F9FAFB",
                      }}
                    >
                      question
                    </div>
                  </div>

                  <div>
                    <label
                      style={{
                        fontSize: 14,
                        fontWeight: 600,
                        color: COLORS.dark,
                        fontFamily: "system-ui, sans-serif",
                        display: "block",
                        marginBottom: 8,
                      }}
                    >
                      Judge Type
                    </label>
                    <div style={{ display: "flex", gap: 12 }}>
                      {["LLM as Judge", "Exact Match", "F1 Score"].map((type, i) => (
                        <div
                          key={type}
                          style={{
                            padding: "12px 20px",
                            borderRadius: 10,
                            border: i === 0 ? `2px solid ${COLORS.mint}` : "2px solid #E5E7EB",
                            background: i === 0 ? `${COLORS.mint}10` : "#fff",
                            fontSize: 14,
                            fontWeight: 600,
                            color: i === 0 ? COLORS.mint : COLORS.gray,
                            fontFamily: "system-ui, sans-serif",
                          }}
                        >
                          {type}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Pick Models */}
            {currentStep === 3 && (
              <div style={{ opacity: stepContentOpacity(3) }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
                  <span style={{ fontSize: 32 }}>🤖</span>
                  <h3
                    style={{
                      fontSize: 28,
                      fontWeight: 700,
                      color: COLORS.dark,
                      fontFamily: "system-ui, sans-serif",
                      margin: 0,
                    }}
                  >
                    Select Models
                  </h3>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  {[
                    { label: "Completion Model", model: "GPT-4o", provider: "OpenAI" },
                    { label: "Judge Model", model: "Claude 3.5 Sonnet", provider: "Anthropic" },
                  ].map((item, i) => {
                    const cardBounce = spring({
                      frame: frame - 320 - i * 30,
                      fps,
                      config: { damping: 12, stiffness: 200 },
                    });
                    return (
                      <div
                        key={item.label}
                        style={{
                          transform: `scale(${cardBounce})`,
                          padding: 24,
                          borderRadius: 16,
                          border: `2px solid ${COLORS.mint}`,
                          background: `${COLORS.mint}08`,
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <div>
                          <div
                            style={{
                              fontSize: 12,
                              fontWeight: 600,
                              color: COLORS.gray,
                              fontFamily: "system-ui, sans-serif",
                              marginBottom: 4,
                              letterSpacing: 0.5,
                            }}
                          >
                            {item.label.toUpperCase()}
                          </div>
                          <div
                            style={{
                              fontSize: 20,
                              fontWeight: 700,
                              color: COLORS.dark,
                              fontFamily: "system-ui, sans-serif",
                            }}
                          >
                            {item.model}
                          </div>
                          <div
                            style={{
                              fontSize: 14,
                              color: COLORS.gray,
                              fontFamily: "system-ui, sans-serif",
                            }}
                          >
                            via {item.provider}
                          </div>
                        </div>
                        <div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: "50%",
                            background: COLORS.mint,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <span style={{ color: "#fff", fontSize: 18 }}>✓</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Step 4: Submit */}
            {currentStep === 4 && (
              <div style={{ opacity: stepContentOpacity(4) }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
                  <span style={{ fontSize: 32 }}>🚀</span>
                  <h3
                    style={{
                      fontSize: 28,
                      fontWeight: 700,
                      color: COLORS.dark,
                      fontFamily: "system-ui, sans-serif",
                      margin: 0,
                    }}
                  >
                    Ready to Launch!
                  </h3>
                </div>

                {/* Summary */}
                <div
                  style={{
                    background: "#F9FAFB",
                    borderRadius: 16,
                    padding: 24,
                    marginBottom: 24,
                  }}
                >
                  {[
                    { label: "Dataset", value: "My Custom QA" },
                    { label: "Samples", value: "250" },
                    { label: "Model", value: "GPT-4o" },
                    { label: "Judge", value: "Claude 3.5 Sonnet" },
                  ].map((item, i) => (
                    <div
                      key={item.label}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        padding: "10px 0",
                        borderBottom: i < 3 ? "1px solid #E5E7EB" : "none",
                      }}
                    >
                      <span
                        style={{
                          fontSize: 14,
                          color: COLORS.gray,
                          fontFamily: "system-ui, sans-serif",
                        }}
                      >
                        {item.label}
                      </span>
                      <span
                        style={{
                          fontSize: 14,
                          fontWeight: 600,
                          color: COLORS.dark,
                          fontFamily: "system-ui, sans-serif",
                        }}
                      >
                        {item.value}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Submit button with pulse */}
                <div
                  style={{
                    position: "relative",
                    display: "inline-block",
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      inset: -8,
                      borderRadius: 20,
                      background: COLORS.mint,
                      opacity: 0.3,
                      animation: "pulse 1.5s infinite",
                      transform: `scale(${1 + Math.sin(frame * 0.1) * 0.05})`,
                    }}
                  />
                  <button
                    style={{
                      position: "relative",
                      padding: "18px 48px",
                      background: `linear-gradient(135deg, ${COLORS.mint} 0%, #059669 100%)`,
                      border: "none",
                      borderRadius: 14,
                      fontSize: 18,
                      fontWeight: 700,
                      color: "#fff",
                      fontFamily: "system-ui, sans-serif",
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      cursor: "pointer",
                      boxShadow: `0 8px 24px ${COLORS.mint}50`,
                    }}
                  >
                    Start Evaluation
                    <span style={{ fontSize: 20 }}>→</span>
                  </button>
                </div>
              </div>
            )}

            {/* Progress indicator */}
            <div
              style={{
                position: "absolute",
                bottom: 24,
                left: 40,
                right: 40,
                height: 4,
                background: "#E5E7EB",
                borderRadius: 2,
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${(currentStep / 4) * 100}%`,
                  background: `linear-gradient(90deg, ${COLORS.mint} 0%, ${COLORS.blue} 100%)`,
                  borderRadius: 2,
                  transition: "width 0.5s ease",
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
