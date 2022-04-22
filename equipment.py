from parsetag import ParseInfoTag
from bs4.element import Tag
import re


class EquipmentInformation:
    """
    name, scroll, category, stats_dict, potential, additional, starforce, superior, (amazing,) hammer
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
        """parsed_tag.title -> name of the equip"""
        if self._parsed_tag.title[-1] != ")":
            equip_name = self._parsed_tag.title
        else:
            pattern = re.compile(r".+(?=\s\(\+\d+\))")
            equip_name = pattern.search(self._parsed_tag.title).group()
        self._type_checker(equip_name, str)
        return equip_name

    def _set_scroll(self) -> int:
        """parsed_tag.title -> scroll success times"""
        if self._parsed_tag.title[-1] != ")":
            scroll_times = 0
        else:
            pattern = re.compile(r"\s\(\+(\d+)\)")
            scroll_times = pattern.search(self._parsed_tag.title).group(1)
        scroll_times = int(scroll_times)
        self._type_checker(scroll_times, int)
        return scroll_times

    def _set_category(self) -> str:
        """parsed_tag.category -> category of the equip"""
        self._type_checker(self._parsed_tag.category, str)
        equip_category = self._parsed_tag.category
        return equip_category

    def _set_stats_dict(self) -> dict:
        """parsed_tag.stats_dict -> dict of STR/DEX/INT/LUK/MaxHP/Defense/AllStats/
        AttackPower/MagicAttack/BossDamage/IgnoreDEF/... -> """
        equip_stats_dict = {}
        for key_str, value_tag in self._parsed_tag.stats_dict.items():
            if (key_str[:4] == "잠재옵션") | (key_str[:9] == "에디셔널 잠재옵션") | (key_str == "기타"):
                pass
            else:
                equip_stats_dict[key_str] = value_tag.text
        return equip_stats_dict

    def _set_potential(self) -> tuple[str, list]:
        """parsed_tag.stats_dict -> tier and 3 options of potential"""
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
        """parsed_tag.stats_dict -> tier and 3 options of additional potential"""
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
        """parsed_tag.stats_dict 의 기타의 값 -> list split"""
        etc_list = []
        for key_str, value_tag in self._parsed_tag.stats_dict.items():
            if key_str == "기타":
                etc_list = value_tag.get_text(strip=True, separator='\n').splitlines()
        return etc_list

    def _set_starforce(self) -> tuple[int, int]:
        """parsed_tag.stats_dict -> (max starforce, starforce of the equip)"""
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
        """parsed_tag.stats_dict -> whether to be superior item"""
        etc_list = self._etc_to_list()
        superior = False
        for text in etc_list:
            if text.__contains__("슈페리얼"):
                superior = True
        return superior

    def _set_amazing(self) -> bool:
        """미구현미구현미구현미구현미구현미구현미구현"""
        return False

    def _set_hammer(self) -> bool:
        """parsed_tag.stats_dict -> whether to use hammer"""
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
    def __init__(self, equipment_info_tag: Tag):
        parsed_tag = ParseInfoTag(equipment_info_tag)
        super(TrimmedInformation, self).__init__(parsed_tag)
        self._stat_options = self._trim_stats_dict()
        self._potential_tier = super().potential[0]
        self._potential_options = self._trim_potential(super().potential)
        self._additional_tier = super().additional[0]
        self._additional_options = self._trim_potential(super().additional)

    def _trim_stats_dict(self) -> dict:
        trimmed = {}
        for key, value in super().stats_dict.items():
            trimmed[key] = value.split()[0]
        return trimmed

    def _trim_potential(self, super_pot_add) -> dict:
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
        print("name__", self.name)
        print("scroll", self.scroll)
        print("cate__", self.category)
        # print("stat__", self.stats_dict)
        print("t_stat", self.stat_options)
        # print("poten_", self.potential)
        print("potier", self.potential_tier)
        print("pot_op", self.potential_options)
        # print("addi__", self.additional)
        print("adtier", self.additional_tier)
        print("add_op", self.additional_options)
        print("star_m", self.starforce_max)
        print("star_n", self.starforce_now)
        print("superi", self.superior)
        print("amazin", self.amazing)
        print("hammer", self.hammer)
