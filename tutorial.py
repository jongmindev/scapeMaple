from selenium import webdriver
from selenium.webdriver.common.by import By
import time


browser = webdriver.Chrome()

# browser.get("http://python.org")
#
# # menus = browser.find_elements_by_css_selector('#top ul.menu li')
# menus = browser.find_elements(by=By.CSS_SELECTOR, value='#top ul.menu li')
#
# pypi = None
# for m in menus:
#     if m.text == "PyPI":
#         pypi = m
#     print(m.text)
#
# pypi.click()  # 클릭
#
# time.sleep(5) # 5초 대기
# browser.quit() # 브라우저 종료

url = "https://maplestory.nexon.com/Common/Character/Detail/%ed%9e%88%ec%8a%88%ec%99%80/Equipment" \
      "?p=mikO8qgdC4hElCwBGQ6GOx8CmO11EvduZkV0bRbPAh" \
      "aRzW5LQRf8%2f4r4oCWC0wKML5gmImzNTiIxKN9nZv55Kkg56a2qImGHSENhY" \
      "4orAkJSLirlbSciSAERq3rRq3FtApA2cUvPUoWCeBavuh7eML5ZllW09Xu4dHrGWLC1pw4%3d"

browser.get(url)