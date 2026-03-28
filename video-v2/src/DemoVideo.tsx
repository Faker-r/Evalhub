import { AbsoluteFill, Sequence } from "remotion";
import { BillboardCascadeScene } from "./scenes/BillboardCascadeScene";
import { HookScene } from "./scenes/HookScene";
import { SolutionIntroScene } from "./scenes/SolutionIntroScene";
import { LeaderboardDemoScene } from "./scenes/LeaderboardDemoScene";
import { SubmitEvalScene } from "./scenes/SubmitEvalScene";
import { ResultsScene } from "./scenes/ResultsScene";
import { OutroScene } from "./scenes/OutroScene";
import { TeamInfoScene } from "./scenes/TeamInfoScene";
import { BackgroundMusic, Voiceover, VideoSoundEffects } from "./Audio";

// Scene timings (in seconds) - total 28s
const FPS = 30;
const SCENES = {
  cascade: { start: 0, duration: 8 },         // 0-8s:   Billboard cascade
  hook: { start: 8, duration: 11 },           // 8-19s:  Problem hook
  solutionIntro: { start: 19, duration: 6 },  // 19-25s: Introduce EvalHub
  // leaderboard: { start: 36, duration: 14 },   // 36-50s: Leaderboard demo
  // submitEval: { start: 50, duration: 14 },    // 50-64s: Submit evaluation
  // results: { start: 64, duration: 10 },       // 64-74s: Results dashboard
  // outro: { start: 74, duration: 12 },         // 74-86s: CTA
  teamInfo: { start: 25, duration: 3 },       // 25-28s: Team info
};

export const DemoVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#fefefe" }}>
      {/* Audio tracks */}
      {/* <BackgroundMusic volume={0.2} /> */}
      {/* <Voiceover volume={1} /> */}{/* Uncomment when you have a voiceover recording */}
      <VideoSoundEffects />

      {/* Billboard Cascade Opening */}
      <Sequence
        from={SCENES.cascade.start * FPS}
        durationInFrames={SCENES.cascade.duration * FPS}
      >
        <BillboardCascadeScene />
      </Sequence>

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
      {/* <Sequence
        from={SCENES.leaderboard.start * FPS}
        durationInFrames={SCENES.leaderboard.duration * FPS}
      >
        <LeaderboardDemoScene />
      </Sequence> */}

      {/* Submit Evaluation Demo */}
      {/* <Sequence
        from={SCENES.submitEval.start * FPS}
        durationInFrames={SCENES.submitEval.duration * FPS}
      >
        <SubmitEvalScene />
      </Sequence> */}

      {/* Results Dashboard */}
      {/* <Sequence
        from={SCENES.results.start * FPS}
        durationInFrames={SCENES.results.duration * FPS}
      >
        <ResultsScene />
      </Sequence> */}

      {/* Outro/CTA */}
      {/* <Sequence
        from={SCENES.outro.start * FPS}
        durationInFrames={SCENES.outro.duration * FPS}
      >
        <OutroScene />
      </Sequence> */}

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
