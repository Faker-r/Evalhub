import React from 'react';
import { AbsoluteFill, interpolate } from 'remotion';
import { C, FONT } from '../theme';

interface IsometricDiagramProps {
  localFrame: number;
}

const ThickSlice: React.FC<{
  z: number;
  color: string;
  sideColor: string;
  thickness: number;
  floatOffset?: number;
}> = ({ z, color, sideColor, thickness, floatOffset = 0 }) => {
  return (
    <div style={{
      position: 'absolute',
      transformStyle: 'preserve-3d',
      transform: `translateZ(${z + floatOffset}px)`,
    }}>
      {Array.from({ length: thickness }).map((_, i) => (
        <div key={i} style={{
          position: 'absolute',
          width: 240, height: 240,
          left: -120, top: -120, // Center origin
          borderRadius: '50%',
          backgroundColor: i === thickness - 1 ? color : sideColor,
          transform: `translateZ(${i}px)`,
          border: i === thickness - 1 ? `3px solid ${sideColor}` : 'none',
          boxSizing: 'border-box'
        }} />
      ))}
    </div>
  );
};

const DataTag: React.FC<{ x: number; y: number; z: number; label: string }> = ({ x, y, z, label }) => {
  return (
    <div style={{
      position: 'absolute',
      transformStyle: 'preserve-3d',
      transform: `translate3d(${x}px, ${y}px, ${z}px) rotateZ(45deg) rotateX(-90deg) rotateY(0deg)`, 
    }}>
      <div style={{
        backgroundColor: C.white,
        border: `3px solid ${C.black}`,
        padding: '12px 24px',
        color: C.black,
        fontFamily: FONT.mono,
        fontWeight: 'bold',
        fontSize: 24,
        boxShadow: `8px 8px 0px ${C.black}`,
        whiteSpace: 'nowrap',
        transform: 'translate(-50%, -50%)', // Center on coordinates
      }}>
        {label}
      </div>
    </div>
  );
};

export const IsometricDiagram: React.FC<IsometricDiagramProps> = ({ localFrame }) => {
  // Sine wave for floating slice
  const floatZ = Math.max(0, Math.sin(localFrame / 15) * 60);

  const PINK_SIDE = "#C465C2";
  const GREEN_SIDE = "#0EBD55";

  const particles = [
    { letter: 'S', offset: 0 },
    { letter: 'B', offset: 15 },
    { letter: 'T', offset: 30 },
    { letter: 'N', offset: 45 },
  ];

  return (
    <AbsoluteFill style={{
      backgroundColor: '#FAFAFA',
      backgroundImage: `radial-gradient(${C.grayMid}40 2px, transparent 2px)`,
      backgroundSize: '40px 40px',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute',
        top: '50%', left: '50%',
        width: 0, height: 0,
        transformStyle: 'preserve-3d',
        transform: `rotateX(60deg) rotateZ(-45deg)`, // Classic isometric
      }}>
        
        {/* Tether Lines - Bottom base tags */}
        <div style={{ position: 'absolute', transform: 'translateZ(20px)' }}>
          <svg style={{ position: 'absolute', width: 2000, height: 2000, left: -1000, top: -1000, overflow: 'visible' }}>
            {/* Left tag */}
            <line x1="1000" y1="1000" x2="680" y2="840" stroke={C.black} strokeWidth={4} />
            {/* Back tag */}
            <line x1="1000" y1="1000" x2="880" y2="600" stroke={C.black} strokeWidth={4} />
            {/* Front tag */}
            <line x1="1000" y1="1000" x2="1140" y2="1320" stroke={C.black} strokeWidth={4} />
          </svg>
        </div>

        {/* Tether Lines - Top floating slice tag */}
        <div style={{ position: 'absolute', transform: `translateZ(${floatZ + 90 + 15}px)` }}>
          <svg style={{ position: 'absolute', width: 2000, height: 2000, left: -1000, top: -1000, overflow: 'visible' }}>
            {/* Right tag tethered to moving slice */}
            <line x1="1000" y1="1000" x2="1460" y2="1080" stroke={C.black} strokeWidth={4} />
          </svg>
        </div>

        {/* Central Stack */}
        <ThickSlice z={0} color={C.pink} sideColor={PINK_SIDE} thickness={30} />
        <ThickSlice z={45} color={C.green} sideColor={GREEN_SIDE} thickness={30} />
        
        {/* Floating Middle Slice */}
        <ThickSlice z={90} color={C.green} sideColor={GREEN_SIDE} thickness={30} floatOffset={floatZ} />
        
        {/* Top slices staying above float */}
        <ThickSlice z={170} color={C.green} sideColor={GREEN_SIDE} thickness={30} />
        <ThickSlice z={215} color={C.green} sideColor={GREEN_SIDE} thickness={30} />

        {/* Data Tags */}
        <DataTag label="3000 REQUESTS/M" x={-320} y={-160} z={50} />
        <DataTag label="415 REPLICAS" x={-120} y={-400} z={80} />
        <DataTag label="93 TPS" x={140} y={320} z={50} />
        <DataTag label="75% GPU UTILIZATION" x={460} y={80} z={floatZ + 120} />

        {/* Main Labels (Text Boxes) */}
        {/* PRODUCTION */}
        <div style={{
          position: 'absolute', transformStyle: 'preserve-3d',
          transform: `translate3d(-100px, 300px, 450px) rotateZ(45deg) rotateX(-90deg)`,
        }}>
          <div style={{
            background: C.green, color: C.black, padding: '20px 40px',
            fontFamily: FONT.display, fontSize: 56, fontWeight: 'bold',
            border: `6px solid ${C.black}`, boxShadow: `12px 12px 0px ${C.black}`
          }}>PRODUCTION</div>
        </div>

        {/* STAGING */}
        <div style={{
          position: 'absolute', transformStyle: 'preserve-3d',
          transform: `translate3d(450px, -250px, 150px) rotateZ(45deg) rotateX(-90deg)`,
        }}>
          <div style={{
            background: C.white, color: C.green, padding: '16px 32px',
            fontFamily: FONT.display, fontSize: 48, fontWeight: 'bold',
            border: `6px solid ${C.green}`, boxShadow: `12px 12px 0px ${C.green}`
          }}>STAGING</div>
        </div>

        {/* DEPLOYMENTS */}
        <div style={{
          position: 'absolute', transformStyle: 'preserve-3d',
          transform: `translate3d(-500px, 150px, 0px) rotateZ(45deg) rotateX(-90deg)`,
        }}>
          <div style={{
            background: C.white, color: C.pink, padding: '16px 32px',
            fontFamily: FONT.display, fontSize: 48, fontWeight: 'bold',
            border: `6px solid ${C.pink}`, boxShadow: `12px 12px 0px ${C.pink}`
          }}>DEPLOYMENTS</div>
        </div>

        {/* Particle Stream */}
        {particles.map(({ letter, offset }) => {
          const pFrame = (localFrame + offset) % 120;
          const progress = pFrame / 120;
          
          const startX = -650; const endX = 650;
          const startY = 250;  const endY = -250;
          
          const currentX = interpolate(progress, [0, 1], [startX, endX]);
          const currentY = interpolate(progress, [0, 1], [startY, endY]);
          const currentZ = 100 + Math.sin(progress * Math.PI) * 200;
          
          const opacity = interpolate(progress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);

          return (
            <div key={letter} style={{
              position: 'absolute', transformStyle: 'preserve-3d',
              transform: `translate3d(${currentX}px, ${currentY}px, ${currentZ}px) rotateZ(45deg) rotateX(-90deg)`,
              opacity
            }}>
              <div style={{
                color: C.green, fontFamily: FONT.display, fontSize: 72, fontWeight: 'bold',
                textShadow: `0 0 16px ${C.green}`
              }}>
                {letter}
              </div>
            </div>
          );
        })}

        {/* Hovering Badge / cube */}
        <div style={{
          position: 'absolute', transformStyle: 'preserve-3d',
          transform: `translate3d(500px, 500px, 0px)`
        }}>
           {/* Glowing Cube using multiple planes */}
           <div style={{
             position: 'absolute', width: 120, height: 120, backgroundColor: C.green,
             boxShadow: `0 0 60px ${C.green}`, opacity: 0.6,
             left: -60, top: -60
           }} />
           <div style={{
             position: 'absolute', width: 120, height: 120, backgroundColor: C.green,
             transform: 'translateZ(100px)', border: `4px solid ${C.white}`,
             left: -60, top: -60
           }} />
           {/* Checkmark hovering */}
           <div style={{
             position: 'absolute', transformStyle: 'preserve-3d',
             transform: `translate3d(0px, 0px, ${150 + Math.sin(localFrame / 10) * 20}px) rotateZ(45deg) rotateX(-90deg)`,
           }}>
              <div style={{
                background: '#0a66c2', color: C.white, borderRadius: '50%',
                width: 80, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: `0 15px 30px rgba(0,0,0,0.6)`, marginLeft: -40, marginTop: -40,
                border: `4px solid ${C.white}`
              }}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
           </div>
        </div>

        {/* Floating Background Geometry */}
        {[
          { color: C.green, x: -400, y: -500, z: 250, delay: 0 },
          { color: C.pink, x: 600, y: -200, z: 50, delay: 20 },
          { color: C.black, x: 300, y: 600, z: 350, delay: 40 },
          { color: C.grayMid, x: -600, y: 400, z: 150, delay: 60 },
        ].map((item, i) => (
          <div key={i} style={{
            position: 'absolute',
            width: 50, height: 50,
            border: `6px solid ${item.color}`,
            transform: `translate3d(${item.x}px, ${item.y}px, ${item.z + Math.cos((localFrame + item.delay) / 20) * 40}px) rotateZ(45deg)`,
            opacity: 0.7
          }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
