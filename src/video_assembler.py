"""Assemble final Reels video from stock footage, voiceover, and captions."""
import os
import random
from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger

from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip, CompositeAudioClip
)
from moviepy.video.fx.all import fadein, fadeout

from src.config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, 
    VIDEO_CODEC, AUDIO_CODEC, OUTPUT_DIR, TEMP_DIR
)


class VideoAssembler:
    """Assemble Instagram Reels with professional styling."""

    def __init__(
        self,
        width: int = VIDEO_WIDTH,
        height: int = VIDEO_HEIGHT,
        fps: int = VIDEO_FPS
    ):
        self.width = width
        self.height = height
        self.fps = fps

    def assemble_reel(
        self,
        script_data: Dict,
        stock_clips: List[Path],
        voiceover_path: Path,
        output_filename: Optional[str] = None,
        add_background_music: bool = False,
        music_volume: float = 0.15
    ) -> Path:
        """
        Assemble complete Reel from components.

        Args:
            script_data: Dictionary with captions, hook, etc.
            stock_clips: List of downloaded stock video paths
            voiceover_path: Path to AI-generated voiceover MP3
            output_filename: Optional output filename
            add_background_music: Whether to add subtle background music
            music_volume: Background music volume (0-1)

        Returns:
            Path to final video file
        """
        if not output_filename:
            output_filename = f"reel_{random.randint(10000, 99999)}.mp4"

        output_path = OUTPUT_DIR / output_filename

        try:
            # Load voiceover to determine duration
            voiceover = AudioFileClip(str(voiceover_path))
            target_duration = voiceover.duration

            logger.info(f"Target reel duration: {target_duration:.1f}s")

            # Build B-roll sequence
            b_roll = self._build_b_roll(stock_clips, target_duration)

            # Add voiceover
            b_roll = b_roll.set_audio(voiceover)

            # Generate caption overlays
            caption_clips = self._generate_captions(
                script_data.get("captions", []),
                script_data.get("hook", ""),
                target_duration
            )

            # Build hook overlay (first 3 seconds)
            hook_clip = self._create_hook_overlay(
                script_data.get("hook", ""),
                duration=min(3.5, target_duration * 0.15)
            )

            # Build CTA overlay (last 5 seconds)
            cta_text = script_data.get("cta", "Follow for more tips!")
            cta_clip = self._create_cta_overlay(
                cta_text,
                start_time=target_duration - 5,
                duration=5
            )

            # Composite everything
            layers = [b_roll] + caption_clips
            if hook_clip:
                layers.append(hook_clip)
            if cta_clip:
                layers.append(cta_clip)

            final = CompositeVideoClip(layers, size=(self.width, self.height))
            final = final.set_duration(target_duration)
            final = final.set_fps(self.fps)

            # Add subtle background music if available
            if add_background_music:
                final = self._add_background_music(final, music_volume)

            # Write output
            logger.info(f"Rendering video to {output_path}...")
            final.write_videofile(
                str(output_path),
                codec=VIDEO_CODEC,
                audio_codec=AUDIO_CODEC,
                fps=self.fps,
                preset="fast",  # Use "slow" for better quality in production
                threads=4,
                logger=None  # MoviePy logger is noisy
            )

            # Clean up clips
            voiceover.close()
            b_roll.close()
            for clip in caption_clips:
                clip.close()
            final.close()

            logger.success(f"Reel assembled: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            raise

    def _build_b_roll(self, stock_clips: List[Path], target_duration: float) -> VideoFileClip:
        """Build B-roll sequence from stock clips."""
        if not stock_clips:
            # Fallback: solid color background
            logger.warning("No stock clips provided, using fallback background")
            return ColorClip(
                size=(self.width, self.height),
                color=(15, 15, 20)  # Dark charcoal
            ).set_duration(target_duration)

        processed_clips = []
        clip_duration = target_duration / len(stock_clips)

        for clip_path in stock_clips:
            try:
                clip = VideoFileClip(str(clip_path))

                # Resize to fit 9:16 while maintaining aspect ratio
                clip = self._resize_to_fill(clip, self.width, self.height)

                # Trim or loop to exact duration needed
                if clip.duration > clip_duration:
                    clip = clip.subclip(0, clip_duration)
                elif clip.duration < clip_duration:
                    # Loop if too short
                    n_loops = int(clip_duration / clip.duration) + 1
                    clip = concatenate_videoclips([clip] * n_loops)
                    clip = clip.subclip(0, clip_duration)

                # Add subtle fade transitions
                clip = fadein(clip, 0.5)
                clip = fadeout(clip, 0.5)

                processed_clips.append(clip)

            except Exception as e:
                logger.warning(f"Failed to process clip {clip_path}: {e}")
                continue

        if not processed_clips:
            return ColorClip(
                size=(self.width, self.height),
                color=(15, 15, 20)
            ).set_duration(target_duration)

        # Concatenate all clips
        final_b_roll = concatenate_videoclips(processed_clips, method="compose")

        # Ensure exact duration
        if final_b_roll.duration > target_duration:
            final_b_roll = final_b_roll.subclip(0, target_duration)
        elif final_b_roll.duration < target_duration:
            # Extend last frame
            last_frame = final_b_roll.to_ImageClip(final_b_roll.duration - 0.1)
            last_frame = last_frame.set_duration(target_duration - final_b_roll.duration)
            final_b_roll = concatenate_videoclips([final_b_roll, last_frame])

        return final_b_roll

    def _resize_to_fill(
        self, 
        clip: VideoFileClip, 
        target_w: int, 
        target_h: int
    ) -> VideoFileClip:
        """Resize clip to fill target dimensions (crop if necessary)."""
        clip_w, clip_h = clip.size

        # Calculate scale factors
        scale_w = target_w / clip_w
        scale_h = target_h / clip_h
        scale = max(scale_w, scale_h)

        new_w = int(clip_w * scale)
        new_h = int(clip_h * scale)

        clip = clip.resize(newsize=(new_w, new_h))

        # Center crop
        x_center = new_w // 2
        y_center = new_h // 2
        x1 = x_center - target_w // 2
        y1 = y_center - target_h // 2

        clip = clip.crop(x1=x1, y1=y1, width=target_w, height=target_h)
        return clip

    def _generate_captions(
        self, 
        captions: List[str], 
        hook: str,
        total_duration: float
    ) -> List[TextClip]:
        """Generate animated caption text overlays."""
        if not captions:
            return []

        caption_clips = []
        segment_duration = total_duration / (len(captions) + 1)

        # Style configuration
        font_size = 72
        stroke_width = 3

        for i, text in enumerate(captions):
            start_time = (i + 1) * segment_duration
            duration = segment_duration

            # Main caption text
            txt_clip = TextClip(
                text.upper(),
                fontsize=font_size,
                color="white",
                stroke_color="black",
                stroke_width=stroke_width,
                font="Arial-Bold",
                method="caption",
                size=(self.width - 100, None),
                align="center",
                interline=-10
            )

            # Position in lower third
            txt_clip = txt_clip.set_position(("center", self.height - 400))
            txt_clip = txt_clip.set_start(start_time).set_duration(duration)

            # Add pop-in effect by scaling (simulated with size changes)
            # MoviePy doesn't support easy scale animation, so we use fade
            txt_clip = fadein(txt_clip, 0.2)
            txt_clip = fadeout(txt_clip, 0.2)

            caption_clips.append(txt_clip)

        return caption_clips

    def _create_hook_overlay(self, hook_text: str, duration: float) -> Optional[TextClip]:
        """Create attention-grabbing hook overlay for first few seconds."""
        if not hook_text or duration <= 0:
            return None

        # Split hook into words for dramatic effect
        words = hook_text.split()[:6]  # Max 6 words
        display_text = " ".join(words).upper()

        hook_clip = TextClip(
            display_text,
            fontsize=90,
            color="#FFD700",  # Gold color for attention
            stroke_color="black",
            stroke_width=4,
            font="Arial-Bold",
            method="caption",
            size=(self.width - 80, None),
            align="center"
        )

        hook_clip = hook_clip.set_position("center")
        hook_clip = hook_clip.set_start(0).set_duration(duration)
        hook_clip = fadein(hook_clip, 0.3)
        hook_clip = fadeout(hook_clip, 0.5)

        return hook_clip

    def _create_cta_overlay(
        self, 
        cta_text: str, 
        start_time: float, 
        duration: float
    ) -> Optional[TextClip]:
        """Create call-to-action overlay for end of video."""
        if not cta_text or duration <= 0:
            return None

        cta_clip = TextClip(
            cta_text.upper(),
            fontsize=64,
            color="white",
            stroke_color="black",
            stroke_width=3,
            font="Arial-Bold",
            method="caption",
            size=(self.width - 100, None),
            align="center"
        )

        # Position above center
        cta_clip = cta_clip.set_position(("center", self.height // 2 - 100))
        cta_clip = cta_clip.set_start(start_time).set_duration(duration)
        cta_clip = fadein(cta_clip, 0.5)

        return cta_clip

    def _add_background_music(
        self, 
        video_clip: CompositeVideoClip, 
        volume: float
    ) -> CompositeVideoClip:
        """Add subtle background music (placeholder implementation)."""
        # In production, you would load a royalty-free music file
        # For now, this is a stub that returns the original clip
        logger.info("Background music placeholder (no music file provided)")
        return video_clip


if __name__ == "__main__":
    # Test with dummy data
    assembler = VideoAssembler()
    print("VideoAssembler initialized successfully")
