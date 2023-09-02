import time
import argparse
import pandas as pd

from apscheduler.schedulers.blocking import BlockingScheduler

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_site_list(driver, ground):
    '''提取场地信息，并按照偏好排序，返回场地列表'''
    site_slots = WebDriverWait(driver, 10, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.head')))[1:]
    site_list = [site.text for site in site_slots]
    # print(site_list)
    # 检查用户输入是否在场地列表中
    if ground in site_list:
        # 将用户输入的场地移到列表最前面
        site_list.remove(ground)
        site_list.insert(0, ground)
    else:
        print(f"抱歉，{ground}场不在列表中")
    return site_list

def login_cpu(driver, student_id, password):
    '''cpu账号登录'''
    # 这里使用By模块指定查找方法，以及CSS选择器来找到学号和密码的输入框，并输入相应的值
    student_id_input = driver.find_element(By.CSS_SELECTOR, 'input[name="username"]')
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')

    # 输入学号和密码
    student_id_input.send_keys(student_id)
    password_input.send_keys(password)

    # 提交表单
    password_input.send_keys(Keys.RETURN)

    # 调用login()函数来触发登录
    js_code_cpu = "login();"
    driver.execute_script(js_code_cpu)


def query(driver, time_slots, status, time_len):
    '''查询选择天，各厂地预约情况,返回dataframe和status字典'''
    status_dict = {}
    site_slots = WebDriverWait(driver, 10, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.head')))
    # 创建一个空dataframe
    badminton_gym = pd.DataFrame(columns=[date.text for date in site_slots])
    # 行名为time_slots中的内容
    badminton_gym.iloc[:, 0] = [time.text.replace('\n|\n', '-') for time in time_slots]
    # 在badminton_gym中，填入status中的信息
    for i, state in enumerate(status):
        # 添加入字典中
        status_dict[i] = state.text
        # 添加入dataframe中
        badminton_gym.iloc[i % time_len, i // time_len + 1] = state.text
    return badminton_gym, status_dict


def success_info(driver, success_message):
    '''输出预约成功信息'''
    if '成功' in success_message:
        time.sleep(1.5)
        # 定位包含预约信息的父级 <uni-view> 元素
        order_item = driver.find_element(By.CLASS_NAME, 'order-item')

        # 提取位置信息
        location = order_item.find_element(By.CLASS_NAME, 'line').text

        # 提取日期和时段信息
        date_and_time = order_item.find_elements(By.CLASS_NAME, 'line')[1].text

        # 提取学号/教工号信息
        student_id = \
            order_item.find_element(By.XPATH, "//span[contains(text(), '学号/教工号：')]").text.split('：')[1]

        # 提取预约人姓名信息
        name = \
            order_item.find_element(By.XPATH, "//span[contains(text(), '预约人姓名：')]").text.split('：')[1]

        # 提取预约人电话信息
        telephone = \
            order_item.find_element(By.XPATH, "//span[contains(text(), '预约人电话：')]").text.split('：')[1]

        # 提取预约状态信息
        status = \
            order_item.find_element(By.XPATH, "//span[contains(text(), '预约状态：')]").text.split('：')[1]
        print(location + '/n' + date_and_time + '/n' + "学号/教工号:" + student_id + '/n' + "预约人姓名:" + name +
              '/n' + "预约人电话:" + telephone + '/n' + "预约状态:" + status)
    else:
        print('预约失败')

def reserve(start_time, end_time, ground, date, name, telephone, student_id, password, situation):
    # 不自动关闭浏览器
    option = webdriver.EdgeOptions()
    option.add_experimental_option("detach", True)

    # 使用Edge浏览器，你需要下载对应的edgedriver并配置到系统环境变量中
    driver = webdriver.Edge(options=option)
    url = 'https://cgyy.xiaorankeji.com/h5/index.html#/pages/store/index'
    driver.get(url)

    # 使用JavaScript点击按钮，’我已知晓‘
    js_code = "document.querySelector('.btn-main').click();"
    driver.execute_script(js_code)

    #cpu账号登录
    login_cpu(driver, student_id, password)


    # 使用JavaScript点击按钮,’我已知晓‘
    js_code2 = "document.querySelector('.btn-main').click();"
    driver.execute_script(js_code2)

    # 等待羽毛球馆元素出现
    badminton_gym = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//uni-view[contains(text(), '羽毛球馆')]")))

    # 使用JavaScript点击羽毛球馆项目
    js_code3 = "arguments[0].click();"
    driver.execute_script(js_code3, badminton_gym)

    # 等待日期选择元素出现
    date_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.day-item.textcenter')))

    # 遍历日期元素，选择用户指定的日期
    for date_element in date_elements:
        date_text = date_element.text
        if date in date_text:
            # 点击用户指定的日期
            js_code = "arguments[0].click();"
            driver.execute_script(js_code, date_element)
            break

    # 等待两秒
    time.sleep(1.5)

    # 等待预约时段信息出现
    time_slots = WebDriverWait(driver, 10, 1).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.item1.bgblue')))

    time_len = len(time_slots)
    # 遍历时段信息和场地信息
    times = []

    status = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.item.bglightblue')))
    for index, time_slot in enumerate(time_slots):
        if start_time in time_slot.text and end_time in time_slot.text:
            times.append(time_slot.text)
            # print(index)
            break

    # 查询选择天，各场地预约情况
    if situation:
        badminton_gym, status_dict = query(driver, time_slots, status, time_len)
        print(badminton_gym)

    # 提取场地信息，并按照偏好排序，返回场地列表
    site_list = get_site_list(driver, ground)


    for _,site in enumerate(site_list):
        i = int(site[0])
        print('正在查询' + str(i) + '号场预约情况:' + status_dict[index + (i - 1) * time_len])
        if status_dict[index + (i - 1) * time_len] == '可以预约':  # 写一个else返回保留或者已预约情况
            # 使用JavaScript点击对应的元素
            js_code = "arguments[0].click();"
            driver.execute_script(js_code, status[index + (i - 1) * time_len])

            # 等待姓名输入字段可点击
            time.sleep(0.2)
            name_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@maxlength='5']")))
            driver.execute_script("arguments[0].removeAttribute('disabled');", name_input)

            # 输入姓名
            name_input.send_keys(name)

            # 等待电话输入字段可点击
            telephone_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@maxlength='11']")))
            driver.execute_script("arguments[0].removeAttribute('disabled');", telephone_input)

            # 输入电话号码
            telephone_input.send_keys(telephone)

            time.sleep(2)

            # 提交预约
            submit_button = driver.find_element(By.XPATH, "//uni-button[contains(text(), '提交预约')]")
            js_code = "arguments[0].click();"
            driver.execute_script(js_code, submit_button)

            time.sleep(1.5)
            # 等待预约成功模态框出现
            success_modal = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.uni-modal__bd'))
            )

            # 获取模态框中的提示信息
            success_message = success_modal.text

            # 输出提示信息
            print("预约消息提示：", success_message)

            # 点击确定按钮
            confirm_button = driver.find_element(By.CSS_SELECTOR,
                                                 '.uni-modal__btn.uni-modal__btn_primary')
            js_code = "arguments[0].click();"
            driver.execute_script(js_code, confirm_button)

            # 输出预约成功信息
            success_info(driver, success_message)
            break
    # 运行结束后关闭浏览器
    driver.quit()

# 定义一个可调用的函数，该函数包含您要执行的预约逻辑
def perform_reservation():
    args = parse_args()
    # 在这里调用您的预约函数，并传递参数
    reserve(args.start_time, args.end_time, args.ground, args.date, args.name, args.telephone, args.student_ID, args.password, args.situation)
    # 停止调度器
    scheduler.shutdown()

def parse_args():
    parse = argparse.ArgumentParser(description='预约羽毛球场地')
    parse.add_argument('--start_time', type=str, default='12:00', help='开始时间')
    parse.add_argument('--end_time', type=str, default='13:00', help='结束时间')
    parse.add_argument('--ground', type=str, default='5号', help='偏好几号球场，有1号到6号球场')
    parse.add_argument('--date', type=str, default='周一', help='预约日期')
    parse.add_argument('--name', type=str, default='孙益铭', help='名字')
    parse.add_argument('--telephone', type=int, default=15958104798, help='电话号码')
    parse.add_argument('--student_ID', type=int, default=3322051484, help='学号')
    parse.add_argument('--password', type=str, default='Clearbob2019', help='密码')
    parse.add_argument('--situation', type=bool, default=True, help='是否查询此时预约日期的预约情况')
    parse.add_argument('--headless', type=bool, default=False, help='是否使用无头模式')
    args = parse.parse_args()
    return args


if __name__ == '__main__':

    # 创建一个调度器
    scheduler = BlockingScheduler()

    # 添加一个定时任务，每天晚上12:00执行
    scheduler.add_job(perform_reservation, 'cron', hour=10, minute=7)

    # 启动调度器
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

