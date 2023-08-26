import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def reserve(start_time, end_time, date, name, telephone, student_id, password):
    # 不自动关闭浏览器
    option = webdriver.EdgeOptions()
    option.add_experimental_option("detach", True)

    # 使用Edge浏览器，你需要下载对应的edgedriver并配置到系统环境变量中
    driver = webdriver.Edge(options=option)
    url = 'https://cgyy.xiaorankeji.com/h5/index.html#/pages/store/index'
    driver.get(url)

    # 使用JavaScript点击按钮
    js_code = "document.querySelector('.btn-main').click();"
    driver.execute_script(js_code)

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

    # 使用JavaScript点击按钮
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

    # 遍历日期元素，选择周五或周日
    target_date_elements = []
    for date_element in date_elements:
        date_text = date_element.text
        # print(date_text)
        if date in date_text:
            target_date_elements.append(date_element)

    # 选择周五或周日的第一个日期（示例中为第一个）
    js_code = "arguments[0].click();"
    driver.execute_script(js_code, target_date_elements[0])
    # 等待两秒
    time.sleep(2)

    # 等待预约时段信息出现
    time_slots = WebDriverWait(driver, 10, 1).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.item1.bgblue')))

    # 提取球场信息
    site_slots = WebDriverWait(driver, 10, 1).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.head')))[1:]
    time_len = len(time_slots)
    # 遍历时段信息和场地信息
    times = []
    status_dict = {}

    status = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.item.bglightblue')))
    for index, time_slot in enumerate(time_slots):
        # print(time_slot.text)
        if start_time in time_slot.text and end_time in time_slot.text:
            times.append(time_slot.text)
            print(index)
            break

    for index2, i in enumerate(status):
        # 添加入字典中
        status_dict[index2] = i.text
    print(status_dict)
    for i in range(6):
        print('正在查询' + str(i + 1) + '号场预约情况:' + status_dict[index + i * time_len])
        if status_dict[index + i * time_len] == '可以预约':  # 写一个else返回保留或者已预约情况
            # 使用JavaScript点击对应的元素
            js_code = "arguments[0].click();"
            driver.execute_script(js_code, status[index + i * time_len])

            # name_input = driver.find_element(By.CSS_SELECTOR, '.uni-input-placeholder.uni-input-placeholder')
            # driver.execute_script("arguments[0].value = '孙益铭';", name_input)

            # 等待姓名输入字段可点击
            name_input = WebDriverWait(driver, 10, 1).until(
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

            time.sleep(1)
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

            #输出预约成功信息
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

                # 输出提取的信息
                print(location)
                print(date_and_time)
                print("学号/教工号:", student_id)
                print("预约人姓名:", name)
                print("预约人电话:", telephone)
                print("预约状态:", status)
            break
    print(times)


def parse_args():
    parse = argparse.ArgumentParser(description='预约羽毛球场地')
    parse.add_argument('--start_time', type=str, default='09:00', help='开始时间')
    parse.add_argument('--end_time', type=str, default='10:00', help='结束时间')
    parse.add_argument('--date', type=str, default='周一', help='预约日期')
    parse.add_argument('--name', type=str, default='王健', help='名字')
    parse.add_argument('--telephone', type=int, default=15958104798, help='电话号码')
    parse.add_argument('--student_ID', type=int, default=3322051519, help='学号')
    parse.add_argument('--password', type=str, default='123456WJ', help='密码')
    args = parse.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    reserve(args.start_time, args.end_time, args.date, args.name, args.telephone, args.student_ID, args.password)

'''
# 找到“时段\位置”这一列的元素
time_position_head = driver.find_element(By.CLASS_NAME, "head")

# 找到“时段\位置”为“09:00|10:00”的时间段元素
target_time_element = driver.find_element(By.XPATH, "//uni-view[text()='09:00|10:00']")

# 找到对应的场地元素，比如“2号”
target_court_element = driver.find_element(By.XPATH, "//uni-view[text()='2号']")

# 找到可以预约的选项，这里假设是使用class名字为"small-line"的元素
bookable_option = driver.find_element(By.CLASS_NAME, "small-line")

# 使用JavaScript点击对应的元素
js_code = "arguments[0].click();"
'''
