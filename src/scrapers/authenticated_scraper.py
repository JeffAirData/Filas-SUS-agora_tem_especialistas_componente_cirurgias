from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def login_and_scrape(url: str, username: str, password: str, login_url: str) -> list[dict]:
    """
    Login manual + scraping automático.
    """
    driver = webdriver.Chrome()
    driver.get(login_url)

    # Preenche login
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-btn").click()

    # Aguarda login
    time.sleep(3)

    # Navega para URL alvo
    driver.get(url)
    time.sleep(2)

    # Extrai dados
    elementos = driver.find_elements(By.TAG_NAME, "h2")
    dados = [{"url": url, "titulo": e.text.strip()} for e in elementos if e.text.strip()]

    driver.quit()
    return dados