import { Composition } from "remotion";
import { DemoVideo } from "./DemoVideo";

// 89 seconds at 30 fps = 2670 frames
const FPS = 30;
const DURATION_SECONDS = 89;
const TOTAL_FRAMES = FPS * DURATION_SECONDS;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="DemoVideo"
        component={DemoVideo}
        durationInFrames={TOTAL_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{}}
      />
    </>
  );
};
