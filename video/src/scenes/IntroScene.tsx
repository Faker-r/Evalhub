import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const IntroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Logo animation
  const logoScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Tagline animation
  const taglineOpacity = interpolate(frame, [30, 50], [0, 1], {
    extrapolateRight: "clamp",
  });

  const taglineY = interpolate(frame, [30, 50], [30, 0], {
    extrapolateRight: "clamp",
  });

  // Subtitle animation
  const subtitleOpacity = interpolate(frame, [60, 80], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Features animation
  const featuresOpacity = interpolate(frame, [100, 120], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Pulse animation for the mint accent
  const pulse = Math.sin(frame * 0.1) * 0.1 + 1;

  // Fade out at the end
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 30, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #09090b 0%, #18181b 50%, #09090b 100%)",
        opacity: fadeOut,
      }}
    >
      {/* Background gradient orb */}
      <div
        style={{
          position: "absolute",
          top: "30%",
          left: "50%",
          width: 600 * pulse,
          height: 600 * pulse,
          background: "radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%)",
          transform: "translate(-50%, -50%)",
          borderRadius: "50%",
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
          gap: 32,
        }}
      >
        {/* Logo */}
        <div
          style={{
            transform: `scale(${logoScale})`,
            opacity: logoOpacity,
            display: "flex",
            alignItems: "center",
            gap: 24,
          }}
        >
          {/* Logo icon */}
          <div
            style={{
              width: 100,
              height: 100,
              borderRadius: 20,
              background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 20px 60px rgba(16, 185, 129, 0.4)",
            }}
          >
            <svg
              viewBox="0 0 24 24"
              width="60"
              height="60"
              fill="none"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>

          {/* Logo text */}
          <div
            style={{
              fontSize: 96,
              fontWeight: 800,
              fontFamily: "system-ui, -apple-system, sans-serif",
              letterSpacing: "-2px",
            }}
          >
            <span style={{ color: "#10b981" }}>Eval</span>
            <span style={{ color: "#ffffff" }}>Hub</span>
          </div>
        </div>

        {/* Tagline */}
        <div
          style={{
            opacity: taglineOpacity,
            transform: `translateY(${taglineY}px)`,
            fontSize: 48,
            fontWeight: 700,
            color: "#ffffff",
            fontFamily: "system-ui, -apple-system, sans-serif",
          }}
        >
          Benchmarking is{" "}
          <span
            style={{
              background: "linear-gradient(90deg, #10b981 0%, #34d399 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Clarity
          </span>
        </div>

        {/* Subtitle */}
        <div
          style={{
            opacity: subtitleOpacity,
            fontSize: 28,
            color: "#a1a1aa",
            fontFamily: "system-ui, -apple-system, sans-serif",
            maxWidth: 800,
            textAlign: "center",
            lineHeight: 1.5,
          }}
        >
          The modern standard for evaluating open-source LLMs.
          <br />
          Compare performance across providers with rigorous, transparent benchmarks.
        </div>

        {/* Feature badges */}
        <div
          style={{
            opacity: featuresOpacity,
            display: "flex",
            gap: 24,
            marginTop: 40,
          }}
        >
          {["Lighteval Tasks", "Multiple Providers", "Real-time Results"].map(
            (feature, i) => (
              <div
                key={feature}
                style={{
                  padding: "16px 32px",
                  background: "rgba(16, 185, 129, 0.1)",
                  border: "1px solid rgba(16, 185, 129, 0.3)",
                  borderRadius: 12,
                  color: "#10b981",
                  fontSize: 20,
                  fontWeight: 600,
                  fontFamily: "system-ui, -apple-system, sans-serif",
                }}
              >
                {feature}
              </div>
            )
          )}
        </div>
      </div>

      {/* Version badge */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 60,
          opacity: logoOpacity,
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "8px 16px",
          background: "rgba(16, 185, 129, 0.15)",
          border: "1px solid rgba(16, 185, 129, 0.3)",
          borderRadius: 20,
        }}
      >
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: "#10b981",
            animation: "pulse 2s infinite",
          }}
        />
        <span
          style={{
            color: "#10b981",
            fontSize: 14,
            fontWeight: 700,
            fontFamily: "system-ui, -apple-system, sans-serif",
            letterSpacing: 1,
          }}
        >
          v2.0 LIVE NOW
        </span>
      </div>
    </AbsoluteFill>
  );
};
