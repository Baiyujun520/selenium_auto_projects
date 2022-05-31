# coding=utf-8
from logic.UI.ChromeHelper import ChromeHelper
from common.LoggerHelper import logger

chrome = ChromeHelper()
chrome.open_chrome("https://zwfw.gansu.gov.cn/")
logger.info(chrome.driver.current_window_handle)
