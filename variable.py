#API_TOKEN = '6568149173:AAE5D_BWXZTp_hi0f0asq4UpKQxk97I-khE'
# API_TOKEN ='5530121880:AAG6ZwgO5_cPmE4nviXHlyhqROTNUlohdDI' #мой тест

CAPTION = '''Привіт!🧡
Мене звати Синергія. Приєднуйся до нашої великої родини Synergy Family та отримуй 50 коїнів на свій рахунок! Чи є в тебе додаток?'''
#Біртека скучила за тобою! 
#Хочемо запропонувати тобі приєднатися до нашого BRTK Community Зіграти у гру з нами та отримати один з цих приємних бонусів:
#- Знижка на наступне відвідування
#- Давай по пиву
#- Смаколики від шефа
#- Давай по коктейлю
#Та ще багато іншого, що не залишить тебе байдужим!

BUTTON_TEXT = "Почати гру"
# GDRIVE_LINK = 'https://drive.google.com/file/d/1XgyUykvVyz1hFOgCqiuRQPdJQzGyNMke/view?usp=sharing'
GDRIVE_LINK = 'https://drive.google.com/file/d/1aiJJdgmlqzLbg77NFtotO3nGd-xTa0Py/view?usp=sharing'
#BUTTON_LINK = 'beerteka.com'


REPLY_MARKUP = {
    "inline_keyboard": [
        [
            #{"text": BUTTON_TEXT, "callback_data": 'new_game'}
            {"text": 'Так', "callback_data": 'family_yes'},
            {"text": 'Ні', "callback_data": 'family_no'}
        ]
    ]
}