import scouter


NICKNAME = "히슈와"

pandas_scouter = scouter.PandasScouter(nickname=NICKNAME, background=True, progress_notification=True)
pandas_scouter.print_infomation()
