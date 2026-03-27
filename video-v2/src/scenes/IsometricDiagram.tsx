import React from 'react';
import { AbsoluteFill, Img } from 'remotion';
import { FONT } from '../theme';

interface IsometricDiagramProps {
  localFrame: number;
}

const TOKEN = 'pk_fr5aaea76f743581c84a5e';
const logoUrl = (domain: string) =>
  `https://img.logokit.com/${domain}?token=${TOKEN}`;

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

const getPointOnSegment = (
  x1: number, y1: number, x2: number, y2: number, t: number
): { x: number; y: number } => ({
  x: lerp(x1, x2, t),
  y: lerp(y1, y2, t),
});

const particleT = (frame: number, speed: number, offset: number) =>
  ((frame * speed + offset) % 100) / 100;

// ── Layout constants ──────────────────────────────────────────────────────────
// Application Layer box: x=80, y=40, w=1760, h=110. Right=1840, CenterX=960
// 4 pills evenly spaced, centered at x=960, step=320
const APP_PILL_CX = [480, 800, 1120, 1440]; // pill centers
const APP_PILL_Y = 100;                      // pill center y
const APP_PILL_W = 180;
const APP_PILL_H = 44;

// Fork diamond center
const FORK_CX = 960;
const FORK_CY = 248;
const FORK_TOP_Y = 218;
const FORK_BOT_Y = 278;

// OSS Inference box: x=80, y=350, w=960, h=250. Right=1040, CenterX=560
const OSS_BOX = { x: 80, y: 350, w: 960, h: 250 };
const OSS_CX = 560;
// 4 logos evenly spaced, centered at x=560, step=200
const OSS_LOGO_XS = [160, 360, 560, 760];
const OSS_LOGO_Y = 475;

// Proprietary box: x=1200, y=350, w=640, h=250. Right=1840, CenterX=1520
const PROP_BOX = { x: 1200, y: 350, w: 640, h: 250 };
const PROP_CX = 1520;
// 2 logos evenly spaced, centered at x=1520, offset=±140
const PROP_LOGO_XS = [1380, 1660];
const PROP_LOGO_Y = 475;

// OSS Models box: x=180, y=640, w=760, h=120. Right=940, CenterX=560
const MODELS_BOX = { x: 180, y: 640, w: 760, h: 120 };
const MODELS_CX = 560;
// 3 logos evenly spaced, centered at x=560, step=200
const MODELS_LOGO_XS = [360, 560, 760];
const MODELS_LOGO_Y = 700;

// Infrastructure box: x=80, y=800, w=1760, h=260. Right=1840
// 3 cloud zones with dividers at 670 and 1250
const INFRA_Y = 800;
const INFRA_DIVIDERS = [670, 1250]; // zone dividers
// Cloud provider centers: (80+670)/2=375, (670+1250)/2=960, (1250+1840)/2=1545
const CLOUD_LOGO_Y = 868;
const CLOUD_ZONE_CX = [375, 960, 1545];

// ── Data ─────────────────────────────────────────────────────────────────────

const APP_ITEMS = ['CHAT UI', 'REST API', 'SDK', 'WEB APP'];

const OSS_PROVIDERS = [
  { domain: 'together.ai',  name: 'Together AI' },
  { domain: 'baseten.co',   name: 'Baseten' },
  { domain: 'fireworks.ai', name: 'Fireworks' },
  { domain: 'groq.com',     name: 'Groq' },
];

const PROP_PROVIDERS = [
  { domain: 'openai.com',    name: 'OpenAI' },
  { domain: 'anthropic.com', name: 'Anthropic' },
];

const OSS_MODELS = [
  { domain: 'alibaba.com',  name: 'Qwen' },
  { domain: 'deepseek.com', name: 'DeepSeek' },
  { domain: 'meta.com',     name: 'LLaMA' },
];

const CLOUD_PROVIDERS = [
  { domain: 'aws.amazon.com',      name: 'AWS' },
  { domain: 'cloud.google.com',    name: 'GCP' },
  { domain: 'azure.microsoft.com', name: 'Azure' },
];

// Connectors: each has start/end points and color
// All fork-out connectors start from the bottom point of the diamond
const CONNECTORS: { pts: [number, number, number, number]; color: string }[] = [
  { pts: [FORK_CX, 152, FORK_CX, FORK_TOP_Y],             color: '#18E76F' }, // App → Fork
  { pts: [FORK_CX, FORK_BOT_Y, OSS_CX, OSS_BOX.y],        color: '#18E76F' }, // Fork → OSS Inference
  { pts: [FORK_CX, FORK_BOT_Y, PROP_CX, PROP_BOX.y],      color: '#6366f1' }, // Fork → Proprietary
  { pts: [OSS_CX, OSS_BOX.y + OSS_BOX.h + 1, OSS_CX, MODELS_BOX.y],          color: '#18E76F' }, // OSS Inference → Models
  { pts: [MODELS_CX, MODELS_BOX.y + MODELS_BOX.h + 1, MODELS_CX, INFRA_Y],   color: '#18E76F' }, // Models → Infra
  { pts: [PROP_CX, PROP_BOX.y + PROP_BOX.h + 1, PROP_CX, INFRA_Y],           color: '#6366f1' }, // Proprietary → Infra
];

// GPU bars per cloud zone — each positioned relative to zone center
const GPU_BARS = [
  { zoneCX: CLOUD_ZONE_CX[0], y: 912, baseW: 200, phase: 0,   label: 'GPU A100' },
  { zoneCX: CLOUD_ZONE_CX[0], y: 938, baseW: 180, phase: 1.2, label: 'GPU H100' },
  { zoneCX: CLOUD_ZONE_CX[1], y: 912, baseW: 220, phase: 0.6, label: 'GPU A100' },
  { zoneCX: CLOUD_ZONE_CX[1], y: 938, baseW: 160, phase: 2.1, label: 'GPU H100' },
  { zoneCX: CLOUD_ZONE_CX[2], y: 912, baseW: 190, phase: 1.8, label: 'GPU A100' },
  { zoneCX: CLOUD_ZONE_CX[2], y: 938, baseW: 210, phase: 0.3, label: 'GPU H100' },
];

export const IsometricDiagram: React.FC<IsometricDiagramProps> = ({ localFrame }) => {
  const frame = localFrame;

  const requests = Math.round(2700 + 500 * Math.sin(frame / 40));
  const dashOffset = -(frame * 1.2);
  const pulseR = 32 + 8 * Math.sin(frame / 12);
  const pulseOpacity = 0.3 + 0.2 * Math.sin(frame / 12);

  const logoSize = 52;
  const logoHalf = logoSize / 2;

  return (
    <AbsoluteFill style={{ backgroundColor: '#f8f9fa', overflow: 'hidden', fontFamily: FONT.mono }}>

      {/* ── SVG layer: geometry, connectors, labels ── */}
      <svg
        width="1920"
        height="1080"
        viewBox="0 0 1920 1080"
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        {/* Infra dark background */}
        <rect x={80} y={INFRA_Y} width={1760} height={270} rx={16} fill="#0d1117" />

        {/* ── Section boxes ── */}
        {/* Application Layer */}
        <rect x={80} y={40} width={1760} height={110} rx={12} fill="#ffffff" stroke="#18E76F" strokeWidth={2} />
        {/* Open Source Inference */}
        <rect x={OSS_BOX.x} y={OSS_BOX.y} width={OSS_BOX.w} height={OSS_BOX.h} rx={12} fill="#ffffff" stroke="#18E76F" strokeWidth={2} />
        {/* Proprietary */}
        <rect x={PROP_BOX.x} y={PROP_BOX.y} width={PROP_BOX.w} height={PROP_BOX.h} rx={12} fill="#ffffff" stroke="#6366f1" strokeWidth={2} />
        {/* Open Source Models */}
        <rect x={MODELS_BOX.x} y={MODELS_BOX.y} width={MODELS_BOX.w} height={MODELS_BOX.h} rx={12} fill="#ffffff" stroke="#18E76F" strokeWidth={2} />

        {/* ── Section labels ── */}
        <text x={960} y={62} textAnchor="middle" fontSize={12} fill="#18E76F" fontWeight="700" letterSpacing="2" fontFamily={FONT.mono}>APPLICATION LAYER</text>
        <text x={OSS_CX} y={OSS_BOX.y + 24} textAnchor="middle" fontSize={11} fill="#18E76F" fontWeight="700" letterSpacing="2" fontFamily={FONT.mono}>OPEN SOURCE INFERENCE</text>
        <text x={PROP_CX} y={PROP_BOX.y + 24} textAnchor="middle" fontSize={11} fill="#6366f1" fontWeight="700" letterSpacing="2" fontFamily={FONT.mono}>PROPRIETARY</text>
        <text x={MODELS_CX} y={MODELS_BOX.y + 22} textAnchor="middle" fontSize={11} fill="#18E76F" fontWeight="700" letterSpacing="2" fontFamily={FONT.mono}>OPEN SOURCE MODELS</text>
        <text x={960} y={INFRA_Y + 24} textAnchor="middle" fontSize={11} fill="#18E76F" fontWeight="700" letterSpacing="2" fontFamily={FONT.mono}>CLOUD &amp; GPU INFRASTRUCTURE</text>

        {/* ── App item pills — 4 pills evenly spaced, centered at x=960 ── */}
        {APP_ITEMS.map((label, i) => {
          const cx = APP_PILL_CX[i];
          return (
            <g key={label}>
              <rect
                x={cx - APP_PILL_W / 2} y={APP_PILL_Y - APP_PILL_H / 2}
                width={APP_PILL_W} height={APP_PILL_H}
                rx={APP_PILL_H / 2}
                fill="#f0fdf4" stroke="#18E76F" strokeWidth={1.5}
              />
              <text x={cx} y={APP_PILL_Y + 4} textAnchor="middle" fontSize={11} fill="#16a34a" fontWeight="700" letterSpacing="1" fontFamily={FONT.mono}>{label}</text>
            </g>
          );
        })}

        {/* ── Fork diamond ── */}
        <polygon
          points={`${FORK_CX},${FORK_TOP_Y} ${FORK_CX + 40},${FORK_CY} ${FORK_CX},${FORK_BOT_Y} ${FORK_CX - 40},${FORK_CY}`}
          fill="#0d1117"
          stroke="#18E76F"
          strokeWidth={2}
        />
        {/* Pulse rings centered on diamond */}
        <circle cx={FORK_CX} cy={FORK_CY} r={pulseR} fill="none" stroke="#18E76F" strokeWidth={1.5} opacity={pulseOpacity} />
        <circle cx={FORK_CX} cy={FORK_CY} r={pulseR * 1.6} fill="none" stroke="#18E76F" strokeWidth={1} opacity={pulseOpacity * 0.4} />
        <text x={FORK_CX} y={FORK_CY - 4} textAnchor="middle" fontSize={8} fill="#18E76F" fontWeight="700" fontFamily={FONT.mono}>ROUTER</text>
        <text x={FORK_CX} y={FORK_CY + 8} textAnchor="middle" fontSize={8} fill="#18E76F" fontFamily={FONT.mono}>{requests}/s</text>

        {/* ── Connector lines (dashed, animated offset) ── */}
        {CONNECTORS.map(({ pts: [x1, y1, x2, y2], color }, i) => (
          <line
            key={i}
            x1={x1} y1={y1} x2={x2} y2={y2}
            stroke={color}
            strokeWidth={1.5}
            strokeDasharray="8 6"
            strokeDashoffset={dashOffset}
            opacity={0.75}
          />
        ))}

        {/* ── Particle dots on connectors ── */}
        {CONNECTORS.map(({ pts: [x1, y1, x2, y2], color }, i) => {
          const t1 = particleT(frame, 0.5, i * 33);
          const t2 = particleT(frame, 0.5, i * 33 + 50);
          const p1 = getPointOnSegment(x1, y1, x2, y2, t1);
          const p2 = getPointOnSegment(x1, y1, x2, y2, t2);
          return (
            <g key={i}>
              <circle cx={p1.x} cy={p1.y} r={4} fill={color} />
              <circle cx={p2.x} cy={p2.y} r={4} fill={color} />
            </g>
          );
        })}

        {/* ── GPU utilization bars — centered within each cloud zone ── */}
        {GPU_BARS.map((bar, i) => {
          const usedW = bar.baseW * (0.55 + 0.45 * Math.sin(frame / 25 + bar.phase));
          const pct = Math.round((usedW / bar.baseW) * 100);
          const barX = bar.zoneCX - bar.baseW / 2;
          return (
            <g key={i}>
              <text x={barX} y={bar.y - 4} fontSize={8} fill="#4ade80" fontFamily={FONT.mono} fontWeight="600">{bar.label} {pct}%</text>
              <rect x={barX} y={bar.y} width={bar.baseW} height={10} rx={3} fill="#1e2a1e" />
              <rect x={barX} y={bar.y} width={usedW} height={10} rx={3} fill="#18E76F" opacity={0.9} />
            </g>
          );
        })}

        {/* ── Server rack — complete 5×5 symmetric grid ── */}
        {Array.from({ length: 25 }).map((_, i) => {
          const col = i % 5;
          const row = Math.floor(i / 5);
          const pulse = 0.4 + 0.6 * Math.abs(Math.sin(frame / 18 + i * 0.7));
          // positioned in the right portion of the infra box
          return (
            <rect
              key={i}
              x={1700 + col * 24} y={862 + row * 24}
              width={16} height={16}
              rx={3}
              fill="#18E76F"
              opacity={pulse * 0.8}
            />
          );
        })}

        {/* ── Cloud zone vertical dividers ── */}
        {INFRA_DIVIDERS.map((dx, i) => (
          <line key={i} x1={dx} y1={INFRA_Y + 10} x2={dx} y2={INFRA_Y + 258} stroke="#1e2a1e" strokeWidth={1} />
        ))}

        {/* ── Provider name labels ── */}
        {OSS_PROVIDERS.map((p, i) => (
          <text key={p.name} x={OSS_LOGO_XS[i]} y={OSS_LOGO_Y + logoHalf + 18} textAnchor="middle" fontSize={10} fill="#374151" fontWeight="600" fontFamily={FONT.mono}>{p.name}</text>
        ))}
        {PROP_PROVIDERS.map((p, i) => (
          <text key={p.name} x={PROP_LOGO_XS[i]} y={PROP_LOGO_Y + logoHalf + 18} textAnchor="middle" fontSize={10} fill="#374151" fontWeight="600" fontFamily={FONT.mono}>{p.name}</text>
        ))}
        {OSS_MODELS.map((m, i) => (
          <text key={m.name} x={MODELS_LOGO_XS[i]} y={MODELS_LOGO_Y + logoHalf + 18} textAnchor="middle" fontSize={10} fill="#374151" fontWeight="600" fontFamily={FONT.mono}>{m.name}</text>
        ))}
        {CLOUD_PROVIDERS.map((c, i) => (
          <text key={c.name} x={CLOUD_ZONE_CX[i]} y={CLOUD_LOGO_Y + logoHalf + 20} textAnchor="middle" fontSize={10} fill="#4ade80" fontWeight="600" fontFamily={FONT.mono}>{c.name}</text>
        ))}
      </svg>

      {/* ── Logo images — Remotion <Img> for reliable render-time loading ── */}

      {/* OSS Inference Providers */}
      {OSS_PROVIDERS.map((p, i) => (
        <div
          key={p.domain}
          style={{
            position: 'absolute',
            left: OSS_LOGO_XS[i] - logoHalf,
            top: OSS_LOGO_Y - logoHalf,
            width: logoSize,
            height: logoSize,
            borderRadius: '50%',
            overflow: 'hidden',
            border: '2px solid #18E76F',
            background: '#fff',
          }}
        >
          <Img src={logoUrl(p.domain)} style={{ width: logoSize, height: logoSize, objectFit: 'contain' }} />
        </div>
      ))}

      {/* Proprietary Providers */}
      {PROP_PROVIDERS.map((p, i) => (
        <div
          key={p.domain}
          style={{
            position: 'absolute',
            left: PROP_LOGO_XS[i] - logoHalf,
            top: PROP_LOGO_Y - logoHalf,
            width: logoSize,
            height: logoSize,
            borderRadius: '50%',
            overflow: 'hidden',
            border: '2px solid #6366f1',
            background: '#fff',
          }}
        >
          <Img src={logoUrl(p.domain)} style={{ width: logoSize, height: logoSize, objectFit: 'contain' }} />
        </div>
      ))}

      {/* Open Source Models */}
      {OSS_MODELS.map((m, i) => (
        <div
          key={m.domain}
          style={{
            position: 'absolute',
            left: MODELS_LOGO_XS[i] - logoHalf,
            top: MODELS_LOGO_Y - logoHalf,
            width: logoSize,
            height: logoSize,
            borderRadius: '50%',
            overflow: 'hidden',
            border: '2px solid #18E76F',
            background: '#fff',
          }}
        >
          <Img src={logoUrl(m.domain)} style={{ width: logoSize, height: logoSize, objectFit: 'contain' }} />
        </div>
      ))}

      {/* Cloud Providers */}
      {CLOUD_PROVIDERS.map((c, i) => (
        <div
          key={c.domain}
          style={{
            position: 'absolute',
            left: CLOUD_ZONE_CX[i] - logoHalf,
            top: CLOUD_LOGO_Y - logoHalf,
            width: logoSize,
            height: logoSize,
            borderRadius: '50%',
            overflow: 'hidden',
            border: '2px solid #18E76F',
            background: '#111',
          }}
        >
          <Img src={logoUrl(c.domain)} style={{ width: logoSize, height: logoSize, objectFit: 'contain' }} />
        </div>
      ))}
    </AbsoluteFill>
  );
};
