from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from bs4.element import Tag


EQUIPMENT_INDEX = {'반지1': 1, '모자': 3, '엠블렘': 5,
                   '반지2': 6, '펜던트1': 7, '얼굴장식': 8, '뱃지': 10,
                   '반지3': 11, '펜던트2': 12, '눈장식': 13, '귀고리': 14, '훈장': 15,
                   '반지4': 16, '무기': 17, '상의': 18, '어깨장식': 19, '보조무기': 20,
                   '포켓': 21, '벨트': 22, '하의': 23, '장갑': 24, '망토': 25,
                   '신발': 28, '암드로이드': 29, '기계심장': 30}


class BrowserForEquipmentTag:
    def __init__(self, url: str):
        # 캐릭터 정보창 url 을 입력받아 브라우저 실행
        self._browser = webdriver.Chrome()
        self._browser.get(url)

    def _get_equipment_webelement(self, item: str | int):
        """장비 부위 이름 str 또는 li:(n)th-child int n을 받아서 해당 장비 WebElement 반환"""
        if type(item) == int:
            element = self._browser.find_element(by=By.CSS_SELECTOR,
                                                 value=f"#container ul.item_pot > li:nth-child({item})")
        elif type(item) == str:
            item = EQUIPMENT_INDEX[item]
            element = self._browser.find_element(by=By.CSS_SELECTOR,
                                                 value=f"#container ul.item_pot > li:nth-child({item})")
        else:
            raise TypeError("parameter : str or int")
        return element

    def get_equipment_info_tag(self, equip: str | int):
        # 찾고자 하는 장비를 클릭
        item_element = self._get_equipment_webelement(equip)
        item_element.click()
        # 클릭 이후 바뀐 html get
        html = self._browser.page_source
        # BSoup 으로 전체 html 파싱
        soup = BeautifulSoup(html, 'html.parser')
        # 해당 장비 정보 탭 부분만 파싱
        item_info = soup.select_one("#container div.tab01_con_wrap > div.item_info > div")
        return item_info

    def quit_browser(self):
        self._browser.quit()


class ParseInfoTag:
    def __init__(self, equipment_info_tag: Tag):
        self._equip_tag = equipment_info_tag
        self._title = self._equip_title()
        self._category = self._equip_category()
        self._stats_dict = self._equip_stats_tag_dict()

    def _equip_title(self):
        title_tag = self._equip_tag.select_one(".item_title h1")
        title_text = title_tag.text
        title_text = title_text.replace("\n", "")
        title_text = title_text.replace(u"\xa0", "")
        title_text = title_text.strip()
        if title_text.__contains__("성 강화"):
            title_text = title_text[:-6]
        title_text = title_text.strip()
        return title_text

    def _equip_category(self):
        category_tag = self._equip_tag.select_one(".item_ability > div:nth-child(3) > span > em")
        category_text = category_tag.text
        return category_text

    def _equip_stats_tag_dict(self):
        """return bs4.element.ResultSet
        [0] : STR, [1]: DEX, [2] : INT, [3] : LUK, [4] : MaxHP, [5] : 공격력, [6] : 물리방어력"""
        stet_tag_set = self._equip_tag.select(".stet_info > ul > li")
        stats_dict = {}
        for li_tag in stet_tag_set:
            attr = li_tag.select_one(".stet_th span").text
            attr = attr.replace("\n", "")
            attr = attr.strip()
            value_tag = li_tag.select_one(".point_td")
            stats_dict[attr] = value_tag
        return stats_dict

    @property
    def title(self):
        return self._title

    @property
    def category(self):
        return self._category

    @property
    def stats_dict(self):
        return self._stats_dict
