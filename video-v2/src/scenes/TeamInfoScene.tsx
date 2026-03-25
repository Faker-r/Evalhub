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
  dark: "#1F2937",
  light: "#F9FAFB",
  gray: "#6B7280",
};

export const TeamInfoScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Card entrance
  const cardScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 120 },
  });

  const cardOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Staggered text animations
  const teamOpacity = interpolate(frame, [15, 30], [0, 1], {
    extrapolateRight: "clamp",
  });
  const projectOpacity = interpolate(frame, [25, 40], [0, 1], {
    extrapolateRight: "clamp",
  });
  const sponsorOpacity = interpolate(frame, [35, 50], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${COLORS.light} 0%, ${COLORS.mintLight}60 100%)`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Main card */}
      <div
        style={{
          opacity: cardOpacity,
          transform: `scale(${cardScale})`,
          background: "#fff",
          borderRadius: 32,
          padding: "60px 100px",
          boxShadow: `0 30px 80px ${COLORS.mint}30`,
          border: `3px solid ${COLORS.mint}40`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 32,
        }}
      >
        {/* Logo */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginBottom: 16,
          }}
        >
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 14,
              background: `linear-gradient(135deg, ${COLORS.mint} 0%, #059669 100%)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: `0 12px 32px ${COLORS.mint}40`,
            }}
          >
            <svg
              viewBox="0 0 24 24"
              width="32"
              height="32"
              fill="none"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <span
            style={{
              fontSize: 48,
              fontWeight: 800,
              fontFamily: "system-ui, -apple-system, sans-serif",
              letterSpacing: -1,
            }}
          >
            <span style={{ color: COLORS.mint }}>Eval</span>
            <span style={{ color: COLORS.dark }}>Hub</span>
          </span>
        </div>

        {/* Divider */}
        <div
          style={{
            width: 120,
            height: 4,
            borderRadius: 2,
            background: `linear-gradient(90deg, ${COLORS.mint} 0%, #059669 100%)`,
          }}
        />

        {/* Team number */}
        <div
          style={{
            opacity: teamOpacity,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: 16,
              fontWeight: 600,
              color: COLORS.gray,
              fontFamily: "system-ui, sans-serif",
              letterSpacing: 2,
              marginBottom: 8,
            }}
          >
            TEAM
          </div>
          <div
            style={{
              fontSize: 56,
              fontWeight: 800,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
            }}
          >
            KB-207
          </div>
        </div>

        {/* Project name */}
        <div
          style={{
            opacity: projectOpacity,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: 16,
              fontWeight: 600,
              color: COLORS.gray,
              fontFamily: "system-ui, sans-serif",
              letterSpacing: 2,
              marginBottom: 8,
            }}
          >
            PROJECT
          </div>
          <div
            style={{
              fontSize: 36,
              fontWeight: 700,
              color: COLORS.mint,
              fontFamily: "system-ui, sans-serif",
            }}
          >
            EvalHub
          </div>
        </div>

        {/* Sponsor */}
        <div
          style={{
            opacity: sponsorOpacity,
            textAlign: "center",
            marginTop: 8,
          }}
        >
          <div
            style={{
              fontSize: 16,
              fontWeight: 600,
              color: COLORS.gray,
              fontFamily: "system-ui, sans-serif",
              letterSpacing: 2,
              marginBottom: 8,
            }}
          >
            SPONSORED BY
          </div>
          <div
            style={{
              fontSize: 32,
              fontWeight: 700,
              color: COLORS.dark,
              fontFamily: "system-ui, sans-serif",
            }}
          >
            Baseten
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
