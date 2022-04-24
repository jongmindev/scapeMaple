import requests
from bs4 import BeautifulSoup
import re


class GetCharacterDetailUrl:
    MAIN_URL = "https://maplestory.nexon.com"
    HOME_URL = MAIN_URL + "/Home/Main"
    RANKING_URL = MAIN_URL + "/Ranking/World/Total"

    def __init__(self, nickname: str):
        """
        해당 nickname 의 캐릭터 정보 page 의 url 을 get.

        각 캐릭터의 정보 page url 에 뚜렷한 규칙이 보이지 않고, 심지어 주기적으로 변경되는 듯 함.
        따라서 매번 랭킹 검색하여 알아냄.

        너무 자주 실행하는 경우 서버에서 막아버리는 듯.

        단독으로 사용되지는 않고, 아래 GetDetailEquipmentUrl 에서 내부적으로 선언하는 방식으로만 사용됨.

        :param nickname: want to search (str)
        """
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
            raise RuntimeError("랭킹 검색 결과 존재하지 않음. 닉네임을 확인하세요.")
        return GetCharacterDetailUrl.MAIN_URL + url_suffix

    @property
    def detail_url(self):
        return self._detail_url


class GetDetailEquipmentUrl:
    MAIN_URL = "https://maplestory.nexon.com"
    HOME_URL = MAIN_URL + "/Home/Main"
    RANKING_URL = MAIN_URL + "/Ranking/World/Total"

    def __init__(self, nickname: str):
        """
        해당 nickname 의 장비 정보 page 의 url 을 get.

        :param nickname: want to search (str)
        """
        self.nickname = nickname
        detail_url = GetCharacterDetailUrl(nickname).detail_url
        response = requests.get(detail_url)
        self._soup = BeautifulSoup(response.text, 'html.parser')
        self._equipment_url = self._find_equipment_url()

    def _find_equipment_url(self) -> str:
        target_tag = self._soup.find("a", string=re.compile(r"장비"))
        url_suffix = target_tag['href']
        # url suffix 를 제대로 찾았는지 유효성 검사
        pattern = re.compile(r"/Common/Character/Detail/.+/Equipment\?p.+")
        if pattern.match(url_suffix) is None:
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
