import geturl
import parsetag
import equipment
from parsetag import EQUIPMENT_INDEX


class ItemScouter:
    def __init__(self, nickname: str):
        self._equipments_info_dict = {}
        self.scout(nickname)

    def scout(self, nickname):
        equipment_url = geturl.GetDetailEquipmentUrl(nickname).equipment_url
        open_browser = parsetag.BrowserForEquipmentTag(equipment_url)
        for item in EQUIPMENT_INDEX.keys():
            item_info_tag = open_browser.get_equipment_info_tag(item)
            item_information = equipment.TrimmedInformation(item_info_tag)
            self._equipments_info_dict[item] = item_information
        open_browser.quit_browser()

    @property
    def equipments_info_dict(self):
        return self._equipments_info_dict


if __name__ == "__main__":
    my_equipments = ItemScouter("히슈와")
