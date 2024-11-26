import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from time import sleep
from random import randint

# Bot configuration
BOT_ID = 'your_bot_ID'
GROUPME_API_URL = 'https://api.groupme.com/v3/bots/post'

# Notify the start of the bot
requests.post(GROUPME_API_URL, params={'bot_id': BOT_ID, 'text': "Starting Uniqlo bot"})

# Configure Selenium WebDriver
options = Options()
options.add_argument('--headless')  # Run Chrome in headless mode
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

# Uniqlo product tracking URL
PRODUCT_URL = "https://www.uniqlo.com/us/en/men/sale"

# List to keep track of notified items
sent_list = set()


def check_exists_by_xpath(item, xpath):
    """
    Checks if an element exists within an item using XPath.
    """
    try:
        item.find_element('xpath', xpath)
        return True
    except NoSuchElementException:
        return False


def check_for_price(class_name, sale_price_xpath, standard_price_xpath, item_name_xpath):
    """
    Checks for items on sale and sends notifications for significant discounts.
    """
    try:
        driver.get(PRODUCT_URL)
        for item in driver.find_elements('class name', class_name):
            # Validate existence of price elements
            if not (check_exists_by_xpath(item, standard_price_xpath) and check_exists_by_xpath(item, sale_price_xpath)):
                continue

            # Extract price information
            product_standard_price = float(item.find_element('xpath', standard_price_xpath).text[1:])
            product_sale_price = float(item.find_element('xpath', sale_price_xpath).text[1:])
            discount_percent = (1 - product_sale_price / product_standard_price) * 100

            # Notify if discount is significant
            if discount_percent > 25 and id(item) not in sent_list:
                item_name = item.find_element('xpath', item_name_xpath).text
                message = f"{item_name} ON SALE for ${product_sale_price:.2f} at {discount_percent:.2f}% off"
                print(message)
                requests.post(GROUPME_API_URL, params={'bot_id': BOT_ID, 'text': message})
                sent_list.add(id(item))

    except WebDriverException as e:
        print(f"WebDriverException: {e}")
    except requests.exceptions.RequestException as e:
        print(f"RequestsException: {e}")


# Main loop
if __name__ == "__main__":
    class_name = 'product-tile'
    sale_price_xpath = ".//span[@class='product-sales-price']"
    standard_price_xpath = ".//span[@class='product-standard-price']"
    item_name_xpath = ".//a[@class='name-link']"

    try:
        while True:
            check_for_price(class_name, sale_price_xpath, standard_price_xpath, item_name_xpath)
            sleep(randint(30, 60))  # Wait before checking again
    finally:
        driver.quit()  # Ensure the driver quits at the end
