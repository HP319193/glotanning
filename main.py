import undetected_chromedriver as uc
import time
import os
from selenium.webdriver.common.by import By
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

load_dotenv()

downloads_folder = os.getenv("DOWNLOAD_DIR")

opts = uc.ChromeOptions()

opts.user_data_dir = "./browser_profile"

driver = uc.Chrome(options=opts)

def search():
    driver.get('https://employers.indeed.com/candidates?statusName=Awaiting+Review&id=0')
    time.sleep(10)
    try:
        print("Awaiting candidates found!")
        tbody_element = driver.find_element(By.XPATH, '//tbody[@data-testid="table-row"]')
        tbody_element.click()
    except:
        print("Awaiting candidates not found!")
        return
    
    results = []
    time.sleep(30)

    # while True:
    #     try:
    #         print("not")
    #         loadmore_element = driver.find_element(By.ID, "fetchNextCandidates")
    #         loadmore_element.click()
    #     except:
    #         print("Got")
    #         break
    
    # time.sleep(60)

    awaiting_elements = driver.find_elements(By.XPATH, '//*[@data-testid="CandidateListItem"]')

    print(len(awaiting_elements))

    for awaiting_element in awaiting_elements:
        awaiting_element.click()
        time.sleep(10)

        result = {}
        name = driver.find_element(By.XPATH, '//span[@data-testid="namePlate-candidateName"]').text
        result['name'] = name
        print(name)

        questions = driver.find_element(By.XPATH, '//*[@data-testid="iqcp-question-list"]').find_elements(By.XPATH, '//*[@data-testid="question"]')
        custom_question = []
        for question in questions:
            query = question.find_element(By.CLASS_NAME, "css-sfm6zc").text
            custom_question.append(query)
            try:
                answer = question.find_element(By.CLASS_NAME, "css-ioodws").text
                custom_question.append(answer)
            except:
                answer = question.find_elements(By.CLASS_NAME, "ecydgvn1")[1].text
                custom_question.append(answer)

        result['custom_question'] = custom_question

        isResumeChecked = False

        try:
            download_but = driver.find_element(By.XPATH, '//a[@data-dd-action-name="download-resume-inline"]')
            download_but.click()

            while True:
                files = os.listdir(downloads_folder)

                isDownloaded = False
                Index = -1

                for index, file in enumerate(files):
                    _, file_extension = os.path.splitext(os.path.join(downloads_folder, file))
                    if file_extension.lower() == '.pdf':
                        isDownloaded = True
                        Index = index
                        break
                
                if isDownloaded == True:
                    resume = extract_text(os.path.join(downloads_folder, files[Index]))
                    result['resume'] = resume
                    os.remove(os.path.join(downloads_folder, files[Index]))
                    
                    break

            isResumeChecked = True

        except:
            pass

        try:
            if isResumeChecked == True:
                maybe_element = driver.find_element(By.XPATH, '//label[@title="Maybe"]')
                maybe_element.click()
                print("Maybe is clicked")

        except:
            pass

        results.append(result)

    return results

while True:
    results = search()
