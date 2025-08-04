# Facebook Page Testing Flow

A complete testing application for Facebook page integration with AI-generated content. This application allows you to connect your Facebook page, generate AI content based on industry trends, preview and edit posts, and publish them directly to your Facebook page.

## Features

- **Facebook Page Connection**: Securely connect your Facebook page using Page ID and Access Token
- **AI Content Generation**: Generate industry-specific content with customizable tone and style
- **Post Preview & Editing**: Preview generated content and make edits before publishing
- **Direct Publishing**: Publish posts directly to your connected Facebook page
- **Real-time Validation**: Track published posts and validate their appearance on Facebook
- **Business Analysis**: Analyze business websites to extract profile information
- **Industry News**: Generate industry-specific news headlines
- **Enhanced Content Generation**: Advanced content generation with multiple post types and tones
- **Weekly Planner**: Schedule posts across different days of the week
- **Mock Facebook Integration**: Test functionality without real Facebook credentials

## Tech Stack

- **Backend**: Python + Flask
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **API Integration**: Facebook Graph API v18.0
- **CORS Support**: Flask-CORS for cross-origin requests
- **Web Scraping**: BeautifulSoup4 for business analysis
- **RSS Feeds**: Feedparser for industry news

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Facebook App Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or use an existing one
3. Add the "Facebook Login" product to your app
4. Generate a Page Access Token:
   - Go to Graph API Explorer
   - Select your app
   - Generate a User Access Token with `pages_manage_posts` permission
   - Use the token to get a Page Access Token

### 3. Environment Variables (Optional)

Create a `.env` file in the project root:

```env
FB_ACCESS_TOKEN=your_facebook_access_token
FB_PAGE_ID=your_facebook_page_id
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Testing Flow

### Step 1: Connect Facebook Page (Optional)
1. Enter your Facebook Page ID
2. Enter your Page Access Token
3. Click "Connect Page"
4. Verify the connection is successful
5. **Note**: Facebook connection is optional - you can generate content without connecting a page

### Step 2: Generate AI Content
Choose from three content generation modes (all work with or without Facebook connection):

#### Simple Mode (Basic parameters)
1. Select your industry:
   - **Fitness & Wellness**: Gym, personal training, wellness
   - **Beauty & Salon**: Hair, makeup, spa services
   - **Healthcare**: Medical, dental, wellness
   - **Technology**: Software, IT, digital services
   - **Finance**: Banking, investment, financial services
   - **Food & Restaurant**: Dining, catering, food services
   - **Education**: Training, courses, learning
   - **General**: Any other business type
2. Choose the tone (Professional, Casual, or Friendly)
3. Select content type (Trending, Industry Insights, General)
4. Click "Generate Content"

#### Advanced Mode (Business profile)
1. Enter business name, industry, and services
2. Choose tone and post type
3. Set post frequency
4. Click "Generate Content"

#### Enhanced Mode (Industry news + templates)
1. Enter business profile details
2. Choose from professional, witty, or friendly tones
3. Select post type (promotional, tips, updates)
4. Set frequency for multiple posts
5. Click "Generate Content"

### Step 2.5: Business Analysis (Optional)
1. Enter a business website URL
2. Click "Analyze Website"
3. Review extracted business profile (name, industry, services, tone)
4. Optionally use this data for content generation

### Step 2.6: Industry News
1. Enter an industry keyword (e.g., "technology", "healthcare")
2. Click "Get News Headlines"
3. Review latest industry news for content inspiration

### Step 2.7: Weekly Planner
1. Enter multiple posts (one per line)
2. Set post frequency (3, 5, or 7 times per week)
3. Optionally select preferred days
4. Click "Create Weekly Schedule"
5. Review the scheduled posts for each day

### Step 3: Preview & Edit
1. Preview the generated content
2. Edit the content if needed
3. **Add photos** (optional) - Upload images to include with your Facebook post
4. Save changes or proceed to publish
5. Click "Publish to Facebook"

### Step 4: Validation
1. Check the published post on your Facebook page
2. Verify content matches the generated tone and industry
3. Confirm timing and formatting are correct

## Validation Criteria

### To check if it works:

1. **Go to the test Facebook Page**
   - Navigate to your connected Facebook page
   - Look for the newly published post

2. **Ensure the post appears as expected**
   - Post should be visible on the page timeline
   - Content should be properly formatted
   - No error messages should appear

3. **Content should match the tone, industry, and timing set in the backend**
   - **Professional tone**: Formal language, industry-specific terminology
   - **Casual tone**: Informal language, emojis, conversational style
   - **Witty tone**: Humorous, engaging content with personality
   - **Friendly tone**: Warm, approachable content
   - **Industry-specific content**: Relevant hashtags and topics
   - **Timing**: Post should appear immediately after publishing

### Enhanced Features Validation:

4. **Business Analysis**
   - Website analysis should extract business name, industry, services, and tone
   - Extracted data should populate content generation forms correctly

5. **Industry News**
   - News headlines should be relevant to the specified industry
   - Headlines should be current and from reliable sources

6. **Weekly Planner**
   - Posts should be distributed across selected days
   - Schedule should respect preferred days when specified
   - Schedule should be viewable and editable

7. **Enhanced Content Generation**
   - Multiple posts should be generated based on frequency setting
   - Content should match the selected tone and post type
   - Templates should be industry-appropriate

## API Endpoints

### Core Facebook Integration
- **POST** `/api/connect-page` - Connect Facebook page
- **POST** `/api/generate-post` - Generate AI post content
- **PUT** `/api/update-post` - Update existing post
- **POST** `/api/publish-post` - Publish post to Facebook
- **GET** `/api/connected-pages` - Get connected pages
- **GET** `/api/generated-posts` - Get generated posts
- **GET** `/api/published-posts` - Get published posts

### Business Analysis
- **POST** `/api/business-understanding` - Analyze business website
  - **Body**: `{"url": "https://example.com"}`
  - **Returns**: Business name, industry, services, tone

### Industry News
- **POST** `/api/news` - Get industry-specific news
  - **Body**: `{"industry": "technology"}`
  - **Returns**: Array of news headlines

### Enhanced Content Generation
- **POST** `/api/generate-content` - Advanced content generation
- **POST** `/api/generate-content-standalone` - Content generation without Facebook connection
  - **Body**: 
    ```json
    {
      "business_profile": {
        "name": "Business Name",
        "industry": "Technology",
        "services": ["Service 1", "Service 2"]
      },
      "post_preferences": {
        "tone": "professional",
        "post_type": "promo",
        "frequency": 3
      }
    }
    ```
  - **Returns**: Array of generated posts

### Weekly Planner
- **POST** `/api/weekly-planner` - Schedule posts for the week
  - **Body**: 
    ```json
    {
      "posts": ["Post 1", "Post 2", "Post 3"],
      "post_frequency": 3,
      "preferred_days": ["monday", "wednesday", "friday"]
    }
    ```
- **GET** `/api/weekly-planner` - Get current weekly schedule
- **PUT** `/api/weekly-planner/<day>` - Update post for specific day
- **DELETE** `/api/weekly-planner/<day>` - Delete post for specific day

### Testing & Mock Endpoints
- **POST** `/api/mock-facebook` - Mock Facebook connection for testing

## Content Types

### Post Types
- **promo**: Promotional content about services
- **tip**: Business tips and advice
- **update**: Company updates and news

### Tones
- **professional**: Formal, business-focused content
- **witty**: Humorous, engaging content
- **friendly**: Warm, approachable content

## Business Profiles

The application includes demo business profiles for testing:
- **Gym**: FitLife Gym (Fitness industry)
- **Salon**: Glow Salon (Beauty industry)
- **Cafe**: Brewed Awakening (Food & Beverage industry)

