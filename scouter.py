import geturl
import parsetag
import equipment
from parsetag import EQUIPMENT_INDEX
import requests
from bs4 import BeautifulSoup


class ItemScouter:
    def __init__(self, nickname: str, background: bool = False, progress_notification: bool = False):
        self._equipments_info_dict = {}
        self.scout(nickname, background, progress_notification)

    def _equip_or_not_dict(self, equipment_url: str):
        # shallow copy : no problem (key : str, value: int)
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

    def scout(self, nickname: str, background: bool, progress_notification: bool):
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

        # selenium 가동
        open_browser = parsetag.BrowserForEquipmentTag(equipment_url, background)
        for item in i_equip_dict.keys():
            item_info_tag = open_browser.get_equipment_info_tag(item)
            item_information = equipment.TrimmedInformation(item_info_tag)
            self._equipments_info_dict[item] = item_information
            if progress_notification:
                print(f"<<< Save the information of {item} : Done >>>")
        if progress_notification:
            print()
        open_browser.quit_browser()

    @property
    def equipments_info_dict(self):
        return self._equipments_info_dict


if __name__ == "__main__":
    my_equipments = ItemScouter("히슈와", background=True, progress_notification=True)
    for key, value in my_equipments.equipments_info_dict.items():
        print("<<< " + key + " >>>")
        value.print_all_attribute()
        print()
