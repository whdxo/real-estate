from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import time

app = Flask(__name__)

def search_apartment_info(dong_number, ho_number):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://land.seoul.go.kr/land/wskras/generalInfo.do#")
    print("[INFO] 페이지 로드 완료")

    wait = WebDriverWait(driver, 10)

    try:
        # 부동산종합정보 - 건축물정보 클릭
        print("[INFO] 건축물정보 탭 클릭")
        building_info_tab = wait.until(EC.presence_of_element_located((By.ID, "eaisInfo")))
        building_info_tab.click()

        # 자치구 선택 드롭다운
        print("[INFO] 자치구 선택")
        region_dropdown = wait.until(EC.presence_of_element_located((By.ID, "selSgg")))
        region_dropdown.click()
        gu_option = wait.until(EC.presence_of_element_located((By.XPATH, "//option[text()='노원구']")))
        gu_option.click()

        # 동 선택 드롭다운
        print("[INFO] 동 선택")
        dong_dropdown = driver.find_element(By.ID, "selBjdong")
        dong_dropdown.click()
        dong_option = wait.until(EC.presence_of_element_located((By.XPATH, "//option[text()='상계동']")))
        dong_option.click()

        # 번호 입력 필드 (동 번호에 따라 다른 고정값 사용)
        print("[INFO] 번호 입력")
        number_input = driver.find_element(By.ID, "bonbeon")
        number_input.clear()
        
        # 동 번호에 따라 다른 고정값 설정
        if dong_number in [301, 302]:
            fixed_number = "730"
            print(f"[INFO] 301동, 302동용 고정값 {fixed_number} 사용")
            number_input.send_keys(fixed_number)
            
            # 부번 입력 (301, 302동의 경우 "2" 입력)
            print("[INFO] 부번 입력")
            bubeon_input = driver.find_element(By.ID, "bubeon")
            bubeon_input.clear()
            bubeon_input.send_keys("2")
            print("[INFO] 부번 '2' 입력 완료")
        else:
            fixed_number = "737"
            print(f"[INFO] 303동~326동용 고정값 {fixed_number} 사용")
            number_input.send_keys(fixed_number)

        # 검색 버튼 클릭
        print("[INFO] 검색 버튼 클릭")
        search_button = driver.find_element(By.ID, "btnSearch")
        search_button.click()

        # 검색 결과에서 동명칭 선택
        building_name = f"{dong_number}동"  # 동 번호를 사용하여 건물명 생성
        print(f"[INFO] 검색 결과에서 {building_name} 선택")
        result_row = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[@title='{building_name}']/a[text()='{building_name}']")))
        driver.execute_script("arguments[0].scrollIntoView();", result_row)
        driver.execute_script("arguments[0].click();", result_row)

        # 전유부 층 선택
        print("[INFO] 전유부 층 선택")
        floor_dropdown = wait.until(EC.presence_of_element_located((By.ID, "selPartTab1")))
        floor_dropdown.click()

        # 입력한 층 선택
        floor_number = str(ho_number)  # ho_number를 문자열로 변환
        floor_digit = int(floor_number) // 100
        floor_xpath = f"//option[contains(text(), '지상 {floor_digit}층')]"
        print(f"[DEBUG] 층 XPath: {floor_xpath}")
        floor_option = wait.until(EC.presence_of_element_located((By.XPATH, floor_xpath)))
        driver.execute_script("arguments[0].scrollIntoView();", floor_option)
        floor_option.click()

        # 전유부 동 선택
        print("[INFO] 전유부 동 선택")
        unit_dropdown = wait.until(EC.presence_of_element_located((By.ID, "selPartTab2")))
        unit_dropdown.click()
        unit = f"{ho_number}호"  # 호수 문자열 생성
        unit_xpath = f"//option[contains(text(), '{building_name} {unit}')]"
        print(f"[DEBUG] 동 XPath: {unit_xpath}")
        unit_option = wait.until(EC.presence_of_element_located((By.XPATH, unit_xpath)))
        driver.execute_script("arguments[0].scrollIntoView();", unit_option)
        unit_option.click()

        # 전용면적 데이터 추출
        print("[INFO] 전용면적 데이터 추출")
        area_xpath = f"//tr[td/div[@title='{building_name} {unit}']]//td[@class='txt-r']/div[@class='nowrap']"
        print(f"[DEBUG] 전용면적 XPath: {area_xpath}")
        area_element = wait.until(EC.presence_of_element_located((By.XPATH, area_xpath)))
        area = area_element.get_attribute("title").strip()

        # 대지권지분비율 동 선택
        print("[INFO] 대지권지분비율 동 선택")
        ratio_dong_dropdown = wait.until(EC.presence_of_element_located((By.ID, "selRateDongEais0096")))
        ratio_dong_dropdown.click()
        ratio_dong_xpath = f"//option[text()='{dong_number}']"
        print(f"[DEBUG] 대지권지분비율 동 XPath: {ratio_dong_xpath}")
        ratio_dong_option = wait.until(EC.presence_of_element_located((By.XPATH, ratio_dong_xpath)))
        driver.execute_script("arguments[0].scrollIntoView();", ratio_dong_option)
        ratio_dong_option.click()
        print("[INFO] 대지권지분비율 동 선택 완료")
        time.sleep(1)

        # 대지권지분비율 호 선택
        print("[INFO] 대지권지분비율 호 선택")
        ratio_ho_dropdown = wait.until(EC.presence_of_element_located((By.ID, "selRateHoEais0096")))
        ratio_ho_dropdown.click()

        # 입력된 ho_number 값에서 호수 정보 추출
        unit_number = str(ho_number)
        print(f"[DEBUG] 추출된 호수 번호: {unit_number}")

        # 드롭다운 옵션들을 가져오기
        options = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#selRateHoEais0096 option")))
        found_option = False

        for option in options:
            option_text = option.text
            print(f"[DEBUG] 옵션 텍스트: {option_text}")
            # 옵션 텍스트에서 호수 부분 추출 및 비교
            option_unit_match = re.search(r'(\d+)', option_text)
            if option_unit_match:
                option_unit = option_unit_match.group(1)
                if option_unit == unit_number:
                    print(f"[INFO] 일치하는 옵션 찾음: {option_text}")
                    driver.execute_script("arguments[0].scrollIntoView();", option)  # 스크롤
                    option.click()
                    found_option = True
                    break  # 찾았으면 루프 종료
            else:
                print(f"[DEBUG] 옵션 텍스트에서 호수 번호 추출 실패: {option_text}")

        if not found_option:
            print(f"[ERROR] 드롭다운에서 '{ho_number}'에 해당하는 호수를 찾을 수 없습니다. 종료합니다.")
            return None, None

        print("[INFO] 대지권지분비율 호 선택 완료")
        time.sleep(1)  # 안정성을 위해 잠시 대기

        # 대지권지분비율 데이터 추출
        print("[INFO] 대지권지분비율 데이터 추출")
        ratio_element = wait.until(EC.presence_of_element_located((By.XPATH, "//td[@id='txtRateE0096']")))
        ratio_text = ratio_element.text.strip()
        print(f"[INFO] 원본 대지권지분비율 데이터: {ratio_text}")

        # 정규표현식을 사용하여 원하는 값만 추출
        pattern = r'\d+\.\d+/\d+\.\d+'  # 예: "58.06/99571.5" 형태 찾기
        matches = re.findall(pattern, ratio_text)
        if matches:
            # 첫 번째 매칭에서 분자값만 추출
            ratio_value = matches[0].split('/')[0]  # "58.06/99571.5" -> "58.06"
            print(f"[INFO] 추출된 대지권지분비율: {ratio_value}")
        else:
            ratio_value = "추출 실패"
            print("[ERROR] 대지권지분비율 값 추출 실패")

        time.sleep(2)

        return area, ratio_value

    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        return None, None

    finally:
        print("[INFO] 브라우저 종료")
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dong_number = int(request.form['dong_number'])
        ho_number = int(request.form['ho_number'])
        
        # 동 번호 유효성 검사
        if dong_number < 301 or dong_number > 326:
            return render_template('index.html', error="유효한 동 번호가 아닙니다. (301~326)")
            
        area, ratio = search_apartment_info(dong_number, ho_number)
        return render_template('result.html', dong_number=dong_number, ho_number=ho_number, area=area, ratio=ratio)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)