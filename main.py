import scouter


# 정보공개 되어있는 경우
NICKNAME = "히슈와"
pandas_scouter = scouter.PandasScouter(nickname=NICKNAME, background=True, progress_notification=True)
pandas_scouter.print_infomation()

# 정보공개 되어있지 않은 경우
# NICKNAME = "오지환"
# pandas_scouter = scouter.PandasScouter(nickname=NICKNAME, background=True, progress_notification=True)
# pandas_scouter.print_infomation()

# 존재하지 않거나 랭킹에 노출되지 않는 캐릭터인 경우
NICKNAME = "!@#$%^&*()"
pandas_scouter = scouter.PandasScouter(nickname=NICKNAME, background=True, progress_notification=True)
pandas_scouter.print_infomation()
