from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
import logging
from config import Config
import traceback
import feedparser
import random
import hashlib
import time
from PIL import Image
import io
from utils.business_info_api import url_scrape
from utils.content_api import generate_content, get_industry_news, generate_ai_content
from utils.weekly_planner import auto_distribute_days

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

warnings = Config.validate_config()
for warning in warnings:
    logger.warning(warning)

connected_pages = {}
generated_posts = {}
published_posts = {}

scheduled_posts = {
    "monday": None,
    "tuesday": None,
    "wednesday": None,
    "thursday": None,
    "friday": None,
    "saturday": None,
    "sunday": None,
}

business_profiles = {
    "gym": {
        "name": "FitLife Gym",
        "industry": "Fitness",
        "services": ["Personal Training", "Yoga", "Gym Memberships"],
        "tone": "friendly"
    },
    "salon": {
        "name": "Glow Salon",
        "industry": "Beauty",
        "services": ["Haircuts", "Coloring", "Styling", "Nails"],
        "tone": "witty"
    },
    "cafe": {
        "name": "Brewed Awakening",
        "industry": "Food & Beverage",
        "services": ["Coffee", "Pastries", "Breakfast Menus"],
        "tone": "professional"
    }
}

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


POSTS_FILE = "generated_posts.json"

def load_generated_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_generated_posts(posts):
    with open(POSTS_FILE, "w") as file:
        json.dump(posts, file)

generated_posts = load_generated_posts()



@app.route('/api/create-post', methods=['POST'])
def create_post():
    """Create a new post and add it to generated_posts."""
    try:
        post_content = request.form.get('content')
        page_id = request.form.get('page_id')
        
        post_id = f"post_{str(datetime.now().strftime('%Y%m%d_%H%M%S'))}"
        
        generated_posts[post_id] = {
            'page_id': page_id,
            'content': post_content,
            'status': 'generated',
            'created_at': datetime.now().isoformat(),
        }
        
        save_generated_posts(generated_posts)
        
        return jsonify({'success': True, 'post_id': post_id, 'message': 'Post created successfully'})

    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        return jsonify({'error': 'Failed to create post'}), 500


@app.route('/api/connect-page', methods=['POST'])
def connect_page():
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        access_token = data.get('access_token')
        
        if not page_id or not access_token:
            return jsonify({'error': 'Page ID and access token are required'}), 400
        
        verify_url = f"{Config.FACEBOOK_GRAPH_URL}/{page_id}"
        params = {
            'access_token': access_token,
            'fields': 'id,name,access_token'
        }
        
        response = requests.get(verify_url, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': 'Invalid page access token'}), 400
        
        page_info = response.json()
        
        connected_pages[page_id] = {
            'name': page_info.get('name', 'Unknown Page'),
            'access_token': access_token,
            'connected_at': datetime.now().isoformat()
        }
        
        logger.info(f"Connected page: {page_info.get('name')} (ID: {page_id})")
        
        return jsonify({
            'success': True,
            'page_id': page_id,
            'page_name': page_info.get('name'),
            'message': 'Page connected successfully'
        })
        
    except Exception as e:
        logger.error(f"Error connecting page: {str(e)}")
        return jsonify({'error': 'Failed to connect page'}), 500


@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    """Generate AI post content using existing generate-content route"""
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        industry = data.get('industry', 'general')
        tone = data.get('tone', 'professional')
        content_type = data.get('content_type', 'trending')
        
        # Make Facebook connection optional
        if page_id and page_id not in connected_pages:
            return jsonify({'error': 'Page not connected. Please connect a page first or leave page_id empty for standalone generation.'}), 400
        
        # Prepare data for existing generate-content route
        business_profile = {
            'name': f"Test Business ({industry})",
            'industry': industry,
            'services': [f"{industry} services", "Consulting", "Solutions"]
        }
        
        post_preferences = {
            'tone': tone,
            'post_type': content_type,
            'frequency': 3
        }
        
        generate_data = {
            'business_profile': business_profile,
            'post_preferences': post_preferences
        }
        
        generated_content = generate_ai_content(industry, tone, content_type)
        
        post_id = f"post_{len(generated_posts) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        generated_posts[post_id] = {
            'page_id': page_id,
            'content': generated_content,
            'industry': industry,
            'tone': tone,
            'content_type': content_type,
            'generated_at': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        logger.info(f"Generated post {post_id} for page {page_id}")
        
        return jsonify({
            'success': True,
            'post_id': post_id,
            'content': generated_content,
            'message': 'Post content generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error generating post: {str(e)}")
        return jsonify({'error': 'Failed to generate post content'}), 500




@app.route('/api/update-post', methods=['PUT'])
def update_post():
    """Update post content before publishing"""
    try:
        data = request.get_json()
        post_id = data.get('post_id')
        content = data.get('content')
        
        if not post_id or not content:
            return jsonify({'error': 'Post ID and content are required'}), 400
        
        if post_id not in generated_posts:
            return jsonify({'error': 'Post not found'}), 404
        
        generated_posts[post_id]['content'] = content
        generated_posts[post_id]['updated_at'] = datetime.now().isoformat()
        
        logger.info(f"Updated post {post_id}")
        
        return jsonify({
            'success': True,
            'message': 'Post updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating post: {str(e)}")
        return jsonify({'error': 'Failed to update post'}), 500
    
    


@app.route('/api/publish-post', methods=['POST'])
def publish_post():
    try:
        post_id = request.form.get('post_id')
        image_file = request.files.get('image')
        
        
        scheduled_time_str = request.form.get('scheduled_time')      
        scheduled_time = None
        unix_timestamp = None
        if scheduled_time_str:
            scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%dT%H:%M')
            unix_timestamp = int(scheduled_time.timestamp())
            print(unix_timestamp)

        if not post_id:
            return jsonify({'error': 'Post ID is required'}), 400
        
        # if post_id not in generated_posts:
        #     return jsonify({'error': f'Post {post_id} not found'}), 404
        
        post_data = generated_posts[post_id]
        
        # logger.info(f"Post data for {post_id}: {post_data}")
        
        page_id = None
        page_id = os.getenv("FB_PAGE_ID", None)
        
        if not page_id:
            if 'page_id' in post_data:
                page_id = post_data['page_id']
            elif 'page_id' in request.form:
                page_id = request.form.get('page_id')
            elif len(connected_pages) == 1:
                page_id = list(connected_pages.keys())[0]

        if not page_id:
            logger.error(f"Post {post_id} does not have a valid page_id.")
            return jsonify({'error': 'Invalid page ID associated with this post'}), 400
        
        if page_id not in connected_pages:
            logger.error(f"Page ID {page_id} is not connected.")
            return jsonify({'error': 'Page not connected'}), 400


        publish_url = f"{Config.FACEBOOK_GRAPH_URL}/{page_id}/feed"
        params = {
            'access_token': connected_pages[page_id]['access_token'],
            'message': post_data['content']
        }

        logger.info(f"Initial params: {params}")
        
        if image_file:
            try:
                modified_image = add_unique_watermark(image_file)
                
                upload_url = f"{Config.FACEBOOK_GRAPH_URL}/{page_id}/photos"
                if unix_timestamp:
                    image_params = {
                        'access_token': connected_pages[page_id]['access_token'],
                        'caption': post_data['content'],
                        'published': 'false',
                        "scheduled_publish_time": unix_timestamp
                    }
                else:
                    image_params = {
                        'access_token': connected_pages[page_id]['access_token'],
                        'caption': post_data['content'],
                        'published': 'false'
                    }
                
                files = {'file': ('image.jpg', modified_image, 'image/jpeg')}
                
                upload_response = requests.post(upload_url, data=image_params, files=files)
                print(upload_response.status_code)
                
                logger.info(f"Image upload response: {upload_response.text}")
                
                if upload_response.status_code != 200:
                    logger.error(f"Error uploading image to Facebook: {upload_response.text}")
                    
                    logger.info("Attempting to post without attached_media as fallback")
                    response = requests.post(publish_url, data=params)
                    
                    if unix_timestamp:
                        params['published'] = 'false'
                        params['scheduled_publish_time'] = unix_timestamp

                    response = requests.post(publish_url, data=params)
                    
                else:
                    upload_data = upload_response.json()
                    media_fbid = upload_data.get('id')
                    
                    if media_fbid:
                        params['attached_media'] = json.dumps([{"media_fbid": media_fbid}])

                        if unix_timestamp:
                            params['published'] = 'false'
                            params['scheduled_publish_time'] = unix_timestamp
                        
                        logger.info(f"Params after adding image: {params}")
                        response = requests.post(publish_url, data=params)
                        
                    else:
                        logger.error("No media_fbid returned after image upload.")
                        
                        if unix_timestamp:
                            params['published'] = 'false'
                            params['scheduled_publish_time'] = unix_timestamp
                                                    
                        response = requests.post(publish_url, data=params)
            
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                logger.info("Posting without image due to processing error")
                
                
                if unix_timestamp:
                    params['published'] = 'false'
                    params['scheduled_publish_time'] = unix_timestamp
                                    
                response = requests.post(publish_url, data=params)
        else:
            if unix_timestamp:
                params['published'] = 'false'
                params['scheduled_publish_time'] = unix_timestamp
                
            response = requests.post(publish_url, data=params)
        
        logger.info(f"Facebook API response: {response.text}")
        
        if response.status_code != 200:
            fb_response = response.json()
            error_message = fb_response.get('error', {}).get('message', 'Unknown error')
            error_details = fb_response.get('error', {}).get('error_user_msg', 'No details provided')
            
            if "already posted" in error_details.lower() or "already posted" in error_message.lower():
                logger.warning(f"Duplicate image detected, posting text-only version")
                
                text_only_params = {
                    'access_token': connected_pages[page_id]['access_token'],
                    'message': post_data['content'] + "\n\n[Note: Image was previously posted]"
                }
                
                if unix_timestamp:
                    text_only_params['published'] = 'false'
                    text_only_params['scheduled_publish_time'] = unix_timestamp                
                
                retry_response = requests.post(publish_url, data=text_only_params)
                
                if retry_response.status_code == 200:
                    try:
                        fb_response = retry_response.json()
                        post_url = f"https://www.facebook.com/{fb_response.get('id')}"
                        
                        # Save published post data
                        published_posts[post_id] = {
                            'fb_post_id': fb_response.get('id'),
                            'fb_post_url': post_url,
                            'published_at': datetime.now().isoformat(),
                            'original_content': post_data['content'],
                            'has_image': False,
                            'note': 'Posted as text-only due to duplicate image'
                        }
                        
                        generated_posts[post_id]['status'] = 'published'
                        save_generated_posts(generated_posts)
                        
                        return jsonify({
                            'success': True,
                            'fb_post_id': fb_response.get('id'),
                            'fb_post_url': post_url,
                            'message': 'Post published successfully (text-only due to duplicate image)',
                            'warning': 'Image was already posted, published text-only version'
                        })
                    finally:
                        print("waiting...")
            
            logger.error(f"Facebook API error: {response.status_code} - {error_message}. Details: {error_details}")
            return jsonify({'error': f'Failed to publish to Facebook: {error_message}. {error_details}'}), 500
        
        fb_response = response.json()
        post_url = f"https://www.facebook.com/{fb_response.get('id')}"
        
        # Save published post data
        published_posts[post_id] = {
            'fb_post_id': fb_response.get('id'),
            'fb_post_url': post_url,
            'published_at': datetime.now().isoformat(),
            'original_content': post_data['content'],
            'has_image': bool(image_file)
        }
        
        generated_posts[post_id]['status'] = 'published'
        
        # Save updated posts to file
        save_generated_posts(generated_posts)
        
        logger.info(f"Published post {post_id} to Facebook: {post_url}")
        
        if unix_timestamp and unix_timestamp > int(datetime.now().timestamp()):
            message = 'Post scheduled successfully on Facebook.'
        else:
            message = 'Post published successfully to Facebook.'
            
        return jsonify({
            'success': True,
            'fb_post_id': fb_response.get('id'),
            'fb_post_url': post_url,
            'message': message
        })

    
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to publish post'}), 500


def add_unique_watermark(image_file):
    """Add a subtle timestamp watermark to make image unique"""
    try:
        # Reset file pointer to beginning
        image_file.seek(0)
        
        # Open image with PIL
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create a copy to modify
        modified_image = image.copy()
        
        # Add a tiny transparent timestamp in bottom-right corner
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(modified_image)
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        
        # Try to use a small font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 10)
        except:
            font = ImageFont.load_default()
        
        # Get image dimensions
        width, height = modified_image.size
        
        # Add nearly invisible watermark (very light gray)
        draw.text((width-50, height-15), timestamp, fill=(250, 250, 250, 1), font=font)
        
        # Convert back to bytes
        img_byte_arr = io.BytesIO()
        modified_image.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)
        
        return img_byte_arr
        
    except Exception as e:
        logger.error(f"Error adding watermark: {e}")
        image_file.seek(0)
        return image_file


@app.route('/api/publish-post-alternative', methods=['POST'])
def publish_post_alternative():
    """Alternative method: Post image directly with caption instead of using attached_media"""
    try:
        post_id = request.form.get('post_id')
        image_file = request.files.get('image')

        if not post_id:
            return jsonify({'error': 'Post ID is required'}), 400
        
        if post_id not in generated_posts:
            return jsonify({'error': f'Post {post_id} not found'}), 404
        
        post_data = generated_posts[post_id]
        page_id = post_data.get('page_id') or request.form.get('page_id') or list(connected_pages.keys())[0]

        if not page_id or page_id not in connected_pages:
            return jsonify({'error': 'Invalid or unconnected page ID'}), 400

        if image_file:
            # Post directly to photos endpoint (this creates the post automatically)
            upload_url = f"{Config.FACEBOOK_GRAPH_URL}/{page_id}/photos"
            
            # Add timestamp to make image unique
            modified_image = add_unique_watermark(image_file)
            
            params = {
                'access_token': connected_pages[page_id]['access_token'],
                'caption': post_data['content']
            }
            
            files = {'file': ('image.jpg', modified_image, 'image/jpeg')}
            
            response = requests.post(upload_url, data=params, files=files)
        else:
            # Regular text post
            publish_url = f"{Config.FACEBOOK_GRAPH_URL}/{page_id}/feed"
            params = {
                'access_token': connected_pages[page_id]['access_token'],
                'message': post_data['content']
            }
            response = requests.post(publish_url, data=params)

        if response.status_code == 200:
            fb_response = response.json()
            post_url = f"https://www.facebook.com/{fb_response.get('id')}"
            
            return jsonify({
                'success': True,
                'fb_post_id': fb_response.get('id'),
                'fb_post_url': post_url,
                'message': 'Post published successfully to Facebook'
            })
        else:
            return jsonify({'error': 'Failed to publish post'}), 500
            
    except Exception as e:
        logger.error(f"Error in alternative publish: {e}")
        return jsonify({'error': 'Failed to publish post'}), []



@app.route('/api/generate-content', methods=['POST'])
def generate_content_route():
    """Generate content using the enhanced content generation system"""
    try:
        data = request.get_json()
        
        business_profile = data.get('business_profile')
        if not business_profile:
            return jsonify({"error": "Business profile not found"}), 400
        
        post_preferences = data.get('post_preferences')
        if not post_preferences:
            return jsonify({"error": "Post Preferences not found"}), 400
           
        b_name = data['business_profile']['name']
        industry = data['business_profile']['industry']
        services = data['business_profile']['services']
        tone = data['post_preferences']['tone']
        post_type = data['post_preferences']['post_type']
        frequency = data['post_preferences'].get('frequency') or 3
        
        industry_news = get_industry_news(business_profile["industry"])

        # Don't fail if no industry news - use default content instead
        if not industry_news:
            logger.warning(f"No industry news found for {industry}, using default content")
            industry_news = [
                f"Latest {industry} trends and developments",
                f"New innovations in {industry} sector",
                f"Industry insights for {industry} professionals"
            ]

        content = generate_content(business_profile, industry_news, tone, post_type, frequency)
        return jsonify({"posts": content}), 200
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({'error': 'Failed to generate content'}), 500



@app.route('/api/generate-content-integrated', methods=['POST'])
def generate_content_integrated():
    """Generate content using the existing generate-content route"""
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        
        # Make Facebook connection optional
        if page_id and page_id not in connected_pages:
            return jsonify({'error': 'Page not connected. Please connect a page first or leave page_id empty for standalone generation.'}), 400
        
        # Extract data from the request
        business_profile = data.get('business_profile')
        post_preferences = data.get('post_preferences')
        
        if not business_profile:
            return jsonify({"error": "Business profile not found"}), 400
        
        if not post_preferences:
            return jsonify({"error": "Post Preferences not found"}), 400
        
        # Call your existing generate-content route
        # This would be an internal call to your existing endpoint
        # For now, we'll simulate the response structure
        b_name = business_profile['name']
        industry = business_profile['industry']
        services = business_profile['services']
        tone = post_preferences['tone']
        post_type = post_preferences['post_type']
        frequency = post_preferences.get('frequency') or 3
        
        # Simulate the content generation (replace with actual call to your route)
        generated_content = generate_ai_content(industry, tone, post_type)
        
        post_id = f"post_{len(generated_posts) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        generated_posts[post_id] = {
            'page_id': page_id,
            'content': generated_content,
            'industry': industry,
            'tone': tone,
            'content_type': post_type,
            'business_name': b_name,
            'services': services,
            'frequency': frequency,
            'generated_at': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        logger.info(f"Generated integrated post {post_id} for page {page_id}")
        
        return jsonify({
            'success': True,
            'post_id': post_id,
            'content': generated_content,
            'message': 'Content generated successfully using integrated route'
        })
        
    except Exception as e:
        logger.error(f"Error generating integrated content: {str(e)}")
        return jsonify({'error': 'Failed to generate content'}), 500

@app.route('/api/connected-pages', methods=['GET'])
def get_connected_pages():
    """Get list of connected pages"""
    return jsonify({
        'pages': [
            {
                'page_id': page_id,
                'name': page_info['name'],
                'connected_at': page_info['connected_at']
            }
            for page_id, page_info in connected_pages.items()
        ]
    })

@app.route('/api/generated-posts', methods=['GET'])
def get_generated_posts():
    """Get list of generated posts"""
    return jsonify({
        'posts': [
            {
                'post_id': post_id,
                'page_id': post_data['page_id'],
                'content': post_data['content'],
                'industry': post_data['industry'],
                'tone': post_data['tone'],
                'status': post_data['status'],
                'generated_at': post_data['generated_at']
            }
            for post_id, post_data in generated_posts.items()
        ]
    })

@app.route('/api/published-posts', methods=['GET'])
def get_published_posts():
    """Get list of published posts"""
    return jsonify({
        'posts': [
            {
                'post_id': post_id,
                'fb_post_id': pub_data['fb_post_id'],
                'fb_post_url': pub_data['fb_post_url'],
                'published_at': pub_data['published_at'],
                'original_content': pub_data['original_content']
            }
            for post_id, pub_data in published_posts.items()
        ]
    })


@app.route('/api/business-understanding', methods=['POST'])
def business_understanding():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({"error": "Missing URL"}), 400

        logger.info(f"Analyzing business website: {url}")
        result = url_scrape(url)
        
        if result is None:
            logger.error("url_scrape returned None")
            return jsonify({"error": "Failed to analyze website"}), 500

        if isinstance(result, tuple):
            result = result[0]
            logger.info(f"Extracted result from tuple: {result}")
        
        logger.info(f"Business analysis result: {result}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in business understanding: {str(e)}")
        return jsonify({'error': 'Failed to analyze business website'}), 500


@app.route('/api/generate-content-standalone', methods=['POST'])
def generate_content_standalone():
    """Generate content without requiring Facebook page connection"""
    try:
        data = request.get_json()
        logger.info(f"Enhanced mode request data: {data}")
        
        business_profile = data.get('business_profile')
        if not business_profile:
            return jsonify({"error": "Business profile not found"}), 400
        
        post_preferences = data.get('post_preferences')
        if not post_preferences:
            return jsonify({"error": "Post Preferences not found"}), 400
           
        b_name = data['business_profile']['name']
        industry = data['business_profile']['industry']
        services = data['business_profile']['services']
        tone = data['post_preferences']['tone']
        post_type = data['post_preferences']['post_type']
        frequency = data['post_preferences'].get('frequency') or 3
        
        logger.info(f"Processing enhanced content: {industry}, {tone}, {post_type}, {frequency}")
        
        industry_news = get_industry_news(business_profile["industry"])
        logger.info(f"Industry news received: {len(industry_news) if industry_news else 0} items")

        # Don't fail if no industry news - use default content instead
        if not industry_news:
            logger.warning(f"No industry news found for {industry}, using default content")
            industry_news = [
                f"Latest {industry} trends and developments",
                f"New innovations in {industry} sector",
                f"Industry insights for {industry} professionals"
            ]

        content = generate_content(business_profile, industry_news, tone, post_type, frequency)
        logger.info(f"Generated {len(content)} posts")
        return jsonify({"posts": content}), 200
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({'error': 'Failed to generate content'}), 500


@app.route('/api/news', methods=['POST'])
def generate_news():
    try:
        data = request.get_json()
        industry = data.get('industry')
        if not industry:
            return jsonify({"error": "Missing industry parameter"}), 400
            
        url = f"https://news.google.com/rss/search?q={industry}"
        feed = feedparser.parse(url)
        headlines = [entry.title for entry in feed.entries[:5]]
        return jsonify(headlines), 200
        
    except Exception as e:
        logger.error(f"Error generating news: {str(e)}")
        return jsonify({'error': 'Failed to generate news'}), 500







@app.route('/api/weekly-planner', methods=['POST'])
def weekly_planner():
    """Schedule posts across different days of the week"""
    try:
        data = request.get_json()
        posts = data.get("posts", [])
        frequency = data.get("post_frequency", len(posts))
        preferred_days = data.get("preferred_days", [])

        if not posts or frequency == 0:
            return jsonify({"error": "Missing posts or post frequency"}), 400
        if len(posts) < frequency:
            return jsonify({"error": "Not enough posts provided"}), 400

        all_days = list(scheduled_posts.keys())
        selected_days = [day.lower() for day in preferred_days][:frequency] if preferred_days else random.sample(all_days, frequency)

        for day in scheduled_posts:
            scheduled_posts[day] = None

        for i, day in enumerate(selected_days):
            scheduled_posts[day] = posts[i]

        return jsonify({"schedule": scheduled_posts})
        
    except Exception as e:
        logger.error(f"Error in weekly planner: {str(e)}")
        return jsonify({'error': 'Failed to create weekly schedule'}), 500




@app.route('/api/weekly-planner', methods=['GET'])
def get_weekly_schedule():
    """Get the current weekly schedule"""
    return jsonify({"schedule": scheduled_posts})




@app.route('/api/weekly-planner/<day>', methods=['PUT'])
def update_weekly_post(day):
    """Update a post for a specific day"""
    try:
        day = day.lower()
        if day not in scheduled_posts:
            return jsonify({"error": f"{day.capitalize()} is not a valid day"}), 400

        data = request.get_json()
        new_content = data.get("post")
        if not new_content:
            return jsonify({"error": "No post content provided"}), 400

        scheduled_posts[day] = new_content
        return jsonify({"message": f"Post for {day.capitalize()} updated", "post": new_content})
        
    except Exception as e:
        logger.error(f"Error updating weekly post: {str(e)}")
        return jsonify({'error': 'Failed to update weekly post'}), 500




@app.route('/api/weekly-planner/<day>', methods=['DELETE'])
def delete_weekly_post(day):
    """Delete a post for a specific day"""
    try:
        day = day.lower()
        if day not in scheduled_posts:
            return jsonify({"error": f"{day.capitalize()} is not a valid day"}), 400

        if scheduled_posts[day] is None:
            return jsonify({"error": f"No post to delete on {day.capitalize()}"}), 404

        deleted_post = scheduled_posts[day]
        scheduled_posts[day] = None
        return jsonify({"message": f"Post for {day.capitalize()} deleted", "deleted_post": deleted_post})
        
    except Exception as e:
        logger.error(f"Error deleting weekly post: {str(e)}")
        return jsonify({'error': 'Failed to delete weekly post'}), 500




@app.route('/api/mock-facebook', methods=['POST'])
def connect_facebook():
    """Mock Facebook connection for testing purposes"""
    return jsonify({
        "status": "connected",
        "page_id": "mock12345",
        "access_token": "abc123"
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 