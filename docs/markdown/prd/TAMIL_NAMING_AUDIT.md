# Tamil Phonetic Transliteration Audit — Canonical Astrological Entities

**Purpose:** This document is the canonical, durable reference for Tamil phonetic (Roman-letter) transliteration of every astrological entity Josi displays to B2C users and astrologer-facing surfaces. It implements the language display policy: **Sanskrit-IAST (canonical, for internal/API) + Tamil phonetic transliteration (Roman letters, for UI)** — Tamil script is listed only for audit completeness and is NOT displayed.

**Policy reference:** See `DECISIONS.md` §1.5 (Language Display Policy) for the locked decision.

**Transliteration conventions used here:**
- Phonetic Roman spellings as naturally written in Tamil-English published panchangams (Vakya / Nirayana / Drik Tamil / AstroVed Tamil / agathiyarmaharishi).
- NOT IAST diacritics; NOT Hindi transliteration.
- Where a Tamil-specific term supersedes Sanskrit, the Tamil term is used (e.g., *Emakandam* for *Yamagaṇḍa*, *Kuligai* for *Gulika Kāla*, *Nazhigai* for *ghaṭi*).
- English gloss is documentation-only and is **not displayed to end users**.
- Entries flagged **[AMBIG]** have more than one commonly-published Tamil spelling; the primary form is listed first, alternates noted.

---

## 1. Nakshatras (27 + Abhijit)

| IAST | Tamil Phonetic | Tamil Script | English Gloss |
|---|---|---|---|
| Aśvinī | Aswini | அசுவினி | "Horse-headed twins"; 1st nakshatra |
| Bharaṇī | Bharani | பரணி | "Bearer"; ruled by Yama |
| Kṛttikā | Karthikai | கார்த்திகை | "The cutters"; Pleiades |
| Rohiṇī | Rohini | ரோகிணி | "The red one"; Aldebaran |
| Mṛgaśīrā | Mirugasirsham | மிருகசீரிடம் | "Deer-head"; [AMBIG: also *Mrigasheersham*, *Mirugasirisham*] |
| Ārdrā | Thiruvathirai | திருவாதிரை | "The moist one"; Betelgeuse (Tamil name supersedes) |
| Punarvasu | Punarpoosam | புனர்பூசம் | "Return of light"; [AMBIG: also *Punarvasu*] |
| Puṣya | Poosam | பூசம் | "Nourisher" |
| Āśleṣā | Ayilyam | ஆயில்யம் | "The entwiner" (Tamil name supersedes) |
| Maghā | Magham | மகம் | "The mighty"; Regulus |
| Pūrva Phalgunī | Pooram | பூரம் | "Former reddish one" |
| Uttara Phalgunī | Uthiram | உத்திரம் | "Latter reddish one" |
| Hasta | Hastham | ஹஸ்தம் | "The hand" [AMBIG: also *Astham*] |
| Citrā | Chithirai | சித்திரை | "The bright one"; Spica |
| Svāti | Swathi | சுவாதி | "The independent"; Arcturus |
| Viśākhā | Visakam | விசாகம் | "Forked branches" [AMBIG: also *Vishakam*] |
| Anurādhā | Anusham | அனுஷம் | "Following Radha" (Tamil name supersedes) |
| Jyeṣṭhā | Kettai | கேட்டை | "The eldest" (Tamil name supersedes) |
| Mūla | Moolam | மூலம் | "The root" |
| Pūrva Āṣāḍhā | Pooradam | பூராடம் | "Former invincible" |
| Uttara Āṣāḍhā | Uthiradam | உத்திராடம் | "Latter invincible" |
| Śravaṇa | Thiruvonam | திருவோணம் | "The hearing" (Tamil name supersedes) |
| Dhaniṣṭhā | Avittam | அவிட்டம் | "Most wealthy" (Tamil name supersedes) |
| Śatabhiṣā | Sathayam | சதயம் | "Hundred healers" [AMBIG: also *Sadayam*] |
| Pūrva Bhādrapadā | Pooratadhi | பூரட்டாதி | "Former lucky feet" |
| Uttara Bhādrapadā | Uthiratadhi | உத்திரட்டாதி | "Latter lucky feet" |
| Revatī | Revathi | ரேவதி | "The wealthy"; final nakshatra |
| Abhijit | Abhijit | அபிஜித் | "Victorious"; 28th (SBC/muhurta only) |

---

## 2. Rasis (12 Zodiac Signs)

| IAST | Tamil Phonetic | Tamil Script | English Gloss |
|---|---|---|---|
| Meṣa | Mesham | மேஷம் | Aries |
| Vṛṣabha | Rishabam | ரிஷபம் | Taurus |
| Mithuna | Mithunam | மிதுனம் | Gemini |
| Karka | Kadagam | கடகம் | Cancer |
| Siṃha | Simmam | சிம்மம் | Leo |
| Kanyā | Kanni | கன்னி | Virgo |
| Tulā | Thulam | துலாம் | Libra |
| Vṛścika | Viruchigam | விருச்சிகம் | Scorpio |
| Dhanu | Dhanusu | தனுசு | Sagittarius |
| Makara | Magaram | மகரம் | Capricorn |
| Kumbha | Kumbam | கும்பம் | Aquarius |
| Mīna | Meenam | மீனம் | Pisces |

---

## 3. Grahas (9 Planets)

| IAST | Tamil Phonetic | Tamil Script | English Gloss |
|---|---|---|---|
| Sūrya | Sooriyan | சூரியன் | Sun |
| Candra | Chandran | சந்திரன் | Moon |
| Maṅgala (Kuja) | Sevvai | செவ்வாய் | Mars (Tamil name supersedes; alt: *Angarakan*) |
| Budha | Budhan | புதன் | Mercury |
| Bṛhaspati (Guru) | Guru | குரு | Jupiter (alt: *Viyalan*) |
| Śukra | Sukran | சுக்கிரன் | Venus |
| Śani | Sani | சனி | Saturn |
| Rāhu | Ragu | ராகு | North lunar node |
| Ketu | Kethu | கேது | South lunar node |

---

## 4. Vargas (16 Divisional Charts)

| IAST | Tamil Phonetic | Tamil Script | English Gloss |
|---|---|---|---|
| D1 Rāśi | Rasi | ராசி | Birth chart |
| D2 Horā | Horai (Tamil phonetic) / **Hora (Josi convention per DECISIONS §1.5 Hora exception)** | ஓரை | Wealth (2 parts) |
| D3 Drekkāṇa | Drekkanam | திரேக்காணம் | Siblings (3 parts) |
| D4 Caturthāṃśa | Chathurthamsam | சதுர்த்தாம்சம் | Fortune/assets (4) |
| D7 Saptāṃśa | Sapthamsam | சப்தாம்சம் | Children (7) |
| D9 Navāṃśa | Navamsam | நவாம்சம் | Spouse/dharma (9) |
| D10 Daśāṃśa | Dasamsam | தசாம்சம் | Career (10) |
| D12 Dvādaśāṃśa | Dwadasamsam | துவாதசாம்சம் | Parents (12) |
| D16 Ṣoḍaśāṃśa | Shodasamsam | ஷோடசாம்சம் | Vehicles/luxury (16) |
| D20 Viṃśāṃśa | Vimsamsam | விம்சாம்சம் | Spiritual practice (20) |
| D24 Caturviṃśāṃśa | Chathurvimsamsam | சதுர்விம்சாம்சம் | Education (24) |
| D27 Bhāṃśa | Bhamsam | பாம்சம் | Strength/weakness (27); alt *Saptavimsamsam* |
| D30 Triṃśāṃśa | Thrimsamsam | திரிம்சாம்சம் | Misfortunes (30) |
| D40 Khavedāṃśa | Khavedamsam | கவேதாம்சம் | Maternal legacy (40) |
| D45 Akṣavedāṃśa | Akshavedamsam | அக்ஷவேதாம்சம் | Paternal legacy (45) |
| D60 Ṣaṣṭyāṃśa | Shastiamsam | ஷஷ்டியாம்சம் | Past karma (60) |

---

## 5. Samvatsaras (60 Jovian Years)

| # | IAST | Tamil Phonetic | Tamil Script |
|---|---|---|---|
| 1 | Prabhava | Prabhava | பிரபவ |
| 2 | Vibhava | Vibhava | விபவ |
| 3 | Śukla | Sukla | சுக்ல |
| 4 | Pramoda | Pramoda / Pramodhootha | பிரமோதூத | [AMBIG: Tamil panchangams use *Pramodhoodha*] |
| 5 | Prajāpati | Prajapathi | பிரஜாபதி |
| 6 | Aṅgirasa | Angirasa | ஆங்கீரச |
| 7 | Śrīmukha | Srimukha | ஸ்ரீமுக | [AMBIG: also *Sreemukha*] |
| 8 | Bhāva | Bhava | பவ |
| 9 | Yuva | Yuva | யுவ |
| 10 | Dhātā | Dhatru | தாது |
| 11 | Īśvara | Eeswara | ஈஸ்வர |
| 12 | Bahudhānya | Bahudanya | பஹுதான்ய |
| 13 | Pramāthi | Pramathi | பிரமாதி |
| 14 | Vikrama | Vikrama | விக்ரம |
| 15 | Vṛṣa | Vrisha / Visu | விஷு | [AMBIG: Tamil Nadu publishes as *Visu*] |
| 16 | Citrabhānu | Chithrabanu | சித்ரபானு |
| 17 | Subhānu | Subanu / Swabanu | சுபானு | [AMBIG: also *Svabhanu*] |
| 18 | Tāraṇa | Tharana | தாரண |
| 19 | Pārthiva | Parthiva | பார்த்திவ |
| 20 | Vyaya | Vyaya | வியய |
| 21 | Sarvajit | Sarvajith | ஸர்வஜித் |
| 22 | Sarvadhārī | Sarvadhari | ஸர்வதாரி |
| 23 | Virodhi | Virodhi | விரோதி |
| 24 | Vikṛti | Vikruthi | விக்ருதி |
| 25 | Khara | Khara | கர |
| 26 | Nandana | Nandana | நந்தன |
| 27 | Vijaya | Vijaya | விஜய |
| 28 | Jaya | Jaya | ஜய |
| 29 | Manmatha | Manmatha | மன்மத |
| 30 | Durmukhī | Durmukhi | துர்முகி |
| 31 | Hevilambī | Hevilambi | ஹேவிளம்பி |
| 32 | Vilambī | Vilambi | விளம்பி |
| 33 | Vikārī | Vikari | விகாரி |
| 34 | Śārvarī | Sarvari | சார்வரி |
| 35 | Plava | Plava | பிலவ |
| 36 | Śubhakṛt | Subhakrit | சுபகிருது |
| 37 | Śobhakṛt | Sobhakrit | சோபகிருது |
| 38 | Krodhi | Krodhi | குரோதி |
| 39 | Viśvāvasu | Viswavasu | விஸ்வாவசு |
| 40 | Parābhava | Parabhava | பராபவ |
| 41 | Plavaṅga | Plavanga | பிலவங்க |
| 42 | Kīlaka | Keelaka | கீலக |
| 43 | Saumya | Saumya | சௌமிய |
| 44 | Sādhāraṇa | Sadharana | சாதாரண |
| 45 | Virodhikṛt | Virodhikrit | விரோதிகிருது |
| 46 | Paridhāvī | Paridhavi | பரிதாபி | [AMBIG: also *Paridhavi*] |
| 47 | Pramādi | Pramadhi / Pramathi | பிரமாதி |
| 48 | Ānanda | Ananda | ஆனந்த |
| 49 | Rākṣasa | Rakshasa | ராக்ஷஸ |
| 50 | Nala | Nala | நள |
| 51 | Piṅgala | Pingala | பிங்கள |
| 52 | Kālayukti | Kalayukthi | காளயுக்தி |
| 53 | Siddhārthī | Siddharthi | சித்தார்த்தி |
| 54 | Raudra | Raudra / Roudhri | ரௌத்ரி |
| 55 | Durmati | Durmathi | துர்மதி |
| 56 | Dundubhi | Dhundhubi | துந்துபி |
| 57 | Rudhirodgārī | Rudhirothgari | ருதிரோத்காரி |
| 58 | Raktākṣī | Raktakshi | ரக்தாக்ஷி |
| 59 | Krodhana | Krodhana | க்ரோதன |
| 60 | Akṣaya | Akshaya | அக்ஷய |

---

## 6. Tithis (30)

### Shukla Paksham (waxing)
| # | IAST | Tamil Phonetic | Tamil Script | Gloss |
|---|---|---|---|---|
| S1 | Prathamā | Prathamai | பிரதமை | 1st day |
| S2 | Dvitīyā | Dwithiyai | துவிதியை | 2nd |
| S3 | Tṛtīyā | Thrithiyai | திருதியை | 3rd |
| S4 | Caturthī | Chathurthi | சதுர்த்தி | 4th |
| S5 | Pañcamī | Panchami | பஞ்சமி | 5th |
| S6 | Ṣaṣṭhī | Shashti | சஷ்டி | 6th |
| S7 | Saptamī | Sapthami | சப்தமி | 7th |
| S8 | Aṣṭamī | Ashtami | அஷ்டமி | 8th |
| S9 | Navamī | Navami | நவமி | 9th |
| S10 | Daśamī | Dasami | தசமி | 10th |
| S11 | Ekādaśī | Ekadasi | ஏகாதசி | 11th |
| S12 | Dvādaśī | Dwadasi | துவாதசி | 12th |
| S13 | Trayodaśī | Thrayodasi | திரயோதசி | 13th |
| S14 | Caturdaśī | Chathurdasi | சதுர்த்தசி | 14th |
| S15 | Pūrṇimā | Pournami | பௌர்ணமி | Full moon |

### Krishna Paksham (waning)
Same 1–14 names prefixed "Krishna" in convention; Tamil publications typically label by number with *Tey Pirai*. Day 15 is *Amavasai*.

| # | IAST | Tamil Phonetic | Tamil Script | Gloss |
|---|---|---|---|---|
| K1–K14 | (as S1–S14) | Prathamai … Chathurdasi | (same) | Krishna paksha equivalents |
| K15 | Amāvāsyā | Amavasai | அமாவாசை | New moon |

---

## 7. Karanams (11)

| IAST | Tamil Phonetic | Tamil Script | Type |
|---|---|---|---|
| Bava | Bavam | பவம் | Movable |
| Bālava | Balavam | பாலவம் | Movable |
| Kaulava | Kaulavam | கௌலவம் | Movable |
| Taitila | Taitulam | தைதுலம் | Movable |
| Garaja | Garajai | கரசை | Movable |
| Vaṇija | Vanijam | வணிஜம் | Movable |
| Viṣṭi (Bhadra) | Vishti / Bhathirai | பத்திரை | Movable; Tamil: *Bhathirai* |
| Śakuni | Sakuni | சகுனி | Fixed |
| Catuṣpāda | Chathushpadam | சதுஷ்பாதம் | Fixed |
| Nāga | Nagavam | நாகவம் | Fixed |
| Kiṃstughna | Kimstugna | கிம்ஸ்துக்னம் | Fixed |

---

## 8. Yogams (27 Panchanga Yogas)

| # | IAST | Tamil Phonetic | Tamil Script |
|---|---|---|---|
| 1 | Viṣkambha | Vishkambam | விஷ்கம்பம் |
| 2 | Prīti | Preethi | ப்ரீதி |
| 3 | Āyuṣmān | Ayushman | ஆயுஷ்மான் |
| 4 | Saubhāgya | Saubhagyam | சௌபாக்யம் |
| 5 | Śobhana | Sobanam | சோபனம் |
| 6 | Atigaṇḍa | Athigandam | அதிகண்டம் |
| 7 | Sukarma | Sukarma | சுகர்மா |
| 8 | Dhṛti | Dhruthi | த்ருதி |
| 9 | Śūla | Soolam | சூலம் |
| 10 | Gaṇḍa | Gandam | கண்டம் |
| 11 | Vṛddhi | Vruddhi | விருத்தி |
| 12 | Dhruva | Dhruvam | துருவம் |
| 13 | Vyāghāta | Vyagadham | வியாகாதம் |
| 14 | Harṣaṇa | Harshanam | ஹர்ஷணம் |
| 15 | Vajra | Vajram | வஜ்ரம் |
| 16 | Siddhi | Siddhi | சித்தி |
| 17 | Vyatīpāta | Vyathipadam | வியதீபாதம் |
| 18 | Varīyān | Variyan | வரியன் |
| 19 | Parigha | Parigham | பரிகம் |
| 20 | Śiva | Sivam | சிவம் |
| 21 | Siddha | Siddham | சித்தம் |
| 22 | Sādhya | Sadhyam | சாத்யம் |
| 23 | Śubha | Subam | சுபம் |
| 24 | Śukla | Suklam | சுக்லம் |
| 25 | Brahma | Brahmam | ப்ரம்மம் |
| 26 | Indra | Indram | இந்திரம் |
| 27 | Vaidhṛti | Vaidhruthi | வைதிருதி |

---

## 9. Muhurtham Labels (30)

### Day Muhurtas (1–15)
| # | IAST | Tamil Phonetic | Tamil Script |
|---|---|---|---|
| 1 | Rudra | Rudhran | ருத்திரன் |
| 2 | Āhi | Aahi | ஆஹி |
| 3 | Mitra | Mithran | மித்ரன் |
| 4 | Pitṛ | Pithru | பித்ரு |
| 5 | Vasu | Vasu | வசு |
| 6 | Vārāha | Varaham | வராஹம் |
| 7 | Viśvedeva | Viswadeva | விஸ்வதேவ |
| 8 | Abhijit | Abhijit | அபிஜித் |
| 9 | Vidhātṛ | Vidhatru | விதாத்ரு |
| 10 | Indra | Indiran | இந்திரன் |
| 11 | Indrāgni | Indragni | இந்திராக்னி |
| 12 | Nirṛti | Nirruthi | நிருதி |
| 13 | Varuṇa | Varunan | வருணன் |
| 14 | Aryaman | Ariyaman | அர்யமன் |
| 15 | Bhaga | Bhagan | பகன் |

### Night Muhurtas (16–30)
| # | IAST | Tamil Phonetic | Tamil Script |
|---|---|---|---|
| 16 | Girīśa | Girisan | கிரீசன் |
| 17 | Ajapāda | Ajapadam | அஜபாதம் |
| 18 | Ahirbudhnya | Ahirbudhnyam | அஹிர்புத்ன்யம் |
| 19 | Pūṣā | Pooshan | பூஷன் |
| 20 | Aśvinī | Aswini | அசுவினி |
| 21 | Yama | Yaman | யமன் |
| 22 | Agni | Agni | அக்னி |
| 23 | Vidhātṛ (night) | Vidhatru-iravu | விதாத்ரு |
| 24 | Kaṇḍa | Kandam | கண்டம் |
| 25 | Aditi | Adhithi | அதிதி |
| 26 | Jīva-amṛta | Jeevamrutham | ஜீவாம்ருதம் |
| 27 | Viṣṇu | Vishnu | விஷ்ணு |
| 28 | Dyumad-gadyuti | Dyumadgadyuthi | த்யுமத்கத்யுதி | [AMBIG: rarely published in Tamil; use IAST transliterated] |
| 29 | Brahma | Brahmam | ப்ரம்மம் |
| 30 | Samudra | Samudhram | சமுத்ரம் |

---

## 10. Panchaka Subtypes (5)

Weekday mapping (Sun→Sat) in Tamil Nadu almanacs:
| IAST | Tamil Phonetic | Tamil Script | Weekday | Gloss |
|---|---|---|---|---|
| Roga | Roga Panchakam | ரோக பஞ்சகம் | Sunday | Illness |
| Rāja | Raja Panchakam | ராஜ பஞ்சகம் | Monday | Royal/favorable |
| Mṛtyu | Mrithyu Panchakam | மிருத்யு பஞ்சகம் | Tuesday | Death-risk |
| Agni | Agni Panchakam | அக்னி பஞ்சகம் | Wednesday/Sat | Fire |
| Chora | Chora Panchakam | சோர பஞ்சகம் | Friday | Theft |

*Note:* Weekday mapping varies by tradition; Tamil Vakya panchangam and North Indian sources differ. Flag at service layer, not UI.

---

## 11. Tamil-Specific Panchanga Terms

| Term | Tamil Phonetic | Tamil Script | Gloss |
|---|---|---|---|
| Pongal | Pongal | பொங்கல் | Tamil harvest festival (mid-Jan) |
| Tamil Puthandu | Tamil Puthandu | தமிழ் புத்தாண்டு | Tamil New Year (Chithirai 1) |
| Aadi Perukku | Aadi Perukku | ஆடி பெருக்கு | Aadi 18 — river-rising festival |
| Karthigai Deepam | Karthigai Deepam | கார்த்திகை தீபம் | Festival of lights on Karthikai nakshatra |
| Vishu | Vishu | விஷு | Malayali/Tamil New Year (Mesha sankranti) |
| Onam | Onam | ஓணம் | Kerala harvest festival (Thiruvonam nakshatra) |
| Baisakhi | Baisakhi | பைசாகி | Punjabi new year (Mesha sankranti) |
| Poila Boishakh | Poila Boishakh | பொய்லா பொய்ஷாக் | Bengali new year |
| Bestu Varsh | Bestu Varsh | பேஸ்டு வர்ஷ் | Gujarati new year |
| Labh Panchami | Labh Panchami | லாப் பஞ்சமி | Gujarati business new year |
| Gudi Padwa | Gudi Padwa | குடி பட்வா | Marathi new year |
| Nalla Neram | Nalla Neram | நல்ல நேரம் | "Good time"; daily auspicious windows |
| Kari Naal | Kari Naal | கரி நாள் | "Black day"; monthly inauspicious day |
| Lagna Nilai | Lagna Nilai | லக்ன நிலை | Ascendant position/status |
| Emakandam | Emakandam | எமகண்டம் | Yamagaṇḍa (Tamil supersedes Sanskrit) |
| Kuligai | Kuligai | குளிகை | Gulika Kāla (Tamil supersedes) |
| Pradosham | Pradosham | பிரதோஷம் | Twilight period — Trayodasi evening |
| Ekadasi | Ekadasi | ஏகாதசி | 11th tithi — fasting day |
| Pournami | Pournami | பௌர்ணமி | Full moon |
| Amavasai | Amavasai | அமாவாசை | New moon |
| Sankaranthi | Sankaranthi | சங்கராந்தி | Sun's entry into a rasi |
| Nazhigai | Nazhigai | நாழிகை | Tamil time unit (24 min) = *ghaṭi* |
| Rahu Kalam | Ragu Kalam | ராகு காலம் | Daily Rahu period |
| Yamagandam | Emakandam | எமகண்டம் | (alt spelling of above) |
| Gowri Panchangam | Gowri Panchangam | கௌரி பஞ்சாங்கம் | Tamil time-division system |

---

## 12. Dasa Systems

| IAST | Tamil Phonetic | Tamil Script | Gloss |
|---|---|---|---|
| Vimśottarī Daśā | Vimsothari Dasai | விம்சோத்தரி தசை | 120-year nakshatra-based dasa |
| Yoginī Daśā | Yogini Dasai | யோகினி தசை | 36-year dasa |
| Aṣṭottarī Daśā | Ashtothari Dasai | அஷ்டோத்தரி தசை | 108-year dasa |
| Cara Daśā | Chara Dasai | சர தசை | Jaimini sign-based dasa |
| Nārāyaṇa Daśā | Narayana Dasai | நாராயண தசை | Jaimini padakrama dasa |
| Kālacakra Daśā | Kalachakra Dasai | காலசக்ர தசை | Time-wheel dasa |
| Piṇḍa Āyur-daśā | Pinda Ayur-dasai | பிண்ட ஆயுர் தசை | Longevity dasa (planetary-mass based) |
| Aṃśa Āyur-daśā | Amsa Ayur-dasai | அம்ச ஆயுர் தசை | Longevity dasa (navamsa-based) |
| Naisargika Āyur-daśā | Naisargika Ayur-dasai | நைசர்கிக ஆயுர் தசை | Natural longevity dasa |
| Jaimini Āyur-daśā | Jaimini Ayur-dasai | ஜைமினி ஆயுர் தசை | Jaimini longevity method |

---

## 13. Shadbalam Components

### Six main balams
| IAST | Tamil Phonetic | Tamil Script | Gloss |
|---|---|---|---|
| Sthāna Bala | Sthana Balam | ஸ்தான பலம் | Positional strength |
| Dig Bala | Dik Balam | திக் பலம் | Directional strength |
| Kāla Bala | Kala Balam | கால பலம் | Temporal strength |
| Ceṣṭā Bala | Cheshta Balam | சேஷ்டா பலம் | Motional strength |
| Naisargika Bala | Naisargika Balam | நைசர்கிக பலம் | Natural/innate strength |
| Dṛk Bala | Drik Balam | திருக் பலம் | Aspectual strength |

### Sub-components
| IAST | Tamil Phonetic | Tamil Script |
|---|---|---|
| Uccha Bala | Uccha Balam | உச்ச பலம் |
| Saptavargaja Bala | Sapthavargaja Balam | சப்தவர்கஜ பலம் |
| Oja-Yugma Bala | Oja-Yugma Balam | ஓஜ-யுக்ம பலம் |
| Kendra Bala | Kendra Balam | கேந்திர பலம் |
| Drekkāṇa Bala | Drekkana Balam | திரேக்காண பலம் |
| Nata-Unnata Bala | Natha-Unnatha Balam | நத-உன்னத பலம் |
| Pakṣa Bala | Paksha Balam | பக்ஷ பலம் |
| Tribhāga Bala | Thribhaga Balam | த்ரிபாக பலம் |
| Varṣa Bala | Varsha Balam | வர்ஷ பலம் |
| Māsa Bala | Masa Balam | மாச பலம் |
| Dina Bala | Dina Balam | தின பலம் |
| Horā Bala | Horai Balam (phonetic) / **Hora Bala (Josi convention per DECISIONS §1.5 Hora exception)** | ஓரை பலம் |
| Ayana Bala | Ayana Balam | அயன பலம் |
| Yuddha Bala | Yuddha Balam | யுத்த பலம் |

---

## 14. Ashtakavargam Terms

| IAST | Tamil Phonetic | Tamil Script | Gloss |
|---|---|---|---|
| Bhinnāṣṭakavarga (BAV) | Binna Ashtakavargam | பின்ன அஷ்டகவர்கம் | Individual planet's 8-source score |
| Sarvāṣṭakavarga (SAV) | Sarva Ashtakavargam | ஸர்வ அஷ்டகவர்கம் | Combined 8-source score |
| Trikoṇa Śodhana | Thrikona Sodhanai | த்ரிகோண சோதனை | Triangular reduction |
| Ekādhipatya Śodhana | Ekadhipathya Sodhanai | ஏகாதிபத்ய சோதனை | Single-lordship reduction |
| Sodhya Piṇḍa | Sodhya Pindam | சோத்ய பிண்டம் | Reduced total |
| Graha Piṇḍa | Graha Pindam | கிரஹ பிண்டம் | Planet-sum |
| Rāśi Piṇḍa | Rasi Pindam | ராசி பிண்டம் | Sign-sum |
| Kakṣa Vibhāga | Kaksha Vibhagam | கக்ஷ விபாகம் | 8-division of each rasi |

---

## 15. Chart Yogas

### Pañca Mahāpuruṣa Yogas (5)
| IAST | Tamil Phonetic | Tamil Script | Planet |
|---|---|---|---|
| Rucaka Yoga | Ruchaka Yogam | ருசக யோகம் | Mars |
| Bhadra Yoga | Bhadra Yogam | பத்ர யோகம் | Mercury |
| Haṃsa Yoga | Hamsa Yogam | ஹம்ச யோகம் | Jupiter |
| Mālavya Yoga | Malavya Yogam | மாலவ்ய யோகம் | Venus |
| Śaśa Yoga | Sasa Yogam | சச யோகம் | Saturn |

### Candra Yogas (Moon-based)
| IAST | Tamil Phonetic | Tamil Script |
|---|---|---|
| Sunaphā | Sunabha Yogam | சுனபா யோகம் |
| Anaphā | Anabha Yogam | அனபா யோகம் |
| Durudharā | Dhuruthura Yogam | துருதுரா யோகம் |
| Kemadruma | Kemadhruma Yogam | கேமத்ரும யோகம் |

### Sūrya Yogas (Sun-based)
| IAST | Tamil Phonetic | Tamil Script |
|---|---|---|
| Veṣi | Veshi Yogam | வேஷி யோகம் |
| Voṣi | Voshi Yogam | வோஷி யோகம் |
| Ubhayacārī | Ubhayachari Yogam | உபயசாரி யோகம் |

### Other major yogas
| IAST | Tamil Phonetic | Tamil Script | Gloss |
|---|---|---|---|
| Rāja Yoga | Raja Yogam | ராஜ யோகம் | Royal/success combinations |
| Dhana Yoga | Dhana Yogam | தன யோகம் | Wealth combinations |
| Gaja-Kesari Yoga | Gaja-Kesari Yogam | கஜ கேசரி யோகம் | Jupiter-Moon kendra |
| Cāmara Yoga | Chamara Yogam | சாமர யோகம் | Royal-honor yoga |
| Śakaṭa Yoga | Sakata Yogam | சகட யோகம் | Moon-Jupiter 6/8 |
| Amala Yoga | Amala Yogam | அமல யோகம் | Benefic in 10th from Moon/Lagna |
| Pāriyātra Yoga | Pariyatra Yogam | பாரியாத்ர யோகம் | Classical dignity yoga |
| Nīca-Bhaṅga Rāja Yoga | Neecha-Banga Raja Yogam | நீச பங்க ராஜ யோகம் | Cancellation of debilitation |

---

## 16. Classical Source Texts

| IAST | Tamil Phonetic | Tamil Script | Abbr |
|---|---|---|---|
| Bṛhat Parāśara Horā Śāstra | Brihat Parasara Hora Sastram | பிருஹத் பராசர ஓரா சாஸ்திரம் | BPHS |
| Sārāvalī | Saravali | சாராவளி | — |
| Phaladīpikā | Phaladeepika | பலதீபிகா | — |
| Jātaka Pārijāta | Jataka Parijatham | ஜாதக பாரிஜாதம் | JP |
| Jaimini Upadeśa Sūtrāṇi | Jaimini Upadesa Suthram | ஜைமினி உபதேச சூத்ரம் | JUS |
| Muhūrta Cintāmaṇi | Muhurtha Chintamani | முஹூர்த்த சிந்தாமணி | MC |
| Nāradīya Saṃhitā | Naradiya Samhitai | நாரதீய சம்ஹிதை | NS |
| Kāḷaprakāśikā | Kalaprakasika | காலப்ரகாசிகா | KP |
| Praśna Mārga | Prasna Margam | பிரச்ன மார்கம் | PM |
| Uttara Kālāmṛta | Uttara Kalamrutham | உத்தர காலாம்ருதம் | UK |
| Tājaka Nīlakaṇṭhī | Tajaka Neelakanti | தாஜக நீலகண்டி | TN |
| Sūryasiddhānta | Soorya Siddhantam | சூர்ய சித்தாந்தம் | SS |

---

## Ambiguity Summary (entries needing editorial lock)

The following entries have two+ commonly-published Tamil spellings. Josi should **pick one and lock it** in a seed-data migration; the alternate is retained in notes only.

| Entity | Primary (recommended) | Alternate | Source bias |
|---|---|---|---|
| Mṛgaśīrā | **Mirugasirsham** | Mrigasheersham / Mirugasirisham | Vakya panchangam |
| Punarvasu | **Punarpoosam** | Punarvasu | Drik Tamil |
| Hasta | **Hastham** | Astham | AstroVed Tamil |
| Viśākhā | **Visakam** | Vishakam | Vakya |
| Śatabhiṣā | **Sathayam** | Sadayam | Drik Tamil |
| Samvatsara #4 Pramoda | **Pramodhootha** | Pramoda | Tamil Nadu govt panchangam |
| Samvatsara #7 Śrīmukha | **Srimukha** | Sreemukha | Split; Tamil Brahmin publications use *Sreemukha* |
| Samvatsara #15 Vṛṣa | **Visu** | Vrisha | TN panchangam override |
| Samvatsara #17 Subhānu | **Subanu** | Swabanu / Svabhanu | Drik Tamil primary |
| Samvatsara #46 Paridhāvī | **Paridhabi** | Paridhavi | Vakya |
| Samvatsara #54 Raudra | **Roudhri** | Raudra | Most Tamil publications use feminine form |
| Muhurta #28 Dyumad-gadyuti | **Dyumadgadyuthi** | (rare in Tamil; fall back to IAST-phonetic) | — |
| Guru | **Guru** | Viyalan | Weekday name uses *Viyalan*; planet uses *Guru* |
| Maṅgala | **Sevvai** | Angarakan / Mangal | *Sevvai* is weekday + planet |

---

## Implementation Notes

- **Display strings live in** `src/josi/core/i18n/tamil_phonetic.py` (or equivalent seed table). UI layer reads from this map by IAST canonical key.
- **API canonical** = IAST (diacritic-stripped ASCII) as documented in `DECISIONS.md` §1.5.
- **Astrologer-facing** screens show the Tamil phonetic string next to IAST in parentheses; B2C shows Tamil phonetic primary, IAST tooltip.
- **English gloss column in this file is reference-only** — per locked decision, it is NEVER displayed in UI.
- **Seed migration** should include `tamil_phonetic`, `tamil_script` (nullable), `iast_canonical` columns on each of: nakshatra, rasi, graha, varga, samvatsara, tithi, karana, yoga_panchanga, muhurta, panchaka, dasa_system, balam, ashtakavarga_term, chart_yoga, source_text.
- **Alembic migration title suggestion:** `"seed tamil phonetic names for canonical entities"`.

---

*End of audit. 76 PRDs reference entity names; this file is the single source of truth for the Tamil display layer.*
