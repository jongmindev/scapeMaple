import requests
from bs4 import BeautifulSoup
import re


class GetCharacterDetailUrl:
    MAIN_URL = "https://maplestory.nexon.com"
    HOME_URL = MAIN_URL + "/Home/Main"
    RANKING_URL = MAIN_URL + "/Ranking/World/Total"

    def __init__(self, nickname: str):
        self.nickname = nickname
        url = GetCharacterDetailUrl.RANKING_URL + "?c=" + nickname + "&w=0"
        response = requests.get(url)
        self._soup = BeautifulSoup(response.text, 'html.parser')
        self._detail_url = self._find_detail_url()

    def _find_detail_url(self) -> str:
        result_set = self._soup.select("#container div.rank_table_wrap > table.rank_table "
                                      "> tbody > tr > td.left > dl > dt > a")
        url_suffix = ""
        for tag in result_set:
            if tag.get_text() == self.nickname:
                url_suffix = tag['href']
                break
        if url_suffix == "":
            raise RuntimeError("Cannot find the Ranking search result. Wrong nickname OR changed html.")
        return GetCharacterDetailUrl.MAIN_URL + url_suffix

    @property
    def detail_url(self):
        return self._detail_url


class GetDetailEquipmentUrl:
    MAIN_URL = "https://maplestory.nexon.com"
    HOME_URL = MAIN_URL + "/Home/Main"
    RANKING_URL = MAIN_URL + "/Ranking/World/Total"

    def __init__(self, nickname: str):
        self.nickname = nickname
        detail_url = GetCharacterDetailUrl(nickname).detail_url
        response = requests.get(detail_url)
        self._soup = BeautifulSoup(response.text, 'html.parser')
        self._equipment_url = self._find_equipment_url()

    def _find_equipment_url(self) -> str:
        target_tag = self._soup.find("a", string=re.compile(r"장비"))
        url_suffix = target_tag['href']
        # url suffix 를 제대로 찾았는지 유효성 검사
        pattern = re.compile(r"/Common/Character/Detail/.+/Equipment\?p\=.+")
        if type(pattern.match(url_suffix)) == type(None):
            raise RuntimeError("Cannot find the Equipment/.../Equipment url suffix. Changed html.")
        return GetDetailEquipmentUrl.MAIN_URL + url_suffix

    @property
    def equipment_url(self):
        return self._equipment_url


if __name__ == "__main__":
    # print(GetCharacterDetailUrl("히슈와").detail_url)
    # print(GetCharacterDetailUrl("로하예").detail_url)
    # print(GetCharacterDetailUrl("신남").detail_url)
    print(GetDetailEquipmentUrl("히슈와").equipment_url)
    print(GetDetailEquipmentUrl("로하예").equipment_url)
    print(GetDetailEquipmentUrl("신남").equipment_url)
