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

# Try to import Gemini (free) - use google-genai if available, fallback to deprecated
try:
    from google import genai
    GEMINI_AVAILABLE = True
    GEMINI_MODE = "new"
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        GEMINI_MODE = "old"
    except ImportError:
        GEMINI_AVAILABLE = False
        GEMINI_MODE = None

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
            if GEMINI_MODE == "new":
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                self.gemini_model = "gemini-1.5-flash"
            else:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Using Gemini (free tier) for script generation")
        else:
            logger.warning("No free AI provider configured. Install groq or google-genai.")

    def generate_script(self, topic: Optional[str] = None, style: str = "educational", duration: int = 60) -> Dict:
        """Generate script using available free provider."""
        if not topic:
            topic = self._generate_topic()

        logger.info(f"Generating script: {topic}")

        system_prompt = """You are an expert Instagram Reels content strategist who creates viral, engaging short-form video scripts.

Rules:
- First 3 seconds MUST be a pattern-interrupt hook
- Use short, punchy sentences optimized for voiceover
- Each caption overlay should be 2-5 words maximum
- Visual prompts should describe specific, searchable stock footage scenes
- Include 5-8 relevant hashtags
- Total script should be readable in the target duration at natural pace"""

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

        if self.groq_client:
            return self._generate_with_groq(system_prompt, user_prompt, topic, style, duration)
        elif self.gemini_model:
            return self._generate_with_gemini(system_prompt, user_prompt, topic, style, duration)
        else:
            raise RuntimeError("No free AI provider available. Install groq or google-genai.")

    def _generate_with_groq(self, system_prompt: str, user_prompt: str, topic: str, style: str, duration: int) -> Dict:
        """Use Groq API (free, 1M tokens/day)."""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
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

    def _generate_with_gemini(self, system_prompt: str, user_prompt: str, topic: str, style: str, duration: int) -> Dict:
        """Use Google Gemini API (free, 60 req/min)."""
        try:
            if GEMINI_MODE == "new":
                response = self.gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=f"{system_prompt}

{user_prompt}",
                    config=genai.types.GenerateContentConfig(
                        temperature=0.8,
                        max_output_tokens=1500
                    )
                )
                text = response.text
            else:
                response = self.gemini_model.generate_content(
                    f"{system_prompt}

{user_prompt}",
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.8,
                        max_output_tokens=1500
                    )
                )
                text = response.text

            # Gemini sometimes wraps JSON in markdown
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
