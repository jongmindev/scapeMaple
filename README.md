# Crawling all Equipments stats of a character.

|STEP|python file|Function|
|:---:|:---------:|:------:|
|1|geturl.py|해당 캐릭터 장비 정보 페이지의 url 획득|
|2|parsetag.py|장비 정보 페이지에서 모든 착용 장비 각각의 정보가 담긴 Tag 획득|
|3|equipment.py|획득한 Tag 를 parsing 하여 장비 option 정보 추출
|4|scouter.py|1 ~ 3 단계의 과정을 종합하여 one-click 수행 및 pandas DataFrame 으로 시각화|
|5|main.py|이상 모든 단계 추상화|
