"""
Transit monitoring service for real-time astrological updates.
"""
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from josi.services.astrology_service import AstrologyCalculator
from josi.services.realtime_service import realtime_manager
from josi.models.chart_model import AstrologyChart
from josi.models.user_model import User
from josi.db.async_db import get_async_db as get_async_session
import structlog

logger = structlog.get_logger(__name__)


class TransitMonitorService:
    """Monitor and broadcast significant astrological transits."""
    
    def __init__(self):
        self.active_monitors: Dict[str, asyncio.Task] = {}
        self.astrology_calculator = AstrologyCalculator()
        self.monitoring_interval = 300  # 5 minutes
        self.significance_thresholds = {
            "conjunction": 2.0,  # degrees
            "opposition": 2.0,
            "square": 2.0,
            "trine": 2.0,
            "sextile": 2.0,
            "house_ingress": 0.5,  # degrees before entering new house
            "sign_ingress": 0.5,   # degrees before entering new sign
            "retrograde": 1.0      # degrees within station
        }
    
    async def start_monitoring(self, user_id: str, chart_id: str):
        """Start monitoring transits for a user's chart."""
        monitor_key = f"{user_id}:{chart_id}"
        
        if monitor_key in self.active_monitors:
            logger.info("Transit monitoring already active", monitor_key=monitor_key)
            return
        
        task = asyncio.create_task(
            self._monitor_transits(user_id, chart_id)
        )
        self.active_monitors[monitor_key] = task
        
        logger.info("Transit monitoring started", user_id=user_id, chart_id=chart_id)
    
    async def stop_monitoring(self, user_id: str, chart_id: str):
        """Stop monitoring transits for a user's chart."""
        monitor_key = f"{user_id}:{chart_id}"
        
        if monitor_key in self.active_monitors:
            task = self.active_monitors.pop(monitor_key)
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            logger.info("Transit monitoring stopped", user_id=user_id, chart_id=chart_id)
    
    async def _monitor_transits(self, user_id: str, chart_id: str):
        """Background task to monitor transits for a specific chart."""
        try:
            # Get chart data
            async with get_async_session() as db:
                chart = await self._get_chart(db, chart_id)
                if not chart:
                    logger.warning("Chart not found for monitoring", chart_id=chart_id)
                    return
            
            last_positions = None
            
            while True:
                try:
                    # Calculate current planetary positions
                    current_positions = await self._calculate_current_positions()
                    
                    if last_positions:
                        # Check for significant changes
                        significant_events = await self._check_significant_changes(
                            chart=chart,
                            last_positions=last_positions,
                            current_positions=current_positions
                        )
                        
                        if significant_events:
                            # Broadcast updates
                            await realtime_manager.broadcast_transit_update(
                                chart_id=chart_id,
                                transit_data={
                                    "events": significant_events,
                                    "current_positions": current_positions,
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            )
                            
                            # Send notification if it's a major event
                            major_events = [e for e in significant_events if e.get("importance", 0) >= 8]
                            if major_events:
                                await self._send_transit_notification(user_id, major_events)
                    
                    last_positions = current_positions
                    
                    # Wait before next check
                    await asyncio.sleep(self.monitoring_interval)
                
                except Exception as e:
                    logger.error(
                        "Error in transit monitoring loop",
                        error=str(e),
                        user_id=user_id,
                        chart_id=chart_id
                    )
                    await asyncio.sleep(60)  # Wait a minute before retrying
        
        except asyncio.CancelledError:
            logger.info("Transit monitoring cancelled", user_id=user_id, chart_id=chart_id)
        except Exception as e:
            logger.error(
                "Transit monitoring failed",
                error=str(e),
                user_id=user_id,
                chart_id=chart_id
            )
    
    async def _get_chart(self, db: AsyncSession, chart_id: str) -> Optional[AstrologyChart]:
        """Get chart from database."""
        try:
            result = await db.execute(
                select(AstrologyChart).where(
                    AstrologyChart.chart_id == UUID(chart_id),
                    AstrologyChart.is_deleted == False
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Failed to get chart", error=str(e), chart_id=chart_id)
            return None
    
    async def _calculate_current_positions(self) -> Dict[str, Any]:
        """Calculate current planetary positions."""
        try:
            now = datetime.utcnow()
            
            # Calculate positions for all major planets
            positions = self.astrology_calculator.calculate_western_chart(
                birth_time=now,
                latitude=0.0,  # Use geocentric positions
                longitude=0.0
            )
            
            return {
                "timestamp": now.isoformat(),
                "planets": positions.get("planets", {}),
                "houses": positions.get("houses", [])
            }
        
        except Exception as e:
            logger.error("Failed to calculate current positions", error=str(e))
            return {}
    
    async def _check_significant_changes(
        self,
        chart: AstrologyChart,
        last_positions: Dict,
        current_positions: Dict
    ) -> List[Dict[str, Any]]:
        """Check for significant astrological events."""
        events = []
        
        try:
            natal_planets = chart.chart_data.get("planets", {})
            last_planets = last_positions.get("planets", {})
            current_planets = current_positions.get("planets", {})
            
            # Check for aspects to natal planets
            for transit_planet, transit_data in current_planets.items():
                if transit_planet not in last_planets:
                    continue
                
                transit_long = transit_data.get("longitude", 0)
                last_transit_long = last_planets[transit_planet].get("longitude", 0)
                
                for natal_planet, natal_data in natal_planets.items():
                    natal_long = natal_data.get("longitude", 0)
                    
                    # Check if we're crossing an aspect
                    aspect_events = self._check_aspect_crossings(
                        transit_planet=transit_planet,
                        transit_long=transit_long,
                        last_transit_long=last_transit_long,
                        natal_planet=natal_planet,
                        natal_long=natal_long
                    )
                    events.extend(aspect_events)
            
            # Check for house and sign ingresses
            ingress_events = self._check_ingresses(last_planets, current_planets)
            events.extend(ingress_events)
            
            # Check for retrograde stations
            retrograde_events = self._check_retrograde_stations(last_planets, current_planets)
            events.extend(retrograde_events)
        
        except Exception as e:
            logger.error("Failed to check significant changes", error=str(e))
        
        return events
    
    def _check_aspect_crossings(
        self,
        transit_planet: str,
        transit_long: float,
        last_transit_long: float,
        natal_planet: str,
        natal_long: float
    ) -> List[Dict[str, Any]]:
        """Check if transit planet is crossing an aspect to natal planet."""
        events = []
        
        aspect_angles = {
            "conjunction": 0,
            "sextile": 60,
            "square": 90,
            "trine": 120,
            "opposition": 180
        }
        
        for aspect_name, aspect_angle in aspect_angles.items():
            # Calculate distances
            current_distance = abs(self._normalize_angle(transit_long - natal_long))
            last_distance = abs(self._normalize_angle(last_transit_long - natal_long))
            
            # Check if we're within orb of exact aspect
            orb = self.significance_thresholds[aspect_name]
            
            # Check for approaching exact aspect (getting closer)
            current_diff = abs(current_distance - aspect_angle)
            last_diff = abs(last_distance - aspect_angle)
            
            if current_diff < orb and current_diff < last_diff:
                importance = self._calculate_aspect_importance(
                    transit_planet, natal_planet, aspect_name, current_diff
                )
                
                events.append({
                    "type": "aspect_forming",
                    "transit_planet": transit_planet,
                    "natal_planet": natal_planet,
                    "aspect": aspect_name,
                    "orb": round(current_diff, 2),
                    "importance": importance,
                    "description": f"{transit_planet} forming {aspect_name} to natal {natal_planet}",
                    "exact_date": self._estimate_exact_date(
                        transit_planet, current_diff, aspect_name
                    )
                })
        
        return events
    
    def _check_ingresses(
        self,
        last_planets: Dict,
        current_planets: Dict
    ) -> List[Dict[str, Any]]:
        """Check for sign and house ingresses."""
        events = []
        
        for planet, current_data in current_planets.items():
            if planet not in last_planets:
                continue
            
            current_long = current_data.get("longitude", 0)
            last_long = last_planets[planet].get("longitude", 0)
            
            # Check sign ingress
            current_sign = int(current_long / 30)
            last_sign = int(last_long / 30)
            
            if current_sign != last_sign:
                sign_names = [
                    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
                ]
                
                events.append({
                    "type": "sign_ingress",
                    "planet": planet,
                    "new_sign": sign_names[current_sign],
                    "importance": self._calculate_ingress_importance(planet, "sign"),
                    "description": f"{planet} enters {sign_names[current_sign]}",
                    "longitude": current_long
                })
        
        return events
    
    def _check_retrograde_stations(
        self,
        last_planets: Dict,
        current_planets: Dict
    ) -> List[Dict[str, Any]]:
        """Check for planets stationing retrograde or direct."""
        events = []
        
        for planet, current_data in current_planets.items():
            if planet not in last_planets or planet in ["Sun", "Moon"]:
                continue
            
            current_speed = current_data.get("speed", 0)
            last_speed = last_planets[planet].get("speed", 0)
            
            # Check for speed sign change (station)
            if (last_speed > 0 and current_speed < 0) or (last_speed < 0 and current_speed > 0):
                station_type = "retrograde" if current_speed < 0 else "direct"
                
                events.append({
                    "type": "station",
                    "planet": planet,
                    "station_type": station_type,
                    "importance": self._calculate_station_importance(planet),
                    "description": f"{planet} stations {station_type}",
                    "longitude": current_data.get("longitude", 0)
                })
        
        return events
    
    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to 0-360 range."""
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle
    
    def _calculate_aspect_importance(
        self,
        transit_planet: str,
        natal_planet: str,
        aspect: str,
        orb: float
    ) -> int:
        """Calculate importance of an aspect (1-10 scale)."""
        base_importance = {
            "conjunction": 9,
            "opposition": 8,
            "square": 7,
            "trine": 6,
            "sextile": 5
        }.get(aspect, 3)
        
        # Adjust for planets involved
        planet_weights = {
            "Sun": 3, "Moon": 3, "Mercury": 2, "Venus": 2,
            "Mars": 2, "Jupiter": 3, "Saturn": 3, "Uranus": 2,
            "Neptune": 2, "Pluto": 2
        }
        
        weight_modifier = (
            planet_weights.get(transit_planet, 1) + 
            planet_weights.get(natal_planet, 1)
        ) / 2
        
        # Adjust for orb (closer = more important)
        orb_modifier = max(0.5, 1 - (orb / 2))
        
        importance = int(base_importance * weight_modifier * orb_modifier)
        return min(10, max(1, importance))
    
    def _calculate_ingress_importance(self, planet: str, ingress_type: str) -> int:
        """Calculate importance of an ingress."""
        planet_weights = {
            "Sun": 7, "Moon": 5, "Mercury": 4, "Venus": 4,
            "Mars": 5, "Jupiter": 8, "Saturn": 9, "Uranus": 7,
            "Neptune": 6, "Pluto": 6
        }
        
        base_importance = 6 if ingress_type == "sign" else 4
        return min(10, planet_weights.get(planet, 3) + base_importance - 5)
    
    def _calculate_station_importance(self, planet: str) -> int:
        """Calculate importance of a station."""
        station_weights = {
            "Mercury": 6, "Venus": 5, "Mars": 7, "Jupiter": 8,
            "Saturn": 9, "Uranus": 7, "Neptune": 6, "Pluto": 6
        }
        return station_weights.get(planet, 5)
    
    def _estimate_exact_date(
        self,
        planet: str,
        current_orb: float,
        aspect: str
    ) -> Optional[str]:
        """Estimate when aspect will be exact."""
        try:
            # Rough estimation based on average planetary speeds
            daily_motion = {
                "Sun": 1.0, "Moon": 13.0, "Mercury": 1.3, "Venus": 1.2,
                "Mars": 0.5, "Jupiter": 0.08, "Saturn": 0.03, "Uranus": 0.01,
                "Neptune": 0.006, "Pluto": 0.004
            }
            
            motion = daily_motion.get(planet, 0.5)
            if motion > 0:
                days_to_exact = current_orb / motion
                exact_date = datetime.utcnow() + timedelta(days=days_to_exact)
                return exact_date.isoformat()
        
        except Exception:
            pass
        
        return None
    
    async def _send_transit_notification(self, user_id: str, events: List[Dict]):
        """Send notification for major transit events."""
        try:
            notification = {
                "title": "Important Astrological Transit",
                "message": self._format_transit_message(events),
                "events": events,
                "type": "transit_alert"
            }
            
            await realtime_manager.send_notification(user_id, notification)
        
        except Exception as e:
            logger.error(
                "Failed to send transit notification",
                error=str(e),
                user_id=user_id
            )
    
    def _format_transit_message(self, events: List[Dict]) -> str:
        """Format transit events into a readable message."""
        if len(events) == 1:
            event = events[0]
            return event.get("description", "Significant transit occurring")
        else:
            return f"{len(events)} significant transits are occurring in your chart"
    
    def get_active_monitors(self) -> List[str]:
        """Get list of active monitor keys."""
        return list(self.active_monitors.keys())
    
    def get_monitor_stats(self) -> Dict:
        """Get monitoring statistics."""
        return {
            "active_monitors": len(self.active_monitors),
            "monitoring_interval_seconds": self.monitoring_interval,
            "significance_thresholds": self.significance_thresholds
        }


# Global transit monitor instance
transit_monitor = TransitMonitorService()