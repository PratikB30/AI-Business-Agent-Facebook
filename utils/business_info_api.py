import requests
from bs4 import BeautifulSoup
import random, re

UserAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/139.0.7258.60 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.180 Mobile Safari/537.36'
]

def url_scrape(url):
    try:
        headers = {'user-agent': f"{random.choice(UserAgents)}"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
    title_1 = soup.title.string.strip() if soup.title else None
    title_2 = soup.find("meta", {"property": "og:site_name"})
    og_site_name = title_2.get("content") if title_2 else None
    title, cleaned_title = clean_title(title_1 or og_site_name)
    if not title:
        title = url
    
    text_content = soup.get_text(separator=' ', strip=True)
    
    industry = find_industry(title, cleaned_title, text_content)
    services = find_services(soup, text_content)
    tone = find_tone(text_content)
    
    return {
        "Name": title,
        "Industry": industry,
        "Services": services if services else "Not Found",
        "Tone of voice": tone
    }, 200
    
    
def clean_title(raw_title):
    if not raw_title:
        return None
    
    title = raw_title.strip()
    
    title = re.sub(r'#\w+', '', title)
    title = re.sub(r'[^\w\s\-\|–—•]', '', title) 
    cleaned_title = title.replace(" | ", " ").replace("|", " ").strip()
    title = re.split(r'\||-|–|—|•', title)[0]
    
    return title.strip(), cleaned_title

def find_industry(title, cleaned_title, text_content):
    industry_list = {
        "gym": "Fitness",
        "salon": "Beauty",
        "cafe": "Cafe",
        "coffee": "Cafe",
        "restaurant": "Restaurant",
        "law": "Legal",
        "real estate": "Real Estate",
        "hotel": "rooms",
        "hospital": "doctor"
    }
    
    industry = None
    business_title = title.lower()
    business_title1 = cleaned_title.lower()
    text_content = text_content.lower()
    
    for keyword, info in industry_list.items():
        if keyword in business_title1:
            industry = info
            break

    if industry is None:
        for keyword, info in industry_list.items():
            if keyword in text_content.lower():
                industry = info
                break
            
    if industry is None:
        industry = "Business"
        
    return industry

def find_services(soup, text_content):    
    fitness_keywords = [
        "training", "personal trainer", "class", "yoga", "zumba", "cycling", "spin",
        "crossfit", "physiotherapy", "recovery", "assessment", "weight loss",
        "weight gain", "transformation", "body composition"
    ]
    
    salon_keywords = [
        "haircut", "styling", "blow dry", "coloring", "highlight", "manicure", "pedicure",
        "facial", "massage", "threading", "waxing", "bridal", "makeup", "hair spa", "nail art"
    ]
    
    cafe_keywords = [
        "coffee", "tea", "pastry", "cake", "sandwich", "breakfast", "brunch",
        "smoothie", "latte", "espresso", "menu", "dessert", "vegan", "gluten-free", "specialty",
        "drinks", "food"
    ]
    
    restaurant_keywords = [
        "menu", "dinner", "lunch", "appetizer", "entrees", "dessert", "wine", "cocktail",
        "specials", "vegetarian", "vegan", "brunch", "burgers", "pizza",
        "tacos", "fast food", "fine dining", "organic", "seafood", "pasta", "salads"
    ]
    
    real_estate_keywords= [
        "real estate", "property", "home", "house", "apartment", "sale", "rent", "listing", 
        "agent", "broker", "mortgage", "sell", "investment property", "commercial property",
        "land", "real estate agent", "open house", "housing market", "property management"
    ]
    
    hotel_keywords = [
        "rooms", "booking", "suite", "luxury", "hospitality", "accommodation", "vacation", "stay",
        "check-in", "check-out", "reservation", "concierge", "pool", "spa", "breakfast included", "conference rooms"
    ]
    
    service_list = list(set(fitness_keywords+salon_keywords+cafe_keywords+restaurant_keywords+real_estate_keywords+hotel_keywords))
 
    services = set()
    for keyword in service_list:
        sections = soup.find_all(lambda tag: keyword.lower() in (tag.get("id", "") or "").lower() 
                                 or keyword.lower() in ' '.join(tag.get("class", [])).lower()
                                )
        for section in sections:
            items = section.find_all(['li', 'h3', 'p'])
            for item in items:
                text = item.get_text(strip=True)
                if 3 < len(text.split()) < 10:
                    services.add(text)
        
        if keyword.lower() in text_content.lower():
            services.add(keyword.title())
    
    services = sorted(list(services))
    return ", ".join(services) if services else "General Services"

def find_tone(text_content):
    tone_list = {
        "Friendly": ["welcome", "friendly", "enjoy", "fun", "smile", "hi", "hello", "join", "love", "happy", "comfortable"],
        "Professional": ["certified", "trusted", "professional", "expert", "experienced", "solutions", "team", "reliable", "quality", "trained"],
        "Luxury": ["exclusive", "premium", "luxury", "elegant", "refined", "high-end", "sophisticated", "tailored", "bespoke"],
        "Calm": ["relax", "calm", "peace", "soothing", "gentle", "tranquil", "unwind", "rejuvenate"],
        "Energetic": ["push", "power", "strong", "boost", "achieve", "results", "transform", "grind", "goal", "hustle", "fit", "train hard"],
        "Playful": ["yay", "woohoo", "let's go", "vibe", "cool", "awesome", "pop", "crazy", "quirky", "funny", "weird"],
        "Formal": ["solutions", "corporate", "compliance", "legal", "policy", "agreement", "terms", "respect", "confidential"]
    }

    tone_matches = {tone: 0 for tone in tone_list}
    for tone, keywords in tone_list.items():
        for keyword in keywords:
            tone_matches[tone] += text_content.lower().count(keyword)
            
    sorted_tones = sorted(tone_matches.items(), key=lambda x: -x[1])
    tone = [tone for tone, count in sorted_tones if count > 0][:2]
    if not tone:
        tone = ["Professional"]
        
    return tone[0] if tone else "Professional"