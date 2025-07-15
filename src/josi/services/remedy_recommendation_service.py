"""
Enhanced remedy recommendation service for astrological remedies and pariharam.
"""
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from josi.models.remedy_model import (
    Remedy, RemedyRecommendation, UserRemedyProgress,
    RemedyType, DoshaType, Tradition,
    RecommendationRequest, RecommendationResponse, RemedyResponse
)
from josi.models.chart_model import AstrologyChart
from josi.models.user_model import User
from josi.services.ai.interpretation_service import AIInterpretationService
import structlog

logger = structlog.get_logger(__name__)


class RemedyRecommendationService:
    """Service for analyzing charts and recommending personalized remedies."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIInterpretationService()
        
        # Planetary weakness indicators
        self.weakness_indicators = {
            "Sun": ["low_confidence", "authority_issues", "health_problems", "father_issues"],
            "Moon": ["emotional_instability", "mental_stress", "mother_issues", "memory_problems"],
            "Mars": ["lack_of_energy", "anger_issues", "blood_disorders", "property_disputes"],
            "Mercury": ["communication_problems", "learning_difficulties", "nervous_disorders", "business_issues"],
            "Jupiter": ["lack_of_wisdom", "financial_problems", "relationship_issues", "health_problems"],
            "Venus": ["relationship_problems", "creative_blocks", "luxury_issues", "reproductive_health"],
            "Saturn": ["delays", "obstacles", "joint_problems", "loneliness", "career_stagnation"],
            "Rahu": ["confusion", "obsessions", "foreign_issues", "technology_problems"],
            "Ketu": ["spiritual_disconnection", "past_life_issues", "sudden_losses", "moksha_obstacles"]
        }
    
    async def analyze_and_recommend(
        self,
        user_id: UUID,
        request: RecommendationRequest
    ) -> List[RecommendationResponse]:
        """Analyze chart and recommend personalized remedies."""
        try:
            # Get chart
            chart = await self._get_chart(request.chart_id)
            if not chart:
                raise ValueError("Chart not found")
            
            # Analyze chart for issues
            analysis = await self._analyze_chart_issues(chart, request.concern_areas)
            
            # Find matching remedies
            remedies = await self._find_matching_remedies(
                analysis=analysis,
                tradition_preference=request.tradition_preference,
                difficulty_preference=request.difficulty_preference,
                cost_preference=request.cost_preference
            )
            
            # Create recommendations with personalization
            recommendations = []
            for remedy, relevance_data in remedies[:10]:  # Top 10 recommendations
                recommendation = await self._create_personalized_recommendation(
                    user_id=user_id,
                    chart_id=request.chart_id,
                    remedy=remedy,
                    relevance_data=relevance_data,
                    chart_analysis=analysis
                )
                recommendations.append(recommendation)
            
            # Save recommendations to database
            await self._save_recommendations(recommendations)
            
            logger.info(
                "Remedy recommendations generated",
                user_id=str(user_id),
                chart_id=str(request.chart_id),
                recommendation_count=len(recommendations)
            )
            
            return recommendations
        
        except Exception as e:
            logger.error(
                "Failed to generate remedy recommendations",
                error=str(e),
                user_id=str(user_id),
                chart_id=str(request.chart_id)
            )
            raise
    
    async def _analyze_chart_issues(
        self,
        chart: AstrologyChart,
        concern_areas: List[str]
    ) -> Dict[str, Any]:
        """Analyze chart for various astrological issues."""
        analysis = {
            "planetary_afflictions": {},
            "doshas": [],
            "house_issues": {},
            "aspect_problems": [],
            "strength_weaknesses": {},
            "concern_mapping": {},
            "overall_assessment": {}
        }
        
        try:
            chart_data = chart.chart_data
            planets = chart_data.get("planets", {})
            houses = chart_data.get("houses", [])
            aspects = chart_data.get("aspects", [])
            
            # Analyze planetary afflictions
            analysis["planetary_afflictions"] = self._analyze_planetary_afflictions(planets, aspects)
            
            # Check for major doshas
            analysis["doshas"] = self._check_doshas(planets, houses)
            
            # Analyze house-specific issues
            analysis["house_issues"] = self._analyze_house_issues(planets, houses)
            
            # Check problematic aspects
            analysis["aspect_problems"] = self._analyze_problematic_aspects(aspects)
            
            # Evaluate planetary strengths and weaknesses
            analysis["strength_weaknesses"] = self._evaluate_planetary_strengths(planets)
            
            # Map concern areas to astrological factors
            analysis["concern_mapping"] = self._map_concerns_to_astrology(
                concern_areas, planets, houses
            )
            
            # Overall assessment
            analysis["overall_assessment"] = self._create_overall_assessment(analysis)
        
        except Exception as e:
            logger.warning("Error in chart analysis", error=str(e))
        
        return analysis
    
    def _analyze_planetary_afflictions(
        self,
        planets: Dict,
        aspects: List[Dict]
    ) -> Dict[str, List[str]]:
        """Analyze planetary afflictions."""
        afflictions = {}
        
        for planet_name, planet_data in planets.items():
            afflictions[planet_name] = []
            
            # Check dignity
            dignity = planet_data.get("dignity", "neutral")
            if dignity == "debilitated":
                afflictions[planet_name].append("debilitation")
            
            # Check retrograde status
            if planet_data.get("speed", 0) < 0 and planet_name not in ["Sun", "Moon"]:
                afflictions[planet_name].append("retrograde")
            
            # Check combustion
            if planet_data.get("is_combust", False):
                afflictions[planet_name].append("combustion")
            
            # Check malefic aspects
            malefic_aspects = [
                asp for asp in aspects 
                if (asp["planet1"] == planet_name or asp["planet2"] == planet_name) 
                and asp["aspect"] in ["square", "opposition"]
                and asp["orb"] <= 3
            ]
            
            if malefic_aspects:
                afflictions[planet_name].append("malefic_aspects")
        
        return afflictions
    
    def _check_doshas(self, planets: Dict, houses: List) -> List[Dict[str, Any]]:
        """Check for major doshas in the chart."""
        doshas = []
        
        try:
            # Mangal Dosha (Mars in 1st, 2nd, 4th, 7th, 8th, 12th houses)
            if "Mars" in planets:
                mars_house = planets["Mars"].get("house", 0)
                if mars_house in [1, 2, 4, 7, 8, 12]:
                    doshas.append({
                        "type": DoshaType.MANGAL_DOSHA,
                        "severity": self._calculate_mangal_dosha_severity(mars_house, planets),
                        "description": f"Mars in {mars_house} house causing Mangal Dosha",
                        "affected_areas": ["marriage", "relationships", "partnerships"]
                    })
            
            # Kaal Sarp Dosha (all planets between Rahu and Ketu)
            if "Rahu" in planets and "Ketu" in planets:
                rahu_long = planets["Rahu"]["longitude"]
                ketu_long = planets["Ketu"]["longitude"]
                
                kaal_sarp = self._check_kaal_sarp_dosha(planets, rahu_long, ketu_long)
                if kaal_sarp:
                    doshas.append(kaal_sarp)
            
            # Pitra Dosha (afflicted 9th house or Sun)
            pitra_dosha = self._check_pitra_dosha(planets, houses)
            if pitra_dosha:
                doshas.append(pitra_dosha)
            
            # Guru Chandal Dosha (Jupiter with Rahu/Ketu)
            if "Jupiter" in planets and ("Rahu" in planets or "Ketu" in planets):
                guru_chandal = self._check_guru_chandal_dosha(planets)
                if guru_chandal:
                    doshas.append(guru_chandal)
        
        except Exception as e:
            logger.warning("Error checking doshas", error=str(e))
        
        return doshas
    
    def _analyze_house_issues(self, planets: Dict, houses: List) -> Dict[int, List[str]]:
        """Analyze house-specific issues."""
        house_issues = {}
        
        for house_num in range(1, 13):
            issues = []
            
            # Check for malefic planets in the house
            house_planets = [
                planet for planet, data in planets.items()
                if data.get("house") == house_num
            ]
            
            malefics = ["Mars", "Saturn", "Rahu", "Ketu"]
            house_malefics = [p for p in house_planets if p in malefics]
            
            if house_malefics:
                issues.append(f"malefic_planets: {', '.join(house_malefics)}")
            
            # Check for empty houses (depending on context)
            if not house_planets and house_num in [1, 5, 7, 10]:  # Important houses
                issues.append("empty_house")
            
            # Check for overcrowded houses
            if len(house_planets) >= 4:
                issues.append("overcrowded")
            
            if issues:
                house_issues[house_num] = issues
        
        return house_issues
    
    def _analyze_problematic_aspects(self, aspects: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze problematic aspects."""
        problems = []
        
        for aspect in aspects:
            if aspect["aspect"] in ["square", "opposition"] and aspect["orb"] <= 3:
                # Determine severity based on planets involved
                planet1 = aspect["planet1"]
                planet2 = aspect["planet2"]
                
                severity = "medium"
                if {planet1, planet2} & {"Sun", "Moon", "Jupiter"}:
                    severity = "high"
                elif {planet1, planet2} & {"Mars", "Saturn", "Rahu", "Ketu"}:
                    severity = "high" if aspect["aspect"] == "opposition" else "medium"
                
                problems.append({
                    "aspect": aspect,
                    "severity": severity,
                    "description": f"{planet1} {aspect['aspect']} {planet2}",
                    "suggested_remedies": self._get_aspect_remedies(planet1, planet2, aspect["aspect"])
                })
        
        return problems
    
    def _evaluate_planetary_strengths(self, planets: Dict) -> Dict[str, Dict]:
        """Evaluate planetary strengths and weaknesses."""
        evaluations = {}
        
        for planet_name, planet_data in planets.items():
            strength_score = 50  # Base score
            factors = []
            
            # Dignity scoring
            dignity = planet_data.get("dignity", "neutral")
            if dignity == "exalted":
                strength_score += 30
                factors.append("exalted")
            elif dignity == "own_sign":
                strength_score += 20
                factors.append("own_sign")
            elif dignity == "debilitated":
                strength_score -= 30
                factors.append("debilitated")
            
            # Speed/retrograde
            if planet_data.get("speed", 0) < 0 and planet_name not in ["Sun", "Moon"]:
                strength_score -= 10
                factors.append("retrograde")
            
            # Combustion
            if planet_data.get("is_combust", False):
                strength_score -= 15
                factors.append("combust")
            
            # House position (simplified)
            house = planet_data.get("house", 1)
            if house in [1, 4, 7, 10]:  # Angular houses
                strength_score += 10
                factors.append("angular")
            elif house in [3, 6, 8, 12]:  # Dusthana houses
                strength_score -= 10
                factors.append("dusthana")
            
            evaluations[planet_name] = {
                "strength_score": max(0, min(100, strength_score)),
                "factors": factors,
                "status": "strong" if strength_score >= 70 else "weak" if strength_score <= 30 else "moderate"
            }
        
        return evaluations
    
    def _map_concerns_to_astrology(
        self,
        concern_areas: List[str],
        planets: Dict,
        houses: List
    ) -> Dict[str, Dict]:
        """Map user concern areas to astrological factors."""
        mapping = {}
        
        # Concern area to astrological factor mapping
        concern_mapping = {
            "career": {"houses": [10, 6], "planets": ["Sun", "Saturn", "Jupiter"]},
            "relationships": {"houses": [7, 5], "planets": ["Venus", "Mars", "Jupiter"]},
            "health": {"houses": [1, 6, 8], "planets": ["Sun", "Moon", "Mars"]},
            "finance": {"houses": [2, 11], "planets": ["Jupiter", "Venus", "Mercury"]},
            "education": {"houses": [4, 5], "planets": ["Mercury", "Jupiter"]},
            "family": {"houses": [2, 4], "planets": ["Moon", "Jupiter"]},
            "spirituality": {"houses": [9, 12], "planets": ["Jupiter", "Ketu"]},
            "marriage": {"houses": [7], "planets": ["Venus", "Jupiter"]},
            "children": {"houses": [5], "planets": ["Jupiter"]},
            "property": {"houses": [4], "planets": ["Mars", "Saturn"]}
        }
        
        for concern in concern_areas:
            if concern in concern_mapping:
                astrological_factors = concern_mapping[concern]
                issues_found = []
                
                # Check relevant houses
                for house_num in astrological_factors.get("houses", []):
                    house_planets = [
                        planet for planet, data in planets.items()
                        if data.get("house") == house_num
                    ]
                    
                    if not house_planets:
                        issues_found.append(f"Empty {house_num} house")
                    else:
                        malefics = [p for p in house_planets if p in ["Mars", "Saturn", "Rahu", "Ketu"]]
                        if malefics:
                            issues_found.append(f"Malefics in {house_num} house: {malefics}")
                
                # Check relevant planets
                for planet_name in astrological_factors.get("planets", []):
                    if planet_name in planets:
                        planet_data = planets[planet_name]
                        if planet_data.get("dignity") == "debilitated":
                            issues_found.append(f"{planet_name} debilitated")
                        if planet_data.get("is_combust"):
                            issues_found.append(f"{planet_name} combust")
                
                mapping[concern] = {
                    "astrological_factors": astrological_factors,
                    "issues_found": issues_found,
                    "priority": len(issues_found)  # More issues = higher priority
                }
        
        return mapping
    
    def _create_overall_assessment(self, analysis: Dict) -> Dict[str, Any]:
        """Create overall assessment of the chart."""
        assessment = {
            "total_issues": 0,
            "severity_distribution": {"high": 0, "medium": 0, "low": 0},
            "primary_concerns": [],
            "immediate_attention": [],
            "long_term_remedies": []
        }
        
        # Count issues
        assessment["total_issues"] = (
            len(analysis["doshas"]) +
            len(analysis["aspect_problems"]) +
            sum(len(issues) for issues in analysis["house_issues"].values())
        )
        
        # Categorize by severity
        for dosha in analysis["doshas"]:
            severity = dosha.get("severity", "medium")
            assessment["severity_distribution"][severity] += 1
            
            if severity == "high":
                assessment["immediate_attention"].append(dosha["type"])
        
        # Identify weak planets needing attention
        weak_planets = [
            planet for planet, data in analysis["strength_weaknesses"].items()
            if data["status"] == "weak"
        ]
        assessment["primary_concerns"] = weak_planets[:3]  # Top 3 concerns
        
        return assessment
    
    async def _find_matching_remedies(
        self,
        analysis: Dict,
        tradition_preference: Optional[str],
        difficulty_preference: Optional[int],
        cost_preference: Optional[int]
    ) -> List[Tuple[Remedy, Dict]]:
        """Find remedies matching the chart analysis."""
        query = select(Remedy).where(
            Remedy.is_active == True,
            Remedy.is_deleted == False
        )
        
        # Apply filters
        if tradition_preference:
            query = query.where(Remedy.tradition == tradition_preference)
        
        if difficulty_preference:
            query = query.where(Remedy.difficulty_level <= difficulty_preference)
        
        if cost_preference:
            query = query.where(Remedy.cost_level <= cost_preference)
        
        result = await self.db.execute(query)
        remedies = result.scalars().all()
        
        # Score and rank remedies
        scored_remedies = []
        for remedy in remedies:
            relevance_data = self._calculate_remedy_relevance(remedy, analysis)
            if relevance_data["score"] > 0:
                scored_remedies.append((remedy, relevance_data))
        
        # Sort by relevance score
        scored_remedies.sort(key=lambda x: x[1]["score"], reverse=True)
        
        return scored_remedies
    
    def _calculate_remedy_relevance(self, remedy: Remedy, analysis: Dict) -> Dict:
        """Calculate how relevant a remedy is to the chart issues."""
        score = 0
        reasons = []
        
        # Planet-specific remedies
        if remedy.planet:
            planet_afflictions = analysis["planetary_afflictions"].get(remedy.planet, [])
            if planet_afflictions:
                score += 20 * len(planet_afflictions)
                reasons.append(f"Addresses {remedy.planet} afflictions: {planet_afflictions}")
            
            # Check planetary strength
            planet_strength = analysis["strength_weaknesses"].get(remedy.planet, {})
            if planet_strength.get("status") == "weak":
                score += 30
                reasons.append(f"Strengthens weak {remedy.planet}")
        
        # Dosha-specific remedies
        if remedy.dosha_type:
            chart_doshas = [d["type"] for d in analysis["doshas"]]
            if remedy.dosha_type in chart_doshas:
                score += 40
                reasons.append(f"Directly addresses {remedy.dosha_type}")
        
        # General remedies get lower but still positive scores
        if not remedy.planet and not remedy.dosha_type:
            score += 10
            reasons.append("General spiritual remedy")
        
        # Bonus for high effectiveness
        if remedy.effectiveness_rating >= 8:
            score += 10
            reasons.append("High effectiveness rating")
        
        # Penalty for high difficulty/cost if user prefers easier options
        # This would be applied in the filtering stage
        
        return {
            "score": score,
            "reasons": reasons,
            "priority": "high" if score >= 50 else "medium" if score >= 25 else "low"
        }
    
    async def _create_personalized_recommendation(
        self,
        user_id: UUID,
        chart_id: UUID,
        remedy: Remedy,
        relevance_data: Dict,
        chart_analysis: Dict
    ) -> RecommendationResponse:
        """Create a personalized recommendation."""
        # Generate AI-enhanced personalization if available
        personalized_instructions = await self._generate_personalized_instructions(
            remedy, chart_analysis, relevance_data
        )
        
        # Estimate timeline based on remedy and chart severity
        timeline = self._estimate_timeline(remedy, chart_analysis)
        
        # Determine priority level
        priority_level = self._determine_priority_level(relevance_data, chart_analysis)
        
        # Create recommendation object
        recommendation = RemedyRecommendation(
            user_id=user_id,
            chart_id=chart_id,
            remedy_id=remedy.remedy_id,
            relevance_score=relevance_data["score"],
            priority_level=priority_level,
            issue_type="multiple",  # Could be more specific
            issue_description="; ".join(relevance_data["reasons"]),
            expected_timeline=timeline,
            personalized_instructions=personalized_instructions,
            recommended_by="ai",
            confidence_score=min(95, relevance_data["score"] + 20)
        )
        
        return RecommendationResponse(
            recommendation_id=recommendation.recommendation_id,
            remedy=RemedyResponse(
                remedy_id=remedy.remedy_id,
                name=remedy.name,
                type=remedy.type.value,
                tradition=remedy.tradition.value,
                planet=remedy.planet,
                dosha_type=remedy.dosha_type.value if remedy.dosha_type else None,
                description=remedy.description,
                instructions=remedy.instructions,
                benefits=remedy.benefits,
                precautions=remedy.precautions,
                duration_days=remedy.duration_days,
                frequency=remedy.frequency,
                best_time=remedy.best_time,
                materials_needed=remedy.materials_needed,
                effectiveness_rating=remedy.effectiveness_rating,
                difficulty_level=remedy.difficulty_level,
                cost_level=remedy.cost_level,
                mantra_text=remedy.mantra_text,
                mantra_audio_url=remedy.mantra_audio_url,
                instruction_video_url=remedy.instruction_video_url,
                yantra_image_url=remedy.yantra_image_url,
                created_at=remedy.created_at
            ),
            relevance_score=relevance_data["score"],
            priority_level=priority_level,
            issue_description="; ".join(relevance_data["reasons"]),
            expected_timeline=timeline,
            personalized_instructions=personalized_instructions,
            confidence_score=min(95, relevance_data["score"] + 20),
            created_at=datetime.utcnow()
        )
    
    async def _generate_personalized_instructions(
        self,
        remedy: Remedy,
        chart_analysis: Dict,
        relevance_data: Dict
    ) -> Optional[str]:
        """Generate AI-powered personalized instructions."""
        try:
            if not self.ai_service.openai_client:
                return None
            
            prompt = f"""
            Create personalized instructions for this astrological remedy:
            
            Remedy: {remedy.name} ({remedy.type.value})
            Standard Instructions: {remedy.get_localized_content('instructions', 'en')}
            
            Chart Issues: {relevance_data['reasons']}
            Overall Assessment: {chart_analysis.get('overall_assessment', {})}
            
            Provide specific, personalized instructions considering:
            1. The person's specific chart issues
            2. How to modify the remedy for maximum effectiveness
            3. What to focus on during practice
            4. Any additional considerations
            
            Keep instructions practical and encouraging.
            """
            
            response = await self.ai_service.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert Vedic astrologer providing personalized remedy guidance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.warning("Failed to generate personalized instructions", error=str(e))
            return None
    
    def _estimate_timeline(self, remedy: Remedy, chart_analysis: Dict) -> str:
        """Estimate timeline for seeing results."""
        base_duration = remedy.duration_days or 40
        severity = chart_analysis.get("overall_assessment", {}).get("severity_distribution", {})
        
        if severity.get("high", 0) > 2:
            # High severity issues take longer
            return f"{base_duration * 2}-{base_duration * 3} days for initial results"
        elif remedy.type in [RemedyType.MANTRA, RemedyType.MEDITATION]:
            return f"{base_duration // 2}-{base_duration} days for noticeable effects"
        else:
            return f"{base_duration}-{base_duration * 2} days for meaningful results"
    
    def _determine_priority_level(self, relevance_data: Dict, chart_analysis: Dict) -> int:
        """Determine priority level (1-5) for the recommendation."""
        score = relevance_data["score"]
        high_severity_count = chart_analysis.get("overall_assessment", {}).get("severity_distribution", {}).get("high", 0)
        
        if score >= 60 and high_severity_count > 0:
            return 5  # Urgent
        elif score >= 40:
            return 4  # High
        elif score >= 25:
            return 3  # Medium
        elif score >= 15:
            return 2  # Low
        else:
            return 1  # Very low
    
    async def _save_recommendations(self, recommendations: List[RecommendationResponse]):
        """Save recommendations to database."""
        try:
            for rec in recommendations:
                rec_entity = RemedyRecommendation(
                    user_id=rec.remedy.remedy_id,  # This should be user_id, fix needed
                    chart_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder, fix needed
                    remedy_id=rec.remedy.remedy_id,
                    relevance_score=rec.relevance_score,
                    priority_level=rec.priority_level,
                    issue_type="multiple",
                    issue_description=rec.issue_description,
                    expected_timeline=rec.expected_timeline,
                    personalized_instructions=rec.personalized_instructions,
                    recommended_by="ai",
                    confidence_score=rec.confidence_score
                )
                self.db.add(rec_entity)
            
            await self.db.commit()
        
        except Exception as e:
            logger.error("Failed to save recommendations", error=str(e))
            await self.db.rollback()
    
    # Helper methods for dosha checking
    
    def _calculate_mangal_dosha_severity(self, mars_house: int, planets: Dict) -> str:
        """Calculate Mangal Dosha severity."""
        if mars_house in [1, 8]:
            return "high"
        elif mars_house in [2, 7]:
            return "medium"
        else:
            return "low"
    
    def _check_kaal_sarp_dosha(self, planets: Dict, rahu_long: float, ketu_long: float) -> Optional[Dict]:
        """Check for Kaal Sarp Dosha."""
        # Simplified check - all planets should be between Rahu and Ketu
        main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        
        # Normalize Rahu-Ketu axis
        if rahu_long > ketu_long:
            ketu_long += 360
        
        planets_between = 0
        for planet in main_planets:
            if planet in planets:
                p_long = planets[planet]["longitude"]
                # Normalize planet longitude
                if p_long < rahu_long:
                    p_long += 360
                
                if rahu_long <= p_long <= ketu_long:
                    planets_between += 1
        
        if planets_between == len(main_planets):
            return {
                "type": DoshaType.KAAL_SARP_DOSHA,
                "severity": "high",
                "description": "All planets between Rahu-Ketu axis",
                "affected_areas": ["general_obstacles", "delays", "spiritual_growth"]
            }
        
        return None
    
    def _check_pitra_dosha(self, planets: Dict, houses: List) -> Optional[Dict]:
        """Check for Pitra Dosha."""
        issues = []
        
        # Check 9th house for malefic influence
        ninth_house_planets = [
            planet for planet, data in planets.items()
            if data.get("house") == 9
        ]
        
        malefics_in_9th = [p for p in ninth_house_planets if p in ["Mars", "Saturn", "Rahu", "Ketu"]]
        if malefics_in_9th:
            issues.append("Malefics in 9th house")
        
        # Check Sun's condition
        if "Sun" in planets:
            sun = planets["Sun"]
            if sun.get("dignity") == "debilitated":
                issues.append("Debilitated Sun")
            if sun.get("is_combust"):
                issues.append("Sun with malefics")
        
        if issues:
            return {
                "type": DoshaType.PITRA_DOSHA,
                "severity": "medium" if len(issues) == 1 else "high",
                "description": "; ".join(issues),
                "affected_areas": ["father_issues", "ancestral_problems", "career_obstacles"]
            }
        
        return None
    
    def _check_guru_chandal_dosha(self, planets: Dict) -> Optional[Dict]:
        """Check for Guru Chandal Dosha (Jupiter with Rahu/Ketu)."""
        if "Jupiter" not in planets:
            return None
        
        jupiter_house = planets["Jupiter"].get("house")
        jupiter_sign = planets["Jupiter"].get("sign")
        
        # Check if Rahu or Ketu is with Jupiter
        rahu_ketu_with_jupiter = []
        
        if "Rahu" in planets:
            if (planets["Rahu"].get("house") == jupiter_house or 
                planets["Rahu"].get("sign") == jupiter_sign):
                rahu_ketu_with_jupiter.append("Rahu")
        
        if "Ketu" in planets:
            if (planets["Ketu"].get("house") == jupiter_house or 
                planets["Ketu"].get("sign") == jupiter_sign):
                rahu_ketu_with_jupiter.append("Ketu")
        
        if rahu_ketu_with_jupiter:
            return {
                "type": DoshaType.GURU_CHANDAL_DOSHA,
                "severity": "high" if "Rahu" in rahu_ketu_with_jupiter else "medium",
                "description": f"Jupiter with {', '.join(rahu_ketu_with_jupiter)}",
                "affected_areas": ["wisdom_problems", "spiritual_confusion", "judgment_issues"]
            }
        
        return None
    
    def _get_aspect_remedies(self, planet1: str, planet2: str, aspect_type: str) -> List[str]:
        """Get suggested remedies for problematic aspects."""
        remedies = []
        
        if aspect_type in ["square", "opposition"]:
            if {planet1, planet2} & {"Sun"}:
                remedies.extend(["Surya mantra", "Red coral", "Sunday fasting"])
            if {planet1, planet2} & {"Moon"}:
                remedies.extend(["Chandra mantra", "Pearl", "Monday fasting"])
            if {planet1, planet2} & {"Mars"}:
                remedies.extend(["Mangal mantra", "Red coral", "Tuesday fasting"])
            if {planet1, planet2} & {"Mercury"}:
                remedies.extend(["Budh mantra", "Emerald", "Wednesday fasting"])
            if {planet1, planet2} & {"Jupiter"}:
                remedies.extend(["Guru mantra", "Yellow sapphire", "Thursday fasting"])
            if {planet1, planet2} & {"Venus"}:
                remedies.extend(["Shukra mantra", "Diamond", "Friday fasting"])
            if {planet1, planet2} & {"Saturn"}:
                remedies.extend(["Shani mantra", "Blue sapphire", "Saturday oil donation"])
        
        return remedies[:3]  # Return top 3 suggestions
    
    # Utility methods
    
    async def _get_chart(self, chart_id: UUID) -> Optional[AstrologyChart]:
        """Get chart by ID."""
        result = await self.db.execute(
            select(AstrologyChart).where(
                AstrologyChart.chart_id == chart_id,
                AstrologyChart.is_deleted == False
            )
        )
        return result.scalar_one_or_none()