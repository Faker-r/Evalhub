import { Audio, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";

// Audio file paths using staticFile for proper bundling
export const AUDIO_FILES = {
  // Background music (SoundHelix - public domain)
  backgroundMusic: staticFile("audio/background-music.mp3"),

  // Voiceover track - replace with your recorded voiceover
  voiceover: staticFile("audio/voiceover.mp3"),

  // Sound effects
  sfx: {
    whoosh: staticFile("audio/sfx/whoosh.mp3"),
    pop: staticFile("audio/sfx/pop.mp3"),
    click: staticFile("audio/sfx/click.mp3"),
    success: staticFile("audio/sfx/success.mp3"),
    typing: staticFile("audio/sfx/typing.mp3"),
    chime: staticFile("audio/sfx/chime.mp3"),
  },
};

// Background music component with fade in/out
export const BackgroundMusic: React.FC<{ volume?: number }> = ({ volume = 0.3 }) => {
  const frame = useCurrentFrame();

  // Fade in over first 30 frames, fade out over last 30 frames
  const fadeIn = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [3060, 3090], [1, 0], { extrapolateLeft: "clamp" });
  const dynamicVolume = volume * fadeIn * fadeOut;

  return (
    <Audio
      src={AUDIO_FILES.backgroundMusic}
      volume={dynamicVolume}
    />
  );
};

// Voiceover component
export const Voiceover: React.FC<{ volume?: number }> = ({ volume = 1 }) => {
  return (
    <Audio
      src={AUDIO_FILES.voiceover}
      volume={volume}
    />
  );
};

// Sound effect with proper Sequence timing
const SfxTrigger: React.FC<{
  src: string;
  volume: number;
  durationFrames?: number;
}> = ({ src, volume, durationFrames = 45 }) => {
  return (
    <Audio
      src={src}
      volume={volume}
    />
  );
};

// All sound effects for the video with their timings
export const VideoSoundEffects: React.FC = () => {
  const sfx = AUDIO_FILES.sfx;

  // Define all sound effect timings (in frames, 30fps)
  // Each effect plays for ~1.5 seconds (45 frames)
  const soundEffects = [
    // Hook Scene (0-540 frames / 0-18s)
    { src: sfx.whoosh, frame: 0, volume: 0.3 },
    { src: sfx.pop, frame: 30, volume: 0.25 },
    { src: sfx.pop, frame: 65, volume: 0.2 },
    { src: sfx.pop, frame: 80, volume: 0.2 },
    { src: sfx.pop, frame: 95, volume: 0.2 },
    { src: sfx.whoosh, frame: 155, volume: 0.3 },
    { src: sfx.pop, frame: 190, volume: 0.25 },
    { src: sfx.whoosh, frame: 400, volume: 0.3 },

    // Solution Intro Scene (540-840 frames / 18-28s)
    { src: sfx.chime, frame: 540, volume: 0.4 },
    { src: sfx.pop, frame: 640, volume: 0.25 },
    { src: sfx.pop, frame: 660, volume: 0.25 },
    { src: sfx.pop, frame: 680, volume: 0.25 },

    // Leaderboard Scene (840-1500 frames / 28-50s)
    { src: sfx.whoosh, frame: 840, volume: 0.3 },
    { src: sfx.pop, frame: 920, volume: 0.15 },
    { src: sfx.pop, frame: 950, volume: 0.15 },
    { src: sfx.pop, frame: 980, volume: 0.15 },
    { src: sfx.click, frame: 1020, volume: 0.35 },

    // Submit Eval Scene (1500-2160 frames / 50-72s)
    { src: sfx.whoosh, frame: 1500, volume: 0.3 },
    { src: sfx.click, frame: 1560, volume: 0.25 },
    { src: sfx.pop, frame: 1620, volume: 0.2 },
    { src: sfx.click, frame: 1680, volume: 0.25 },
    { src: sfx.click, frame: 1800, volume: 0.25 },
    { src: sfx.pop, frame: 1860, volume: 0.2 },
    { src: sfx.click, frame: 1920, volume: 0.25 },
    { src: sfx.success, frame: 2040, volume: 0.4 },

    // Results Scene (2160-2640 frames / 72-88s)
    { src: sfx.whoosh, frame: 2160, volume: 0.3 },
    { src: sfx.success, frame: 2400, volume: 0.4 },
    { src: sfx.chime, frame: 2520, volume: 0.35 },

    // Outro Scene (2640-3000 frames / 88-100s)
    { src: sfx.whoosh, frame: 2640, volume: 0.3 },
    { src: sfx.chime, frame: 2700, volume: 0.4 },
    { src: sfx.pop, frame: 2820, volume: 0.25 },

    // Team Info Scene (3000-3090 frames / 100-103s)
    { src: sfx.chime, frame: 3000, volume: 0.35 },
  ];

  return (
    <>
      {soundEffects.map((effect, index) => (
        <Sequence
          key={`sfx-${index}`}
          from={effect.frame}
          durationInFrames={45}
        >
          <SfxTrigger
            src={effect.src}
            volume={effect.volume}
          />
        </Sequence>
      ))}
    </>
  );
};
