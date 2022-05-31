# coding=utf-8
import os
import time
import random

from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


from common.LoggerHelper import logger
from config import conf


def kill_chromedriver(is_kill_chrome=conf.common.ChromeConfig.isKillChrome):
    logger.debug("Start to clean testcase's environment...")
    # noinspection PyBroadException
    try:
        os.system("taskkill /im chromedriver.exe /F >nul 2>nul")
        if is_kill_chrome:
            os.system("taskkill /im chrome.exe /F >nul 2>nul")
    except Exception:
        logger.debug("Fail to clean testcase's environment, continue.")
    logger.debug("Finish cleaning testcase's environment.")


def check_chromedriver():
    logger.debug("Start to check chromedriver.exe ...")
    project_path = os.path.dirname(__file__)
    chromedriver_path = os.path.join(project_path, "chromedriver.exe")
    if not os.path.isfile(chromedriver_path):
        logger.error("Can not find the file: %s", str(chromedriver_path))
        raise IOError("The file: " + chromedriver_path + " is not exist!!!")
    logger.debug("%s exists.", chromedriver_path)
    return str(chromedriver_path)


class ChromeHelper:

    def __init__(self, time_out=conf.common.ChromeConfig.timeout):
        try:
            kill_chromedriver()
            driver_path = check_chromedriver()
            self.time_out = time_out
            self.xpath = "xpath"
            self.driver = None
            options = webdriver.ChromeOptions()
            if conf.common.ChromeConfig.isIncognito:
                options.add_argument('--incognito')  # 隐身模式（无痕模式）
                logger.debug("The chrome will use Incognito mode")
            if conf.common.ChromeConfig.isHeadless:
                options.add_argument("--headless")  # 浏览器不提供可视化页面
                logger.debug("The chrome will be headless")
            options.add_argument("--start-maximized")  # 浏览器窗口最大化
            self.driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
            logger.info("Open chrome successfully !!!")
            self.driver.implicitly_wait(self.time_out)
            logger.debug("timeout is: %s s", self.time_out)
        except SessionNotCreatedException as err:
            logger.error(str(err.msg))
            raise err
        except WebDriverException as wd_err:
            logger.error(wd_err.msg)
            raise wd_err
        except Exception as e:
            logger.error(e.message)
            raise e

    def set_timeout(self, timeout):
        if type(timeout) is int:
            self.time_out = timeout
            logger.info("Set timeout: %s ", self.time_out)
        else:
            logger.error("The parameter: timeout need to be int !!!")
            logger.info("timeout is default: %s", self.time_out)

    def open_chrome(self, url):
        logger.info("Browse the url: %s", str(url))
        self.driver.get(str(url))

    def close_chrome(self):
        self.driver.quit()
        logger.info("Close chrome successfully (^_^)")

    def cycle_to_find(self, by, value, frame_tag):
        element = None
        try:
            element = self.driver.find_element(by=by, value=value)
            logger.info("Find the element: %s", value)
            return element
        except NoSuchElementException as no_element:
            frames = self.driver.find_elements_by_tag_name(name=frame_tag)
            if len(frames) == 0:
                logger.debug("There are no frames: %s in current content.", frame_tag)
                raise no_element
            logger.debug("Switch to the list of frames to find the element......")
            for each_frame in frames:
                self.driver.switch_to.frame(each_frame)
                logger.debug("Switch to the frame: %s", str(each_frame.id))
                # noinspection PyBroadException
                try:
                    element = self.cycle_to_find(by=by, value=value, frame_tag=frame_tag)
                except NoSuchElementException:
                    logger.debug("After switch to the frame: %s , can not find the element: %s , continue to find.",
                                 str(each_frame.id), value)
                    self.driver.switch_to.parent_frame()
                    logger.debug("Switch to parent frame.")
                    continue
                if element is not None:
                    logger.debug("After switch to the frame: %s , find the element: %s", str(each_frame.id), value)
                    break
            if element is None:
                raise no_element
            else:
                return element

    def retreat_safely(self):
        if self.driver is not None:
            self.get_screenshot()
            self.driver.quit()
            self.driver = None
        else:
            kill_chromedriver(is_kill_chrome=False)

    def check_parm(self, by, value):
        if self.driver is None:
            raise ValueError("Fail to open chrome, and chromedriver is None!!!")
        if value is None or value == "":
            logger.error("The parameter: value can not be null!!!")
            raise ValueError("The parameter: value can not be null!!!")
        # value = value.decode("utf-8")
        if by.lower() == "xpath":
            by = By.XPATH
        elif by.lower() == "id":
            by = By.ID
        elif by.lower() == "tag_name":
            by = By.TAG_NAME
        else:
            logger.error("The parameter: by only support xpath/id/tag_name")
            raise ValueError("The parameter: by error!!!")
        return by, value

    def find_element(self, by, value, frame_tag="iframe"):
        by, value = self.check_parm(by=by, value=value)
        try:
            self.driver.switch_to.default_content()
            logger.info("Start to find the element: %s", value)
            element = self.cycle_to_find(by=by, value=value, frame_tag=frame_tag)
            WebDriverWait(self.driver, 10, 0.5).until(ec.visibility_of(element))
            return element
        except NoSuchElementException as no_element:
            logger.error("Can not find the element: %s ", value)
            logger.error(no_element.msg)
            self.retreat_safely()
            raise no_element
        except WebDriverException as wd_err:
            logger.error(wd_err.msg)
            self.retreat_safely()
            raise wd_err
        except Exception as err:
            logger.error(err.message)
            self.retreat_safely()
            raise err

    def click_element(self, by, value, frame_tag="iframe"):
        try:
            element = self.find_element(by=by, value=value, frame_tag=frame_tag)
            element.click()
            logger.info("Click the element: %s", value)
        except WebDriverException as wd_err:
            logger.error(wd_err.msg)
            self.retreat_safely()
            raise wd_err
        except Exception as err:
            logger.error(err.message)
            self.retreat_safely()
            raise err

    def auto_set_window_size(self):
        cur_window = self.driver.get_window_size()
        cur_width = cur_window.get("width")
        cur_height = cur_window.get("height")
        doc_width = self.driver.execute_script("return document.body.scrollWidth")
        doc_height = self.driver.execute_script("return document.body.scrollHeight")
        if cur_width < doc_width or cur_height < doc_height:
            width = max(cur_width, doc_width)
            height = max(cur_height, doc_height)
            self.driver.set_window_size(width, height)
            logger.debug("Set the window size: %s x %s", width, height)

    def get_screenshot(self, time_out=2):
        file_path = os.path.dirname(os.path.dirname(__file__))
        project_path = os.path.dirname(file_path)
        pic_path = os.path.join(project_path, "log", "ScreenShots")
        if not os.path.exists(pic_path):
            os.makedirs(pic_path)
        date = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))
        random_str = random.randint(10, 20)
        file_name = date + "_" + str(random_str) + ".png"
        file_path = os.path.join(pic_path, file_name)
        time.sleep(time_out)

        self.auto_set_window_size()
        # self.driver.get_screenshot_as_file(file_path)
        self.driver.save_screenshot(file_path)
        logger.info("Capture current screenshot, and save as png file: %s", file_path)

    def is_find(self, by, value, frame_tag="iframe"):
        by, value = self.check_parm(by=by, value=value)
        try:
            self.driver.switch_to.default_content()
            self.cycle_to_find(by=by, value=value, frame_tag=frame_tag)
            logger.info("Find the element: %s", value)
            return True
        except NoSuchElementException:
            logger.info("Can not find the element: %s", value)
            return False
        except Exception as err:
            logger.error(err.message)
            self.retreat_safely()
            raise err

    def is_element_exist(self, by, value, expect, frame_tag="iframe"):
        if expect is None:
            raise ValueError("The parameter: expect must not be None!!!")
        elif type(expect) is not bool:
            raise ValueError("The parameter: expect need to be bool !!!")
        answer = self.is_find(by, value, frame_tag)
        if answer is expect:
            logger.info("The actual value is the same as expect: %s", str(expect))
        else:
            logger.error("The actual value: %s is different from the expect: %s", str(answer), str(expect))
            self.retreat_safely()
            raise ValueError("The actual value is different from your expect!!!")

    def input_keys(self, by, value, keys, frame_tag="iframe"):
        try:
            element = self.find_element(by=by, value=value, frame_tag=frame_tag)
            keys = keys.decode("utf-8")
            element.send_keys(keys)
            logger.info("Input the value: %s in the input box: %s", keys, value)
        except WebDriverException as wd_err:
            logger.error(wd_err.msg)
            self.retreat_safely()
            raise wd_err
        except Exception as err:
            logger.error(err.message)
            self.retreat_safely()
            raise err
