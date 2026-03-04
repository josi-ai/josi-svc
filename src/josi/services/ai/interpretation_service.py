"""
AI-powered interpretation service for astrological charts.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json
import asyncio
from enum import Enum

import structlog
from openai import AsyncOpenAI
import anthropic
from sqlalchemy import text as sa_text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer

from josi.core.config import settings
from josi.models.chart_model import InterpretationEmbedding

logger = structlog.get_logger(__name__)


class InterpretationStyle(str, Enum):
    """Interpretation style preferences."""
    BALANCED = "balanced"
    PSYCHOLOGICAL = "psychological"
    SPIRITUAL = "spiritual"
    PRACTICAL = "practical"
    PREDICTIVE = "predictive"


class AIProvider(str, Enum):
    """AI provider options."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


ASTROLOGY_SYSTEM_PROMPT = """You are an expert astrologer with deep knowledge of multiple astrological systems including Vedic, Western, Chinese, Hellenistic, Mayan, and Celtic astrology. You provide insightful, compassionate, and nuanced interpretations that empower people to understand themselves better.

Your interpretations should:
1. Be specific to the chart data provided, not generic
2. Consider the cultural context of the astrological system being used
3. Balance traditional interpretations with modern psychological insights
4. Avoid fatalistic predictions - emphasize free will and personal growth
5. Highlight both challenges and opportunities
6. Use clear, accessible language while maintaining depth
7. Incorporate relevant astrological terminology appropriately
8. Consider the interconnections between different chart elements

Remember that astrology is a tool for self-understanding and growth, not deterministic prediction."""


class AIInterpretationService:
    """Generate AI-powered astrological interpretations."""

    def __init__(self):
        # Initialize AI clients
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None

        # Initialize sentence encoder for embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    async def generate_interpretation(
        self,
        chart_data: Dict[str, Any],
        question: str,
        db: Optional[AsyncSession] = None,
        user_context: Optional[Dict] = None,
        style: InterpretationStyle = InterpretationStyle.BALANCED,
        provider: Optional[AIProvider] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered chart interpretation."""
        try:
            # Search for similar interpretations if DB session is available
            similar_interpretations = []
            if db:
                similar_interpretations = await self._search_similar_interpretations(
                    db, chart_data, question
                )

            # Build context-aware prompt
            prompt = self._build_interpretation_prompt(
                chart_data=chart_data,
                question=question,
                user_context=user_context,
                similar_interpretations=similar_interpretations,
                style=style
            )

            # Determine AI provider
            if not provider:
                provider = AIProvider.OPENAI if self.openai_client else AIProvider.ANTHROPIC

            # Generate interpretation
            if provider == AIProvider.OPENAI and self.openai_client:
                response_text = await self._generate_openai_response(prompt)
            elif provider == AIProvider.ANTHROPIC and self.anthropic_client:
                response_text = await self._generate_anthropic_response(prompt)
            else:
                raise ValueError(f"AI provider {provider} is not configured")

            # Store interpretation for future reference
            if db:
                await self._store_interpretation(db, chart_data, question, response_text)

            # Calculate confidence and extract insights
            confidence = self._calculate_confidence(response_text, similar_interpretations)
            follow_up_questions = await self._generate_follow_up_questions(
                chart_data, question, response_text
            )

            return {
                "interpretation": response_text,
                "confidence": confidence,
                "sources": self._extract_sources(similar_interpretations),
                "follow_up_questions": follow_up_questions,
                "style": style.value,
                "provider": provider.value,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(
                "Failed to generate interpretation",
                error=str(e),
                question=question,
                style=style.value
            )
            raise

    def _build_interpretation_prompt(
        self,
        chart_data: Dict,
        question: str,
        user_context: Optional[Dict],
        similar_interpretations: List[Dict],
        style: InterpretationStyle
    ) -> str:
        """Build a comprehensive prompt for the AI model."""
        # Extract key chart information
        chart_type = chart_data.get("system", "western")
        planets = chart_data.get("planets", {})
        houses = chart_data.get("houses", [])
        aspects = chart_data.get("aspects", [])

        # Style-specific instructions
        style_instructions = {
            InterpretationStyle.BALANCED: "Provide a balanced interpretation considering both traditional and modern perspectives.",
            InterpretationStyle.PSYCHOLOGICAL: "Focus on psychological insights, unconscious patterns, and personal growth opportunities.",
            InterpretationStyle.SPIRITUAL: "Emphasize spiritual lessons, karmic patterns, and soul evolution.",
            InterpretationStyle.PRACTICAL: "Focus on practical applications, concrete advice, and real-world implications.",
            InterpretationStyle.PREDICTIVE: "Discuss timing, cycles, and potential future developments while emphasizing free will."
        }

        prompt = f"""Chart Type: {chart_type.upper()}

PLANETARY POSITIONS:
{self._format_planets(planets)}

HOUSE CUSPS:
{self._format_houses(houses)}

MAJOR ASPECTS:
{self._format_aspects(aspects)}

{self._format_special_features(chart_data)}

USER QUESTION: {question}

{f"USER CONTEXT: {json.dumps(user_context)}" if user_context else ""}

INTERPRETATION STYLE: {style_instructions.get(style, "")}

{self._format_similar_insights(similar_interpretations)}

Please provide a detailed, insightful interpretation addressing the user's question. Be specific to this chart and avoid generic statements."""

        return prompt

    def _format_planets(self, planets: Dict) -> str:
        """Format planetary positions for the prompt."""
        lines = []
        for planet, data in planets.items():
            sign = data.get("sign", "Unknown")
            degree = data.get("longitude", 0) % 30
            house = data.get("house", "?")
            retrograde = " (R)" if data.get("is_retrograde", False) else ""

            lines.append(f"{planet}: {sign} {degree:.2f}° in House {house}{retrograde}")

        return "\n".join(lines)

    def _format_houses(self, houses: List) -> str:
        """Format house cusps for the prompt."""
        if not houses:
            return "House information not available"

        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

        lines = []
        for i, cusp in enumerate(houses[:12]):
            sign_index = int(cusp / 30)
            degree = cusp % 30
            lines.append(f"House {i+1}: {signs[sign_index]} {degree:.2f}°")

        return "\n".join(lines)

    def _format_aspects(self, aspects: List) -> str:
        """Format planetary aspects for the prompt."""
        if not aspects:
            return "No major aspects found"

        lines = []
        for aspect in aspects[:15]:  # Limit to 15 most important
            lines.append(
                f"{aspect['planet1']} {aspect['aspect']} {aspect['planet2']} "
                f"(orb: {aspect['orb']}°)"
            )

        return "\n".join(lines)

    def _format_special_features(self, chart_data: Dict) -> str:
        """Format system-specific features."""
        features = []

        # Vedic features
        if "panchang" in chart_data:
            panchang = chart_data["panchang"]
            features.append(f"VEDIC FEATURES:\nNakshatra: {panchang.get('nakshatra', 'Unknown')}")
            features.append(f"Tithi: {panchang.get('tithi', 'Unknown')}")
            features.append(f"Yoga: {panchang.get('yoga', 'Unknown')}")

        # Chinese features
        if "pillars" in chart_data:
            features.append(f"CHINESE FEATURES:\n{json.dumps(chart_data['pillars'], indent=2)}")

        # Hellenistic features
        if "sect" in chart_data:
            features.append(f"HELLENISTIC FEATURES:\nSect: {chart_data['sect']}")
            if "lots" in chart_data:
                features.append(f"Lot of Fortune: {chart_data['lots'].get('fortune', {}).get('sign', 'Unknown')}")

        return "\n\n".join(features) if features else ""

    def _format_similar_insights(self, similar_interpretations: List[Dict]) -> str:
        """Format insights from similar charts."""
        if not similar_interpretations:
            return ""

        insights = ["INSIGHTS FROM SIMILAR CHARTS:"]
        for interp in similar_interpretations[:3]:
            insights.append(f"- {interp.get('key_insight', '')}")

        return "\n".join(insights)

    async def _generate_openai_response(self, prompt: str) -> str:
        """Generate response using OpenAI."""
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": ASTROLOGY_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content

    async def _generate_anthropic_response(self, prompt: str) -> str:
        """Generate response using Anthropic Claude."""
        response = await self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1500,
            temperature=0.7,
            system=ASTROLOGY_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text

    async def _search_similar_interpretations(
        self,
        db: AsyncSession,
        chart_data: Dict,
        question: str
    ) -> List[Dict]:
        """Search for similar interpretations using pgvector cosine similarity."""
        try:
            # Create search embedding
            search_text = f"{question} {self._extract_chart_features(chart_data)}"
            embedding = self.encoder.encode(search_text).tolist()

            # Search using pgvector cosine distance (<=> operator)
            result = await db.execute(
                sa_text("""
                    SELECT chart_features, question, interpretation, chart_type,
                           1 - (embedding <=> :query_embedding::vector) AS score
                    FROM interpretation_embedding
                    WHERE is_deleted = false
                    ORDER BY embedding <=> :query_embedding::vector
                    LIMIT 5
                """),
                {"query_embedding": str(embedding)}
            )
            rows = result.mappings().all()

            similar = []
            for row in rows:
                if row["score"] > 0.7:  # Similarity threshold
                    similar.append({
                        "score": row["score"],
                        "question": row["question"],
                        "key_insight": self._extract_key_insight(row["interpretation"]),
                        "chart_similarity": row["chart_features"]
                    })

            return similar

        except Exception as e:
            logger.warning("Failed to search similar interpretations", error=str(e))
            return []

    def _extract_chart_features(self, chart_data: Dict) -> str:
        """Extract key features from chart for similarity matching."""
        features = []

        # Sun, Moon, Ascendant signs (the "big three")
        planets = chart_data.get("planets", {})
        if "Sun" in planets:
            features.append(f"Sun in {planets['Sun'].get('sign', '')}")
        if "Moon" in planets:
            features.append(f"Moon in {planets['Moon'].get('sign', '')}")

        # Major aspects
        aspects = chart_data.get("aspects", [])
        for aspect in aspects[:5]:
            features.append(f"{aspect['planet1']} {aspect['aspect']} {aspect['planet2']}")

        return " ".join(features)

    def _extract_key_insight(self, interpretation: str) -> str:
        """Extract the most important insight from an interpretation."""
        # Simple extraction - take first substantial sentence
        sentences = interpretation.split(". ")
        for sentence in sentences:
            if len(sentence) > 50:
                return sentence + "."
        return interpretation[:150] + "..."

    async def _store_interpretation(
        self,
        db: AsyncSession,
        chart_data: Dict,
        question: str,
        interpretation: str
    ) -> None:
        """Store interpretation in PostgreSQL with pgvector embedding."""
        try:
            # Create content hash for upsert
            chart_hash = hashlib.md5(
                json.dumps(chart_data, sort_keys=True).encode()
            ).hexdigest()[:16]
            question_hash = hashlib.md5(question.encode()).hexdigest()[:16]
            content_hash = f"{chart_hash}_{question_hash}"

            # Create embedding
            embed_text = f"{question} {interpretation}"
            embedding = self.encoder.encode(embed_text).tolist()

            chart_features = self._extract_chart_features(chart_data)
            chart_type = chart_data.get("system", "unknown")

            # Upsert using ON CONFLICT
            stmt = pg_insert(InterpretationEmbedding).values(
                embedding=embedding,
                chart_features=chart_features,
                question=question,
                interpretation=interpretation,
                chart_type=chart_type,
                content_hash=content_hash,
                organization_id=chart_data.get("organization_id"),
            ).on_conflict_do_update(
                index_elements=["content_hash"],
                set_={
                    "embedding": embedding,
                    "interpretation": interpretation,
                    "chart_features": chart_features,
                    "updated_at": datetime.utcnow(),
                }
            )
            await db.execute(stmt)
            await db.commit()

        except Exception as e:
            logger.warning("Failed to store interpretation", error=str(e))

    def _calculate_confidence(
        self,
        interpretation: str,
        similar_interpretations: List[Dict]
    ) -> float:
        """Calculate confidence score for the interpretation."""
        base_confidence = 0.7

        # Increase confidence if we have similar interpretations
        if similar_interpretations:
            avg_similarity = sum(s["score"] for s in similar_interpretations) / len(similar_interpretations)
            base_confidence += avg_similarity * 0.2

        # Increase confidence based on interpretation length and detail
        if len(interpretation) > 500:
            base_confidence += 0.05

        if len(interpretation.split(". ")) > 5:
            base_confidence += 0.05

        return min(base_confidence, 0.95)

    async def _generate_follow_up_questions(
        self,
        chart_data: Dict,
        original_question: str,
        interpretation: str
    ) -> List[str]:
        """Generate relevant follow-up questions."""
        # Simple rule-based generation for now
        questions = []

        planets = chart_data.get("planets", {})

        # Based on prominent placements
        if "Moon" in planets:
            moon_sign = planets["Moon"].get("sign", "")
            questions.append(f"How does my Moon in {moon_sign} influence my emotional patterns?")

        if "aspects" in chart_data and chart_data["aspects"]:
            aspect = chart_data["aspects"][0]
            questions.append(
                f"What does the {aspect['aspect']} between {aspect['planet1']} "
                f"and {aspect['planet2']} mean for my life?"
            )

        # Based on chart type
        if chart_data.get("system") == "vedic" and "dasha" in chart_data:
            questions.append("What can I expect during my current Dasha period?")

        # Generic but relevant
        questions.append("What are my biggest strengths according to this chart?")
        questions.append("What life areas should I focus on for growth?")

        return questions[:3]  # Return top 3

    async def generate_neural_pathway_questions(
        self,
        chart_data: Dict,
        previous_responses: List[Dict],
        focus_area: Optional[str] = None
    ) -> List[Dict]:
        """Generate psychological self-awareness questions based on chart."""
        # Extract psychological indicators
        psych_indicators = self._extract_psychological_indicators(chart_data)

        # Analyze response patterns
        response_patterns = self._analyze_response_patterns(previous_responses)

        # Generate questions using AI if available
        if self.openai_client or self.anthropic_client:
            questions = await self._generate_ai_questions(
                psych_indicators,
                response_patterns,
                focus_area
            )
        else:
            # Fallback to rule-based generation
            questions = self._generate_rule_based_questions(
                psych_indicators,
                focus_area
            )

        return questions

    def _extract_psychological_indicators(self, chart_data: Dict) -> Dict:
        """Extract psychological indicators from chart."""
        indicators = {
            "emotional_nature": [],
            "communication_style": [],
            "relationship_patterns": [],
            "career_drives": [],
            "shadow_aspects": []
        }

        planets = chart_data.get("planets", {})

        # Moon placement - emotional nature
        if "Moon" in planets:
            moon = planets["Moon"]
            indicators["emotional_nature"].append({
                "placement": f"Moon in {moon.get('sign', '')}",
                "theme": "emotional security needs"
            })

        # Mercury - communication
        if "Mercury" in planets:
            mercury = planets["Mercury"]
            indicators["communication_style"].append({
                "placement": f"Mercury in {mercury.get('sign', '')}",
                "theme": "thinking and communication patterns"
            })

        # Venus - relationships
        if "Venus" in planets:
            venus = planets["Venus"]
            indicators["relationship_patterns"].append({
                "placement": f"Venus in {venus.get('sign', '')}",
                "theme": "love language and values"
            })

        return indicators

    def _analyze_response_patterns(self, previous_responses: List[Dict]) -> Dict:
        """Analyze patterns in user's previous responses."""
        patterns = {
            "recurring_themes": [],
            "avoidance_areas": [],
            "growth_edges": []
        }

        # Simple analysis for now
        if previous_responses:
            # Count theme mentions
            theme_counts = {}
            for response in previous_responses:
                for theme in response.get("themes", []):
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1

            # Identify recurring themes
            patterns["recurring_themes"] = [
                theme for theme, count in theme_counts.items()
                if count >= 2
            ]

        return patterns

    async def _generate_ai_questions(
        self,
        psych_indicators: Dict,
        response_patterns: Dict,
        focus_area: Optional[str]
    ) -> List[Dict]:
        """Generate questions using AI."""
        prompt = f"""Based on these astrological indicators and previous response patterns, generate 5 thought-provoking questions for psychological self-exploration.

ASTROLOGICAL INDICATORS:
{json.dumps(psych_indicators, indent=2)}

PREVIOUS PATTERNS:
{json.dumps(response_patterns, indent=2)}

FOCUS AREA: {focus_area or "General self-awareness"}

Generate questions that:
1. Are open-ended and reflective
2. Connect astrological themes to lived experience
3. Encourage deep self-examination
4. Avoid yes/no answers
5. Build on previous insights

Format as JSON array with structure:
[{{"question": "...", "theme": "...", "astrological_connection": "..."}}]"""

        try:
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a skilled psychological astrologer creating self-reflection questions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    response_format={"type": "json_object"}
                )
                questions_data = json.loads(response.choices[0].message.content)
                return questions_data.get("questions", [])

        except Exception as e:
            logger.warning("Failed to generate AI questions", error=str(e))

        # Fallback to rule-based
        return self._generate_rule_based_questions(psych_indicators, focus_area)

    def _generate_rule_based_questions(
        self,
        psych_indicators: Dict,
        focus_area: Optional[str]
    ) -> List[Dict]:
        """Generate questions using rules."""
        questions = []

        # Emotional nature questions
        for indicator in psych_indicators.get("emotional_nature", []):
            questions.append({
                "question": f"How does your {indicator['placement']} manifest in your daily emotional experiences?",
                "theme": "emotional_awareness",
                "astrological_connection": indicator["placement"]
            })

        # Communication questions
        for indicator in psych_indicators.get("communication_style", []):
            questions.append({
                "question": f"In what ways does your {indicator['placement']} influence how you express yourself to others?",
                "theme": "communication",
                "astrological_connection": indicator["placement"]
            })

        # Add general questions
        questions.extend([
            {
                "question": "What patterns do you notice in how you respond to challenges?",
                "theme": "resilience",
                "astrological_connection": "General chart patterns"
            },
            {
                "question": "How do you experience the tension between your desires and your responsibilities?",
                "theme": "balance",
                "astrological_connection": "Planetary aspects"
            }
        ])

        return questions[:5]  # Return top 5
