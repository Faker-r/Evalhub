import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  spring,
} from "remotion";

export const OutroScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Logo animation
  const logoScale = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  const logoOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // CTA animation
  const ctaOpacity = interpolate(frame, [40, 60], [0, 1], {
    extrapolateRight: "clamp",
  });
  const ctaY = interpolate(frame, [40, 60], [30, 0], {
    extrapolateRight: "clamp",
  });

  // Features animation
  const featuresOpacity = interpolate(frame, [80, 100], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Pulse animation
  const pulse = Math.sin(frame * 0.15) * 0.5 + 1;

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #09090b 0%, #18181b 50%, #09090b 100%)",
      }}
    >
      {/* Background gradient orbs */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          left: "30%",
          width: 400 * pulse,
          height: 400 * pulse,
          background: "radial-gradient(circle, rgba(16, 185, 129, 0.1) 0%, transparent 70%)",
          borderRadius: "50%",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "20%",
          right: "30%",
          width: 300 * pulse,
          height: 300 * pulse,
          background: "radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%)",
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
          gap: 40,
        }}
      >
        {/* Logo */}
        <div
          style={{
            transform: `scale(${logoScale})`,
            opacity: logoOpacity,
            display: "flex",
            alignItems: "center",
            gap: 20,
          }}
        >
          <div
            style={{
              width: 80,
              height: 80,
              borderRadius: 16,
              background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 20px 60px rgba(16, 185, 129, 0.4)",
            }}
          >
            <svg
              viewBox="0 0 24 24"
              width="48"
              height="48"
              fill="none"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <div
            style={{
              fontSize: 72,
              fontWeight: 800,
              fontFamily: "system-ui, -apple-system, sans-serif",
              letterSpacing: "-2px",
            }}
          >
            <span style={{ color: "#10b981" }}>Eval</span>
            <span style={{ color: "#ffffff" }}>Hub</span>
          </div>
        </div>

        {/* CTA */}
        <div
          style={{
            opacity: ctaOpacity,
            transform: `translateY(${ctaY}px)`,
            textAlign: "center",
          }}
        >
          <h2
            style={{
              fontSize: 42,
              fontWeight: 700,
              color: "#ffffff",
              fontFamily: "system-ui, sans-serif",
              margin: 0,
            }}
          >
            Start Evaluating Your LLMs Today
          </h2>
          <p
            style={{
              fontSize: 22,
              color: "#a1a1aa",
              fontFamily: "system-ui, sans-serif",
              marginTop: 16,
            }}
          >
            Open-source, transparent, and rigorous benchmarking
          </p>
        </div>

        {/* Action buttons */}
        <div
          style={{
            opacity: featuresOpacity,
            display: "flex",
            gap: 20,
            marginTop: 20,
          }}
        >
          <div
            style={{
              padding: "18px 40px",
              background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              borderRadius: 12,
              color: "#ffffff",
              fontSize: 20,
              fontWeight: 700,
              fontFamily: "system-ui, sans-serif",
              display: "flex",
              alignItems: "center",
              gap: 12,
              boxShadow: "0 10px 40px rgba(16, 185, 129, 0.3)",
            }}
          >
            Get Started Free
            <svg
              viewBox="0 0 24 24"
              width="22"
              height="22"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </div>
          <div
            style={{
              padding: "18px 40px",
              background: "transparent",
              border: "2px solid rgba(255, 255, 255, 0.2)",
              borderRadius: 12,
              color: "#ffffff",
              fontSize: 20,
              fontWeight: 600,
              fontFamily: "system-ui, sans-serif",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <svg
              viewBox="0 0 24 24"
              width="22"
              height="22"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
            </svg>
            View on GitHub
          </div>
        </div>

        {/* Feature highlights */}
        <div
          style={{
            opacity: featuresOpacity,
            display: "flex",
            gap: 40,
            marginTop: 40,
          }}
        >
          {[
            { icon: "zap", text: "100+ Benchmarks" },
            { icon: "users", text: "Multiple Providers" },
            { icon: "chart", text: "Real-time Results" },
            { icon: "shield", text: "Open Source" },
          ].map((feature) => (
            <div
              key={feature.text}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                color: "#71717a",
                fontSize: 16,
                fontFamily: "system-ui, sans-serif",
              }}
            >
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: "rgba(16, 185, 129, 0.15)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <svg
                  viewBox="0 0 24 24"
                  width="16"
                  height="16"
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="2"
                >
                  {feature.icon === "zap" && <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />}
                  {feature.icon === "users" && (
                    <>
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </>
                  )}
                  {feature.icon === "chart" && (
                    <>
                      <line x1="12" y1="20" x2="12" y2="10" />
                      <line x1="18" y1="20" x2="18" y2="4" />
                      <line x1="6" y1="20" x2="6" y2="16" />
                    </>
                  )}
                  {feature.icon === "shield" && (
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  )}
                </svg>
              </div>
              {feature.text}
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div
        style={{
          position: "absolute",
          bottom: 40,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: featuresOpacity,
        }}
      >
        <p
          style={{
            color: "#52525b",
            fontSize: 14,
            fontFamily: "system-ui, sans-serif",
          }}
        >
          evalhub.io
        </p>
      </div>
    </AbsoluteFill>
  );
};
