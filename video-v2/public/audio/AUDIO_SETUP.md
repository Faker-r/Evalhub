# Audio Setup for EvalHub Demo Video

## Directory Structure

Place your audio files in `public/audio/`:

```
public/audio/
├── background-music.mp3    # Background music track (~103 seconds)
├── voiceover.mp3           # Voiceover narration (~103 seconds)
└── sfx/                    # Sound effects
    ├── whoosh.mp3          # Scene transitions (0.5-1s)
    ├── pop.mp3             # Element appearances (0.2-0.5s)
    ├── click.mp3           # UI interactions (0.1-0.3s)
    ├── success.mp3         # Completion/celebration (1-2s)
    ├── typing.mp3          # Typing/progress effects (1-2s)
    └── chime.mp3           # Notifications/reveals (0.5-1s)
```

## Audio Timing

The video is 103 seconds (3090 frames at 30fps). Here's the scene breakdown for voiceover timing:

| Scene | Time | Frames | Suggested Voiceover |
|-------|------|--------|---------------------|
| Hook (Phase 1) | 0-5s | 0-150 | "You use AI every day. Chatbots, search, writing, creating..." |
| Hook (Phase 2) | 5-13s | 150-400 | "But did you know... the same AI model can give completely different results depending on who runs it?" |
| Hook (Phase 3) | 13-18s | 400-540 | "So how do you know which one to trust?" |
| Solution Intro | 18-28s | 540-840 | "Meet EvalHub. Finally see how AI really compares. Open, transparent, rigorous testing to help you make better decisions." |
| Leaderboard | 28-50s | 840-1500 | "Compare AI models side by side. See real benchmark scores. Filter by dataset, metric, or provider to find exactly what you need." |
| Submit Eval | 50-72s | 1500-2160 | "Run your own evaluations in just 4 simple steps. Select your dataset, configure options, pick your models, and submit." |
| Results | 72-88s | 2160-2640 | "Watch results in real-time. See exactly how your AI performs with detailed metrics and sample previews." |
| Outro | 88-100s | 2640-3000 | "Make better AI decisions. Benchmarking is clarity. Try EvalHub free today at evalhub.io" |
| Team Info | 100-103s | 3000-3090 | (Music only, no voiceover) |

## Recommended Royalty-Free Audio Sources

### Background Music
- [Pixabay Music](https://pixabay.com/music/) - Free for commercial use
- [Free Music Archive](https://freemusicarchive.org/) - Various licenses
- [Uppbeat](https://uppbeat.io/) - Free with attribution

Look for: upbeat, tech, corporate, inspiring (100-120 BPM works well)

### Sound Effects
- [Pixabay Sound Effects](https://pixabay.com/sound-effects/)
- [Freesound](https://freesound.org/)
- [Zapsplat](https://www.zapsplat.com/)

## Volume Levels

The audio is configured with these default volumes:
- Background music: 25% (0.25)
- Voiceover: 100% (1.0)
- Sound effects: 20-50% (varies by effect)

Adjust in `src/Audio.tsx` if needed.

## Disabling Audio

To render without audio (while you don't have files yet):

1. Comment out the audio components in `src/DemoVideo.tsx`:
```tsx
{/* <BackgroundMusic volume={0.25} /> */}
{/* <Voiceover volume={1} /> */}
{/* <VideoSoundEffects /> */}
```

Or create empty placeholder files to prevent errors.
