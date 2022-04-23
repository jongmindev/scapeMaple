from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from bs4.element import Tag
import requests


EQUIPMENT_INDEX = {'반지1': 1, '모자': 3, '엠블렘': 5,
                   '반지2': 6, '펜던트1': 7, '얼굴장식': 8, '뱃지': 10,
                   '반지3': 11, '펜던트2': 12, '눈장식': 13, '귀고리': 14, '훈장': 15,
                   '반지4': 16, '무기': 17, '상의': 18, '어깨장식': 19, '보조무기': 20,
                   '포켓': 21, '벨트': 22, '하의': 23, '장갑': 24, '망토': 25,
                   '신발': 28, '안드로이드': 29, '기계심장': 30}


def is_available(url):
    """
    홈페이지가 점검 중인지, 그래서 크롤링이 가능한지, 불가능하다면 raise RuntimeError
    해당 캐릭터 정보가 공개되었는지, 그래서 크롤링이 가능한지, 불가능하다면 raise RuntimeError

    :param url: url of equipment detail page (str)
    :return: None
    """
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    maintenance = soup.select_one("#container [alt='메이플스토리 게임 점검 중에는 이용하실 수 없습니다.']") is not None
    if maintenance:
        raise RuntimeError("메이플스토리 게임 점검 중")
    closed = soup.select_one("#container [alt='공개하지 않은 정보입니다.']") is not None
    if closed:
        raise RuntimeError("공개하지 않은 정보입니다.")

class BrowserForEquipmentTag:
    """
    equipment detail page 에서 특정 장비의 item pot 을 클릭하여 html 를 바꾼 후,
    target equipment 의 정보를 bs4.element.Tag 로 크롤링할 수 있도록 함. (get_equipment_info_tag())

    이후 이 Tag 를 ParseInfoTag 로 넘겨서 파싱하도록 함.

    :param url: url of equipment detail page (str)
    :param background: webdriver.ChromeOptions --headless (bool)
    """
    def __init__(self, url: str, background: bool = True):
        # chrome browser 를 열지 않고 background 에서 실행
        options = webdriver.ChromeOptions()
        if background:
            options.add_argument("--headless")
        # 캐릭터정보/장비탭 url 을 입력받아 브라우저 실행
        self._browser = webdriver.Chrome('./chromedriver', chrome_options=options)
        self._browser.get(url)

    def _get_equipment_webelement(self, item: str | int):
        """
        장비 부위 이름 str 또는 li:(n)th-child int n을 받아서 해당 장비 item pot 에 대한 WebElement 반환.

        get_equipment_info_tag 함수의 도구로서, 단독으로 사용되지 않음.

        :param item: category or number of target item pot (EQUIPMENT_INDEX) (str or int)
        :return: Webelement of the target item pot(selenium.webdriver.remote.webelement.WebElement)
        """
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
        """
        target equipment 를 클릭한 한 후 바뀐 html 에서 해당 장비 정보 부분만 Tag 로 파싱

        :param equip: category or number of target item pot (EQUIPMENT_INDEX) (str or int)
        :return: Tag of information about the target(clicked) equipment (bs4.element.Tag)
        """
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
        """
        브라우저 종료. background=True 옵션일 경우, 반드시 명시적으로 호출하여야 함.

        :return: None
        """
        self._browser.quit()
        print("Browser quit!")
        print()


class ParseInfoTag:
    """
    BrowserForEquipmentTag 로 얻은 target equipment 의 정보가 담긴 Tag 를 일차적으로 Parsing.

    :param equipment_info_tag: bs4 Tag about information of target equipments (bs4.element.Tag)
    """
    def __init__(self, equipment_info_tag: Tag):
        self._equip_tag = equipment_info_tag
        self._title = self._equip_title()
        self._category = self._equip_category()
        self._stats_dict = self._equip_stats_tag_dict()

    def _equip_title(self):
        """
        장비이름, 주문서강화 횟수 등이 담긴 title 부분에서 해당 정보를 parsing.
        개행 및 과도한 공백은 적절히 처리

        :return: parsed text (str)
        """
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
        """
        장비 분류가 담긴 부분에서 해당 정보를 parsing

        :return: parsed text (str)
        """
        category_tag = self._equip_tag.select_one(".item_ability > div:nth-child(3) > span > em")
        category_text = category_tag.text
        return category_text

    def _equip_stats_tag_dict(self):
        """
        장비옵션, 잠재능력, 에디셔널 잠재능력, 기타 정보가 담긴 부분을 parsing.

        지금 단계에서는 이상을 곧바로 구분하지 않고
        항목(STR. DEX, ..., 잠재옵션(전체), 에디셔널(전체), 기타)을 key 로,
        해당 항목에 대한 내용을 담근 Tag 를 value 로 갖는 dictionary 에 모두 저장

        :return: information of options, potential, additional, and etc. (dict[str, bs4.element.Tag])
        """
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
