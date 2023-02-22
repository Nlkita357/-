from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json

dict = {"datas":[]}
dict_for_save_url = {"pars_urls":[]}

def read_pars_urls():
    list = []
    with open("save_pars_url_file.json", encoding = "utf-8") as file:
        dict_save_url_read = json.load(file)

    for i in dict_save_url_read["pars_urls"]:
        list.append(i["url"])
        dict_for_save_url["pars_urls"].append(i)
    return list

def save_pars_url(url):
    dict_urls = {"url":url}

    with open("save_pars_url_file.json", "w", encoding = "utf-8") as file_for_data:
        dict_for_save_url["pars_urls"].append(dict_urls)
        json.dump(dict_for_save_url, file_for_data, ensure_ascii=False)

def save_json_data():
    global dict_read

    with open('data_pars.json', encoding = "utf-8") as file:
        dict_read = json.load(file)

def create_json(name, adress, grade, phone_number, site, schedule, list_text_massengers, logotip, photo_list, reviews_list):
    dict_for_datas = {"name":name, "adress":adress, "grade":grade, "phone_number":phone_number, "site":site, "schedule":schedule, "list_text_massengers":list_text_massengers, "logotip":logotip, "photo_list":photo_list, "reviews_list":reviews_list}

    with open("data_pars.json", "w", encoding = "utf-8") as file_for_data:

        dict["datas"].append(dict_for_datas)
        json.dump(dict, file_for_data, ensure_ascii=False)

def create_webdriver():
    global driver

    driver_options = webdriver.ChromeOptions()
    #driver_options.add_argument('Chrome/37.0.2049.0')
    #driver_options.add_argument('headless')#запуск в фоне
    driver = webdriver.Chrome(chrome_options=driver_options)#веб драйвер

    def pars_urls():
        html = driver.page_source
        with open("code_for_site.html", "w", encoding = "utf-8") as file:
            file.write(html)

def scroll_pages_site():
    global flag_selen

    flag_link = 1
    list_urls = []
 
    url = "https://yandex.ru/maps/213/moscow/search/ресторан москва"
    flag_browse = 1
    res = driver.get(url)
    start_program = input("Запуск парсера")
    while True:
        try:
            get_link = driver.find_element_by_xpath(f"/html/body/div[1]/div[2]/div[7]/div[2]/div[1]/div[1]/div[1]/div/div[1]/div/div/ul/li[{str(flag_link)}]/div/div/a").get_attribute("href")
            print(get_link)
            list_urls.append(get_link)
            flag_link += 1
        except:
            print(f"Всего скрипт нашёл {len(list_urls)} сайтов")
            return list_urls

def pars_site(list_urls, save_urls_list):
    global flag_browse
    flag_browse = 0
    flag_pars = 0
    for url in list_urls:

        if url in save_urls_list:
            print(f"сайт {url} уже есть в базе")
            continue

        try:
            res = driver.get(url)

            name = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[3]/div[2]/h1").text.replace("Посмотреть все товары и услуги", "").replace("\n", "")

        except:
            try:
                res = driver.get(url)
                name = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[3]/div[2]/h1").text.replace("Посмотреть все товары и услуги", "").replace("\n", "")

            except:
                continue

        adress = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[5]/a/div/span[1]").text + " " + driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[5]/a/div/span[1]").text
        adress = adress.replace("Показать входы", "").replace("Маршрут", "").replace("\n", "")

        try:
            grade = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[4]/div[1]/div/div/span[1]/span/span[2]").text
        except:
            grade = None

        try:
            phone_number = driver.find_element_by_class_name("card-phones-view__number").text.replace("Показать телефон", "").replace("\n", "")
        except:
            phone_number = None

        try:
            site = driver.find_element_by_class_name("business-urls-view__link").get_attribute('href')
        except:
            site = None

        html = driver.page_source
        with open("code_for_site.html", "w", encoding = "utf-8") as file:
            file.write(html)
        soup = BeautifulSoup(html, 'html.parser')

        try:
            list_massengers = soup.find("div", class_ = "card-feature-view _view_normal _size_small _no-side-padding business-contacts-view__social-links").find("div", class_ = "card-feature-view__main-content").find_all("div", class_ = "business-contacts-view__social-button")
            list_text_massengers = []
            for i in list_massengers:
                list_text_massengers.append(i.find("a").get("href"))
        except:
            list_massengers = []
        
        try:
            show_schedule = driver.find_element_by_class_name("card-feature-view__additional").click()
            schedule = driver.find_element_by_class_name("business-working-intervals-view").text
            schedule = schedule.replace("\n", " ").replace("Понедельник ", "").replace("Вторник ", "").replace("Среда ", "").replace("Четверг ", "").replace("Пятница ", "").replace("Суббота ", "").replace("Воскресенье ", "").replace(" ", "")

            list_schedule = []
            str = ""
            for i in schedule:
                if len(str) == 11:
                    list_schedule.append(str)
                    str = ""
                str += i
        except:
            schedule = []

        time.sleep(1)
        logotip, photo_list = pars_photo(url)
        time.sleep(1)

        reviews_text_list = pars_sites_photo_and_otzivi(url)
        flag_pars += 1
        print(f"Скрипт спарсил {flag_pars} из {len(list_urls)} сайтов")
        save_pars_url(url)
        create_json(name, adress, grade, phone_number, site, list_schedule, list_text_massengers, logotip, photo_list, reviews_text_list)
def pars_photo(url):

    url += "gallery"
    try:
        logotip = driver.find_element_by_class_name("img-with-alt").get_attribute('src')
    except:
        logotip = None

    res = driver.get(url)

    flag_photo = 2
    photo_list = []
    time.sleep(1)

    flag_element = 4
    while True:
        try:
            photo = driver.find_element_by_xpath(f"/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[3]/div/div/div[{str(flag_element)}]/div/div/div[3]/div/div[{str(flag_photo)}]/div/div/img").get_attribute('src')
            flag_photo += 1
        except:

            if flag_photo == 2:
                flag_element += 1
                while True:
                    try:
                        photo = driver.find_element_by_xpath(f"/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[3]/div/div/div[{str(flag_element)}]/div/div/div[3]/div/div[{str(flag_photo)}]/div/div/img").get_attribute('src')
                        break
                    except:
                        flag_element += 1

            else:

                flag_photo -= 1
                element = driver.find_element_by_xpath(f"/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[3]/div/div/div[{str(flag_element)}]/div/div/div[3]/div/div[{str(flag_photo)}]/div/div/img")


                element.location_once_scrolled_into_view
                flag_photo += 1
                try:
                    photo = driver.find_element_by_xpath(f"/html/body/div[1]/div[2]/div[7]/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/div/div[3]/div/div/div[{str(flag_element)}]/div/div/div[3]/div/div[{str(flag_photo)}]/div/div/img").get_attribute('src')
                except:
                    break

        photo_list.append(photo)

    return logotip, photo_list

def pars_sites_photo_and_otzivi(url):

    url_rewies = url + "reviews"

    res = driver.get(url_rewies)

    html = driver.page_source

    with open("code_for_site.html", "w", encoding = "utf-8") as file:
        file.write(html)

    with open("code_for_site.html", "r", encoding = "utf-8") as file:
        file_html = file.read()

    soup = BeautifulSoup(file_html, 'html.parser')


    reviws = soup.find_all("span", class_ = "business-review-view__body-text")
    date = soup.find_all("span", class_ = "business-review-view__date")
    rating = soup.find_all("div", class_ = "business-rating-badge-view__stars")

    reviews_text_list = []
    for i in range(0, len(reviws)):
        reviews_text_list.append([reviws[i].text, date[i].text, len(rating[i])])

    return reviews_text_list
1
save_json_data()
create_webdriver()
save_urls_list = read_pars_urls()
list_urls = scroll_pages_site()
pars_site(list_urls, save_urls_list)
