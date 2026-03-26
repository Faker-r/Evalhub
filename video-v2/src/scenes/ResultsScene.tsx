import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  random,
} from "remotion";
import { C, FONT, popIn } from "../theme";

export const ResultsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Section title
  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [0, 15], [-20, 0], {
    extrapolateRight: "clamp",
  });

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Data for the bar chart
  const CHART_DATA = [
    { model: "Llama 3 70B", score: 82, color: C.pink },
    { model: "Gemini 1.5 Pro", score: 88, color: C.pink },
    { model: "Claude 3.5 Sonnet", score: 94, color: C.green },
  ];

  // Particles config
  const particles = Array.from({ length: 40 }).map((_, i) => ({
    id: i,
    x: random(i) * 100,
    y: random(i + 100) * 100,
    size: random(i + 200) * 15 + 10,
    color: random(i + 300) > 0.5 ? C.green : C.pink,
    delay: random(i + 400) * 30 + 120, // start after chart animates
  }));

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
        <filter id="results-noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#results-noise)" />
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
          zIndex: 10,
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
            boxShadow: `4px 4px 0px ${C.green}`,
          }}
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={C.green} strokeWidth="2.5" strokeLinecap="square">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
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
            Clear Results
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
            Insights you can act on
          </p>
        </div>
      </div>

      {/* Main Container */}
      <div
        style={{
          transform: `scale(${popIn(frame, fps, 0, { damping: 16, stiffness: 100 })})`,
          height: 700,
          background: C.white,
          border: `4px solid ${C.black}`,
          boxShadow: `16px 16px 0px ${C.black}`,
          display: "flex",
          position: "relative",
          zIndex: 5,
        }}
      >
        {/* Left column: Chart */}
        <div style={{ flex: 1.5, padding: 60, borderRight: `4px solid ${C.black}`, background: C.white }}>
          <h3 style={{ fontSize: 32, color: C.black, fontFamily: FONT.display, marginTop: 0, marginBottom: 40 }}>
            PERFORMANCE COMPARISON
          </h3>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
            {CHART_DATA.map((item, i) => {
              const animStart = 30 + i * 20;
              const barWidth = interpolate(frame, [animStart, animStart + 30], [0, item.score], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
              const textOpacity = interpolate(frame, [animStart + 15, animStart + 30], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
              
              return (
                <div key={item.model}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                    <span style={{ fontSize: 20, fontWeight: 800, color: C.black, fontFamily: FONT.body, textTransform: "uppercase" }}>
                      {item.model}
                    </span>
                    <span style={{ fontSize: 24, fontWeight: 800, color: item.color, fontFamily: FONT.display, opacity: textOpacity }}>
                      {Math.round(barWidth)}%
                    </span>
                  </div>
                  <div style={{ height: 40, background: C.grayLight, border: `3px solid ${C.black}`, position: "relative" }}>
                    <div
                      style={{
                        position: "absolute",
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: `${barWidth}%`,
                        background: item.color,
                        borderRight: `3px solid ${C.black}`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right column: Winner */}
        <div style={{ flex: 1, padding: 60, background: C.black, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          
          <div
            style={{
              opacity: interpolate(frame, [100, 120], [0, 1], { extrapolateRight: "clamp" }),
              transform: `scale(${popIn(frame, fps, 100)})`,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 24,
            }}
          >
            <div
              style={{
                width: 140,
                height: 140,
                background: C.green,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: `4px solid ${C.black}`,
                boxShadow: `8px 8px 0px ${C.white}`,
                transform: "rotate(4deg)",
              }}
            >
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke={C.black} strokeWidth="2.5" strokeLinecap="square">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            
            <h3 style={{ fontSize: 32, color: C.white, fontFamily: FONT.body, fontWeight: 800, margin: 0, textTransform: "uppercase", letterSpacing: 2 }}>
              CLEAR WINNER
            </h3>
            <div style={{ fontSize: 56, color: C.green, fontFamily: FONT.display, margin: 0, textAlign: "center", lineHeight: 1.1 }}>
              CLAUDE 3.5<br/>SONNET
            </div>
            
            <div style={{ display: "flex", gap: 16, marginTop: 16 }}>
              <div style={{ padding: "8px 16px", border: `2px solid ${C.green}`, color: C.green, fontFamily: FONT.mono, fontWeight: 800 }}>FASTEST</div>
              <div style={{ padding: "8px 16px", border: `2px solid ${C.pink}`, color: C.pink, fontFamily: FONT.mono, fontWeight: 800 }}>MOST HELPFUL</div>
            </div>
          </div>
        </div>
      </div>

      {/* Celebration Particles */}
      {particles.map((p) => {
        if (frame < p.delay) return null;
        
        const yAnim = interpolate(frame, [p.delay, p.delay + 40], [p.y, p.y - 400], { extrapolateRight: "clamp" });
        const opacity = interpolate(frame, [p.delay + 20, p.delay + 40], [1, 0], { extrapolateRight: "clamp" });
        const rotation = interpolate(frame, [p.delay, p.delay + 40], [0, 360]);

        return (
          <div
            key={p.id}
            style={{
              position: "absolute",
              left: `${p.x}%`,
              top: `${yAnim}%`,
              width: p.size,
              height: p.size,
              backgroundColor: p.color,
              opacity,
              border: `2px solid ${C.black}`,
              transform: `rotate(${rotation}deg)`,
              zIndex: 20,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
