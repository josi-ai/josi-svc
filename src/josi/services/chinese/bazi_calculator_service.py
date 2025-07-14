"""
Chinese BaZi (Four Pillars of Destiny) calculator.
Implements authentic Chinese astrology calculations based on solar calendar.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import math
import pytz
from lunarcalendar import Converter, Solar


class BaZiCalculator:
    """Calculate Chinese Four Pillars (BaZi) chart."""
    
    # Heavenly Stems (天干)
    HEAVENLY_STEMS = [
        ("甲", "Jia", "Yang Wood"),
        ("乙", "Yi", "Yin Wood"),
        ("丙", "Bing", "Yang Fire"),
        ("丁", "Ding", "Yin Fire"),
        ("戊", "Wu", "Yang Earth"),
        ("己", "Ji", "Yin Earth"),
        ("庚", "Geng", "Yang Metal"),
        ("辛", "Xin", "Yin Metal"),
        ("壬", "Ren", "Yang Water"),
        ("癸", "Gui", "Yin Water")
    ]
    
    # Earthly Branches (地支)
    EARTHLY_BRANCHES = [
        ("子", "Zi", "Rat", "Yang Water"),
        ("丑", "Chou", "Ox", "Yin Earth"),
        ("寅", "Yin", "Tiger", "Yang Wood"),
        ("卯", "Mao", "Rabbit", "Yin Wood"),
        ("辰", "Chen", "Dragon", "Yang Earth"),
        ("巳", "Si", "Snake", "Yin Fire"),
        ("午", "Wu", "Horse", "Yang Fire"),
        ("未", "Wei", "Goat", "Yin Earth"),
        ("申", "Shen", "Monkey", "Yang Metal"),
        ("酉", "You", "Rooster", "Yin Metal"),
        ("戌", "Xu", "Dog", "Yang Earth"),
        ("亥", "Hai", "Pig", "Yin Water")
    ]
    
    # Five Elements relationships
    ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]
    GENERATING_CYCLE = {
        "Wood": "Fire",
        "Fire": "Earth",
        "Earth": "Metal",
        "Metal": "Water",
        "Water": "Wood"
    }
    CONTROLLING_CYCLE = {
        "Wood": "Earth",
        "Fire": "Metal",
        "Earth": "Water",
        "Metal": "Wood",
        "Water": "Fire"
    }
    
    def calculate_bazi(
        self,
        birth_datetime: datetime,
        latitude: float,
        longitude: float,
        timezone: str
    ) -> Dict:
        """
        Calculate complete BaZi chart.
        
        Args:
            birth_datetime: Date and time of birth
            latitude: Birth latitude (for solar time correction)
            longitude: Birth longitude (for solar time correction)
            timezone: Birth timezone
        
        Returns:
            Complete BaZi chart with Four Pillars and analysis
        """
        # Convert to local solar time
        local_solar_time = self._calculate_local_solar_time(
            birth_datetime, longitude, timezone
        )
        
        # Calculate Four Pillars
        year_pillar = self._calculate_year_pillar(local_solar_time)
        month_pillar = self._calculate_month_pillar(local_solar_time, year_pillar)
        day_pillar = self._calculate_day_pillar(local_solar_time)
        hour_pillar = self._calculate_hour_pillar(local_solar_time, day_pillar)
        
        # Analyze chart
        day_master = self._get_day_master(day_pillar)
        elements_strength = self._analyze_elements(
            year_pillar, month_pillar, day_pillar, hour_pillar
        )
        
        # Calculate luck pillars
        gender = "male"  # TODO: Add gender parameter
        luck_pillars = self._calculate_luck_pillars(
            birth_datetime, month_pillar, gender
        )
        
        # Get current luck pillar
        current_luck = self._get_current_luck_pillar(birth_datetime, luck_pillars)
        
        return {
            "system": "chinese_bazi",
            "calculation_time": local_solar_time.isoformat(),
            "four_pillars": {
                "year": self._format_pillar(year_pillar, "Year"),
                "month": self._format_pillar(month_pillar, "Month"),
                "day": self._format_pillar(day_pillar, "Day"),
                "hour": self._format_pillar(hour_pillar, "Hour")
            },
            "day_master": {
                "element": day_master["element"],
                "polarity": day_master["polarity"],
                "strength": self._calculate_day_master_strength(
                    day_master, elements_strength, month_pillar
                )
            },
            "elements_analysis": elements_strength,
            "favorable_elements": self._determine_favorable_elements(
                day_master, elements_strength
            ),
            "luck_pillars": luck_pillars,
            "current_luck_pillar": current_luck,
            "personality_traits": self._analyze_personality(day_master, elements_strength),
            "life_areas": self._analyze_life_areas(
                year_pillar, month_pillar, day_pillar, hour_pillar
            )
        }
    
    def _calculate_local_solar_time(
        self,
        birth_datetime: datetime,
        longitude: float,
        timezone: str
    ) -> datetime:
        """Convert clock time to local solar time."""
        # Get timezone offset
        tz = pytz.timezone(timezone)
        
        # Calculate equation of time (simplified)
        day_of_year = birth_datetime.timetuple().tm_yday
        b = 2 * 3.14159 * (day_of_year - 81) / 365
        equation_of_time = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
        
        # Calculate local solar time correction
        # 4 minutes per degree of longitude
        standard_meridian = round(longitude / 15) * 15
        longitude_correction = 4 * (longitude - standard_meridian)
        
        # Total correction in minutes
        total_correction = equation_of_time + longitude_correction
        
        # Apply correction
        solar_time = birth_datetime + timedelta(minutes=total_correction)
        
        return solar_time
    
    def _calculate_year_pillar(self, solar_time: datetime) -> Tuple[int, int]:
        """Calculate year pillar based on solar calendar."""
        # Chinese solar year starts around Feb 4 (Li Chun)
        year = solar_time.year
        
        # Check if before Li Chun (Spring Start)
        li_chun = self._get_li_chun_date(year)
        if solar_time < li_chun:
            year -= 1
        
        # Calculate stem and branch
        stem = (year - 4) % 10
        branch = (year - 4) % 12
        
        return (stem, branch)
    
    def _calculate_month_pillar(
        self,
        solar_time: datetime,
        year_pillar: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Calculate month pillar based on solar terms."""
        # Solar months based on 24 solar terms
        solar_terms = self._get_solar_terms(solar_time.year)
        
        # Find which solar month we're in
        month_branch = 0
        for i, (term_date, _) in enumerate(solar_terms):
            if solar_time >= term_date:
                month_branch = i // 2
            else:
                break
        
        # Calculate month stem based on year stem
        year_stem = year_pillar[0]
        month_stem_base = ((year_stem % 5) * 2) % 10
        month_stem = (month_stem_base + month_branch) % 10
        
        return (month_stem, month_branch)
    
    def _calculate_day_pillar(self, solar_time: datetime) -> Tuple[int, int]:
        """Calculate day pillar using perpetual calendar method."""
        # Reference date: 1900-01-01 = 甲子 (0, 0)
        reference = datetime(1900, 1, 1)
        days_diff = (solar_time.date() - reference.date()).days
        
        stem = days_diff % 10
        branch = days_diff % 12
        
        return (stem, branch)
    
    def _calculate_hour_pillar(
        self,
        solar_time: datetime,
        day_pillar: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Calculate hour pillar based on double-hour system."""
        # Chinese double-hours
        hour = solar_time.hour
        minute = solar_time.minute
        
        # Adjust for half-hour boundaries
        if minute >= 30:
            hour += 1
        
        # Convert to double-hour (0-11)
        double_hour = ((hour + 1) % 24) // 2
        hour_branch = double_hour
        
        # Calculate hour stem based on day stem
        day_stem = day_pillar[0]
        hour_stem_base = ((day_stem % 5) * 2) % 10
        hour_stem = (hour_stem_base + hour_branch) % 10
        
        return (hour_stem, hour_branch)
    
    def _get_li_chun_date(self, year: int) -> datetime:
        """Get Li Chun (Spring Start) date for given year."""
        # Simplified - usually around Feb 4
        # In practice, use astronomical calculations
        base_date = datetime(year, 2, 4, 0, 0, 0)
        
        # Adjust based on year (simplified)
        if year % 4 == 0:  # Leap year
            base_date -= timedelta(days=1)
        
        return base_date
    
    def _get_solar_terms(self, year: int) -> List[Tuple[datetime, str]]:
        """Get 24 solar terms for the year."""
        # Simplified - in practice, calculate astronomically
        # Starting with Li Chun (Spring Start)
        terms = []
        base_date = self._get_li_chun_date(year)
        
        term_names = [
            "立春 (Spring Start)", "雨水 (Rain Water)",
            "惊蛰 (Awakening)", "春分 (Spring Equinox)",
            "清明 (Clear Bright)", "谷雨 (Grain Rain)",
            "立夏 (Summer Start)", "小满 (Grain Full)",
            "芒种 (Grain in Ear)", "夏至 (Summer Solstice)",
            "小暑 (Minor Heat)", "大暑 (Major Heat)",
            "立秋 (Autumn Start)", "处暑 (Heat Limit)",
            "白露 (White Dew)", "秋分 (Autumn Equinox)",
            "寒露 (Cold Dew)", "霜降 (Frost Descent)",
            "立冬 (Winter Start)", "小雪 (Minor Snow)",
            "大雪 (Major Snow)", "冬至 (Winter Solstice)",
            "小寒 (Minor Cold)", "大寒 (Major Cold)"
        ]
        
        # Approximate: 15 days between terms
        for i, name in enumerate(term_names):
            term_date = base_date + timedelta(days=15 * i)
            terms.append((term_date, name))
        
        return terms
    
    def _format_pillar(self, pillar: Tuple[int, int], pillar_type: str) -> Dict:
        """Format a pillar with all relevant information."""
        stem_idx, branch_idx = pillar
        
        stem_info = self.HEAVENLY_STEMS[stem_idx]
        branch_info = self.EARTHLY_BRANCHES[branch_idx]
        
        # Get hidden stems in branch
        hidden_stems = self._get_hidden_stems(branch_idx)
        
        return {
            "stem": {
                "chinese": stem_info[0],
                "pinyin": stem_info[1],
                "element": stem_info[2],
                "index": stem_idx
            },
            "branch": {
                "chinese": branch_info[0],
                "pinyin": branch_info[1],
                "animal": branch_info[2],
                "element": branch_info[3],
                "index": branch_idx
            },
            "hidden_stems": hidden_stems,
            "na_yin": self._get_na_yin(stem_idx, branch_idx),
            "combination": f"{stem_info[0]}{branch_info[0]}"
        }
    
    def _get_hidden_stems(self, branch_idx: int) -> List[Dict]:
        """Get hidden heavenly stems within earthly branch."""
        # Each branch contains 1-3 hidden stems
        hidden_stems_map = {
            0: [9],           # 子 Zi: 癸
            1: [5, 9, 7],     # 丑 Chou: 己癸辛
            2: [2, 4, 0],     # 寅 Yin: 丙戊甲
            3: [1],           # 卯 Mao: 乙
            4: [4, 1, 9],     # 辰 Chen: 戊乙癸
            5: [2, 4, 6],     # 巳 Si: 丙戊庚
            6: [3, 5],        # 午 Wu: 丁己
            7: [5, 3, 1],     # 未 Wei: 己丁乙
            8: [6, 4, 8],     # 申 Shen: 庚戊壬
            9: [7],           # 酉 You: 辛
            10: [4, 7, 3],    # 戌 Xu: 戊辛丁
            11: [8, 0]        # 亥 Hai: 壬甲
        }
        
        hidden = []
        for stem_idx in hidden_stems_map.get(branch_idx, []):
            stem_info = self.HEAVENLY_STEMS[stem_idx]
            hidden.append({
                "chinese": stem_info[0],
                "pinyin": stem_info[1],
                "element": stem_info[2]
            })
        
        return hidden
    
    def _get_na_yin(self, stem_idx: int, branch_idx: int) -> str:
        """Get Na Yin (纳音) element for stem-branch combination."""
        # 60 Na Yin cycle
        na_yin_elements = [
            "海中金", "炉中火", "大林木", "路旁土", "剑锋金",
            "山头火", "涧下水", "城头土", "白蜡金", "杨柳木",
            "泉中水", "屋上土", "霹雳火", "松柏木", "长流水",
            "砂中金", "山下火", "平地木", "壁上土", "金箔金",
            "覆灯火", "天河水", "大驿土", "钗钏金", "桑拓木",
            "大溪水", "砂中土", "天上火", "石榴木", "大海水"
        ]
        
        # Calculate 60-cycle position
        position = (stem_idx * 6 + branch_idx // 2) % 30
        return na_yin_elements[position]
    
    def _get_day_master(self, day_pillar: Tuple[int, int]) -> Dict:
        """Get day master (日主) information."""
        stem_idx = day_pillar[0]
        stem_info = self.HEAVENLY_STEMS[stem_idx]
        
        element = stem_info[2].split()[1]  # Extract element from "Yang Wood" etc.
        polarity = stem_info[2].split()[0]  # Yang or Yin
        
        return {
            "stem": stem_info[1],
            "chinese": stem_info[0],
            "element": element,
            "polarity": polarity
        }
    
    def _analyze_elements(self, *pillars) -> Dict[str, Dict]:
        """Analyze element distribution in the chart."""
        element_count = {element: 0 for element in self.ELEMENTS}
        element_strength = {element: 0.0 for element in self.ELEMENTS}
        
        # Count elements from stems and branches
        for pillar in pillars:
            stem_idx, branch_idx = pillar
            
            # Stem element
            stem_element = self.HEAVENLY_STEMS[stem_idx][2].split()[1]
            element_count[stem_element] += 1
            element_strength[stem_element] += 1.0
            
            # Branch main element
            branch_element = self.EARTHLY_BRANCHES[branch_idx][3].split()[1]
            element_count[branch_element] += 1
            element_strength[branch_element] += 0.7
            
            # Hidden stems
            for hidden_idx in self._get_hidden_stems_indices(branch_idx):
                hidden_element = self.HEAVENLY_STEMS[hidden_idx][2].split()[1]
                element_count[hidden_element] += 1
                element_strength[hidden_element] += 0.3
        
        # Calculate percentages
        total_strength = sum(element_strength.values())
        element_percentage = {
            element: (strength / total_strength * 100)
            for element, strength in element_strength.items()
        }
        
        return {
            "counts": element_count,
            "strength": element_strength,
            "percentage": element_percentage,
            "dominant_element": max(element_strength.items(), key=lambda x: x[1])[0],
            "weakest_element": min(element_strength.items(), key=lambda x: x[1])[0]
        }
    
    def _get_hidden_stems_indices(self, branch_idx: int) -> List[int]:
        """Get indices of hidden stems (for calculation)."""
        hidden_map = {
            0: [9], 1: [5, 9, 7], 2: [2, 4, 0], 3: [1],
            4: [4, 1, 9], 5: [2, 4, 6], 6: [3, 5], 7: [5, 3, 1],
            8: [6, 4, 8], 9: [7], 10: [4, 7, 3], 11: [8, 0]
        }
        return hidden_map.get(branch_idx, [])
    
    def _calculate_day_master_strength(
        self,
        day_master: Dict,
        elements: Dict,
        month_pillar: Tuple[int, int]
    ) -> str:
        """Determine if day master is strong or weak."""
        dm_element = day_master["element"]
        dm_strength = elements["percentage"][dm_element]
        
        # Consider supporting elements
        supporting_element = self._get_generating_element(dm_element)
        support_strength = elements["percentage"].get(supporting_element, 0)
        
        # Consider month branch season
        month_branch = month_pillar[1]
        seasonal_strength = self._get_seasonal_strength(dm_element, month_branch)
        
        # Total strength calculation
        total_strength = dm_strength + (support_strength * 0.5) + seasonal_strength
        
        if total_strength > 40:
            return "Strong"
        elif total_strength > 25:
            return "Balanced"
        else:
            return "Weak"
    
    def _get_generating_element(self, element: str) -> str:
        """Get element that generates given element."""
        for gen, produced in self.GENERATING_CYCLE.items():
            if produced == element:
                return gen
        return element
    
    def _get_seasonal_strength(self, element: str, month_branch: int) -> float:
        """Get seasonal strength bonus for element."""
        # Seasonal correspondence
        season_elements = {
            (1, 2): "Wood",      # Spring
            (4, 5): "Fire",      # Summer
            (7, 8): "Metal",     # Autumn
            (10, 11): "Water",   # Winter
            (3, 6, 9, 0): "Earth"  # Transitional months
        }
        
        for months, season_element in season_elements.items():
            if isinstance(months, tuple) and month_branch in months:
                return 10.0 if element == season_element else 0.0
            elif month_branch == months:
                return 5.0 if element == season_element else 0.0
        
        return 0.0
    
    def _determine_favorable_elements(
        self,
        day_master: Dict,
        elements: Dict
    ) -> List[str]:
        """Determine favorable elements based on chart balance."""
        dm_element = day_master["element"]
        dm_strength = elements["percentage"][dm_element]
        
        favorable = []
        
        if dm_strength > 35:  # Strong day master
            # Favor elements that release or control
            favorable.append(self.GENERATING_CYCLE[dm_element])  # Produced element
            favorable.append(self.CONTROLLING_CYCLE[dm_element])  # Controlled element
        else:  # Weak day master
            # Favor supporting elements
            favorable.append(dm_element)  # Same element
            favorable.append(self._get_generating_element(dm_element))  # Generating element
        
        return favorable
    
    def _calculate_luck_pillars(
        self,
        birth_datetime: datetime,
        month_pillar: Tuple[int, int],
        gender: str
    ) -> List[Dict]:
        """Calculate 10-year luck pillars (大运)."""
        luck_pillars = []
        
        # Determine forward or backward
        year_stem = month_pillar[0]
        is_yang_year = year_stem % 2 == 0
        forward = (is_yang_year and gender == "male") or (not is_yang_year and gender == "female")
        
        # Calculate starting age
        # Simplified - should calculate exact solar terms
        start_age = 5  # Placeholder
        
        # Generate luck pillars
        for i in range(8):  # 8 luck pillars = 80 years
            if forward:
                stem = (month_pillar[0] + i + 1) % 10
                branch = (month_pillar[1] + i + 1) % 12
            else:
                stem = (month_pillar[0] - i - 1) % 10
                branch = (month_pillar[1] - i - 1) % 12
            
            start_year = birth_datetime.year + start_age + (i * 10)
            end_year = start_year + 9
            
            luck_pillars.append({
                "pillar": self._format_pillar((stem, branch), "Luck"),
                "start_age": start_age + (i * 10),
                "end_age": start_age + (i * 10) + 9,
                "start_year": start_year,
                "end_year": end_year,
                "period": f"{start_year}-{end_year}"
            })
        
        return luck_pillars
    
    def _get_current_luck_pillar(
        self,
        birth_datetime: datetime,
        luck_pillars: List[Dict]
    ) -> Optional[Dict]:
        """Get current luck pillar."""
        current_year = datetime.now().year
        age = current_year - birth_datetime.year
        
        for pillar in luck_pillars:
            if pillar["start_age"] <= age <= pillar["end_age"]:
                return pillar
        
        return None
    
    def _analyze_personality(
        self,
        day_master: Dict,
        elements: Dict
    ) -> List[str]:
        """Analyze personality based on day master and elements."""
        traits = []
        
        # Day master element traits
        element_traits = {
            "Wood": ["Creative", "Benevolent", "Growth-oriented", "Flexible"],
            "Fire": ["Passionate", "Dynamic", "Charismatic", "Impulsive"],
            "Earth": ["Stable", "Reliable", "Practical", "Nurturing"],
            "Metal": ["Disciplined", "Organized", "Righteous", "Decisive"],
            "Water": ["Intelligent", "Adaptable", "Intuitive", "Diplomatic"]
        }
        
        dm_element = day_master["element"]
        traits.extend(element_traits.get(dm_element, []))
        
        # Modify based on strength
        if elements["percentage"][dm_element] > 40:
            traits.append("Strong-willed")
            traits.append("Independent")
        elif elements["percentage"][dm_element] < 20:
            traits.append("Cooperative")
            traits.append("Adaptive")
        
        return traits
    
    def _analyze_life_areas(self, *pillars) -> Dict[str, str]:
        """Analyze different life areas based on pillars."""
        year_pillar, month_pillar, day_pillar, hour_pillar = pillars
        
        return {
            "ancestry_family": "Based on Year Pillar - represents ancestors and early childhood",
            "parents_career": "Based on Month Pillar - represents parents and career",
            "self_marriage": "Based on Day Pillar - represents self and spouse",
            "children_legacy": "Based on Hour Pillar - represents children and later life"
        }