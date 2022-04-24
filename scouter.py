import geturl
import parsetag
import equipment
from parsetag import EQUIPMENT_INDEX
import requests
from bs4 import BeautifulSoup
import pandas as pd


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
        parsetag.is_available(equipment_url)
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

    def print_all(self, option_summary: bool = True):
        if option_summary:
            dictionary = self._summary_info_dict
        else:
            dictionary = self._equipments_info_dict

        for category, information in dictionary.items():
            print(f"<<<<< {category} >>>>>")
            information.print_all_attribute()
            print()

    @property
    def equipments_info_dict(self):
        return self._equipments_info_dict

    @property
    def summary_info_dict(self):
        return self._summary_info_dict


class PandasScouter(ItemScouter):
    def __init__(self, nickname: str, background: bool = False, progress_notification: bool = False):
        """
        ItemScouter 클래스를 상속받아 기능추가.

        모든 아이템 정보를 하나의 pandas dataframe 으로 저장.

        :param nickname: want to search (str)
        :param background: selenium browser background run or not option (bool)
        :param progress_notification: print progress option (bool)
        """
        super().__init__(nickname, background, progress_notification)
        self._summary_info_pandas = self._convert_summary_info_dict_to_df()
        self._total_stat = self._summary_info_pandas.iloc[:-1, 2:].sum(axis=0)

    @staticmethod
    def _summary_info_to_dict(summary_info: equipment.SummaryInformation):
        """
        pandas DataFrame 의 각 row 가 되도록 dictionary 로 변환.

        단독으로 쓰이지 않고 아래 _convert_summary_info_dict_to_df() 안에서 호출.

        :param summary_info: summarized information of the target equipment (equipment.SummaryInformation)
        :return: dictionarized information (dict)
        """
        dictionary = {}
        for attr, value in summary_info.__dict__.items():
            if type(value) == str:
                dictionary[attr[1:].upper()] = value
            elif type(value) == tuple:
                dictionary[attr[1:].upper()] = value[0]
                dictionary[attr[1:].upper()+'(%)'] = value[1]
            else:
                pass
        return dictionary

    def _convert_summary_info_dict_to_df(self):
        """
        아이템 정보를 하나의 pandas DataFrame 으로 저장.

        마지막 row 는 모든 아이템 option 수치의 합.

        :return: information DataFrame (pandas.DataFrame)
        """
        df = pd.DataFrame()
        for category, summary_info in super().summary_info_dict.items():
            index = parsetag.EQUIPMENT_INDEX[category]
            data = self._summary_info_to_dict(summary_info)
            new_df = pd.DataFrame(data=data, index=[index])
            df = pd.concat([df, new_df])

        # 합계 row 추가
        total_row = df.iloc[:, 2:].sum(axis=0)
        df.loc['Total'] = total_row
        return df

    def tabulate_information(self):
        import tabulate
        print(tabulate.tabulate(self.summary_info_pandas, headers='keys', tablefmt='presto'))

    @property
    def summary_info_pandas(self):
        return self._summary_info_pandas

    @property
    def total_stat(self):
        return self._total_stat


if __name__ == "__main__":
    pass
