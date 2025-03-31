from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from textblob import TextBlob

app = Flask(__name__)

def scrape_amazon_reviews(url):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")
        
        # Extract product name (from element with id 'productTitle')
        product_title_tag = soup.find("span", {"id": "productTitle"})
        product_name = product_title_tag.get_text(strip=True) if product_title_tag else "Unknown Product"
        
        # Extract product image (from img with id 'landingImage')
        img_tag = soup.find("img", {"id": "landingImage"})
        product_image = img_tag.get("src") if img_tag else None
        
        # Extract star rating (from span with class 'a-icon-alt')
        rating_tag = soup.find("span", {"class": "a-icon-alt"})
        product_rating = rating_tag.get_text(strip=True) if rating_tag else "No Rating"
        
        # Extract reviews
        reviews = soup.select("span[data-hook='review-body']")
        review_texts = [review.get_text(strip=True) for review in reviews]
    except Exception as e:
        review_texts = [f"Error scraping reviews: {str(e)}"]
        product_name = "Unknown Product"
        product_image = None
        product_rating = "No Rating"
    finally:
        driver.quit()
    
    return review_texts, product_name, product_image, product_rating

def analyze_sentiment(reviews):
    sentiments = []
    for review in reviews:
        blob = TextBlob(review)
        sentiment = blob.sentiment.polarity
        sentiments.append(sentiment)
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return sentiments, avg_sentiment

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        if not url.startswith("https://www.amazon.in"):
            return render_template("index.html", error="Please enter a valid Amazon URL")
        
        reviews, product_name, product_image, product_rating = scrape_amazon_reviews(url)
        if not reviews:
            return render_template("index.html", error="No reviews found or scraping failed")
        
        sentiments, avg_sentiment = analyze_sentiment(reviews)
        results = list(zip(reviews, sentiments))
        
        total_reviews = len(results)
        threshold = 50  # Adjust threshold as needed
        sales_percentage = (total_reviews / threshold) * 100
        if sales_percentage > 100:
            sales_percentage = 100
        
        return render_template(
            "results.html",
            results=results,
            avg_sentiment=avg_sentiment,
            product_name=product_name,
            product_image=product_image,
            product_rating=product_rating,
            total_reviews=total_reviews,
            threshold=threshold,
            sales_percentage=sales_percentage
        )
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
