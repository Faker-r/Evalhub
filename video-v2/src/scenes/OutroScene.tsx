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
  pink: "#EC4899",
  dark: "#1F2937",
  light: "#F9FAFB",
  gray: "#6B7280",
};

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Logo animation
  const logoScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 120 },
  });

  const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Tagline animation
  const taglineOpacity = interpolate(frame, [30, 50], [0, 1], {
    extrapolateRight: "clamp",
  });
  const taglineY = interpolate(frame, [30, 50], [20, 0], {
    extrapolateRight: "clamp",
  });

  // CTA button animation
  const ctaScale = spring({
    frame: frame - 70,
    fps,
    config: { damping: 10, stiffness: 150 },
  });

  // Sub-text animation
  const subTextOpacity = interpolate(frame, [120, 140], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Floating animation
  const float = (offset: number) => Math.sin((frame + offset) * 0.06) * 8;

  // Pulse for CTA
  const pulse = 1 + Math.sin(frame * 0.1) * 0.03;

  // Background gradient animation
  const gradientRotation = frame * 0.3;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(${gradientRotation}deg, ${COLORS.light} 0%, ${COLORS.mintLight}60 50%, #FEF3C7 100%)`,
      }}
    >
      {/* Decorative floating shapes */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "10%",
          width: 120,
          height: 120,
          borderRadius: "50%",
          background: `linear-gradient(135deg, ${COLORS.mint}30 0%, ${COLORS.blue}30 100%)`,
          transform: `translateY(${float(0)}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "60%",
          right: "12%",
          width: 80,
          height: 80,
          borderRadius: "30%",
          background: `linear-gradient(135deg, ${COLORS.purple}25 0%, ${COLORS.pink}25 100%)`,
          transform: `translateY(${float(50)}px) rotate(${frame * 0.5}deg)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "20%",
          left: "20%",
          width: 60,
          height: 60,
          borderRadius: "40%",
          background: `linear-gradient(135deg, ${COLORS.yellow}30 0%, ${COLORS.coral}30 100%)`,
          transform: `translateY(${float(100)}px) rotate(${-frame * 0.3}deg)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "25%",
          right: "25%",
          width: 40,
          height: 40,
          borderRadius: "50%",
          background: `${COLORS.mint}20`,
          transform: `translateY(${float(30)}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "35%",
          right: "8%",
          width: 100,
          height: 100,
          borderRadius: "50%",
          background: `${COLORS.blue}15`,
          transform: `translateY(${float(70)}px)`,
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
        {/* Logo */}
        <div
          style={{
            opacity: logoOpacity,
            transform: `scale(${logoScale})`,
            display: "flex",
            alignItems: "center",
            gap: 20,
          }}
        >
          {/* Logo icon */}
          <div
            style={{
              width: 80,
              height: 80,
              borderRadius: 20,
              background: `linear-gradient(135deg, ${COLORS.mint} 0%, #059669 100%)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: `0 16px 48px ${COLORS.mint}50`,
            }}
          >
            <svg
              viewBox="0 0 24 24"
              width="44"
              height="44"
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
              fontSize: 72,
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
            transform: `translateY(${taglineY}px)`,
          }}
        >
          <h2
            style={{
              fontSize: 42,
              fontWeight: 700,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
              textAlign: "center",
              margin: 0,
            }}
          >
            Make better AI decisions.
          </h2>
          <p
            style={{
              fontSize: 24,
              color: COLORS.gray,
              fontFamily: "system-ui, sans-serif",
              textAlign: "center",
              marginTop: 12,
            }}
          >
            <span
              style={{
                fontStyle: "italic",
                background: `linear-gradient(90deg, ${COLORS.mint} 0%, ${COLORS.blue} 100%)`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              Benchmarking is Clarity.
            </span>
          </p>
        </div>

        {/* CTA Button */}
        <div
          style={{
            marginTop: 32,
            transform: `scale(${ctaScale * pulse})`,
          }}
        >
          <div
            style={{
              position: "relative",
            }}
          >
            {/* Glow effect */}
            <div
              style={{
                position: "absolute",
                inset: -12,
                borderRadius: 24,
                background: `linear-gradient(135deg, ${COLORS.mint}60 0%, ${COLORS.blue}60 100%)`,
                filter: "blur(20px)",
                opacity: 0.6,
              }}
            />
            <button
              style={{
                position: "relative",
                padding: "22px 56px",
                background: `linear-gradient(135deg, ${COLORS.mint} 0%, #059669 100%)`,
                border: "none",
                borderRadius: 18,
                fontSize: 22,
                fontWeight: 700,
                color: "#fff",
                fontFamily: "system-ui, sans-serif",
                display: "flex",
                alignItems: "center",
                gap: 14,
                cursor: "pointer",
                boxShadow: `0 12px 40px ${COLORS.mint}50`,
              }}
            >
              Try EvalHub Free
              <svg
                viewBox="0 0 24 24"
                width="24"
                height="24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </button>
          </div>
        </div>

        {/* Sub-text */}
        <div
          style={{
            opacity: subTextOpacity,
            marginTop: 20,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 12,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 24,
            }}
          >
            {[
              { icon: "🔓", text: "Open Source" },
              { icon: "⚡", text: "Fast Results" },
              { icon: "🎯", text: "Accurate" },
            ].map((item, i) => (
              <div
                key={item.text}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  opacity: interpolate(frame, [120 + i * 15, 135 + i * 15], [0, 1], {
                    extrapolateRight: "clamp",
                  }),
                }}
              >
                <span style={{ fontSize: 18 }}>{item.icon}</span>
                <span
                  style={{
                    fontSize: 16,
                    fontWeight: 600,
                    color: COLORS.gray,
                    fontFamily: "system-ui, sans-serif",
                  }}
                >
                  {item.text}
                </span>
              </div>
            ))}
          </div>

          <p
            style={{
              fontSize: 18,
              color: COLORS.gray,
              fontFamily: "system-ui, sans-serif",
              marginTop: 24,
              opacity: interpolate(frame, [180, 200], [0, 1], { extrapolateRight: "clamp" }),
            }}
          >
            evalhub.io
          </p>
        </div>
      </div>
    </AbsoluteFill>
  );
};
