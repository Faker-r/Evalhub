import { AbsoluteFill, Sequence } from "remotion";
import { HookScene } from "./scenes/HookScene";
import { SolutionIntroScene } from "./scenes/SolutionIntroScene";
import { LeaderboardDemoScene } from "./scenes/LeaderboardDemoScene";
import { SubmitEvalScene } from "./scenes/SubmitEvalScene";
import { ResultsScene } from "./scenes/ResultsScene";
import { OutroScene } from "./scenes/OutroScene";
import { TeamInfoScene } from "./scenes/TeamInfoScene";
import { BackgroundMusic, Voiceover, VideoSoundEffects } from "./Audio";

// Scene timings (in seconds) - total ~103s
const FPS = 30;
const SCENES = {
  hook: { start: 0, duration: 18 },           // 0-18s: Problem hook
  solutionIntro: { start: 18, duration: 10 }, // 18-28s: Introduce EvalHub
  leaderboard: { start: 28, duration: 22 },   // 28-50s: Leaderboard demo
  submitEval: { start: 50, duration: 22 },    // 50-72s: Submit evaluation
  results: { start: 72, duration: 16 },       // 72-88s: Results dashboard
  outro: { start: 88, duration: 12 },         // 88-100s: CTA
  teamInfo: { start: 100, duration: 3 },      // 100-103s: Team info
};

export const DemoVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#fefefe" }}>
      {/* Audio tracks */}
      <BackgroundMusic volume={0.2} />
      {/* <Voiceover volume={1} /> */}{/* Uncomment when you have a voiceover recording */}
      <VideoSoundEffects />

      {/* Hook/Problem Scene */}
      <Sequence
        from={SCENES.hook.start * FPS}
        durationInFrames={SCENES.hook.duration * FPS}
      >
        <HookScene />
      </Sequence>

      {/* Solution Introduction */}
      <Sequence
        from={SCENES.solutionIntro.start * FPS}
        durationInFrames={SCENES.solutionIntro.duration * FPS}
      >
        <SolutionIntroScene />
      </Sequence>

      {/* Leaderboard Demo */}
      <Sequence
        from={SCENES.leaderboard.start * FPS}
        durationInFrames={SCENES.leaderboard.duration * FPS}
      >
        <LeaderboardDemoScene />
      </Sequence>

      {/* Submit Evaluation Demo */}
      <Sequence
        from={SCENES.submitEval.start * FPS}
        durationInFrames={SCENES.submitEval.duration * FPS}
      >
        <SubmitEvalScene />
      </Sequence>

      {/* Results Dashboard */}
      <Sequence
        from={SCENES.results.start * FPS}
        durationInFrames={SCENES.results.duration * FPS}
      >
        <ResultsScene />
      </Sequence>

      {/* Outro/CTA */}
      <Sequence
        from={SCENES.outro.start * FPS}
        durationInFrames={SCENES.outro.duration * FPS}
      >
        <OutroScene />
      </Sequence>

      {/* Team Info (required 3s end card) */}
      <Sequence
        from={SCENES.teamInfo.start * FPS}
        durationInFrames={SCENES.teamInfo.duration * FPS}
      >
        <TeamInfoScene />
      </Sequence>
    </AbsoluteFill>
  );
};
