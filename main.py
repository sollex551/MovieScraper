import sys

import requests
from bs4 import BeautifulSoup
from art import tprint
from colorama import Fore, Back, Style
from tqdm import tqdm

# прогресс бар
def sizeof_fmt(num: int | float) -> str:
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%.1f %s" % (num, x)
        num /= 1024.0
    return "%.1f %s" % (num, 'TB')

films = []

# парсинг ссылок и названия фильмов

def find_data(response):
    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')

        for result in soup.find_all('div', class_='my_razdel film'):
            for i in result.find_all('img'):
                title = i.get("alt")
                for j in result.find_all('a'):
                    link = 'https://ma.anwap.cfd/' + j.get("href")

                    films.append({'title': title, 'page': link})

    else:
        print('Ошибка при выполнении запроса')


filmss = []

# поиск ссылки на скачивания фильма

def download_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for url in soup.find_all('ul', class_='tl2'):
        for i in url.find_all('a'):
            down = 'https://ma.anwap.cfd/' + i.get("href")
            size = i.get_text()
            filmss.append({'size': size, 'url': down})
    return filmss

# функция для загрузки фильмов

def download_film(url, title):

    rs = requests.get(url, stream=True)
    total_size = int(rs.headers.get('content-length', 0))
    chunk_size = 1024
    num_bars = int(total_size / chunk_size)

    with open(f'{title}.mp4', mode='wb') as f:
        for data in tqdm(rs.iter_content(chunk_size), total=num_bars, unit='KB', file=sys.stdout):
            f.write(data)

# меню для выбора фильма

def get_film_title_by_number(films_dict, choice):
    try:
        if choice in films_dict:
            return films_dict[choice]

        else:
            print(Fore.RED + "Неверный номер фильма. Пожалуйста, введите номер от 1 до 10.")

    except ValueError:
        print(Fore.YELLOW + "Пожалуйста, введите корректный номер.")

# меню для выбора качества

def get_url_title_by_number(film_url, choice):
    try:
        if choice in film_url:
            return film_url[choice]

        elif choice == 0:
            return None

        else:
            print(Fore.RED + "Неверный номер загрузки. Пожалуйста, введите номер от 1 до 10.")

    except ValueError:
        print(Fore.YELLOW + "Пожалуйста, введите корректный номер.")


if __name__ == "__main__":
    tprint('Films downloader')
    name = input(Fore.CYAN + 'Введите название фильма: ')
    search_url = f'https://ma.anwap.cfd/films/search/?slv={name}0&vid=1&toch=on'
    response = requests.get(search_url)
    find_data(response)
    films_dict = {}
    film_urls = {}

    index = 1
    # вывол фильмов 
    for j, film in enumerate(films):
        if film.get("title"):
            print(Fore.BLUE + f'[{index}]' + Fore.CYAN + f' {film["title"]}')
            films_dict[index] = film["title"] # для удобства выбора фильма
            index += 1
    choice = int(input("Введите номер фильма для просмотра: "))
    print(Fore.GREEN + f"Вы выбрали: {films_dict.get(choice, 'Фильм не найден')}")
    name = get_film_title_by_number(films_dict, choice) #  получаем название фильма
    page = None
    for i in films:
        if i.get('title') == get_film_title_by_number(films_dict, choice): # по названию находим ссылку на страницу
            page = i.get('page')
            break
    else:
        print(Fore.RED + 'Фильм не найден')
    download_data(page)
    inde = 1
    for j, film in enumerate(filmss):
        if film.get("size"): 
            print(Fore.CYAN + f'[{inde}]' + Fore.BLUE + f' {film["size"]}') #  вывод доступного качества
            film_urls[inde] = film["size"]
            inde += 1
    download_number = int(input("Введите номер загрузки: "))
    dw = None
    for i in filmss:
        if i.get('size') == get_url_title_by_number(film_urls, download_number):
            dw = i.get('url') # получение конкретной ссылки для загрузки фильма
            break
    else:
        print(Fore.RED + 'Ссылка не найдена')
    print(Fore.GREEN, 'Загрузка Началась',  Fore.RESET)
    try:
        download_film(dw, films_dict.get(choice)) # Загрузка фильма если название его коректно
    except Exception as e:
        download_film(dw, 'None') #загрузка со стандартным именем

    print(Fore.YELLOW + 'Загрузка закончилась')
