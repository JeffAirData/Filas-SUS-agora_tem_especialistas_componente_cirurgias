from selenium import webdriver
from selenium.webdriver.common.by import By

def scrape_dynamic(url: str) -> list[dict]:
    driver = webdriver.Chrome()
    driver.get(url)

    elementos = driver.find_elements(By.TAG_NAME, "h2")
    dados = [{"url": url, "titulo": e.text.strip()} for e in elementos if e.text.strip()]

    driver.quit()
    return dados