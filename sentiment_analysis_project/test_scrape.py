from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_amazon_reviews(url):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Auto-download and use ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        driver.get(url)
        time.sleep(3)
        print("Current URL:", driver.current_url)
        print("Page title:", driver.title)
        
        wait = WebDriverWait(driver, 10)
        try:
            reviews_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link-foot']")))
            reviews_link.click()
            print("Clicked 'See all reviews'")
            time.sleep(3)
        except Exception as e:
            print("No 'See all reviews' link found, checking current page")
        
        soup = BeautifulSoup(driver.page_source, "lxml")
        print("Page snippet:", soup.text[:200])
        
        # Extract product name
        product_title_tag = soup.find("span", {"id": "productTitle"})
        product_name = product_title_tag.get_text(strip=True) if product_title_tag else "Unknown Product"
        
        # Extract product image
        img_tag = soup.find("img", {"id": "landingImage"})
        product_image = img_tag.get("src") if img_tag else None
        
        # Extract reviews
        reviews = soup.select("span[data-hook='review-body']")
        review_texts = [review.get_text(strip=True) for review in reviews]
        
        print("Found reviews:", len(review_texts))
        for i, review in enumerate(review_texts, 1):
            print(f"Review {i}: {review}")
        
        print("Product Name:", product_name)
        print("Product Image URL:", product_image)
    except Exception as e:
        print(f"Error: {str(e)}")
        review_texts = []
        product_name = "Unknown Product"
        product_image = None
    finally:
        driver.quit()
    
    return review_texts, product_name, product_image



# Test URL – adjust as needed
url = "https://www.amazon.in/Echo-Dot-5th-Gen-Alexa-smart-speaker/dp/B09B8XJDW5"
reviews, product_name, product_image = scrape_amazon_reviews(url)
if reviews:
    print(f"Found {len(reviews)} reviews.")
    print("Product Name:", product_name)
    print("Product Image URL:", product_image)
else:
    print("No reviews scraped.")
