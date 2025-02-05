from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def validate_input(prompt, pattern):
    while True:
        user_input = input(prompt)
        if re.match(pattern, user_input):
            return user_input
        else:
            print("[ERROR] 잘못된 형식입니다. 다시 입력해주세요.")

def search_apartment_info(building, unit):
    # 크롬 드라이버 설정
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://land.seoul.go.kr/land/wskras/generalInfo.do#")
    print("[INFO] 페이지 로드 완료")

    wait = WebDriverWait(driver, 10)
    action = ActionChains(driver)

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

        # 번호 입력 필드
        print("[INFO] 번호 입력")
        number_input = driver.find_element(By.ID, "bonbeon")
        number_input.clear()
        number_input.send_keys("737")

        # 검색 버튼 클릭
        print("[INFO] 검색 버튼 클릭")
        search_button = driver.find_element(By.ID, "btnSearch")
        search_button.click()

        # 페이지 아래로 스크롤
        print("[INFO] 페이지 스크롤")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 스크롤 후 페이지 로딩 대기

        # 검색 결과에서 동명칭과 호수 선택
        print(f"[INFO] 검색 결과에서 {building} 선택")
        result_row = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[@title='{building}']/a[text()='{building}']")))
        driver.execute_script("arguments[0].scrollIntoView();", result_row)
        driver.execute_script("arguments[0].click();", result_row)

        # 전유부 층 선택
        print("[INFO] 전유부 층 선택")
        floor_dropdown = wait.until(EC.presence_of_element_located((By.ID, "selPartTab1")))
        floor_dropdown.click()

        # 입력한 층 선택
        floor_number = unit.split('호')[0]  # '813호'에서 '813' 추출
        floor_digit = int(floor_number) // 100  # 층수 계산 (예: '813' -> 8)
        floor_xpath = f"//option[contains(text(), '지상\u00a0{floor_digit}층')]"  # &nbsp; 처리
        print(f"[DEBUG] 층 XPath: {floor_xpath}")
        floor_option = wait.until(EC.presence_of_element_located((By.XPATH, floor_xpath)))
        driver.execute_script("arguments[0].scrollIntoView();", floor_option)
        floor_option.click()

        # 전유부 동 선택
        print("[INFO] 전유부 동 선택")
        unit_dropdown = wait.until(EC.presence_of_element_located((By.ID, "selPartTab2")))
        unit_dropdown.click()

        # 입력한 동 선택
        unit_xpath = f"//option[contains(text(), '{building}\u00a0{unit}')]"  # &nbsp; 처리
        print(f"[DEBUG] 동 XPath: {unit_xpath}")
        unit_option = wait.until(EC.presence_of_element_located((By.XPATH, unit_xpath)))
        driver.execute_script("arguments[0].scrollIntoView();", unit_option)
        unit_option.click()

        # 전용면적 데이터 추출
        print("[INFO] 전용면적 데이터 추출")
        area_xpath = f"//tr[td/div[@title='{building} {unit}']]//td[@class='txt-r']/div[@class='nowrap']"
        print(f"[DEBUG] 전용면적 XPath: {area_xpath}")
        area_element = wait.until(EC.presence_of_element_located((By.XPATH, area_xpath)))
        area = area_element.get_attribute("title").strip()

        # 대지권지분비율 데이터 추출을 위해 동 선택
        print("[INFO] 대지권지분비율 동 선택")
        ratio_dong_dropdown = wait.until(EC.presence_of_element_located((By.ID, "selRateDongEais0096")))
        ratio_dong_dropdown.click()
        ratio_dong_xpath = f"//option[text()='{building.split('동')[0]}']"
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

        # 정확한 value 속성을 기반으로 XPath 생성
        input_ho = unit.split('호')[0]  # 입력 호수, 예: '402호' -> '402'
        ratio_ho_value = f"0096|{building.split('동')[0]}|1|{input_ho}"  # 정확한 value 생성
        ratio_ho_xpath = f"//option[@value='{ratio_ho_value}']"  # 정확한 매칭
        print(f"[DEBUG] 대지권지분비율 호 XPath: {ratio_ho_xpath}")

        try:
            ratio_ho_option = wait.until(EC.presence_of_element_located((By.XPATH, ratio_ho_xpath)))
            driver.execute_script("arguments[0].scrollIntoView();", ratio_ho_option)
            print(f"[DEBUG] 선택된 호 옵션 텍스트: {ratio_ho_option.text.strip()}")  # 선택된 옵션 확인
            ratio_ho_option.click()
            print("[INFO] 대지권지분비율 호 선택 완료")
            time.sleep(1)  # 데이터 로딩을 위해 1초간 기다림
        except Exception as e:
            print(f"[ERROR] 대지권지분비율 호 선택 실패: {e}")


        # 대지권지분비율 데이터 추출
        time.sleep(2)
        print("[INFO] 대지권지분비율 데이터 추출")
        ratio_element = wait.until(EC.presence_of_element_located((By.XPATH, "//td[@id='txtRateE0096']")))
        ratio_text = ratio_element.text.strip()
        print(f"[INFO] 대지권지분비율 데이터: {ratio_text}")
        time.sleep(2)
        # 결과 출력
        print("\n검색 결과:")
        print(f"선택한 동: {building}")
        print(f"선택한 호: {unit}")
        print(f"전용면적: {area}")
        print(f"대지권지분비율: {ratio_text}")

    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")

    finally:
        # 브라우저 종료
        print("[INFO] 브라우저 종료")
        driver.quit()

if __name__ == "__main__":

    building = validate_input("동을 입력하세요 (예: 317동): ", r"^\d+동$")
    unit = validate_input("호수를 입력하세요 (예: 501호): ", r"^\d+호$")
    search_apartment_info(building, unit)
