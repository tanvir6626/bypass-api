from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from seleniumbase import Driver
import requests
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cloudflare Bypass Image Downloader")

@app.get("/")
async def download_image(url: str):
    """
    Download an image that's protected by Cloudflare.
    
    Args:
        url: The direct URL to the image
        
    Returns:
        The image file as binary data
    """
    driver = None
    try:
        logger.info(f"Starting download for URL: {url}")
        
        # Initialize SeleniumBase with UC mode (undetected)
        driver = Driver(
            uc=True,  # Undetected Chrome mode
            headless=True,
            browser="chrome"
        )
        
        logger.info("Browser initialized, navigating to URL...")
        
        # Navigate to the image URL
        driver.get(url)
        
        # Wait for Cloudflare challenge to complete
        logger.info("Waiting for page to load...")
        driver.sleep(3)  # Give time for Cloudflare challenge
        
        # Get the current URL (might be redirected)
        current_url = driver.get_current_url()
        logger.info(f"Current URL after navigation: {current_url}")
        
        # Get cookies from the browser
        cookies = driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        
        # Get user agent
        user_agent = driver.execute_script("return navigator.userAgent;")
        
        # Now download the image with the cookies and headers
        headers = {
            'User-Agent': user_agent,
            'Referer': url,
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        }
        
        logger.info("Downloading image with authenticated session...")
        response = requests.get(current_url, cookies=cookie_dict, headers=headers, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to download image: HTTP {response.status_code}"
            )
        
        # Determine content type
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        logger.info(f"Image downloaded successfully. Size: {len(response.content)} bytes")
        
        return Response(
            content=response.content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=image.jpg"
            }
        )
        
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Browser closed")
            except:
                pass

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
