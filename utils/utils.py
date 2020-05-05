from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os.path as path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from time import sleep

# bs4 임포트
from bs4 import BeautifulSoup
import requests

def crawling(site, id, pwd, keyword):
	result = dict()

	browser = get_broser()
	# 크롬 브라우저 내부 대기
	browser.implicitly_wait(5)
	# 페이지 이동
	browser.get(site)

	if site == 'http://www.shop.co.kr':
		if id == 'dandw123':
			result = crawling_shop(browser, id, pwd, keyword)
		else:
			result = crawling_shop1(browser, id, pwd, keyword)
	elif site == 'http://www.hmpmall.co.kr':
		result = crawling_hmpmall(browser, id, pwd, keyword)

	browser.close()
	return result

def crawling_shop(browser, id, pwd, keyword):
	"""
	http://www.shop.co.kr
	"""
	sub_url = 'http://www.shop.co.kr/hos/ajax/goodsDtail.do'

	# id, password 입력
	browser.find_element_by_id('userId').send_keys(id)
	browser.find_element_by_id('userPwd').send_keys(pwd)
	browser.find_element_by_xpath('//*[@id="btn-login"]').click()

	# 검색어 입력 후 버튼 클릭
	if id == 'dandw123':
		WebDriverWait(browser, 30) \
			.until(EC.presence_of_element_located((By.XPATH, '//*[@id="autoCompleteText"]'))).click()
		browser.find_element_by_xpath('//*[@id="autoCompleteText"]').click()
		browser.find_element_by_xpath('//*[@id="autoCompleteText"]').send_keys(keyword)
		browser.find_element_by_xpath('//*[@id="topSearchForm"]/div[2]/div/button').click()
	else:
		WebDriverWait(browser, 30) \
			.until(EC.presence_of_element_located((By.XPATH, '//*[@id="total-search-val"]'))).click()
		browser.find_element_by_xpath('//*[@id="total-search-val"]').click()
		browser.find_element_by_xpath('//*[@id="total-search-val"]').send_keys(keyword)
		browser.find_element_by_xpath('//*[@id="total-search-frm"]/div/div/div/button').click()
		sub_url = 'http://www.shop.co.kr/ajax/goodsDtail.do'

	# 테이블 가격표 노출될때까지 대기
	# WebDriverWait(browser, 20) \
	# 	.until(EC.presence_of_element_located((By.XPATH, '//*[@id="goodsDetail"]/div[1]'))).click()
	# sleep()
	WebDriverWait(browser, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifm")))
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "goobsList")))

	soup = BeautifulSoup(browser.page_source, 'html.parser')
	tr_list = soup.select('#goodsList > div:nth-child(4) > fieldset > table > tbody > tr')

	# 제품명, 제품가격 수집
	product_list = dict()
	for tr in tr_list:
		tds = tr.select('td')
		key = tr.get('alt').strip()
		product_name = tds[1].text.strip()
		product_price = tds[4].text.strip().replace(',', '')
		product_list[key] = [product_name, product_price]
		print(key, product_name, product_price)

	# 제품 수집후 제품별 공급사 제공 정보를 requests로 조회한다.
	result = dict()
	for key in product_list.keys():
		res_text = shop_requests(sub_url, keyword, key, browser)
		product = product_list[key]
		product_name = product[0]
		product_price = product[1]
		soup = BeautifulSoup(res_text, 'html.parser')
		tr_list = soup.select('table.tableBk > tbody > tr')
		# tr_list = soup.select('div.products_view table.table_style5 > tbody > tr')

		for tr in tr_list:
			tds = tr.findAll('td')

			# 공급사, 가격, 세일가, 재고
			company = tds[1].text.strip()
			# company = tds[0].find('input').text.strip()
			price = '0' if tds[2].text.strip() == '' or tds[2].text.strip() == '-' else tds[2].text.strip().replace(',',
			                                                                                                        '')

			discount_price = '0'
			if len(tds) == 5:
				discount_price = '0' if tds[3].text.strip() == '' else tds[3].text.strip().replace(',', '')
			print("{} / {} / {} / {}".format(product_name, product_price, company, price, discount_price))

			uniq_key = key.join(company)
			result[uniq_key] = [product_name, product_price, company, price, discount_price]

		sleep(2)

	return result

def crawling_shop1(browser, id, pwd, keyword):
	# id, password 입력
	browser.find_element_by_id('userId').send_keys(id)
	browser.find_element_by_id('userPwd').send_keys(pwd)
	browser.find_element_by_xpath('//*[@id="btn-login"]').click()

	# 검색어 입력 후 버튼 클릭
	WebDriverWait(browser, 30) \
		.until(EC.presence_of_element_located((By.XPATH, '//*[@id="total-search-val"]'))).click()
	browser.find_element_by_xpath('//*[@id="total-search-val"]').click()
	browser.find_element_by_xpath('//*[@id="total-search-val"]').send_keys(keyword)
	browser.find_element_by_xpath('//*[@id="total-search-frm"]/div/div/div/button').click()
	sub_url = 'http://www.shop.co.kr/ajax/goodsDtail.do'

	# 테이블 가격표 노출될때까지 대기
	WebDriverWait(browser, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifm")))
	WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "table_style4")))

	soup = BeautifulSoup(browser.page_source, 'html.parser')
	tr_list = soup.select('.table_style4 > tbody > tr')

	# 제품명, 제품가격 수집
	product_list = dict()
	for tr in tr_list:
		tds = tr.select('td')
		key = tr.get('alt').strip()
		product_name = tds[1].text.strip()
		product_price = tds[4].text.strip().replace(',', '')
		product_list[key] = [product_name, product_price]
		print(key, product_name, product_price)

	# 제품 수집후 제품별 공급사 제공 정보를 requests로 조회한다.
	result = dict()
	for key in product_list.keys():
		res_text = shop_requests(sub_url, keyword, key, browser)
		product = product_list[key]
		product_name = product[0]
		product_price = product[1]
		soup = BeautifulSoup(res_text, 'html.parser')
		tr_list = soup.select('table.table_style5 > tbody > tr')

		for tr in tr_list:
			tds = tr.findAll('td')

			# 공급사, 가격, 세일가, 재고
			# company = tds[0].find('input').text.strip()
			# if comlen(tds)pany == '':
			company = tds[0].text.strip()

			if company == "":
				continue
			try:
				price = '0' if tds[1].text.strip() == '' or tds[1].text.strip() == '-' else tds[1].text.strip().replace(
					',', '')
			except Exception as e:
				print(e)
				price = '0'

			if price == '0':
				continue

			try:
				discount_price = '0' if tds[2].text.strip() == '' else tds[2].text.strip().replace(',', '')
			except Exception:
				discount_price = '0'

			print("{} / {} / {} / {} / {}".format(product_name, product_price, company, price, discount_price))

			uniq_key = key.join(company)
			result[uniq_key] = [product_name, product_price, company, price, discount_price]

		sleep(2)

	return result

def shop_requests(url, keyword, product_key, browser):
	headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8', 'Accept': 'text/html'}
	cookies = dict()
	for cookie in browser.get_cookies():
		cookies[cookie['name']] = cookie['value']

	data = {'goodsInfoDataBean.goodsMasterCd': product_key, 'goodsInfoDataBean.monoGoodsYn': 'N',
	        'goodsInfoDataBean.searchVal': keyword}

	res = requests.post(url, data=data, headers=headers, cookies=cookies)

	if res.status_code == 200:
		return res.text

	return ''

def crawling_hmpmall(browser, id, pwd, keyword):
	# id, password 입력
	browser.find_element_by_id('memberId').send_keys(id)
	browser.find_element_by_id('memberPassword').send_keys(pwd)
	browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div[1]/fieldset/div/img').click()

	# 검색어 입력 후 버튼 클릭
	WebDriverWait(browser, 30) \
		.until(EC.presence_of_element_located((By.XPATH, '//*[@id="keywordField"]'))).click()
	browser.find_element_by_xpath('//*[@id="searchField"]').send_keys(keyword)
	browser.find_element_by_xpath('//*[@id="searchKeywordBtn"]').click()

	sleep(2)

	result = dict()

	for i in range(0, 9):
		gen_id = "mainList" + str(i)
		browser.find_element_by_xpath('//*[@id="{}"]/td[3]/a'.format(gen_id)).click()
		WebDriverWait(browser, 30) \
			.until(EC.presence_of_element_located((By.XPATH, '//*[@id="area_supply_detail_s"]/table[1]/thead/tr[2]')))
		soup = BeautifulSoup(browser.page_source, "html.parser")

		product_name = soup.select_one('#{} > td.al_lft.name_s'.format(gen_id)).text.strip()
		product_price = soup.select_one('#{} > td.won.al_rgt'.format(gen_id)).text.strip().replace(',', '').replace('원',
		                                                                                                            '')
		trs = soup.select('div.area_supply_detail_s > table.tbl_supply > thead > tr.subListBody')

		for tr in trs:
			tds = tr.findAll('td')
			if not tds:
				continue

			company = tds[1].text.strip()
			price = '0' if tds[2].text.strip() == '' else tds[2].text.strip().replace(',', '')
			discount_price = '0' if tds[3].text.strip() == '' else tds[3].text.strip().replace(',', '')

			print('{} / {} / {} / {} / {}'.format(product_name, product_price, company, price, discount_price))
			result[product_name.join(company)] = [product_name, product_price, company, price, discount_price]

		sleep(1)

	return result

def get_broser():
	chrome_options = Options()
	# chrome_options.add_argument("--headless")
	driver_path = path.join(path.dirname(path.abspath(__file__)), '..', 'webdriver', 'chromedriver')
	return webdriver.Chrome(
		executable_path=driver_path,
		options=chrome_options
	)

if __name__ == '__main__':
	# crawling('http://www.shop.co.kr', 'dandw123', 'dandw123', '밴드골드')
	# crawling('http://www.shop.co.kr', 'jaeback', 'jack58', '밴드골드')
	crawling('http://www.hmpmall.co.kr', 'jis0980', '2946aa', '밴드골드')
