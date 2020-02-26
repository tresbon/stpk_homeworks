#Импортируем библиотеки
from selenium import webdriver
from random import choice
import time
from lxml import etree
from requests import request
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def generate_mail():
    '''Generates email with 3 letters @ 3 letters . 3 letters'''
    letters = [chr(i) for i in range(ord('a'),ord('z')+1)]
    return ''.join(choice(letters) for l in range(3)) + '@' +\
        ''.join([choice(letters) for l in range(3)])  + '.' +\
        ''.join([choice(letters) for l in range(3)]) 

def generate_pass(nletters:int,ndigits:int):
    '''Generates password with nletters and ndigids'''
    letters = [chr(i) for i in range(ord('a'),ord('z')+1)]
    digits = [str(i) for i in range (10)]
    return ''.join([choice(letters) for l in range(nletters)]) + \
    ''.join([choice(digits) for d in range(ndigits)])

mail = generate_mail()
password = generate_pass(5,4)

'''
Тест №1 Регистрация на сайте
1. Перейти по адресу http://selenium1py.pythonanywhere.com/ru/
2. Найти элемент a#login_link и перейти по нему
3. Заполнить поле #id_registration-email валидным e-mail
4. Заполнить поле #id_registration-password1 паролем
(9 символов хотя бы одна цифра и хотя бы одна буква)
5. Повторить пароль в поле #id_registration-password2
6. Выбрать кнопку form#register_form button[name='registration_submit'] и кликнуть
7. Удостовериться что появилось сообщение 'Спасибо за регистрацию!'
'''

try:
    browser = webdriver.Chrome()
    browser.get('http://selenium1py.pythonanywhere.com/ru/')

    l_link = browser.find_element_by_css_selector('a#login_link')
    l_link.click()

    email = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, \
            "#id_registration-email"))
    )
    email.send_keys(mail)

    pass1 = browser.find_element_by_css_selector('#id_registration-password1')
    pass1.send_keys(password)

    pass2 = browser.find_element_by_css_selector('#id_registration-password2')
    pass2.send_keys(password)

    button = browser.find_element_by_css_selector(\
        "form#register_form button[name='registration_submit']")
    button.click()

    success_message = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, \
            "div#messages div.alertinner.wicon"))
    )

    assert 'Спасибо за регистрацию!' in success_message.text
    print('Test #1 Sing Up passed')


    '''
    Тест №2 при повторном открытии вход выполнен
    1. Создать новую вкладку
    2. Закрыть текущую вкладку
    3. Перейти на новой вкладке по адресу http://selenium1py.pythonanywhere.com/ru/
    4. Найти элемент ul.nav.navbar-nav.navbar-right a[href="/ru/accounts/"]
    5. Если в элементе есть текст "Аккаунт" - тест пройден
    '''

    browser.execute_script("window.open('');")
    browser.close()

    browser.switch_to.window(browser.window_handles[0])

    browser.get('http://selenium1py.pythonanywhere.com/ru/')

    acc = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, \
            'ul.nav.navbar-nav.navbar-right a[href="/ru/accounts/"]'))
    )
    assert 'Аккаунт' in acc.text
    print('Test #2 cookies passed')

    '''
    Тест №3 в профиле сохранён верный email
    1. Перейти в аккаунт
    2. Выбрать элемент table tr:nth-child(2) td
    3. Проверить что в поле вписан тот же email что указан при регистрации
    '''

    acc.click()
    em = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, \
            'table tr:nth-child(2) td'))
    )

    assert mail in em.text

    print('Test #3 right email in profile passed')
    
finally:
    # закрываем окно браузера
    browser.quit()

time.sleep(2) #Пауза перед новым запуском браузера


'''Тест 4 Проверка числа товаров в категории
1. Открыть категорию
2. Взять число товаров категории из элемента 
#promotions ~ form strong:nth-child(2)
3. Посчитать число товаров на каждой странице в категории и получить 
суммарное число отображаемых
4. Проверить что полученное число товаров соответствует 
элементу #promotions ~ form strong:nth-child(2)
5. Если число соответствует - вывести сообщение в консоль
6. Повторить для всех категорий из sitemap-categories-ru.xml

Параллельно собрать wordheap из названий товаров'''

try:

    root = etree.fromstring(request('GET',\
        'http://selenium1py.pythonanywhere.com/sitemap-categories-ru.xml'\
            ).content)
    sitemap_categories = [i[0].text.replace('example.com',\
        'selenium1py.pythonanywhere.com') for i in root]

    goods_counter = 0

    goods_links = list()

    browser = webdriver.Chrome()

    for cat in sitemap_categories:

        browser.get(cat)

        ngoods = browser.find_element(By.CSS_SELECTOR, \
            '#promotions ~ form strong:nth-child(2)').text

        ngoods = int(ngoods)

        goods = browser.find_elements(By.CSS_SELECTOR, \
        'article.product_pod h3 a')

        for g in goods:
            goods_links.append('http://selenium1py.pythonanywhere.com' +\
                g.get_attribute('href'))

        goods_counter += len(goods)

        while browser.find_elements(By.CSS_SELECTOR, \
            'ul.pager li.next a'):

            nxt = browser.find_element(By.CSS_SELECTOR, \
            'ul.pager li.next a')
            nxt.click()

            goods = browser.find_elements(By.CSS_SELECTOR, \
            'article.product_pod h3 a')

            for g in goods:
            goods_links.append('http://selenium1py.pythonanywhere.com' +\
                g.get_attribute('href'))

            goods_counter += len(goods)

        else:

            assert goods_counter == ngoods

            print(f'Test #6 ngoods for {cat} passed')

            goods_counter = 0

    '''Тест 5 - проверка числа найденных товаров через поиск
    (в названиях товаров)
    1. Пройти по собранным на предыдущем шаге ссылкам на
    товары и собрать wordheap из названий и описаний товаров
    2. Посчитать число вхождений этого слова в wordheap
    3. Ввести слово в строку поиска на главной странице
    4. Посчитать число найденных товаро
    5. Проверить что число найденных товаров равно
    числу вхождений слова в wordheap
    '''
    
    

    word = choice([i for i in wordheap if len(i) > 3])

    counter = 0

    for w in wordheap:
        if word.lower() in w.lower():
            counter += 1

    browser.get('http://selenium1py.pythonanywhere.com/ru/')

    search = browser.find_element(By.CSS_SELECTOR, \
            'input[type="search"]')

    search.send_keys(word)

    search_button = browser.find_element(By.CSS_SELECTOR, \
            'input[type="submit"][value="Найти"]')
    search_button.click()

    nfound = browser.find_element(By.CSS_SELECTOR, \
            '#promotions ~ form strong').text
    
    try:
        assert int(nfound) == counter
        print ('Test#5 nfound goods in names passed')

    except AssertionError:
        print ('Test#5 nfound goods in names NOT passed')

    '''Тест №6 стоимость добавленного в корзину товара
    отображается возле корзины
    1. Перейти в случайную категорию
    2. Добавить случайный товар в корзину
    3. Проверить что сумма добавленного товара отображается в корзине'''

    def choose_valid_category(sitemap_categories):
        '''Recusrively chooses valid category'''
        cat = choice(sitemap_categories)
        if not browser.find_elements(By.CSS_SELECTOR, \
        'ol.row li button[data-loading-text="Добавление..."]'):
            choose_valid_category(sitemap_categories)
        return cat

    cat = choose_valid_category(sitemap_categories)

    browser.get(cat)

    goods = browser.find_elements(By.CSS_SELECTOR, \
        'article.product_pod')

    good = choice(goods)

    good_price = good.find_element(By.CSS_SELECTOR, \
        'p.price_color').text
    good_price = ''.join([i for i in good_price if
    i.isdigit() or i == ',']).replace(',','.')

    basket_price_before = browser.find_element(By.CSS_SELECTOR, \
        'div.basket-mini').text if browser.find_elements(By.CSS_SELECTOR, \
        'div.basket-mini') else ''
    basket_price_before = ''.join([i for i in basket_price_before if
    i.isdigit() or i == ',']).replace(',','.')

    good_button = good.find_element(By.CSS_SELECTOR, \
        'button[data-loading-text="Добавление..."]')
    good_button.click()

    basket_price_after = browser.find_element(By.CSS_SELECTOR, \
    'div.basket-mini').text if browser.find_elements(By.CSS_SELECTOR, \
    'div.basket-mini') else ''
    basket_price_after = ''.join([i for i in basket_price_after if
    i.isdigit() or i == ',']).replace(',','.')

    assert (float(basket_price_after) - float(basket_price_before)) == \
        float(good_price)
    print('Test #6 adding good to basket passed')

    '''Тест №7 добавленный товар появлятся в корзине
    1. Перейти в случайную категорию
    2. Добавить товар в корзину
    3. Перейти в корзину
    4. Проверить что добавленный товар есть в корзине
    '''

finally:

    browser.close()

# не забываем оставить пустую строку в конце файла