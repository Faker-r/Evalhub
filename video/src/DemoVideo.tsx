import { AbsoluteFill, Sequence } from "remotion";
import { IntroScene } from "./scenes/IntroScene";
import { LeaderboardScene } from "./scenes/LeaderboardScene";
import { BenchmarkScene } from "./scenes/BenchmarkScene";
import { SubmitScene } from "./scenes/SubmitScene";
import { ResultsScene } from "./scenes/ResultsScene";
import { OutroScene } from "./scenes/OutroScene";

// Scene timings (in seconds) - total 120s
const SCENES = {
  intro: { start: 0, duration: 15 },         // 0-15s: Logo & tagline
  leaderboard: { start: 15, duration: 25 },  // 15-40s: Leaderboard showcase
  benchmark: { start: 40, duration: 25 },    // 40-65s: Benchmark explorer
  submit: { start: 65, duration: 25 },       // 65-90s: Submission flow
  results: { start: 90, duration: 20 },      // 90-110s: Results dashboard
  outro: { start: 110, duration: 10 },       // 110-120s: Call to action
};

const FPS = 30;

export const DemoVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#09090b" }}>
      {/* Intro Scene */}
      <Sequence
        from={SCENES.intro.start * FPS}
        durationInFrames={SCENES.intro.duration * FPS}
      >
        <IntroScene />
      </Sequence>

      {/* Leaderboard Scene */}
      <Sequence
        from={SCENES.leaderboard.start * FPS}
        durationInFrames={SCENES.leaderboard.duration * FPS}
      >
        <LeaderboardScene />
      </Sequence>

      {/* Benchmark Scene */}
      <Sequence
        from={SCENES.benchmark.start * FPS}
        durationInFrames={SCENES.benchmark.duration * FPS}
      >
        <BenchmarkScene />
      </Sequence>

      {/* Submit Scene */}
      <Sequence
        from={SCENES.submit.start * FPS}
        durationInFrames={SCENES.submit.duration * FPS}
      >
        <SubmitScene />
      </Sequence>

      {/* Results Scene */}
      <Sequence
        from={SCENES.results.start * FPS}
        durationInFrames={SCENES.results.duration * FPS}
      >
        <ResultsScene />
      </Sequence>

      {/* Outro Scene */}
      <Sequence
        from={SCENES.outro.start * FPS}
        durationInFrames={SCENES.outro.duration * FPS}
      >
        <OutroScene />
      </Sequence>
    </AbsoluteFill>
  );
};
