import geturl
import parsetag
import equipment
from parsetag import EQUIPMENT_INDEX
import requests
from bs4 import BeautifulSoup


class ItemScouter:
    def __init__(self, nickname: str, background: bool = False, progress_notification: bool = False):
        """
        검색하고자 하는 캐릭터 이름을 검색하여
        해당 캐릭터가 장착하고 있는 장비 아이템의 정보를 두가지 버전으로 저장.

        :param nickname: want to search (str)
        :param background: selenium browser background run or not option (bool)
        :param progress_notification: print progress option (bool)
        """
        self._equipments_info_dict = self._scout(nickname, background, progress_notification)
        self._summary_info_dict = self._summarize(progress_notification)

    @staticmethod
    def _equip_or_not_dict(equipment_url: str):
        """
        총 25종의 장비 아이템(모자 ~ 기계심장) 중 착용하고 있는 장비 아이템의 목록을 dictionary 로 저장

        :param equipment_url: url of equipment detail page (str)
        :return: dictionary of equipped category (dict[str, int])
        """
        # shallow copy : no problem (Since key : str, value: int)
        i_equip_dict = EQUIPMENT_INDEX.copy()
        html = requests.get(equipment_url)
        soup = BeautifulSoup(html.content, 'html.parser')
        for key, value in EQUIPMENT_INDEX.items():
            item_pot = soup.select_one(f"#container ul.item_pot > li:nth-child({value}) a")
            item_pot_link = item_pot["href"]
            # 해당 아이템을 착용하지 않은 경우
            if item_pot_link == "":
                i_equip_dict.pop(key)
        return i_equip_dict

    def _scout(self, nickname: str, background: bool, progress_notification: bool)\
            -> dict[str, equipment.TrimmedInformation]:
        """
        해당 nickname 의 캐릭터가 현재 착용하고 있는 장비 아이템에 한해,
        그 아이템의 정보를 dictionary 로 저장.

        :param nickname: want to search (str)
        :param background: selenium browser background run or not option (bool)
        :param progress_notification: print progress option (bool)
        :return: information of equipments (dict[str, equipment.TrimmedInformation])
        """
        # 캐릭터정보 > 장비탭 url get
        equipment_url = geturl.GetDetailEquipmentUrl(nickname).equipment_url
        if progress_notification:
            print("<<< Get equipment detail url : Done >>>")
            print()

        # 점검 중 여부 확인
        parsetag.is_maintenance_in_progress(equipment_url)
        if progress_notification:
            print("<<< Check maintenance : Done >>>")
            print()

        # 착용 중인(정보를 추출할) 아이템만 골라서 dictionary 만들기
        i_equip_dict = self._equip_or_not_dict(equipment_url)
        if progress_notification:
            print("<<< Specify equipments to extract the information : Done >>>")
            print()

        equipments_info_dict = {}
        # selenium 가동
        open_browser = parsetag.BrowserForEquipmentTag(equipment_url, background)
        for item in i_equip_dict.keys():
            item_info_tag = open_browser.get_equipment_info_tag(item)
            item_information = equipment.TrimmedInformation(item_info_tag)
            equipments_info_dict[item] = item_information
            if progress_notification:
                print(f"<<< Save the information of {item} : Done >>>")
        if progress_notification:
            print()
        open_browser.quit_browser()
        return equipments_info_dict

    def _summarize(self, progress_notification: bool) -> dict[str, equipment.SummaryInformation]:
        """
        _scout() method 로 얻은 착용 장비 아이템 정보를 요약하여 저장

        :param progress_notification: print progress option (bool)
        :return: summarized information of the equipments (dict[str, equipment.SummaryInformation])
        """
        summary_info_dict = {}
        for category, info in self._equipments_info_dict.items():
            summary_info = equipment.SummaryInformation(info)
            summary_info_dict[category] = summary_info
            if progress_notification:
                print(f"<<< Summary the information of {category} : Done >>>")
        if progress_notification:
            print()
        return summary_info_dict

    @property
    def equipments_info_dict(self):
        return self._equipments_info_dict

    @property
    def summary_info_dict(self):
        return self._summary_info_dict


if __name__ == "__main__":
    my_equipments = ItemScouter("히슈와", background=False, progress_notification=True)
    # for key, value in my_equipments.equipments_info_dict.items():
    #     print("<<< " + key + " >>>")
    #     value.print_all_attribute()
    #     print()
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
    for key, value in my_equipments.summary_info_dict.items():
        print("<<< " + key + " >>>")
        value.print_all_attribute()
        print()
