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
  dark: "#1F2937",
  light: "#F9FAFB",
};

export const SolutionIntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Logo entrance
  const logoScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 150 },
  });

  const logoOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // "Meet EvalHub" text
  const meetTextOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateRight: "clamp",
  });
  const meetTextY = interpolate(frame, [20, 40], [30, 0], {
    extrapolateRight: "clamp",
  });

  // Tagline
  const taglineOpacity = interpolate(frame, [70, 90], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Feature pills
  const pillsOpacity = interpolate(frame, [120, 150], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Floating animation
  const float = (offset: number) => Math.sin((frame + offset) * 0.06) * 6;

  // Pulse for the logo glow
  const pulse = 0.8 + Math.sin(frame * 0.08) * 0.2;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${COLORS.light} 0%, ${COLORS.mintLight}50 100%)`,
        opacity: fadeOut,
      }}
    >
      {/* Decorative elements */}
      <div
        style={{
          position: "absolute",
          top: 80,
          left: 120,
          width: 120,
          height: 120,
          borderRadius: "50%",
          background: `${COLORS.mint}15`,
          transform: `translateY(${float(0)}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 120,
          right: 180,
          width: 180,
          height: 180,
          borderRadius: "40%",
          background: `${COLORS.purple}10`,
          transform: `translateY(${float(80)}px) rotate(${frame * 0.1}deg)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "50%",
          right: 100,
          width: 60,
          height: 60,
          borderRadius: "30%",
          background: `${COLORS.blue}15`,
          transform: `translateY(${float(40)}px)`,
        }}
      />

      {/* Main content */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "100%",
          gap: 24,
        }}
      >
        {/* "Meet" text */}
        <div
          style={{
            opacity: meetTextOpacity,
            transform: `translateY(${meetTextY}px)`,
            fontSize: 32,
            fontWeight: 600,
            color: "#6B7280",
            fontFamily: "system-ui, sans-serif",
            letterSpacing: 4,
          }}
        >
          MEET
        </div>

        {/* Logo */}
        <div
          style={{
            opacity: logoOpacity,
            transform: `scale(${logoScale})`,
            display: "flex",
            alignItems: "center",
            gap: 24,
            position: "relative",
          }}
        >
          {/* Logo glow */}
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: 400,
              height: 150,
              background: `radial-gradient(ellipse, ${COLORS.mint}30 0%, transparent 70%)`,
              transform: `translate(-50%, -50%) scale(${pulse})`,
              borderRadius: "50%",
              zIndex: -1,
            }}
          />

          {/* Logo icon */}
          <div
            style={{
              width: 90,
              height: 90,
              borderRadius: 22,
              background: `linear-gradient(135deg, ${COLORS.mint} 0%, #059669 100%)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: `0 20px 50px ${COLORS.mint}50`,
            }}
          >
            <svg
              viewBox="0 0 24 24"
              width="50"
              height="50"
              fill="none"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>

          {/* Logo text */}
          <div
            style={{
              fontSize: 88,
              fontWeight: 800,
              fontFamily: "system-ui, -apple-system, sans-serif",
              letterSpacing: -2,
            }}
          >
            <span style={{ color: COLORS.mint }}>Eval</span>
            <span style={{ color: COLORS.dark }}>Hub</span>
          </div>
        </div>

        {/* Tagline */}
        <div
          style={{
            opacity: taglineOpacity,
            marginTop: 16,
          }}
        >
          <h2
            style={{
              fontSize: 42,
              fontWeight: 600,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
              textAlign: "center",
              margin: 0,
            }}
          >
            Finally see how AI{" "}
            <span
              style={{
                background: `linear-gradient(90deg, ${COLORS.mint} 0%, ${COLORS.blue} 100%)`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              really
            </span>{" "}
            compares
          </h2>
        </div>

        {/* Feature pills */}
        <div
          style={{
            opacity: pillsOpacity,
            display: "flex",
            gap: 20,
            marginTop: 40,
          }}
        >
          {[
            { text: "Open & Transparent", icon: "🔓" },
            { text: "Rigorous Testing", icon: "🧪" },
            { text: "Make Better Decisions", icon: "✨" },
          ].map((pill, i) => {
            const pillBounce = spring({
              frame: frame - 120 - i * 10,
              fps,
              config: { damping: 12, stiffness: 200 },
            });
            return (
              <div
                key={pill.text}
                style={{
                  transform: `scale(${pillBounce})`,
                  padding: "16px 28px",
                  background: "#fff",
                  borderRadius: 50,
                  boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
                  border: `2px solid ${COLORS.mint}30`,
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                }}
              >
                <span style={{ fontSize: 22 }}>{pill.icon}</span>
                <span
                  style={{
                    fontSize: 18,
                    fontWeight: 600,
                    color: COLORS.dark,
                    fontFamily: "system-ui, sans-serif",
                  }}
                >
                  {pill.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
