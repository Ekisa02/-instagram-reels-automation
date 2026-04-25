"""AI-powered script generation for Instagram Reels."""
import json
import random
from typing import Dict, List, Optional
from openai import OpenAI
from loguru import logger

from src.config import OPENAI_API_KEY, NICHE


class ScriptGenerator:
    """Generates viral-style Reels scripts using OpenAI GPT-4."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or OPENAI_API_KEY)
        self.niche = NICHE

    def generate_script(
        self, 
        topic: Optional[str] = None,
        style: str = "educational",
        duration: int = 60
    ) -> Dict:
        """
        Generate a complete Reels script with hooks, captions, and visual prompts.

        Args:
            topic: Content topic (auto-generated if None)
            style: Content style (educational, motivational, storytelling, trending)
            duration: Target video duration in seconds

        Returns:
            Dictionary containing hook, script, captions, visual_prompts, hashtags
        """
        if not topic:
            topic = self._generate_topic()

        logger.info(f"Generating script for topic: {topic} (style: {style})")

        system_prompt = """You are an expert Instagram Reels content strategist who creates viral, engaging short-form video scripts.

Rules:
- First 3 seconds MUST be a pattern-interrupt hook
- Use short, punchy sentences optimized for voiceover
- Each caption overlay should be 2-5 words maximum
- Visual prompts should describe specific, searchable stock footage scenes
- Include 5-8 relevant hashtags
- Total script should be readable in {duration} seconds at natural pace"""

        user_prompt = f"""Create an Instagram Reels script about: {topic}

Style: {style}
Target Duration: {duration} seconds
Niche: {self.niche}

Respond with valid JSON only:
{{
    "topic": "exact topic used",
    "hook": "Attention-grabbing first 3 seconds (spoken)",
    "script": "Full voiceover script, 60-90 seconds when read naturally. Use short sentences.",
    "captions": [
        "caption 1 - 3 words",
        "caption 2 - 3 words",
        "caption 3 - 3 words",
        "caption 4 - 3 words",
        "caption 5 - 3 words"
    ],
    "visual_prompts": [
        "specific stock video search term 1",
        "specific stock video search term 2",
        "specific stock video search term 3",
        "specific stock video search term 4",
        "specific stock video search term 5"
    ],
    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5"],
    "cta": "Call-to-action for viewers (comment, follow, save)"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
                max_tokens=1500
            )

            script_data = json.loads(response.choices[0].message.content)
            script_data["style"] = style
            script_data["target_duration"] = duration

            logger.success(f"Script generated: {script_data['topic']}")
            return script_data

        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise

    def _generate_topic(self) -> str:
        """Generate a trending topic based on niche."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": f"Generate one specific, trending Instagram Reels topic for the {self.niche} niche. Respond with just the topic, no explanation. Make it attention-grabbing and specific."
                }],
                temperature=0.9,
                max_tokens=50
            )
            topic = response.choices[0].message.content.strip().strip('"')
            return topic
        except Exception:
            # Fallback topics
            fallbacks = [
                "5 productivity hacks that saved me 10 hours this week",
                "The morning routine that changed my life",
                "Why successful people wake up at 5AM",
                "AI tools that make you 10x more productive",
                "The 2-minute rule that beats procrastination"
            ]
            return random.choice(fallbacks)


if __name__ == "__main__":
    gen = ScriptGenerator()
    script = gen.generate_script()
    print(json.dumps(script, indent=2))
