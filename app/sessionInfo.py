from selenium import webdriver
import time
from app.dbManager import insert_sid, get_session

# Logger started

# Used to obtain the SID just by login in (TO BE CHANGED)
def get_sid():
    driver = webdriver.Edge()
    login_url = 'https://buff.163.com/account/login?back_url=/user-center/asset/recharge/%3F'
    driver.get(login_url)

    max_wait_time = 300 

    start_time = time.time()
    sessionID = None 
    while time.time() - start_time < max_wait_time:
        for cookie in driver.get_cookies():
            if cookie['name'] == 'session':
                sessionID = cookie['value']
                break
            time.sleep(1)
        if sessionID:
            break 
    if not sessionID:
        driver.quit()
        return
    driver.quit()

    insert_sid(sessionID)
    return sessionID

# Check if SID saved if not [get_sid]
def check_sid():
    if not get_session():
        return get_sid()

    session_id, date = get_session()[0]
    if session_id and date == time.strftime("%Y-%m-%d"):
        return session_id
    else:
        sid = get_sid()
        return sid