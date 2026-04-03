"""
Cultural Events Calendar service — static dataset of major festivals for 2026.

Returns cultural/religious events filtered by ethnicity tags and date range.
"""
from datetime import date
from typing import Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Static 2026 festival dataset
# ---------------------------------------------------------------------------

CULTURAL_EVENTS_2026: List[Dict] = [
    # ── Tamil Hindu ────────────────────────────────────────────────────────
    {
        "name": "Pongal",
        "date_2026": "2026-01-14",
        "end_date_2026": "2026-01-17",
        "ethnicity_tags": ["Tamil Hindu"],
        "tradition": "Hindu",
        "description": "Tamil harvest festival celebrating the Sun god",
        "significance": "Marks the end of the winter solstice and the beginning of Uttaraayanam, the Sun's northward journey. A four-day celebration of gratitude for agriculture and nature.",
        "rituals": ["Cook Pongal dish in new pot", "Decorate with kolam", "Thank cattle on Maattu Pongal", "Visit family on Kaanum Pongal"],
        "astrological_significance": "Sun enters Makara (Capricorn) — Makar Sankranti",
    },
    {
        "name": "Thai Poosam",
        "date_2026": "2026-02-03",
        "end_date_2026": None,
        "ethnicity_tags": ["Tamil Hindu"],
        "tradition": "Hindu",
        "description": "Festival dedicated to Lord Murugan",
        "significance": "Celebrates the day Goddess Parvati gave Lord Murugan the Vel (divine lance) to vanquish evil. Major kavadi processions at Murugan temples.",
        "rituals": ["Kavadi bearing", "Milk pot offerings", "Fasting and prayer", "Visit Murugan temples"],
        "astrological_significance": "Full Moon (Poornima) in the Tamil month of Thai, with Pushya nakshatra",
    },
    {
        "name": "Maha Shivaratri",
        "date_2026": "2026-02-15",
        "end_date_2026": None,
        "ethnicity_tags": ["Tamil Hindu", "North Indian Hindu"],
        "tradition": "Hindu",
        "description": "The great night of Lord Shiva",
        "significance": "Celebrates the cosmic dance of Lord Shiva. Devotees observe night-long vigil with fasting and worship.",
        "rituals": ["Night-long vigil", "Shiva Lingam abhishekam", "Chanting Om Namah Shivaya", "Fasting"],
        "astrological_significance": "Chaturdashi (14th day) of Krishna Paksha in Magha/Phalguna month",
    },
    {
        "name": "Tamil New Year (Puthandu)",
        "date_2026": "2026-04-14",
        "end_date_2026": None,
        "ethnicity_tags": ["Tamil Hindu"],
        "tradition": "Hindu",
        "description": "Tamil New Year marking the first day of the Tamil calendar",
        "significance": "Begins the Tamil month of Chithirai. Families read the Panchangam for the year's forecast and prepare a special platter of sweet, sour, bitter, salty, pungent, and astringent items.",
        "rituals": ["Read Panchangam predictions", "Prepare mango pachadi (six-taste dish)", "Visit temples", "Wear new clothes"],
        "astrological_significance": "Sun enters Mesha (Aries) — start of the Tamil solar calendar year",
    },
    {
        "name": "Chithirai Thiruvizha",
        "date_2026": "2026-04-24",
        "end_date_2026": "2026-05-08",
        "ethnicity_tags": ["Tamil Hindu"],
        "tradition": "Hindu",
        "description": "Grand festival at Madurai Meenakshi temple",
        "significance": "Celebrates the divine wedding of Goddess Meenakshi and Lord Sundareswarar (Shiva). One of the oldest and largest temple festivals in India.",
        "rituals": ["Witness the celestial wedding procession", "Visit Meenakshi Amman Temple", "Participate in chariot festivals"],
        "astrological_significance": "Celebrated during the Tamil month of Chithirai when the full moon aligns with the Chitra nakshatra",
    },
    {
        "name": "Aadi Perukku",
        "date_2026": "2026-08-02",
        "end_date_2026": None,
        "ethnicity_tags": ["Tamil Hindu"],
        "tradition": "Hindu",
        "description": "Festival celebrating the rising of river waters",
        "significance": "Marks the seasonal rise of the Kaveri and other rivers. A celebration of water, fertility, and nature's abundance in the month of Aadi.",
        "rituals": ["Offer prayers near rivers", "Cook sweet pongal by riverbanks", "Women perform special pujas", "Float lamps in water"],
        "astrological_significance": "18th day of the Tamil month of Aadi, associated with the monsoon season",
    },
    {
        "name": "Vinayagar Chaturthi",
        "date_2026": "2026-08-22",
        "end_date_2026": None,
        "ethnicity_tags": ["Tamil Hindu", "North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Birthday of Lord Ganesha, remover of obstacles",
        "significance": "Celebrates the birth of Lord Ganesha. Clay idols are installed, worshipped, and immersed in water after the festival period.",
        "rituals": ["Install Ganesha idol", "Offer modak sweets", "Chant Ganesha mantras", "Idol immersion (visarjan)"],
        "astrological_significance": "Shukla Chaturthi in the month of Bhadrapada",
    },
    {
        "name": "Navaratri",
        "date_2026": "2026-10-01",
        "end_date_2026": "2026-10-10",
        "ethnicity_tags": ["Tamil Hindu", "North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Nine nights celebrating the divine feminine (Shakti)",
        "significance": "Nine nights dedicated to Durga, Lakshmi, and Saraswati. In Tamil Nadu, families arrange Golu (doll display) and exchange gifts.",
        "rituals": ["Set up Golu display", "Daily pujas to different forms of Devi", "Saraswati Puja on day 9", "Vijayadashami on day 10"],
        "astrological_significance": "Shukla Paksha of Ashvin month, aligned with autumn equinox energy",
    },
    {
        "name": "Deepavali",
        "date_2026": "2026-10-19",
        "end_date_2026": None,
        "ethnicity_tags": ["Tamil Hindu", "North Indian Hindu", "Jain"],
        "tradition": "Hindu",
        "description": "Festival of lights — triumph of light over darkness",
        "significance": "Celebrates the return of Lord Rama to Ayodhya. In South India, commemorates Krishna's victory over Narakasura. Jains celebrate Mahavira's attainment of Moksha.",
        "rituals": ["Oil bath at dawn", "Light diyas and lamps", "Burst firecrackers", "Exchange sweets and gifts"],
        "astrological_significance": "Amavasya (new moon) in the month of Ashvin/Kartik",
    },
    {
        "name": "Karthigai Deepam",
        "date_2026": "2026-12-04",
        "end_date_2026": None,
        "ethnicity_tags": ["Tamil Hindu"],
        "tradition": "Hindu",
        "description": "Festival of lamps in the Tamil month of Karthigai",
        "significance": "Celebrates Lord Shiva appearing as an infinite column of light. The Maha Deepam is lit on Tiruvannamalai hill, visible for miles.",
        "rituals": ["Light rows of oil lamps at home", "Visit Tiruvannamalai temple", "Prepare special sweets"],
        "astrological_significance": "Full moon in the month of Karthigai, with Krittika nakshatra",
    },
    {
        "name": "Skanda Sashti",
        "date_2026": "2026-11-20",
        "end_date_2026": "2026-11-25",
        "ethnicity_tags": ["Tamil Hindu"],
        "tradition": "Hindu",
        "description": "Six-day festival celebrating Lord Murugan's victory over Surapadman",
        "significance": "Commemorates Lord Murugan's battle and victory over the demon Surapadman. The Soorasamharam (destruction of evil) is enacted on the final day.",
        "rituals": ["Six-day fasting", "Recite Kanda Sashti Kavasam", "Watch Soorasamharam enactment", "Visit Murugan temples"],
        "astrological_significance": "Shukla Sashti in the Tamil month of Aippasi/Karthigai",
    },

    # ── North Indian Hindu ─────────────────────────────────────────────────
    {
        "name": "Lohri",
        "date_2026": "2026-01-13",
        "end_date_2026": None,
        "ethnicity_tags": ["North Indian Hindu", "Sikh"],
        "tradition": "Hindu",
        "description": "Punjabi winter bonfire festival",
        "significance": "Marks the end of winter and the longest night. Celebrated with bonfires, singing, and dancing to welcome the harvest season.",
        "rituals": ["Light bonfire", "Sing Lohri folk songs", "Distribute rewri and peanuts", "Dance bhangra and giddha"],
        "astrological_significance": "Eve of Makar Sankranti — Sun's transition to Capricorn",
    },
    {
        "name": "Makar Sankranti",
        "date_2026": "2026-01-14",
        "end_date_2026": None,
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Harvest festival marking the Sun's entry into Capricorn",
        "significance": "One of the few Hindu festivals based on the solar calendar. Celebrates the Sun's northward journey (Uttaraayanam).",
        "rituals": ["Fly kites", "Take holy bath in rivers", "Eat til-gur (sesame-jaggery) sweets", "Donate to the needy"],
        "astrological_significance": "Sun enters Makara (Capricorn) — beginning of Uttaraayanam",
    },
    {
        "name": "Holi",
        "date_2026": "2026-03-10",
        "end_date_2026": "2026-03-11",
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Festival of colors celebrating spring and love",
        "significance": "Celebrates the victory of Prahlada over Holika and the divine love of Radha and Krishna. People play with colored powders and water.",
        "rituals": ["Holika Dahan bonfire", "Play with colors (gulal)", "Drink thandai/bhang", "Feast and celebrate with community"],
        "astrological_significance": "Full Moon (Purnima) in the month of Phalguna",
    },
    {
        "name": "Ram Navami",
        "date_2026": "2026-04-02",
        "end_date_2026": None,
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Birthday of Lord Rama, the seventh avatar of Vishnu",
        "significance": "Celebrates the birth of Lord Rama in Ayodhya. Devotees fast, read the Ramayana, and visit temples.",
        "rituals": ["Fast until noon", "Read Ramayana", "Visit Rama temples", "Community kirtan"],
        "astrological_significance": "Shukla Navami in the month of Chaitra — considered an auspicious day",
    },
    {
        "name": "Raksha Bandhan",
        "date_2026": "2026-08-11",
        "end_date_2026": None,
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Festival celebrating the bond between brothers and sisters",
        "significance": "Sisters tie a protective thread (rakhi) on brothers' wrists, symbolising love and protection.",
        "rituals": ["Sister ties rakhi", "Brother gives gifts/money", "Special family meal", "Perform aarti"],
        "astrological_significance": "Full Moon (Purnima) in the month of Shravana",
    },
    {
        "name": "Janmashtami",
        "date_2026": "2026-08-25",
        "end_date_2026": None,
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Birthday of Lord Krishna, the eighth avatar of Vishnu",
        "significance": "Celebrates Krishna's birth at midnight in Mathura. One of the most widely celebrated festivals across India.",
        "rituals": ["Fast until midnight", "Midnight puja and celebration", "Dahi Handi (curd pot breaking)", "Sing Krishna bhajans"],
        "astrological_significance": "Ashtami of Krishna Paksha in the month of Bhadrapada, Rohini nakshatra",
    },
    {
        "name": "Dussehra (Vijayadashami)",
        "date_2026": "2026-10-10",
        "end_date_2026": None,
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Victory of good over evil — Rama's triumph over Ravana",
        "significance": "Marks Lord Rama's victory over the demon king Ravana. Effigies of Ravana are burned across North India.",
        "rituals": ["Watch Ramlila performances", "Burn Ravana effigies", "Worship weapons and tools", "Start new ventures"],
        "astrological_significance": "Dashami of Shukla Paksha in Ashvin month — Vijayadashami muhurta",
    },
    {
        "name": "Karva Chauth",
        "date_2026": "2026-10-15",
        "end_date_2026": None,
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Married women fast for their husbands' longevity",
        "significance": "A day-long nirjala (waterless) fast observed by married women. The fast is broken after sighting the moon through a sieve.",
        "rituals": ["Pre-dawn sargi meal", "Day-long fast without water", "Evening puja with karva", "Break fast after moonrise"],
        "astrological_significance": "Chaturthi of Krishna Paksha in Kartik month",
    },
    {
        "name": "Diwali",
        "date_2026": "2026-10-19",
        "end_date_2026": "2026-10-23",
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Five-day festival of lights — the biggest Hindu celebration",
        "significance": "Celebrates Lord Rama's return to Ayodhya, Lakshmi Puja for prosperity, and the triumph of light over darkness.",
        "rituals": ["Dhanteras shopping", "Lakshmi-Ganesh puja", "Light diyas and candles", "Exchange sweets and gifts", "Govardhan Puja", "Bhai Dooj"],
        "astrological_significance": "Amavasya in Kartik month — new moon surrounded by five auspicious days",
    },
    {
        "name": "Chhath Puja",
        "date_2026": "2026-10-25",
        "end_date_2026": "2026-10-26",
        "ethnicity_tags": ["North Indian Hindu"],
        "tradition": "Hindu",
        "description": "Ancient Vedic festival dedicated to the Sun god and Chhathi Maiya",
        "significance": "One of the most rigorous Hindu fasts. Devotees stand in water to offer prayers to the setting and rising Sun.",
        "rituals": ["36-hour nirjala fast", "Standing in water at sunset and sunrise", "Offer thekua and fruits to Sun", "Community celebration"],
        "astrological_significance": "Sashti of Shukla Paksha in Kartik month — direct Sun worship",
    },

    # ── Bengali Hindu ──────────────────────────────────────────────────────
    {
        "name": "Saraswati Puja",
        "date_2026": "2026-01-24",
        "end_date_2026": None,
        "ethnicity_tags": ["Bengali Hindu"],
        "tradition": "Hindu",
        "description": "Worship of Goddess Saraswati, deity of knowledge and arts",
        "significance": "Students and artists worship Saraswati for blessings in learning, music, and the arts. Books and instruments are placed at the deity's feet.",
        "rituals": ["Install Saraswati idol", "Place books and instruments for blessing", "Wear yellow clothes", "Community puja"],
        "astrological_significance": "Vasant Panchami — Shukla Panchami of Magha month",
    },
    {
        "name": "Durga Puja",
        "date_2026": "2026-10-01",
        "end_date_2026": "2026-10-05",
        "ethnicity_tags": ["Bengali Hindu"],
        "tradition": "Hindu",
        "description": "Grand five-day celebration of Goddess Durga's victory over Mahishasura",
        "significance": "The most important festival for Bengali Hindus. Elaborate pandals (temporary structures) house artistic Durga idols. Culminates in Vijaya Dashami immersion.",
        "rituals": ["Pandal hopping", "Pushpanjali (flower offering)", "Dhunuchi dance", "Sindoor Khela on Dashami", "Idol immersion"],
        "astrological_significance": "Shukla Paksha Shashthi to Dashami in Ashvin month",
    },
    {
        "name": "Kali Puja",
        "date_2026": "2026-10-19",
        "end_date_2026": None,
        "ethnicity_tags": ["Bengali Hindu"],
        "tradition": "Hindu",
        "description": "Worship of Goddess Kali on Diwali night",
        "significance": "Bengalis worship Goddess Kali instead of Lakshmi on the Diwali Amavasya night. Midnight tantric rituals are performed.",
        "rituals": ["Midnight puja", "Offer hibiscus flowers", "Light lamps and firecrackers", "Tantric rituals at temples"],
        "astrological_significance": "Amavasya of Kartik month — darkest night for invoking Kali's power",
    },
    {
        "name": "Poila Boishakh (Bengali New Year)",
        "date_2026": "2026-04-15",
        "end_date_2026": None,
        "ethnicity_tags": ["Bengali Hindu"],
        "tradition": "Hindu",
        "description": "Bengali New Year — first day of the Bengali calendar",
        "significance": "Marks the start of the Bengali calendar year. Businesses open new account books (Halkhata) and cultural processions take place.",
        "rituals": ["Halkhata (new ledger)", "Mangal Shobhajatra procession", "Wear new clothes", "Community feast"],
        "astrological_significance": "First day of the month of Boishakh in the Bengali solar calendar",
    },

    # ── Buddhist ───────────────────────────────────────────────────────────
    {
        "name": "Magha Puja",
        "date_2026": "2026-02-12",
        "end_date_2026": None,
        "ethnicity_tags": ["Buddhist"],
        "tradition": "Buddhist",
        "description": "Commemorates Buddha's spontaneous gathering of 1,250 enlightened monks",
        "significance": "One of the three most important Buddhist festivals. Buddha delivered the Ovadhapatimokha (fundamental teachings) to the assembled monks.",
        "rituals": ["Visit temple at dawn", "Make merit and offerings", "Candlelight circumambulation", "Meditation and reflection"],
        "astrological_significance": "Full Moon of the third lunar month (Magha)",
    },
    {
        "name": "Vesak (Buddha Purnima)",
        "date_2026": "2026-05-12",
        "end_date_2026": None,
        "ethnicity_tags": ["Buddhist"],
        "tradition": "Buddhist",
        "description": "Celebrates the birth, enlightenment, and passing of Gautama Buddha",
        "significance": "The most sacred Buddhist holiday. Commemorates the three major events in Buddha's life that all occurred on a full moon day.",
        "rituals": ["Visit temples and monasteries", "Offer flowers, candles, and incense", "Meditate and observe precepts", "Acts of generosity and kindness"],
        "astrological_significance": "Full Moon of Vaishakha month — highly auspicious in Buddhist cosmology",
    },
    {
        "name": "Asalha Puja",
        "date_2026": "2026-07-10",
        "end_date_2026": None,
        "ethnicity_tags": ["Buddhist"],
        "tradition": "Buddhist",
        "description": "Commemorates Buddha's first sermon (Dhammacakkappavattana Sutta)",
        "significance": "Marks the day Buddha delivered his first teaching at the Deer Park in Sarnath, setting the Wheel of Dharma in motion.",
        "rituals": ["Temple visit and sermon", "Candle procession", "Begin Vassa (rain retreat)", "Meditation practice"],
        "astrological_significance": "Full Moon of the eighth lunar month (Asalha)",
    },

    # ── Sikh ───────────────────────────────────────────────────────────────
    {
        "name": "Baisakhi",
        "date_2026": "2026-04-13",
        "end_date_2026": "2026-04-14",
        "ethnicity_tags": ["Sikh"],
        "tradition": "Sikh",
        "description": "Sikh New Year and founding of the Khalsa",
        "significance": "Commemorates the founding of the Khalsa by Guru Gobind Singh in 1699. Also a harvest festival in Punjab.",
        "rituals": ["Visit Gurdwara", "Nagar Kirtan (procession)", "Community langar", "Bhangra and folk celebrations"],
        "astrological_significance": "Solar New Year — Sun enters Mesha (Aries)",
    },
    {
        "name": "Guru Nanak Jayanti",
        "date_2026": "2026-11-08",
        "end_date_2026": None,
        "ethnicity_tags": ["Sikh"],
        "tradition": "Sikh",
        "description": "Birthday of Guru Nanak Dev Ji, founder of Sikhism",
        "significance": "Celebrates the birth of the first Sikh Guru. Prabhat Pheris (early morning processions) and 48-hour Akhand Path readings precede the day.",
        "rituals": ["Prabhat Pheri procession", "Akhand Path reading", "Community langar", "Kirtan at Gurdwara"],
        "astrological_significance": "Full Moon of Kartik month (Kartik Purnima)",
    },

    # ── Jain ───────────────────────────────────────────────────────────────
    {
        "name": "Mahavir Jayanti",
        "date_2026": "2026-04-06",
        "end_date_2026": None,
        "ethnicity_tags": ["Jain"],
        "tradition": "Jain",
        "description": "Birthday of Lord Mahavira, the 24th Tirthankara",
        "significance": "Celebrates the birth of Vardhamana Mahavira, the last and most prominent Tirthankara of Jainism.",
        "rituals": ["Abhisheka of Mahavira idol", "Rath Yatra (chariot procession)", "Charitable acts", "Recitation of Mahavira's teachings"],
        "astrological_significance": "Shukla Trayodashi of Chaitra month",
    },
    {
        "name": "Paryushana",
        "date_2026": "2026-08-20",
        "end_date_2026": "2026-08-28",
        "ethnicity_tags": ["Jain"],
        "tradition": "Jain",
        "description": "Eight-day festival of spiritual purification and forgiveness",
        "significance": "The most important Jain festival. Eight days of fasting, scripture study, and self-reflection culminating in Samvatsari (universal forgiveness day).",
        "rituals": ["Fasting (some observe complete fast)", "Daily scripture reading", "Pratikramana (self-reflection)", "Seek and grant forgiveness on Samvatsari"],
        "astrological_significance": "Occurs during Bhadrapada month — a period of introspection",
    },
    {
        "name": "Diwali (Jain)",
        "date_2026": "2026-10-19",
        "end_date_2026": None,
        "ethnicity_tags": ["Jain"],
        "tradition": "Jain",
        "description": "Marks Lord Mahavira's attainment of Moksha (liberation)",
        "significance": "For Jains, Diwali commemorates the final liberation of Lord Mahavira at Pavapuri. Lights symbolise the light of knowledge.",
        "rituals": ["Light lamps for knowledge", "Recite Mahavira's last sermon", "Visit Jain temples", "New Year begins next day (Annakut)"],
        "astrological_significance": "Amavasya of Kartik — Mahavira's nirvana day",
    },

    # ── Muslim (2026 dates are approximate — based on Islamic lunar calendar) ──
    {
        "name": "Eid al-Fitr",
        "date_2026": "2026-03-20",
        "end_date_2026": "2026-03-21",
        "ethnicity_tags": ["Muslim"],
        "tradition": "Islam",
        "description": "Festival of breaking the fast, marking the end of Ramadan",
        "significance": "Celebrated at the end of the holy month of Ramadan. A day of gratitude, charity, and communal prayer.",
        "rituals": ["Eid prayer at mosque", "Give Zakat al-Fitr (charity)", "Wear new clothes", "Feast and visit family"],
        "astrological_significance": "First day of Shawwal — sighting of the new crescent moon",
    },
    {
        "name": "Eid al-Adha",
        "date_2026": "2026-05-27",
        "end_date_2026": "2026-05-29",
        "ethnicity_tags": ["Muslim"],
        "tradition": "Islam",
        "description": "Festival of sacrifice commemorating Ibrahim's devotion",
        "significance": "Commemorates Prophet Ibrahim's willingness to sacrifice his son as an act of obedience to God. Coincides with the Hajj pilgrimage.",
        "rituals": ["Eid prayer", "Qurbani (animal sacrifice)", "Distribute meat to needy", "Visit family and friends"],
        "astrological_significance": "10th of Dhul Hijjah — during the Hajj pilgrimage",
    },
    {
        "name": "Muharram (Ashura)",
        "date_2026": "2026-06-26",
        "end_date_2026": None,
        "ethnicity_tags": ["Muslim"],
        "tradition": "Islam",
        "description": "Day of mourning commemorating the martyrdom of Imam Hussain",
        "significance": "The 10th of Muharram (Ashura) marks the martyrdom of Imam Hussain at Karbala. A solemn day of reflection and mourning.",
        "rituals": ["Fasting (Sunni)", "Mourning processions (Shia)", "Recitation of Hussain's story", "Acts of charity"],
        "astrological_significance": "10th of Muharram — first month of the Islamic calendar",
    },
    {
        "name": "Milad un-Nabi (Mawlid)",
        "date_2026": "2026-09-04",
        "end_date_2026": None,
        "ethnicity_tags": ["Muslim"],
        "tradition": "Islam",
        "description": "Birthday of Prophet Muhammad (PBUH)",
        "significance": "Celebrates the birth of Prophet Muhammad. Observed with prayers, processions, and gatherings recounting the Prophet's life.",
        "rituals": ["Special prayers and dhikr", "Naat recitation", "Community gatherings", "Charity and feeding the poor"],
        "astrological_significance": "12th of Rabi ul-Awal — third month of the Islamic calendar",
    },

    # ── Christian ──────────────────────────────────────────────────────────
    {
        "name": "Good Friday",
        "date_2026": "2026-04-03",
        "end_date_2026": None,
        "ethnicity_tags": ["Christian"],
        "tradition": "Christian",
        "description": "Commemorates the crucifixion and death of Jesus Christ",
        "significance": "A solemn day of mourning and reflection on the sacrifice of Jesus. Observed with fasting and church services.",
        "rituals": ["Attend church service", "Stations of the Cross", "Fasting and abstinence", "Quiet reflection"],
        "astrological_significance": None,
    },
    {
        "name": "Easter",
        "date_2026": "2026-04-05",
        "end_date_2026": None,
        "ethnicity_tags": ["Christian"],
        "tradition": "Christian",
        "description": "Celebrates the resurrection of Jesus Christ",
        "significance": "The most important Christian festival. Celebrates Jesus rising from the dead three days after crucifixion.",
        "rituals": ["Sunrise service", "Easter Mass", "Easter egg hunts", "Family feast"],
        "astrological_significance": None,
    },
    {
        "name": "Christmas",
        "date_2026": "2026-12-25",
        "end_date_2026": None,
        "ethnicity_tags": ["Christian"],
        "tradition": "Christian",
        "description": "Celebrates the birth of Jesus Christ",
        "significance": "Commemorates the nativity of Jesus in Bethlehem. A global celebration of love, giving, and family.",
        "rituals": ["Midnight Mass / Christmas service", "Exchange gifts", "Christmas feast", "Carol singing"],
        "astrological_significance": None,
    },
]


class CulturalEventsService:
    """Service to query cultural/religious events from a static 2026 dataset."""

    def get_events(
        self,
        ethnicity: Optional[List[str]] = None,
        year: int = 2026,
        month: Optional[int] = None,
    ) -> List[Dict]:
        """Return events filtered by ethnicity tags and optional month.

        Args:
            ethnicity: List of ethnicity tags to filter on (e.g. ["Tamil Hindu", "Buddhist"]).
                       If None or empty, all events are returned.
            year: Calendar year. Currently only 2026 data is available.
            month: Optional month (1-12) to filter events.

        Returns:
            List of event dicts sorted by start date.
        """
        if year != 2026:
            logger.info("cultural_events_requested_for_unsupported_year", year=year)
            return []

        events = CULTURAL_EVENTS_2026

        # Filter by ethnicity
        if ethnicity:
            ethnicity_lower = {e.lower() for e in ethnicity}
            events = [
                evt
                for evt in events
                if any(tag.lower() in ethnicity_lower for tag in evt["ethnicity_tags"])
            ]

        # Filter by month
        if month:
            events = [
                evt
                for evt in events
                if self._event_in_month(evt, month)
            ]

        # Sort by start date
        events = sorted(events, key=lambda e: e["date_2026"])

        return events

    @staticmethod
    def _event_in_month(event: Dict, month: int) -> bool:
        """Check whether an event falls within the given month."""
        start = date.fromisoformat(event["date_2026"])
        if start.month == month:
            return True
        end_str = event.get("end_date_2026")
        if end_str:
            end = date.fromisoformat(end_str)
            # Event spans into this month
            if start.month < month <= end.month:
                return True
        return False
