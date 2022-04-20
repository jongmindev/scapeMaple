from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from bs4 import Tag
from copy import copy


class EquipInfoTag:
    def __init__(self, url: str):
        # 캐릭터 정보창 url 을 입력받아 브라우저 실행
        self._browser = webdriver.Chrome()
        self._browser.get(url)

    def _get_equip_element(self, item: str | int):
        """장비 부위 이름 str 또는 li:nth-child int 를 받아서 해당 장비 WebElement 반환"""
        if type(item) == int:
            element = self._browser.find_element(by=By.CSS_SELECTOR,
                                                 value=f"#container ul.item_pot > li:nth-child({item})")
        elif type(item) == str:
            # equip = dict[equip]
            element = self._browser.find_element(by=By.CSS_SELECTOR,
                                                 value=f"#container ul.item_pot > li:nth-child({item})")
        else:
            raise TypeError("parameter : str or int")
        return element

    def get_equip_info_tag(self, equip: str | int):
        # 찾고자 하는 장비를 클릭
        item_element = self._get_equip_element(equip)
        item_element.click()
        # 클릭 이후 바뀐 html get
        html = self._browser.page_source
        # BSoup 으로 전체 html 파싱
        soup = BeautifulSoup(html, 'html.parser')
        # 해당 장비 정보 탭 부분만 파싱
        item_info = soup.select_one("#container div.tab01_con_wrap > div.item_info > div")
        return item_info

    def browser_quit(self):
        self._browser.quit()


class FirstParsingInfoTag:
    def __init__(self, equip_info_tag: Tag):
        self._equip_tag = equip_info_tag
        self._title = self._equip_title()
        self._category = self._eqiup_category()
        self._stats_dict = self._equip_stats_dict()

    def _equip_title(self):
        title_tag = self._equip_tag.select_one(".item_title h1")
        title_tag.extract("em")
        title_text = title_tag.text
        return title_text

    def _eqiup_category(self):
        category_tag = self._equip_tag.select_one(".item_ability > div:nth-child(3) > span").extract("em")
        category_text = category_tag.text
        return category_text

    def _equip_stats_dict(self):
        """return bs4.element.ResultSet
        [0] : STR, [1]: DEX, [2] : INT, [3] : LUK, [4] : MaxHP, [5] : 공격력, [6] : 물리방어력"""
        stet_tag_set = self._equip_tag.select(".stet_info > ul > li")
        stats_dict = {}
        for li_tag in stet_tag_set:
            attr = li_tag.select_one(".stet_th span").text
            value = li_tag.select_one(".point_td").text
            stats_dict[attr] = value
        return stats_dict

    @property
    def title(self):
        return self._title

    @property
    def category(self):
        return self._category

    @property
    def stat_dict(self):
        return self._stats_dict


# class SecondParsingInfoTag:
#     def __init__(self, first: FirstParsingInfoTag):
#         self._first = first
#
#     def _trim_title(self):
#         first_title = self._first.title


my_url = "https://maplestory.nexon.com/Common/Character/Detail/%ed%9e%88%ec%8a%88%ec%99%80/Equipment" \
      "?p=mikO8qgdC4hElCwBGQ6GOx8CmO11EvduZkV0bRbPAhaRzW5LQRf8%2f4r4oCWC0wKML5gmImzNTiIxKN9nZv55K" \
      "kg56a2qImGHSENhY4orAkJSLirlbSciSAERq3rRq3FtpAqMU%2bqxT7bVxfZCeH0ph%2fdvyNYQdFxnobclv5nlxmE%3d"

hishuwa = EquipInfoTag(my_url)
item_soup = hishuwa.get_equip_info_tag(1)
print(type(item_soup))
hishuwa.browser_quit()
# import bs4
# help(bs4.element.Tag)
# help(bs4.element.ResultSet)
# help(bs4.element.Tag.select)
# help(bs4.Tag)