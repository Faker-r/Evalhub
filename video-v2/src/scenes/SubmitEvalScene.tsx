import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, FONT, popIn } from "../theme";

// Wizard steps
const STEPS = [
  { id: 1, title: "Select Dataset", icon: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
      <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
    </svg>
  ) },
  { id: 2, title: "Choose Metrics", icon: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
      <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  ) },
  { id: 3, title: "Select Models", icon: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
      <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/>
    </svg>
  ) },
  { id: 4, title: "Run Eval", icon: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
      <polygon points="5 3 19 12 5 21 5 3"/>
    </svg>
  ) },
];

export const SubmitEvalScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Section title animation
  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 15], [-20, 0], {
    extrapolateRight: "clamp",
  });

  // Determine active step based on frame
  // Total duration: 420 frames (14s)
  // Step 1: 30-100
  // Step 2: 100-180
  // Step 3: 180-260
  // Step 4: 260-380
  let activeStep = 1;
  if (frame >= 100) activeStep = 2;
  if (frame >= 180) activeStep = 3;
  if (frame >= 260) activeStep = 4;

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
      {/* Noise background */}
      <svg
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.05, pointerEvents: "none" }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <filter id="submit-noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#submit-noise)" />
      </svg>
      
      {/* Grid Lines */}
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
            boxShadow: `4px 4px 0px ${C.pink}`,
          }}
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={C.pink} strokeWidth="2.5" strokeLinecap="square">
            <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
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
            Run Your Own Eval
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
            In just a few clicks
          </p>
        </div>
      </div>

      {/* App Container */}
      <div
        style={{
          transform: `scale(${popIn(frame, fps, 0, { damping: 16, stiffness: 100 })})`,
          height: 700,
          background: C.white,
          border: `4px solid ${C.black}`,
          boxShadow: `16px 16px 0px ${C.green}`,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Progress Stepper */}
        <div
          style={{
            display: "flex",
            borderBottom: `4px solid ${C.black}`,
            background: C.grayLight,
          }}
        >
          {STEPS.map((step, i) => {
            const isActive = step.id === activeStep;
            const isCompleted = step.id < activeStep;
            
            return (
              <div
                key={step.id}
                style={{
                  flex: 1,
                  padding: "20px",
                  borderRight: i < STEPS.length - 1 ? `4px solid ${C.black}` : "none",
                  background: isActive ? C.white : isCompleted ? C.green : C.grayLight,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 12,
                  transition: "background 0.2s",
                }}
              >
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: "50%",
                    background: isActive ? C.black : isCompleted ? C.black : C.white,
                    border: `2px solid ${C.black}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: isActive ? C.white : isCompleted ? C.white : C.black,
                  }}
                >
                  {isCompleted ? (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  ) : (
                    <span style={{ fontSize: 14, fontWeight: 800, fontFamily: FONT.mono }}>{step.id}</span>
                  )}
                </div>
                <span
                  style={{
                    fontSize: 16,
                    fontWeight: 800,
                    color: isActive || isCompleted ? C.black : C.grayMid,
                    fontFamily: FONT.body,
                    textTransform: "uppercase",
                  }}
                >
                  {step.title}
                </span>
              </div>
            );
          })}
        </div>

        {/* Content Area */}
        <div style={{ flex: 1, padding: 40, position: "relative" }}>
          
          {/* STEP 1: Select Dataset */}
          {activeStep === 1 && (
            <div
              style={{
                opacity: interpolate(frame, [30, 40], [0, 1]),
                transform: `translateX(${interpolate(frame, [30, 40], [20, 0])}px)`,
              }}
            >
              <h3 style={{ fontSize: 32, color: C.black, fontFamily: FONT.display, marginTop: 0 }}>Choose a Dataset</h3>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 32 }}>
                {["MMLU-Pro", "HumanEval", "GSM8K"].map((ds, i) => (
                  <div
                    key={ds}
                    style={{
                      padding: "24px",
                      border: `4px solid ${C.black}`,
                      background: i === 0 ? C.black : C.white,
                      boxShadow: i === 0 ? `8px 8px 0px ${C.pink}` : "none",
                      transform: i === 0 && frame >= 60 ? "scale(1.02)" : "scale(1)",
                      transition: "all 0.1s",
                    }}
                  >
                    <div style={{ fontSize: 24, fontWeight: 800, color: i === 0 ? C.white : C.black, fontFamily: FONT.body }}>{ds}</div>
                    <div style={{ fontSize: 16, color: i === 0 ? C.grayLight : C.grayMid, fontFamily: FONT.body, marginTop: 8 }}>
                      {i === 0 ? "Massive Multitask Language Understanding (Professional)" : "Standard evaluation dataset"}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* STEP 2: Choose Metrics */}
          {activeStep === 2 && (
            <div
              style={{
                opacity: interpolate(frame, [100, 110], [0, 1]),
                transform: `translateX(${interpolate(frame, [100, 110], [20, 0])}px)`,
              }}
            >
              <h3 style={{ fontSize: 32, color: C.black, fontFamily: FONT.display, marginTop: 0 }}>Select Evaluation Metrics</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 32 }}>
                {[
                  { name: "Accuracy", selected: true },
                  { name: "Helpfulness", selected: frame >= 130 },
                  { name: "Toxicity", selected: false },
                ].map((metric) => (
                  <div
                    key={metric.name}
                    style={{
                      padding: "20px 24px",
                      border: `4px solid ${C.black}`,
                      background: metric.selected ? C.green : C.white,
                      display: "flex",
                      alignItems: "center",
                      gap: 16,
                      transition: "background 0.1s",
                    }}
                  >
                    <div
                      style={{
                        width: 24,
                        height: 24,
                        border: `3px solid ${C.black}`,
                        background: metric.selected ? C.black : C.white,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      {metric.selected && (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={C.white} strokeWidth="4">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      )}
                    </div>
                    <span style={{ fontSize: 20, fontWeight: 800, color: C.black, fontFamily: FONT.mono, textTransform: "uppercase" }}>
                      {metric.name}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* STEP 3: Select Models */}
          {activeStep === 3 && (
            <div
              style={{
                opacity: interpolate(frame, [180, 190], [0, 1]),
                transform: `translateX(${interpolate(frame, [180, 190], [20, 0])}px)`,
              }}
            >
              <h3 style={{ fontSize: 32, color: C.black, fontFamily: FONT.display, marginTop: 0 }}>Select Models to Compare</h3>
              
              <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginTop: 32 }}>
                {[
                  { name: "GPT-4o", selected: true },
                  { name: "Claude 3.5 Sonnet", selected: true },
                  { name: "Gemini 1.5 Pro", selected: frame >= 210 },
                  { name: "Llama 3 70B", selected: frame >= 230 },
                ].map((model) => (
                  <div
                    key={model.name}
                    style={{
                      padding: "16px 24px",
                      border: `3px solid ${C.black}`,
                      background: model.selected ? C.black : C.white,
                      color: model.selected ? C.white : C.black,
                      fontSize: 18,
                      fontWeight: 800,
                      fontFamily: FONT.body,
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      boxShadow: model.selected ? `4px 4px 0px ${C.pink}` : "none",
                      transition: "all 0.1s",
                    }}
                  >
                    {model.name}
                    {model.selected && (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={C.green} strokeWidth="3">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* STEP 4: Run Eval */}
          {activeStep === 4 && (
            <div
              style={{
                opacity: interpolate(frame, [260, 270], [0, 1]),
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
              }}
            >
              <div
                style={{
                  width: 120,
                  height: 120,
                  background: C.black,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: `8px 8px 0px ${C.green}`,
                  marginBottom: 32,
                  transform: `scale(1) rotate(${frame * 2}deg)`,
                }}
              >
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke={C.green} strokeWidth="2.5" strokeLinecap="square">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
              </div>
              <h3 style={{ fontSize: 40, color: C.black, fontFamily: FONT.display, margin: 0, textAlign: "center" }}>
                Running Evaluation...
              </h3>
              
              <div style={{ width: 400, height: 24, background: C.grayLight, border: `3px solid ${C.black}`, marginTop: 32, position: "relative", overflow: "hidden" }}>
                <div
                  style={{
                    position: "absolute",
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: `${interpolate(frame, [280, 420], [0, 100], { extrapolateRight: "clamp" }) }%`,
                    background: C.green,
                    borderRight: `3px solid ${C.black}`,
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer (Next Button) */}
        {activeStep < 4 && (
          <div
            style={{
              padding: "24px 40px",
              borderTop: `4px solid ${C.black}`,
              background: C.grayLight,
              display: "flex",
              justifyContent: "flex-end",
            }}
          >
            <div
              style={{
                padding: "16px 48px",
                background: C.black,
                color: C.white,
                fontSize: 20,
                fontWeight: 800,
                fontFamily: FONT.display,
                letterSpacing: 2,
                boxShadow: `6px 6px 0px ${C.pink}`,
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              NEXT
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </div>
          </div>
        )}
      </div>

      {/* Animated cursor (black stroke, white fill) */}
      {activeStep < 4 && (
        <div
          style={{
            position: "absolute",
            left: interpolate(frame, [60, 130, 210, 230], [800, 500, 700, 1100], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            top: interpolate(frame, [60, 130, 210, 230], [500, 450, 480, 520], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            zIndex: 100,
            pointerEvents: "none",
          }}
        >
          <svg width="40" height="40" viewBox="0 0 24 24" fill={C.white} stroke={C.black} strokeWidth="2">
            <path d="M5 3l14 9-6.5 1.5L11 20z" />
          </svg>
        </div>
      )}
    </AbsoluteFill>
  );
};
