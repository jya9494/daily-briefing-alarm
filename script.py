from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from gtts import gTTS
import time
import os
import re

EMAIL = os.environ["TB_EMAIL"]
PASSWORD = os.environ["TB_PASSWORD"]

# 브라우저 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# 타임블럭 로그인
driver.get("https://app.timeblocks.com/signin")
time.sleep(2)
driver.find_element(By.NAME, "email").send_keys(EMAIL)
driver.find_element(By.NAME, "password").send_keys(PASSWORD)
driver.find_element(By.NAME, "password").submit()
time.sleep(5)

sentences = []

try:
    # 오늘 날짜 추출
    date_elem = driver.find_element(By.XPATH, '//div[@id="today_position"]//div[contains(@class, "DateCell__Date")]')
    date_text = date_elem.text.strip()
    today_text = time.strftime(f"%m월 {date_text}일").lstrip("0").replace(" 0", " ")

    # 오늘 셀 안의 모든 Block__Content 요소 가져오기
    blocks = driver.find_elements(By.XPATH, '//div[@id="today_position"]//div[contains(@class, "Block__Content")]')

    for block in blocks:
        istodohabit = block.get_attribute("istodohabit") == "true"
        hastime = block.get_attribute("hastime") == "true"

        try:
            title_elem = block.find_element(By.XPATH, './/p[contains(@class, "Title__Text")]')
            raw = title_elem.text.strip()
        except:
            continue

        # 체크 여부 확인 (습관 완료 확인용)
        try:
            has_check = bool(block.find_element(By.XPATH, './/path'))
        except:
            has_check = False

        # 1. 일정 (시간 포함)
        if hastime:
            match = re.match(r"(\d+(?:\.\d+)?)(.+)", raw)
            if match:
                time_raw = match.group(1)
                title = match.group(2).strip()
                hour = int(float(time_raw))
                minute = int((float(time_raw) - hour) * 60)

                if hour < 12:
                    time_label = f"오전 {hour}시"
                elif hour == 12:
                    time_label = "정오 12시"
                else:
                    time_label = f"오후 {hour - 12}시"
                if minute == 30:
                    time_label += " 30분"

                sentences.append(f"{time_label}에 {title}이 있습니다.")
            else:
                sentences.append(f"{raw} 일정이 있습니다.")

        # 2. 할일 / 습관
        elif istodohabit:
            if has_check:
                sentences.append(f"{raw}을 완료했습니다.")
            else:
                # 할일인지 습관인지 구분 어려운 경우
                sentences.append(f"{raw} 할 일이 있습니다.")

        # 3. 구간 (istodohabit=False, hastime=False)
        else:
            sentences.append(f"{raw} 구간이 계획되어 있습니다.")

except Exception as e:
    sentences = ["오늘은 등록된 일정을 불러오는 데 실패했습니다."]
    print("❗ 오류 발생:", e)

# 문장 조립
briefing_text = f"오늘은 {today_text}입니다. " + " ".join(sentences)

# TTS 변환
tts = gTTS(text=briefing_text, lang='ko')
tts.save("daily_briefing.mp3")
print("✅ 저장 완료:", briefing_text)

driver.quit()

