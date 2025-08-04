import requests
import random


def get_industry_news(industry):
    try:
        payload = {"industry": industry}
        # Use the correct endpoint on the same server
        response = requests.post("http://localhost:5000/api/news", json=payload, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            # Return some default news if the API fails
            return [
                f"Latest {industry} trends and developments",
                f"New innovations in {industry} sector",
                f"Industry insights for {industry} professionals",
                f"Breaking news in {industry}",
                f"Expert analysis on {industry} market"
            ]
    except Exception as e:
        # Return default news if request fails
        return [
            f"Latest {industry} trends and developments",
            f"New innovations in {industry} sector", 
            f"Industry insights for {industry} professionals",
            f"Breaking news in {industry}",
            f"Expert analysis on {industry} market"
        ]
    
def generate_content(profile, news, tone, post_type, frequency):
    business_name = profile['name']
    services = profile.get('services', [])

    tone_templates = {
        "professional": {
            "promo": "Discover how {service} can benefit your business with {business_name}.",
            "tip": "Pro tip: {tip} — straight from the experts at {business_name}.",
            "update": "We're excited to share some updates: {update}"
        },
        "witty": {
            "promo": "Need {service}? We got you. {business_name} is making waves!",
            "tip": "Here's a golden nugget for you 💡: {tip} — courtesy of {business_name}.",
            "update": "What’s cooking at {business_name}? Spoiler: {update}"
        },
        "friendly": {
            "promo": "Hey there! Have you tried our {service}? You'll love what {business_name} can do for you!",
            "tip": "Quick tip from your friends at {business_name}: {tip}",
            "update": "We've got some news! {update} — from all of us at {business_name}."
        }
    }
    

    tips = [
        "Automate where you can to save time",
        "Listen to your customer feedback regularly",
        "Stay consistent with your brand messaging",
        "Review your analytics monthly",
        "Keep your online presence up to date"
    ]

    updates = [
        "We're expanding our services!",
        "New team members have joined our mission!",
        "Exciting projects are in the works!",
        "We're moving to a bigger office!",
        "Client satisfaction just hit a new high!"
    ]

    posts = []

    template = tone_templates.get(tone, tone_templates["professional"]).get(post_type)

    if post_type == "promo":
        random.shuffle(services)
        items = services[:frequency] if len(services) >= frequency else [random.choice(services) for _ in range(frequency)]
        for service in items:
            content = template.format(service=service, business_name=business_name)
            posts.append(content)

    elif post_type == "tip":
        random.shuffle(tips)
        items = tips[:frequency] if len(tips) >= frequency else [random.choice(tips) for _ in range(frequency)]
        for tip in items:
            content = template.format(tip=tip, business_name=business_name)
            posts.append(content)

    elif post_type == "update":
        random.shuffle(news)
        items = news[:frequency] if len(news) >= frequency else [random.choice(news) for _ in range(frequency)]
        for update in items:
            content = template.format(update=update, business_name=business_name)
            posts.append(content)

    return posts

def generate_ai_content(industry, tone, content_type):
    content_templates = {
        'fitness': {
            'professional': [
                "🏋️‍♂️ Transform your fitness journey with our expert-led training programs! Our certified trainers are here to help you achieve your goals. Ready to start your transformation? 💪",
                "📊 Fitness Fact: Regular exercise can boost your energy levels by 20%! Join our community of motivated individuals working towards their fitness goals. What's your next milestone? 🎯",
                "💡 Pro Tip: Consistency beats perfection every time! Our structured programs help you build sustainable fitness habits. Start your journey today! 🌟"
            ],
            'casual': [
                "Hey fitness fam! 💪 Just wanted to share some motivation - remember, every workout counts! What's your favorite exercise? Drop it in the comments! 👇",
                "So, who else is crushing their fitness goals this week? 🏃‍♀️ Our community is absolutely killing it! Keep pushing, you've got this! 🔥",
                "Quick fitness update: We're seeing amazing transformations happening! Anyone else feeling stronger today? 💪 Let's celebrate those gains! 🎉"
            ],
            'friendly': [
                "Hey there! 👋 Ready to make today your best workout yet? Our friendly trainers are here to support your fitness journey every step of the way! 💪",
                "Quick reminder: You're doing amazing! 🌟 Every step, every rep, every choice counts towards your goals. We're cheering you on! 🎯",
                "Fitness friends! 💪 How's your week going? Remember, progress over perfection! We're here to help you stay motivated! 🚀"
            ]
        },
        'beauty': {
            'professional': [
                "✨ Discover your natural beauty with our expert beauty services! Our certified stylists use premium products to enhance your unique features. Book your consultation today! 💄",
                "📈 Beauty Trend Alert: Natural makeup is dominating this season! Our team stays updated with the latest techniques and products. What's your signature look? 💋",
                "💡 Beauty Tip: Proper skincare routine is the foundation of flawless makeup! Our specialists can help you create a personalized regimen. Glow from within! ✨"
            ],
            'casual': [
                "Beauty lovers! 💄 Who else is obsessed with the latest makeup trends? Our stylists are sharing some amazing tips today! What's your go-to look? 👄",
                "So, who's trying something new with their hair this week? 💇‍♀️ Our salon is buzzing with creativity! Tag us in your transformations! ✨",
                "Quick beauty update: We're loving all the natural looks we're seeing! Anyone else embracing their natural beauty? 🌟 Share your glow! 💫"
            ],
            'friendly': [
                "Hey beautiful! ✨ Ready to treat yourself to some self-care? Our friendly stylists are here to help you look and feel your best! 💄",
                "Beauty reminder: You're gorgeous just the way you are! 🌟 But if you want to enhance your natural beauty, we're here to help! 💋",
                "Beauty friends! 💄 How's your self-care routine going? Remember, taking time for yourself is never selfish! 💫"
            ]
        },
        'healthcare': {
            'professional': [
                "🏥 Prioritize your health with our comprehensive healthcare services! Our experienced medical professionals are committed to your well-being. Schedule your appointment today! 💊",
                "📊 Health Alert: Regular check-ups can prevent 80% of health issues! Our preventive care programs help you stay healthy and active. Your health is our priority! 🩺",
                "💡 Health Tip: Early detection saves lives! Our screening services help identify potential health concerns before they become serious. Prevention is key! 🔬"
            ],
            'casual': [
                "Health-conscious friends! 🏥 Who else is making their health a priority this year? Our team is here to support your wellness journey! 💪",
                "So, who's scheduled their annual check-up? 🩺 Taking care of your health is the best investment you can make! We're here to help! 💊",
                "Quick health update: We're seeing amazing results with our wellness programs! Anyone else feeling healthier lately? 🌟 Share your wins! 🎉"
            ],
            'friendly': [
                "Hey there! 👋 Taking care of your health doesn't have to be scary! Our friendly healthcare team is here to make your experience comfortable and stress-free! 🏥",
                "Health reminder: You deserve to feel your best! 🌟 Our comprehensive care ensures you get the attention you need. We're here for you! 💊",
                "Healthcare friends! 🩺 How's your wellness journey going? Remember, small steps lead to big changes! We're cheering you on! 💪"
            ]
        },
        'tech': {
            'professional': [
                "🚀 Exciting developments in {industry}! Our latest analysis shows significant growth in AI adoption across businesses. Companies are leveraging machine learning to streamline operations and enhance customer experiences. What's your take on the future of AI in {industry}?",
                "📊 Industry insights: {industry} is experiencing a digital transformation wave. Data shows 73% of companies are investing in automation tools. How is your organization adapting to these changes?",
                "💡 Innovation alert! The {industry} sector is embracing cutting-edge technologies. From blockchain to IoT, companies are redefining traditional business models. Stay ahead of the curve! 🎯"
            ],
            'casual': [
                "Hey {industry} folks! 👋 Just wanted to share some cool stuff happening in our space. AI is literally everywhere now - pretty wild, right? What's the most interesting tech trend you've seen lately?",
                "So, {industry} is getting a major tech upgrade! 🚀 Companies are going all-in on automation and it's actually working. Anyone else seeing these changes in their workplace?",
                "Quick {industry} update: things are getting pretty interesting with all the new tech coming out. From AI to blockchain, it's like living in the future! What's your favorite new tool? 🤖"
            ]
        },
        'finance': {
            'professional': [
                "💰 Financial technology is reshaping the {industry} landscape! Digital banking adoption has reached new heights, with 85% of consumers preferring mobile-first solutions.",
                "📊 Market insights: The {industry} sector is experiencing unprecedented digital transformation. Fintech solutions are driving efficiency and accessibility.",
                "💼 Industry update: {industry} is embracing blockchain and AI technologies. Traditional banking models are evolving rapidly. How is your organization staying competitive?"
            ],
            'casual': [
                "Finance friends! 💰 The {industry} world is getting a major tech makeover. Digital banking is the new normal and it's actually pretty awesome!",
                "Hey {industry} community! 👋 Mobile banking is literally everywhere now. Anyone else loving the convenience of banking from your phone?",
                "Quick {industry} update: technology is making money management so much easier! From AI advisors to blockchain, it's like we're living in the future! 🚀"
            ]
        },
        'food': {
            'professional': [
                "🍽️ Experience culinary excellence with our chef-crafted dishes! Our restaurant combines traditional flavors with modern techniques to create unforgettable dining experiences. Reserve your table today! 🍴",
                "📈 Food Trend Alert: Plant-based dining is on the rise! Our menu features innovative vegetarian and vegan options that don't compromise on taste. What's your favorite dish? 🥗",
                "💡 Dining Tip: The best meals are shared with great company! Our restaurant provides the perfect setting for memorable gatherings. Create lasting memories! 🍷"
            ],
            'casual': [
                "Food lovers! 🍕 Who else is always on the hunt for the best restaurants? Our kitchen is serving up some amazing dishes today! What's your comfort food? 🍔",
                "So, who's trying a new cuisine this week? 🌮 Our menu is packed with delicious surprises! Tag us in your food adventures! 📸",
                "Quick food update: We're loving all the foodie photos we're seeing! Anyone else obsessed with trying new dishes? 🍜 Share your favorites! 😋"
            ],
            'friendly': [
                "Hey foodies! 🍽️ Ready for a delicious dining experience? Our friendly staff is here to make your meal memorable! What are you craving today? 🍴",
                "Food reminder: Good food brings people together! 🌟 Our restaurant is the perfect place for family dinners and friend gatherings! 🍷",
                "Food friends! 🍕 How's your culinary adventure going? Remember, life is too short for boring food! 🍔"
            ]
        },
        'education': {
            'professional': [
                "📚 Empower your future with our comprehensive educational programs! Our experienced instructors are dedicated to helping you achieve your academic and career goals. Enroll today! 🎓",
                "📊 Education Insight: Lifelong learning increases career opportunities by 40%! Our courses are designed to keep you ahead in today's competitive job market. What skills are you developing? 💼",
                "💡 Learning Tip: The best investment you can make is in yourself! Our educational programs provide the knowledge and skills you need to succeed. Start your journey! 🌟"
            ],
            'casual': [
                "Learning enthusiasts! 📚 Who else is always curious about new topics? Our courses are packed with interesting content! What subject fascinates you most? 🧠",
                "So, who's taking an online course this month? 💻 Learning never stops, and we're here to support your educational journey! Share your learning goals! 🎯",
                "Quick education update: We're seeing amazing progress from our students! Anyone else feeling more knowledgeable lately? 📖 Celebrate your growth! 🎉"
            ],
            'friendly': [
                "Hey learners! 📚 Ready to expand your knowledge? Our friendly instructors are here to guide you through your educational journey! What interests you? 🎓",
                "Learning reminder: Every expert was once a beginner! 🌟 Our supportive learning environment helps you build confidence and skills! 💪",
                "Education friends! 📖 How's your learning journey going? Remember, knowledge is power! 🧠"
            ]
        }
    }
    
    # Default to general if industry not found
    if industry not in content_templates:
        industry = 'tech'
    
    if tone not in content_templates[industry]:
        tone = 'professional'
    
    import random
    template = random.choice(content_templates[industry][tone])
    
    content = template.format(industry=industry)
    
    if content_type == 'trending':
        hashtags = {
            'fitness': ['#FitnessGoals', '#WorkoutMotivation', '#HealthyLifestyle'],
            'beauty': ['#BeautyTrends', '#MakeupInspiration', '#SelfCare'],
            'healthcare': ['#Healthcare', '#Wellness', '#HealthyLiving'],
            'tech': ['#TechTrends', '#Innovation', '#DigitalTransformation'],
            'finance': ['#FinTech', '#FinancialFreedom', '#MoneyMatters'],
            'food': ['#Foodie', '#Delicious', '#Culinary'],
            'education': ['#Learning', '#Education', '#Knowledge']
        }
        content += f"\n\n{' '.join(hashtags.get(industry, ['#Trending', '#Innovation']))}"
    
    return content


