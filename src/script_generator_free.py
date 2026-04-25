"""Free AI script generation using Groq or Google Gemini."""
import json
import random
from typing import Dict, Optional
from loguru import logger

# Try to import Groq (free, fast)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Try to import Gemini (free)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from src.config_free import GROQ_API_KEY, GEMINI_API_KEY, USE_GROQ, USE_GEMINI, NICHE


class FreeScriptGenerator:
    """Generates scripts using completely free AI APIs."""

    def __init__(self):
        self.niche = NICHE
        self.groq_client = None
        self.gemini_model = None

        if USE_GROQ and GROQ_AVAILABLE:
            self.groq_client = Groq(api_key=GROQ_API_KEY)
            logger.info("Using Groq (free tier) for script generation")
        elif USE_GEMINI and GEMINI_AVAILABLE:
            genai.configure(api_key=GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Using Gemini (free tier) for script generation")
        else:
            logger.warning("No free AI provider configured. Install groq or google-generativeai.")

    def generate_script(self, topic: Optional[str] = None, style: str = "educational", duration: int = 60) -> Dict:
        """Generate script using available free provider."""
        if not topic:
            topic = self._generate_topic()

        logger.info(f"Generating script: {topic}")

        prompt = f"""Create an Instagram Reels script about: {topic}

Style: {style} | Duration: {duration}s | Niche: {self.niche}

Rules:
- Hook must be a pattern-interrupt in first 3 seconds
- Short punchy sentences for voiceover
- Captions: 2-5 words each, 5 captions total
- Visual prompts: specific searchable stock footage terms
- Include 5-8 hashtags

Respond with ONLY valid JSON:
{{
    "topic": "exact topic",
    "hook": "spoken hook text",
    "script": "full voiceover script",
    "captions": ["caption 1", "caption 2", "caption 3", "caption 4", "caption 5"],
    "visual_prompts": ["term1", "term2", "term3", "term4", "term5"],
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
    "cta": "follow/comment call to action"
}}"""

        if self.groq_client:
            return self._generate_with_groq(prompt, topic, style, duration)
        elif self.gemini_model:
            return self._generate_with_gemini(prompt, topic, style, duration)
        else:
            raise RuntimeError("No free AI provider available. Install groq or google-generativeai.")

    def _generate_with_groq(self, prompt: str, topic: str, style: str, duration: int) -> Dict:
        """Use Groq API (free, 1M tokens/day)."""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # Fast, good quality, free
                messages=[
                    {"role": "system", "content": "You are a viral Instagram Reels scriptwriter. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            script_data = json.loads(response.choices[0].message.content)
            script_data["style"] = style
            script_data["target_duration"] = duration
            logger.success(f"Script generated via Groq: {script_data['topic']}")
            return script_data

        except Exception as e:
            logger.error(f"Groq failed: {e}")
            raise

    def _generate_with_gemini(self, prompt: str, topic: str, style: str, duration: int) -> Dict:
        """Use Google Gemini API (free, 60 req/min)."""
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=1500
                )
            )

            # Gemini sometimes wraps JSON in markdown
            text = response.text
            text = text.replace("```json", "").replace("```", "").strip()

            script_data = json.loads(text)
            script_data["style"] = style
            script_data["target_duration"] = duration
            logger.success(f"Script generated via Gemini: {script_data['topic']}")
            return script_data

        except Exception as e:
            logger.error(f"Gemini failed: {e}")
            raise

    def _generate_topic(self) -> str:
        """Generate a trending topic."""
        fallbacks = [
            "5 productivity hacks that saved me 10 hours this week",
            "The morning routine that changed my life",
            "Why successful people wake up at 5AM",
            "AI tools that make you 10x more productive",
            "The 2-minute rule that beats procrastination",
            "How I read 50 books a year with this method",
            "The truth about passive income nobody tells you",
            "3 habits that made me a top performer"
        ]
        return random.choice(fallbacks)


if __name__ == "__main__":
    gen = FreeScriptGenerator()
    script = gen.generate_script()
    print(json.dumps(script, indent=2))
