---
name: remotion-best-practices
description: "Best practices and domain-specific knowledge for building programmatic videos using Remotion (React-based video framework). Covers scaffolding, rendering, and handling multimedia assets."
---

# Remotion Best Practices

**Domain**: frontend / video-engineering  
**Status**: Stable  

## When to use
Use this skill whenever you are dealing with Remotion code to obtain the domain-specific knowledge.

## New project setup
When in an empty folder or workspace with no existing Remotion project, scaffold one using:
```bash
npx create-video@latest --yes --blank --no-tailwind my-video
```
Replace `my-video` with a suitable project name.

## Starting preview
Start the Remotion Studio to preview a video:
```bash
npx remotion studio
```

## Optional: one-frame render check
You can render a single frame with the CLI to sanity-check layout, colors, or timing.
Skip it for trivial edits, pure refactors, or when you already have enough confidence from Studio or prior renders.
```bash
npx remotion still [composition-id] --scale=0.25 --frame=30
```
*At 30 fps, `--frame=30` is the one-second mark (`--frame` is zero-based).*

## Core Guidelines & Capabilities

When working with Remotion, adhere to these conceptual guidelines. Load the specific local markdown files in `./rules/` for detailed code examples and implementations:

- **3D Content**: Read `./rules/3d.md` for using Three.js and React Three Fiber.
- **Animations**: Read `./rules/animations.md` for fundamental animation skills.
- **Assets**: Read `./rules/assets.md` for importing images, videos, audio, and fonts.
- **Audio**: Read `./rules/audio.md` for importing, trimming, volume, speed, and pitch.
- **Dynamic Metadata**: Read `./rules/calculate-metadata.md` to dynamically set composition duration, dimensions, and props.
- **Can Decode**: Read `./rules/can-decode.md` to check if a video can be decoded by the browser.
- **Charts**: Read `./rules/charts.md` for data visualization patterns (bar, pie, line, stock charts).
- **Compositions**: Read `./rules/compositions.md` for defining compositions, stills, folders, and default props.
- **Extract Frames**: Read `./rules/extract-frames.md` to extract frames from videos.
- **FFmpeg**: Read `./rules/ffmpeg.md` for advanced video operations using FFmpeg.
- **Fonts**: Read `./rules/fonts.md` for loading Google Fonts and local fonts.
- **Media Information**: Read `./rules/get-audio-duration.md`, `./rules/get-video-dimensions.md`, and `./rules/get-video-duration.md`.
- **GIFs**: Read `./rules/gifs.md` for displaying GIFs synchronized with Remotion's timeline.
- **Images**: Read `./rules/images.md` for embedding images.
- **Light Leaks**: Read `./rules/light-leaks.md` for overlay effects.
- **Lottie**: Read `./rules/lottie.md` for embedding Lottie animations.
- **Maps**: Read `./rules/maps.md` to add and animate maps using Mapbox.
- **Measuring DOM & Text**: Read `./rules/measuring-dom-nodes.md` and `./rules/measuring-text.md`.
- **Parameters**: Read `./rules/parameters.md` to make videos parametrizable using Zod schemas.
- **Sequencing & Timing**: Read `./rules/sequencing.md` and `./rules/timing.md`.
- **SFX**: Read `./rules/sfx.md` for sound effects.
- **Silence Detection**: Read `./rules/silence-detection.md` for adaptive silence detection.
- **Subtitles**: Read `./rules/subtitles.md` and `./rules/display-captions.md` for handling captions.
- **Tailwind**: Read `./rules/tailwind.md` for using TailwindCSS in Remotion.
- **Text Animations**: Read `./rules/text-animations.md` for typography animation patterns.
- **Transitions**: Read `./rules/transitions.md` for scene transition patterns.
- **Transparent Videos**: Read `./rules/transparent-videos.md` for rendering videos with transparency.
- **Trimming**: Read `./rules/trimming.md` to cut beginnings or ends of animations.
- **Videos**: Read `./rules/videos.md` for embedding videos, looping, and pitch adjustments.
- **Voiceover**: Read `./rules/voiceover.md` for adding AI-generated voiceover.

*Note: All referenced rules are stored securely within the local `./rules/` directory to ensure complete intranet and offline compatibility.*