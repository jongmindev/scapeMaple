import geturl
import parsetag
import equipment
from parsetag import EQUIPMENT_INDEX


class ItemScouter:
    def __init__(self, nickname: str, background: bool = False, progress_notification: bool = False):
        self._equipments_info_dict = {}
        self.scout(nickname, background, progress_notification)

    def scout(self, nickname: str, background: bool, progress_notification: bool):
        equipment_url = geturl.GetDetailEquipmentUrl(nickname).equipment_url
        if progress_notification:
            print("<<< Get equipment detail url : Done >>>")
            print()
        parsetag.is_maintenance_in_progress(equipment_url)
        if progress_notification:
            print("<<< Check maintenance : Done >>>")
            print()
        open_browser = parsetag.BrowserForEquipmentTag(equipment_url, background)
        if progress_notification:
            print("<<< Soup equipment detail html : Done >>>")
            print()
        for item in EQUIPMENT_INDEX.keys():
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
