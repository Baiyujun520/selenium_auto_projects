# coding=utf-8
from logic.UI.ChromeHelper import ChromeHelper
from common.LoggerHelper import logger

chrome = ChromeHelper()
chrome.open_chrome("https://zwfw.gansu.gov.cn/")
logger.info(chrome.driver.current_window_handle)
search_box = "//input[@id='ty-search-input']"
chrome.input_keys("xpath", search_box, "社保")
search_button = "//input[@value='搜索']"
chrome.click_element("xpath", search_button)

logger.info(chrome.driver.window_handles)
logger.info(chrome.driver.current_window_handle)
chrome.find_element("xpath", "//div[@class='content_title_item']//li[@title='服务应用']")
chrome.close_chrome()
