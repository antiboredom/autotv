import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_links(url, driver):
    out = []
    page = 1
    driver.get(url.format(page))
    time.sleep(2)
    total = driver.execute_script("return document.querySelectorAll('.ui2-pagination-pages a')[document.querySelectorAll('.ui2-pagination-pages a').length-2].textContent")
    total = int(total)
    while page <= total:
        driver.get(url.format(page))
        time.sleep(2)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(2)
        links = driver.find_elements_by_css_selector('h2.title a')
        for l in links:
            href = l.get_attribute('href')
            print(href)
            out.append(href.strip())
        page += 1
    return out


if __name__ == '__main__':
    start_urls = [
        'https://www.alibaba.com/products/house_maid/{}.html',
        'https://www.alibaba.com/products/labor_camp/{}.html'
    ]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)

    out = []
    for url in start_urls:
        try:
            out += get_links(url, driver)
        except:
            continue

    out = set(list(out))
    out = [o.strip() for o in out if o.strip() != '']
    if len(out) > 0:
        with open('shoppinglist.txt', 'w') as outfile:
            outfile.write('\n'.join(out))

    driver.quit()

