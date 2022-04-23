from parsetag import ParseInfoTag
from bs4.element import Tag
import re


class EquipmentInformation:
    """
    1차 parsing 된 정보를 담고 있는 ParseInfoTag 클래스를 받아
    그 많은 정보들 중 스펙 시뮬레이터에 필요할 수 있는 이하의 정보만 선택적으로 2차 parsing

    name, scroll, category, stats_dict, potential, additional, starforce, superior, (amazing,) hammer

    :param parsed_tag: pre-parsed information of the target equipment (ParseInfoTag)
    """
    def __init__(self, parsed_tag: ParseInfoTag):
        self._parsed_tag = parsed_tag
        self._name = self._set_title()
        self._scroll = self._set_scroll()
        self._category = self._set_category()
        self._stats_dict = self._set_stats_dict()
        self._potential = self._set_potential()
        self._additional = self._set_additional_potential()
        starforce_tuple = self._set_starforce()
        self._starforce_max = starforce_tuple[0]
        self._starforce_now = starforce_tuple[1]
        self._superior = self._set_superior()
        self._amazing = self._set_amazing()
        self._hammer = self._set_hammer()

    def _set_title(self) -> str:
        """
        ParseInfoTag.title 에서 장비 이름을 추출

        :return: name of the target equipment (str)
        """
        # title 에 ' (+숫자)' 가 있다면
        if self._parsed_tag.title[-1] != ")":
            equip_name = self._parsed_tag.title
        # title 이 ' (+숫자)' 로 끝난다면.
        else:
            equip_name = re.match(r".+(?=\s\(\+\d+\))", self._parsed_tag.title).group()
        self._type_checker(equip_name, str)
        # title 의 multi whitespace 삭제
        equip_name = re.sub(' +', ' ', equip_name)
        return equip_name

    def _set_scroll(self) -> int:
        """
        ParseInfoTag.title 에서 주문서 성공횟수를 추출

        :return: scroll success times (int)
        """
        if self._parsed_tag.title[-1] != ")":
            scroll_times = 0
        else:
            # title 에 ' (+숫자)' 가 있는지.
            scroll_times = re.search(r"\s\(\+(\d+)\)", self._parsed_tag.title).group(1)
        scroll_times = int(scroll_times)
        self._type_checker(scroll_times, int)
        return scroll_times

    def _set_category(self) -> str:
        """
        ParseInfoTag.category 에서 장비분류를 추출

        :return: category of the equipment (str)
        """
        self._type_checker(self._parsed_tag.category, str)
        equip_category = self._parsed_tag.category
        return equip_category

    def _set_stats_dict(self) -> dict:
        """
        ParseInfoTag.stats_dict 에서 잠재옵션, 에디셔널 잠재옵션, 기타 항목이 아닌
        일반 옵션(STR, DEX, INT, LUK, MaxHP, 공격력, 마력 등) 부분을 dictionary 로 저장 (중복되지 않으므로)

        :return: options of the equipment (dict[str, str])
        """
        equip_stats_dict = {}
        for key_str, value_tag in self._parsed_tag.stats_dict.items():
            if (key_str[:4] == "잠재옵션") | (key_str[:9] == "에디셔널 잠재옵션") | (key_str == "기타"):
                pass
            else:
                equip_stats_dict[key_str] = value_tag.text
        return equip_stats_dict

    def _set_potential(self) -> tuple[str, list]:
        """
        ParseInfoTag.stats_dict 에서 잠재옵션 항목(등급 및 옵션)을 tuple[str, list] 로 저장 (중복 가능성 있으므로)

        :return: tier and 3 (or less) options of potential (tuple[str, list])
        """
        tier = '일반'
        options_list = []
        for key_str, value_tag in self._parsed_tag.stats_dict.items():
            if key_str[:4] == "잠재옵션":
                pattern = re.compile(r"\((\w+).+\)")
                if pattern.search(key_str) is not None:
                    tier = pattern.search(key_str).group(1)
                options_list = value_tag.get_text(strip=True, separator='\n').splitlines()
            else:
                pass
        return tier, options_list

    def _set_additional_potential(self) -> tuple[str, list]:
        """
        ParseInfoTag.stats_dict 에서 에디셔널 잠재옵션 항목(등급 및 옵션)을 tuple[str, list] 로 저장 (중복 가능성 있으므로)

        :return: tier and 3 (or less) options of additional potential (tuple[str, list])
        """
        tier = '일반'
        options_list = []
        for key_str, value_tag in self._parsed_tag.stats_dict.items():
            if key_str[:9] == "에디셔널 잠재옵션":
                pattern = re.compile(r"\((\w+).+\)")
                if pattern.search(key_str) is not None:
                    tier = pattern.search(key_str).group(1)
                options_list = value_tag.get_text(strip=True, separator='\n').splitlines()
            else:
                pass
        return tier, options_list

    def _etc_to_list(self) -> list[str]:
        """
        ParseInfoTag.stats_dict 에서 기타 항목의 값을 split 된 list 로 저장

        :return: contents of etc. (list[str])
        """
        etc_list = []
        for key_str, value_tag in self._parsed_tag.stats_dict.items():
            if key_str == "기타":
                etc_list = value_tag.get_text(strip=True, separator='\n').splitlines()
        return etc_list

    def _set_starforce(self) -> tuple[int, int]:
        """
        ParseInfoTag.stats_dict 기타 항목에서 최대 스타포스 수치, 현재 스타포스 수치를 확인하고 tuple 로 저장

        :return: max starforce and present starforce (tuple[int, int])
        """
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

    def _set_superior(self) -> bool:
        """
        ParseInfoTag.stats_dict 기타 항목에서 슈페리얼 아이템인지 여부를 확인하고 boolean 값으로 저장

        :return: whether superior or not (bool)
        """
        etc_list = self._etc_to_list()
        superior = False
        for text in etc_list:
            if text.__contains__("슈페리얼"):
                superior = True
        return superior

    def _set_amazing(self) -> bool:
        """
        ParseInfoTag.stats_dict 기타 항목에서 놀장강 여부를 확인하고 boolean 값으로 저장.

        아직 미구현.

        :return: whether amazing or not (bool)
        """
        pass

    def _set_hammer(self) -> bool:
        """
        ParseInfoTag.stats_dict 기타 항목에서 황금망치 제련 적용 여부를 확인하고 boolean 값으로 저장.

        :return: whether to use hammer or not (bool)
        """
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

    @property
    def name(self):
        return self._name

    @property
    def scroll(self):
        return self._scroll

    @property
    def category(self):
        return self._category

    @property
    def stats_dict(self):
        return self._stats_dict

    @property
    def potential(self):
        return self._potential

    @property
    def additional(self):
        return self._additional

    @property
    def starforce_max(self):
        return self._starforce_max

    @property
    def starforce_now(self):
        return self._starforce_now

    @property
    def superior(self):
        return self._superior

    @property
    def amazing(self):
        return self._amazing

    @property
    def hammer(self):
        return self._hammer


class TrimmedInformation(EquipmentInformation):
    """
    EquipmentInformation 에서 2차 parsing 한 장비 정보를 재가공.

    2차 parsing 으로 충분했던 정보는 그대로 두고, 추가로 가공해야하는 정보만 재가공함.

    :param equipment_info_tag: 2nd parsed information of the target equipment (EquipmentInformation)
    """
    def __init__(self, equipment_info_tag: Tag):
        parsed_tag = ParseInfoTag(equipment_info_tag)
        super(TrimmedInformation, self).__init__(parsed_tag)
        self._stat_options = self._trim_stats_dict()
        self._potential_tier = super().potential[0]
        self._potential_options = self._trim_potential(super().potential)
        self._additional_tier = super().additional[0]
        self._additional_options = self._trim_potential(super().additional)

    def _trim_stats_dict(self) -> dict:
        """
        장비 option 항목의 정보가 (기본옵션 + 추가옵션 + 주문서 및 스타포스 상승치) 로 구분되어 있는 것을,
        구분된 부분은 삭제하고 합계만 남겨놓음.

        % 수치의 존재 때문에 int 가 아닌 str 로 그대로 저장. 이는 추후에 가공.

        :return: just total stat of each options (dict[str, str])
        """
        trimmed = {}
        for key, value in super().stats_dict.items():
            trimmed[key] = value.split()[0]
        return trimmed

    @staticmethod
    def _trim_potential(super_pot_add: tuple[str, list]) -> dict:
        """
        장비의 잠재능력 또는 에디셔널 잠재능력의 option 에 대한 정보를 전달받아 재가공.

        잠재능력 또는 에디셔널 잠재능력은 중복가능성이 있어 dictionary 로 저장하지 못했던 것을,
        중복된 내용은 하나의 key 에 string 이어 붙이기(+로 구분됨) 하여 dictionary 로 저장.

        :param super_pot_add: potential tuple or additional potential tuple of parent class (tuple[str, list])
        :return: trimmed option information about potential or additional potential (dict[str, str])
        """
        trimmed = {}
        for line in super_pot_add[1]:
            if line.__contains__(' : '):
                stat, value = line.split(' : ')
                try:
                    trimmed[stat] += value
                except KeyError:
                    trimmed[stat] = value
            else:
                try:
                    trimmed[line] += 1
                except KeyError:
                    trimmed[line] = 1
        return trimmed

    # def _trim_additional(self) -> dict:
    #     trimmed = {}
    #     for line in super().additional[1]:
    #         if line.__contains__(' : '):
    #             stat, value = line.split(' : ')
    #             try:
    #                 trimmed[stat] += value
    #             except KeyError:
    #                 trimmed[stat] = value
    #         else:
    #             try:
    #                 trimmed[line] += 1
    #             except KeyError:
    #                 trimmed[line] = 1
    #     return trimmed

    @property
    def stat_options(self):
        return self._stat_options

    @property
    def potential_tier(self):
        return self._potential_tier

    @property
    def potential_options(self):
        return self._potential_options

    @property
    def additional_tier(self):
        return self._additional_tier

    @property
    def additional_options(self):
        return self._additional_options

    def print_all_attribute(self):
        for attr, value in self.__dict__.items():
            print(f"{attr:>19} :", value)


class SummaryInformation:
    def __init__(self, equipment_information: TrimmedInformation):
        """
        장비 정보의 최종 가공(요약).
        스펙 시뮬레이터에 필수적인 정보만 저장.

        option, potential, additional potential 을 구분하지 않고,
        STR, DEX, INT, LUK, ... 등 stat 별로 option 수치를 저장.

        이때 고정값 상승치과 % 상승치를 구분하여 tuple 로 저장.
        tuple 의 첫번째 값이 고정상승치, 두번째 값이 % 상승치.

        :param equipment_information: 3rd parsed information of the target equipment (TrimmedInformation)
        """
        self._equipment_information = equipment_information
        self._name = self._set_name()
        self._category = self._set_category()
        self._str = self._set_str()
        self._dex = self._set_dex()
        self._int = self._set_int()
        self._luk = self._set_luk()
        self._maxhp = self._set_maxhp()
        self._allstat = self._set_allstat()
        self._attack = self._set_attack_power()
        self._magic_attack = self._set_magic_attack()
        self._critical_damage = self._set_critical_damage()
        self._boss_damage = self._set_boss_damage()
        self._damage = self._set_damage()
        self._ignore_def = self._set_ignore_def()
        self._critical_rate = self._set_critical_rate()

    def _set_name(self):
        return self._equipment_information.name

    def _set_category(self):
        return self._equipment_information.category

    def _search_and_append_stats(self, stat_keyword: str) -> str:
        """
        특정 stat (예: STR, DEX, 보공, 크뎀 등) 의 상승수치가 저장되어 있을 dictionary 에서 그 상승수치를 검색한 다음,
        모든 상승수치(str) 을 addition 한 string 을 반환

        (반환 값 예시 : '+45+12%+9%+9%')

        :param stat_keyword: search keyword (str)
        :return: added string about options of 'search keyword' (str)
        """
        try:
            basic = self._equipment_information.stat_options[stat_keyword]
        except KeyError:
            basic = ""
        try:
            potential = self._equipment_information.potential_options[stat_keyword]
        except KeyError:
            potential = ""
        try:
            additional = self._equipment_information.additional_options[stat_keyword]
        except KeyError:
            additional = ""
        return basic + potential + additional

    @staticmethod
    def _summate_stat(string: str) -> tuple[int, int]:
        """
        '+45+12%+9%+9%' 와 같이 저장된 string 에서 + 기준으로 split 한 후,
        고정값 상승치와 %값 상승치를 구분하여 tuple 로 저장.

        :param string: added string of stat options ('+45+12%+9%+9%') (str)
        :return: (+fixed option, +% option) (tuple[int, int])
        """
        fixed, percent = 0, 0
        split_list = string.split('+')
        for split in split_list:
            if split == '':
                pass
            elif split[-1] == '%':
                percent += int(split[:-1])
            else:
                fixed += int(split)
        return fixed, percent

    def _set_str(self):
        aggregated = self._search_and_append_stats('STR')
        return self._summate_stat(aggregated)

    def _set_dex(self):
        aggregated = self._search_and_append_stats('DEX')
        return self._summate_stat(aggregated)

    def _set_int(self):
        aggregated = self._search_and_append_stats('INT')
        return self._summate_stat(aggregated)

    def _set_luk(self):
        aggregated = self._search_and_append_stats('LUK')
        return self._summate_stat(aggregated)

    def _set_maxhp(self):
        # alias 확인 완료
        agg1 = self._search_and_append_stats('MaxHP')
        agg2 = self._search_and_append_stats('최대 HP')
        aggregated = agg1 + agg2
        return self._summate_stat(aggregated)

    def _set_allstat(self):
        aggregated = self._search_and_append_stats('올스탯')
        return self._summate_stat(aggregated)

    def _set_attack_power(self):
        aggregated = self._search_and_append_stats('공격력')
        return self._summate_stat(aggregated)

    def _set_magic_attack(self):
        aggregated = self._search_and_append_stats('마력')
        return self._summate_stat(aggregated)

    def _set_critical_damage(self):
        aggregated = self._search_and_append_stats('크리티컬 데미지')
        return self._summate_stat(aggregated)

    def _set_boss_damage(self):
        agg1 = self._search_and_append_stats('보스 몬스터공격 시 데미지')
        agg2 = self._search_and_append_stats('보스 몬스터 공격 시 데미지')
        aggregated = agg1 + agg2
        return self._summate_stat(aggregated)

    def _set_damage(self):
        aggregated = self._search_and_append_stats('데미지')
        return self._summate_stat(aggregated)

    def _set_ignore_def(self):
        agg1 = self._search_and_append_stats('몬스터 방어율 무시')
        agg2 = self._search_and_append_stats('몬스터 방어력 무시')
        aggregated = agg1 + agg2
        return self._summate_stat(aggregated)

    def _set_critical_rate(self):
        aggregated = self._search_and_append_stats('크리티컬 확률')
        return self._summate_stat(aggregated)

    def print_all_attribute(self):
        for attr, value in self.__dict__.items():
            print(f"{attr:>16} :", value)


if __name__ == "__main__":
    import scouter

    my_equipments = scouter.ItemScouter("히슈와", True, True)
    for category, info in my_equipments.equipments_info_dict.items():
        print(f"<<<<< {category} >>>>>")
        info.print_all_attribute()
        print()
