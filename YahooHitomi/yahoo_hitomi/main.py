from kchobi_selenium.driver import seleniumDriver
from kchobi_selenium.selenium_element import seleniumElement
from kchobi_file_common.file_base import FileBase
from kchobi_logger.logger import Logger
import logging
from selenium import webdriver
from time import sleep
import pyautogui
from urllib.parse import urlparse

class Main:
	STARTUP_DISTANCE = 1
	SEARCH_DISTANCE = 1
	SITE_DISTANCE = 6
	ROOP_ONE_SEASON_FOR_TERM = 2
	ROOP_USE_TERMS = 2
	path = "C:/Users/Yuki/AppData/Local/Programs/Python/Python37/Lib/site-packages/chromedriver_binary/chromedriver.exe"

	start_up_url = "https://yahoo.jp/ylnVGI"

	term_list_file_path = "G:\マイドライブ\ドライブ\IT系\GitHub\YahooHitomi\list.txt"
	last_exit_term_file_path = "G:\マイドライブ\ドライブ\IT系\GitHub\YahooHitomi\dat.txt"
	logger = None

	def __init__(self):
		loggerInstance = Logger("../tests/test.log", 'w')
		loggerInstance.create_logger(__name__, logging.DEBUG)
		self.logger = loggerInstance.logger

	def get_driver(self):
		
		options = webdriver.ChromeOptions()
		options.add_argument('--disable-gpu')
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-dev-shm-usage')
		selenium_d = seleniumDriver()
		driver = selenium_d.create_driver(driver_path=self.path, options=options)
		driver.minimize_window()
		sleep(1)
		driver.maximize_window()
		return driver

	# 用語を読み込む
	def get_term_list(self):
		term_list = FileBase().readlines_text(self.term_list_file_path)
		return term_list
	
	# 全体終了時用語を読み込む
	def get_last_exit_term(self):
		return FileBase().read_text(self.last_exit_term_file_path)
	
	def get_use_terms(self, term_list, last_exit_term):
		use_terms = []
		last_exit_term_index = term_list.index(last_exit_term)
		start_index = last_exit_term_index + 1
		self.logger.debug(f"last_exit_term_index -> {last_exit_term_index} / start_index -> {start_index}")

		for idx in range(start_index, self.ROOP_USE_TERMS + start_index, 1):
			get_list_idx = idx
			self.logger.debug(f"start_index -> {start_index}")
			self.logger.debug(f"get_list_idx -> {get_list_idx}")
			self.logger.debug(f"term_list.class -> {type(term_list)}")
			self.logger.debug(f"len(term_list) -> {len(term_list)}")
			if len(term_list) <= idx:
				get_list_idx = idx - len(term_list)
			use_terms.append(term_list[get_list_idx])

		return use_terms
	
	def search_word(self, element, term):
		search_ctl_txt = element.get_element_by_xpath("//input[@type='search']")
		# キーワード検索に入力した時点で検索されるっぽい
		search_ctl_txt.send_keys(term)
	
	# 微調整
	def adjustment_scroll_by(self, driver, top, down):
		print(f"top: {top} / down: {down}")
		driver.execute_script(f"scrollBy({top},{down})")
	
	def click_sponsor_site(self, driver, element, roop_idx):
		pyautogui.screenshot(f"../tests/screenshot_{roop_idx}.png")
		try:
			element.click()
		except:
			self.adjustment_scroll_by(driver, 0, -100)
			self.click_sponsor_site(driver, element, roop_idx)

	def scroll_to_sponsor(self, driver, site_index):
		self.logger.debug(f"site_idx {site_index}")
		# 対象の位置まで移動
		driver.execute_script(f'document.getElementsByClassName("sw-Badge__text")[{site_index}].scrollIntoView(true);')
		self.adjustment_scroll_by(driver, 0, -200)

	def get_sponsor_domein(self, element):
		href = element.get_attribute("href")
		return urlparse(href).netloc
	
	def get_sponsor_element(self, element, idx):
		print(f"----- //span[@class='sw-Badge__text']//ancestor::div[@class='sw-CardBase'][{idx}]//a")
		return element.get_element_by_xpath(f"(//span[@class='sw-Badge__text']//ancestor::div[@class='sw-CardBase'])[{idx}]//a")
	
	# def select_sponsor(self, already_sponsor_domeins, element, site_idx = 1):

	# 	sponsor_element = self.get_sponsor_element(element, site_idx)
	# 	sponsor_domain = self.get_sponsor_domein(sponsor_element)

	# 	if len(already_sponsor_domeins) <= 0:
	# 		# 既出のリストがなければそのまま返す
	# 		return sponsor_element, site_idx
		
	# 	self.logger.debug(f"{already_sponsor_domeins} in {sponsor_domain}")
	# 	if sponsor_domain in already_sponsor_domeins:
	# 		self.logger.debug(f"既出のurlの場合は新規になるまで繰り返す / {sponsor_domain} / site_idx: {site_idx}")
	# 		sponsor_element, site_idx = self.select_sponsor(already_sponsor_domeins, element, site_idx + 1)
		
	# 	return sponsor_element, site_idx
	
		
	def select_sponsor(self, element, site_idx):

		sponsor_element = self.get_sponsor_element(element, site_idx)
		
		return sponsor_element

	def do_work(self, use_terms):

		roop_idx = 1
		already_sponsor_domeins = []
		for term in use_terms:
			site_index = 1
			for i in range(0, self.ROOP_ONE_SEASON_FOR_TERM, 1):
				# ブラウザを立ち上げる
				driver = self.get_driver()
				# 特定のURLでサイトを表示する
				driver.get(self.start_up_url)
				# 用語を検索する
				element = seleniumElement(driver)
				sleep(self.SEARCH_DISTANCE)
				self.search_word(element, term)
				sleep(self.SEARCH_DISTANCE)
				# どのサイトの情報を収集するか決める
				sponsor = self.select_sponsor(element, site_index)
				already_sponsor_domeins.append(self.get_sponsor_domein(sponsor))
				self.logger.debug(f"already_sponsor_domeins: {already_sponsor_domeins}")
				
				if site_index > 1:
					# リンクが画面上に表示されるまでスクロールする
					self.scroll_to_sponsor(driver, site_index-1)
					sleep(self.SEARCH_DISTANCE)

				# サイトをクリックする
				self.click_sponsor_site(driver, sponsor, roop_idx)
				sleep(self.SITE_DISTANCE)
				# サイトの最下部までスクロール
				driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
				roop_idx = roop_idx + 1
				sleep(1)
				# スクリーンショット
				pyautogui.screenshot(f"../tests/screenshot_{roop_idx}.png")
				roop_idx = roop_idx + 1
				site_index = site_index + 1
				driver.close()

	# 前回終了時用語に２番目の用語上書き記述して保存
	def save_last_exit_term(self, last_term):
		# ↓ あとでfile_baseに移す
		f = open(self.last_exit_term_file_path, 'w', encoding='UTF-8')
		f.write(last_term)
		f.close

	def main(self):
		# 用語を読み込む
		term_list = self.get_term_list()
		# 全体終了時用語を読み込む
		last_exit_term = self.get_last_exit_term()
		self.logger.debug(f"last_exit_term -> {last_exit_term}")
		# 前回終了時用語から用語リストの用語を2つ抽出する
		use_terms = self.get_use_terms(term_list, last_exit_term)
		self.logger.debug(f"use_terms -> {use_terms}")
		# 検索処理の実行
		self.do_work(use_terms)
		# 前回終了時用語に２番目の用語上書き記述して保存
		self.save_last_exit_term(use_terms[-1])
	
if __name__ == "__main__":
	start = Main()
	start.main()