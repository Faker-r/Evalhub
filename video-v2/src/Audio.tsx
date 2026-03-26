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
  // Fade out over last 30 frames of 89s video (2670 frames total)
  const fadeOut = interpolate(frame, [2640, 2670], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
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
  const soundEffects = [
    // Hook Scene (240-780 frames / 8-26s)
    { src: sfx.whoosh, frame: 240, volume: 0.3 },
    { src: sfx.pop, frame: 270, volume: 0.25 },
    { src: sfx.pop, frame: 305, volume: 0.2 },
    { src: sfx.pop, frame: 320, volume: 0.2 },
    { src: sfx.pop, frame: 335, volume: 0.2 },
    { src: sfx.whoosh, frame: 395, volume: 0.3 },
    { src: sfx.pop, frame: 430, volume: 0.25 },
    { src: sfx.whoosh, frame: 640, volume: 0.3 },

    // Solution Intro Scene (780-1080 frames / 26-36s)
    { src: sfx.chime, frame: 780, volume: 0.4 },
    { src: sfx.pop, frame: 880, volume: 0.25 },
    { src: sfx.pop, frame: 900, volume: 0.25 },
    { src: sfx.pop, frame: 920, volume: 0.25 },

    // Leaderboard Scene (1080-1500 frames / 36-50s)
    { src: sfx.whoosh, frame: 1080, volume: 0.3 },
    { src: sfx.pop, frame: 1160, volume: 0.15 },
    { src: sfx.pop, frame: 1190, volume: 0.15 },
    { src: sfx.pop, frame: 1220, volume: 0.15 },
    { src: sfx.click, frame: 1260, volume: 0.35 },

    // Submit Eval Scene (1500-1920 frames / 50-64s)
    { src: sfx.whoosh, frame: 1500, volume: 0.3 },
    { src: sfx.click, frame: 1560, volume: 0.25 },
    { src: sfx.pop, frame: 1620, volume: 0.2 },
    { src: sfx.click, frame: 1680, volume: 0.25 },
    { src: sfx.click, frame: 1800, volume: 0.25 },
    { src: sfx.pop, frame: 1860, volume: 0.2 },
    { src: sfx.click, frame: 1900, volume: 0.25 },

    // Results Scene (1920-2220 frames / 64-74s)
    { src: sfx.whoosh, frame: 1920, volume: 0.3 },
    { src: sfx.success, frame: 2040, volume: 0.4 },
    { src: sfx.chime, frame: 2160, volume: 0.35 },

    // Outro Scene (2220-2580 frames / 74-86s)
    { src: sfx.whoosh, frame: 2220, volume: 0.3 },
    { src: sfx.chime, frame: 2280, volume: 0.4 },
    { src: sfx.pop, frame: 2400, volume: 0.25 },

    // Team Info Scene (2580-2670 frames / 86-89s)
    { src: sfx.chime, frame: 2580, volume: 0.35 },
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
