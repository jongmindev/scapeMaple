from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from bs4 import Tag
import re
# from copy import copy


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
        self._category = self._equip_category()
        self._stats_dict = self._equip_stats_tag_dict()

    def _equip_title(self):
        title_tag = self._equip_tag.select_one(".item_title h1")
        title_tag.select_one("em").extract()
        title_text = title_tag.text
        title_text = title_text.replace("\n", "")
        title_text = title_text.replace(u"\xa0", "")
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


class SecondParsingInfoTag:
    def __init__(self, first: FirstParsingInfoTag):
        self._first = first
        self._name = self._set_title()
        self._scroll = self._set_scroll()
        self._category = self._set_category()
        self._stats_dict = self._set_stats_dict()
        self._potential = self._set_potential()
        self._additional = self._set_additional_potential()
        starforce_tuple = self._set_starforce()
        self._starforce_max = starforce_tuple[0]
        self._starforce_now = starforce_tuple[1]
        self._hammer = self._set_hammer()

    def _set_title(self) -> str:
        """first.title -> name of the equip"""
        if self._first.title[-1] != ")":
            equip_name = self._first.title
        else:
            pattern = re.compile(r".+(?=\s\(\+\d+\))")
            equip_name = pattern.search(self._first.title).group()
        self._type_checker(equip_name, str)
        return equip_name

    def _set_scroll(self) -> int:
        """first.title -> scroll success times"""
        if self._first.title[-1] != ")":
            scroll_times = 0
        else:
            pattern = re.compile(r"\s\(\+(\d+)\)")
            scroll_times = pattern.search(lightly_parsed.title).group(1)
        scroll_times = int(scroll_times)
        self._type_checker(scroll_times, int)
        return scroll_times

    def _set_category(self) -> str:
        """first.category -> category of the equip"""
        self._type_checker(self._first.category, str)
        equip_category = self._first.category
        return equip_category

    def _set_stats_dict(self) -> dict:
        """first.stats_dict -> dict of STR/DEX/INT/LUK/MaxHP/Defense/AllStats/
        AttackPower/MagicAttack/BossDamage/IgnoreDEF/... -> """
        equip_stats_dict = {}
        for key_str, value_tag in self._first.stats_dict.items():
            if (key_str[:4] == "잠재옵션") | (key_str[:9] == "에디셔널 잠재옵션") | (key_str == "기타"):
                pass
            else:
                equip_stats_dict[key_str] = value_tag.text
        return equip_stats_dict

    def _set_potential(self) -> tuple[str, list]:
        """first.stats_dict -> tier and 3 options of potential"""
        tier = '일반'
        options_list = []
        for key_str, value_tag in self._first.stats_dict.items():
            if key_str[:4] == "잠재옵션":
                pattern = re.compile(r"\((\w+).+\)")
                tier = pattern.search(key_str).group(1)
                options_list = value_tag.get_text(strip=True, separator='\n').splitlines()
            else:
                pass
        return tier, options_list

    def _set_additional_potential(self) -> tuple[str, list]:
        """first.stats_dict -> tier and 3 options of additional potential"""
        tier = '일반'
        options_list = []
        for key_str, value_tag in self._first.stats_dict.items():
            if key_str[:9] == "에디셔널 잠재옵션":
                pattern = re.compile(r"\((\w+).+\)")
                tier = pattern.search(key_str).group(1)
                options_list = value_tag.get_text(strip=True, separator='\n').splitlines()
            else:
                pass
        return tier, options_list

    def _etc_to_list(self) -> list[str]:
        """first.stats_dict 의 기타의 값 -> list split"""
        etc_list = []
        for key_str, value_tag in self._first.stats_dict.items():
            if key_str == "기타":
                etc_list = value_tag.get_text(strip=True, separator='\n').splitlines()
        return etc_list

    def _set_starforce(self) -> tuple[int, int]:
        """first.stats_dict -> (max starforce, starforce of the equip)"""
        etc_list = self._etc_to_list()
        star_values = []
        for text in etc_list:
            if text.__contains__("성까지 강화 가능"):
                positive_integers_str = ''.join((ch if ch in '0123456789' else ' ') for ch in text).split()
                for integer in positive_integers_str:
                    star_values.append(int(integer))
            else:
                pass
        if len(star_values) == 0:
            star_values = (0, 0)
        elif len(star_values) == 1:
            star_values = (star_values[-1], 0)
        elif len(star_values) == 2:
            star_values = (star_values[-1], star_values[0])
        else:
            raise ValueError("Wrong starforce parsing.")
        return star_values

    def _set_hammer(self) -> bool:
        """first.stats_dict -> whether to use hammer"""
        etc_list = self._etc_to_list()
        hammer_used = False
        for text in etc_list:
            if text.__contains__("황금망치 제련 적용"):
                hammer_used = True
        return hammer_used

    @staticmethod
    def _type_checker(checked, type_restraint: object):
        if type(checked) != type_restraint:
            raise TypeError(f"{checked} : Wrong type. Should be {type_restraint}, but it is {type(type_restraint)}.")


if __name__ == "__main__":
    my_url = "https://maplestory.nexon.com/Common/Character/Detail/%ed%9e%88%ec%8a%88%ec%99%80/Equipment?p=mikO8qgdC4hElCwBGQ6GOx8CmO11EvduZkV0bRbPAhaRzW5LQRf8%2f4r4oCWC0wKML5gmImzNTiIxKN9nZv55Kkg56a2qImGHSENhY4orAkJSLirlbSciSAERq3rRq3Ftoo99qXg0H4wl0mgR42y%2fHGGoF6ETGipGOuQfOUaPK%2f0%3d"

    hishuwa = EquipInfoTag(my_url)
    item_soup_ring = hishuwa.get_equip_info_tag(3)
    hishuwa.browser_quit()
    lightly_parsed = FirstParsingInfoTag(item_soup_ring)
    print("TITLE")
    print(lightly_parsed.title)
    print()
    print("CATEGORY")
    print(lightly_parsed.category)
    print()
    print("STAT_DICT")
    print(lightly_parsed.stats_dict)

    heavy_parsed = SecondParsingInfoTag(lightly_parsed)
    print(heavy_parsed._set_title())
    print(heavy_parsed._set_scroll())
    print(heavy_parsed._set_category())
    print(heavy_parsed._set_stats_dict())
    print(heavy_parsed._set_potential())
    print(heavy_parsed._set_additional_potential())
    print(heavy_parsed._etc_to_list())
    print(heavy_parsed._set_starforce())
    print(heavy_parsed._set_hammer())

    # import bs4
    # help(bs4.element.Tag)
    # help(bs4.element.ResultSet)
    # help(bs4.element.Tag.select)
    # help(bs4.Tag)
