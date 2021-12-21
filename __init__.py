import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from typing import Union
import os
import pickle
import re
import random
import time



class Posts:
    def __init__(
        self,
        text: str = '',
        images: Union[list[str], tuple[str]] = tuple(),
        background: bool = False
    ) -> None:
        self.text = text
        self.images = images
        self.bg = background if not self.images else False



class Account:
    def __init__(
        self, 
        name: str,
        images: bool, 
        notifications: bool,
        show: bool
    ) -> None:
        self.name = name
        self.file = name + ".pkl"
        self.n_name = ''
        self.groups = []
        self.dir = os.path.join(os.path.dirname(os.path.normcase(__file__)), 'accounts')
        try:
            chromedriver_autoinstaller.install(cwd=True)
        except Exception as e:
            print(e)
        options = webdriver.ChromeOptions()
        if not show:
            options.add_argument("--headless")
        if not images:
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        if not notifications:
            options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
        self.uid = ""
    
    def __enter__(self):
        return self
    
    def __exit__(self, _exc_type, _exc_value, traceback):
        self.driver.quit()
        if traceback:
            print(traceback)

    def cookies(self) -> list:
        return self.driver.get_cookies()
    
    def quit(self) -> None:
        self.driver.quit()
    
    def name_existed(self) -> bool:
        return self.file in os.listdir(self.dir)

    def rename(self, new_name) -> None:
        self.n_name = new_name
    
    def post(self, *args: str, posts: Posts) -> None:
        for group in args:
            print(group, "Posting...")
            self.driver.get("https://m.facebook.com/groups/" + group)
            method = ec.presence_of_element_located((By.CSS_SELECTOR, "div._4g34._6ber._78cq._7cdk._5i2i._52we > div"))
            try:
                write = WebDriverWait(self.driver, timeout=5).until(method)
            except TimeoutException:
                self.quit()
                raise Exception(f"Account {self.name} may not have joined the group id {group}")
            write.click()
            self.driver.find_element_by_css_selector('textarea[class="composerInput mentions-input"]').send_keys(posts.text)
            print("Write", posts.text)
            if posts.bg:
                print("Select background")
                self.driver.find_elements_by_css_selector("div._6iue > div")[random.randint(1, 6)].click()
            for img in posts.images:
                print("Add image", img)
                self.driver.find_element_by_css_selector("#photo_input").send_keys(img)
            time.sleep(.5)
            self.driver.find_element_by_css_selector("div.acw > div > div > button").click()
            print("Submitted! waiting...")
            method = ec.visibility_of_element_located((By.CSS_SELECTOR, "div._7om2._6aij > div._4g34"))
            try:
                WebDriverWait(self.driver, timeout=30).until_not(method)
            except TimeoutException:
                raise Exception(f"Can't post in group id {group}. Check your internet connection!")
            print(group, "Post Successfully!")
    
    def list_groups(self, update: bool = False) -> list[dict]:
        if update or not self.groups:
            self.driver.get("https://m.facebook.com/groups_browse/your_groups/")
            h = 0
            elem_groups = self.driver.find_elements_by_css_selector("div._2pip > div > a")
            while len(elem_groups) > h:
                h = len(elem_groups)
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(0.5)
                elem_groups = self.driver.find_elements_by_css_selector("div._2pip > div > a")
            print(f"Detected {len(elem_groups)} groups in account {self.name}")
            groups = []
            for group in elem_groups:
                name = group.find_element_by_css_selector('div[class="h3z9dlai ld7irhx5 pbevjfx6 igjjae4c"]').text
                if re_id := re.search(pattern=r"(?<=/)\d+(?=/)", string=group.get_attribute("href")):
                    _id = re_id.group()
                    print(f"Group {name} id {_id}")
                    groups.append({"name": name, "id": _id})
            self.groups = groups
        return self.groups

    def comment(self, id_posts: str, cmt: str) -> None:
        print(self.name, "Commenting...")
        self.driver.get("https://m.facebook.com/groups/1255689758211283/permalink/" + id_posts)
        self.driver.find_element_by_css_selector('textarea[class="_uwx mentions-input"]').send_keys(cmt)
        self.driver.find_element_by_css_selector("button[class='_54k8 _52jg _56bs _26vk _3lmf _3fyi _56bv _653w']").click()
        method = ec.presence_of_element_located((By.CSS_SELECTOR, 'div.mentions > div[style="display: none;"]'))
        try:
            WebDriverWait(self.driver, timeout=15).until_not(method)
        except TimeoutException:
            raise Exception(self.name + " Comment Fail! Check your internet connection!")
        print(self.name, "Commented!")



def new_account(
    cookies: str, 
    name: str = '',
    images: bool = True,
    notifications: bool = False,
    show: bool = False
) -> Account:
    n = name if name else f"account{len(os.listdir(os.path.join(os.path.dirname(os.path.normcase(__file__)), 'accounts'))):0>4}"
    print(n, "Creating...")
    account = Account(
        name=n,
        images=images,
        notifications=notifications,
        show=show
    )
    account.driver.get("https://m.facebook.com/")
    try:
        for cookie in cookies.split("; "):
            n, v = cookie.split("=")
            account.driver.add_cookie({"name": n, "value": v})
    except Exception as e:
        account.quit()
        raise Exception(f"Invalid cookies Error: {e}")
    account.driver.refresh()
    # Check login
    method = ec.presence_of_element_located((By.CSS_SELECTOR, "div._5xu4 > a"))
    try:
        home = WebDriverWait(driver=account.driver, timeout=10).until(method)
    except TimeoutException:
        account.quit()
        raise Exception("Login fail!")
    print("Login Successfully!")
    if _id := re.search(pattern=r"(?<=com/).+?(?=[?])", string=home.get_attribute("href")):
        account.uid = _id.group()
    return account


def open_account(
    name: str,
    images: bool = True,
    notifications: bool = False,
    show: bool = False
) -> Account:
    print(name, "Opening...")
    account = Account(
        name=name, 
        images=images, 
        notifications=notifications,
        show=show
    )
    if not account.name_existed():
        account.quit()
        raise Exception(f"Name {name} not existed")
    
    with open(os.path.join(account.dir, account.file), mode="rb") as file:
        data = pickle.load(file=file)
    account.uid = data["uid"]
    # add cookie
    cookies = data["cookies"]
    account.driver.get("https://m.facebook.com")
    for cookie in cookies:
        account.driver.add_cookie(cookie)
    account.driver.refresh()
    # Check Login
    method = ec.presence_of_element_located((By.CSS_SELECTOR, "div._5xu4 > a"))
    try:
        WebDriverWait(driver=account.driver, timeout=10).until(method)
    except TimeoutException:
        account.quit()
        raise Exception("Cookies died!")
    print("Successfully!")
    return account
