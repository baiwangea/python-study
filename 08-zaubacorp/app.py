import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict
from fake_useragent import UserAgent
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='scraper.log'
)


def get_random_user_agent() -> str:
    """生成随机User-Agent"""
    ua = UserAgent()
    return ua.random


def setup_selenium_options(proxy: str = None) -> Options:
    """设置Selenium选项"""
    options = Options()
    options.add_argument(f"user-agent={get_random_user_agent()}")
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    return options


def scrape_page(page_num: int, base_url: str = "https://www.zaubacorp.com", retries: int = 3, proxy: str = None) -> \
List[Dict]:
    """
    使用Selenium爬取单页列表
    """
    url = f"{base_url}/companies-list/status-Active/p-{page_num}-company.html"
    records = []

    for attempt in range(retries):
        driver = None
        try:
            options = setup_selenium_options(proxy)
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            # 等待表格加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            if "captcha" in driver.page_source.lower() or "access denied" in driver.page_source.lower():
                logging.warning(f"第{page_num}页检测到CAPTCHA或访问被拒绝")
                return records

            table = soup.find('table')
            if not table:
                logging.warning(f"第{page_num}页未找到表格")
                return records

            rows = table.find_all('tr')[1:]  # 跳过表头
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 5:
                    record = {
                        'ID': cols[0].get_text(strip=True),
                        '公司名称': cols[1].get_text(strip=True),
                        '状态': cols[2].get_text(strip=True),
                        '注册资本': cols[3].get_text(strip=True),
                        '地址': cols[4].get_text(strip=True)
                    }
                    records.append(record)

            logging.info(f"第{page_num}页爬取到{len(records)}条记录")
            return records

        except Exception as e:
            logging.error(f"第{page_num}页第{attempt + 1}次尝试失败: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return records

        finally:
            if driver:
                driver.quit()


def scrape_detail(record: Dict, retries: int = 3, proxy: str = None) -> Dict:
    """
    使用Selenium爬取公司详情页
    """
    company_id = record['ID']
    company_name = record['公司名称'].replace(' ', '-').upper()
    detail_url = f"https://www.zaubacorp.com/{company_name}-{company_id}"
    detail_data = {}

    for attempt in range(retries):
        driver = None
        try:
            options = setup_selenium_options(proxy)
            driver = webdriver.Chrome(options=options)
            driver.get(detail_url)

            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            if "captcha" in driver.page_source.lower() or "access denied" in driver.page_source.lower():
                logging.warning(f"详情页 {detail_url} 检测到CAPTCHA或访问被拒绝")
                return detail_data

            # 提取Basic Information表格
            basic_table = soup.find('table')
            if basic_table:
                rows = basic_table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 2:
                        key = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        detail_data[key] = value

            # 提取Contact Details
            contact_section = soup.find(string=re.compile("Contact Details", re.I))
            if contact_section:
                contact_text = contact_section.find_next('p').get_text(strip=True) if contact_section.find_next(
                    'p') else ''
                email_match = re.search(r'Email ID:\s*([\w\.-]+@[\w\.-]+)', contact_text)
                website_match = re.search(r'Website:\s*(\S+)', contact_text)
                if email_match:
                    detail_data['Email'] = email_match.group(1)
                detail_data['Website'] = website_match.group(1) if website_match else 'Not Available'

            logging.info(f"详情页 {detail_url} 提取成功")
            return detail_data

        except Exception as e:
            logging.error(f"详情页 {detail_url} 第{attempt + 1}次尝试失败: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return detail_data

        finally:
            if driver:
                driver.quit()


def scrape_multiple_pages(start_page: int, num_pages: int, max_workers: int = 3, delay: float = 2.0,
                          proxy: str = None) -> List[Dict]:
    """
    使用多线程爬取多页列表
    """
    all_records = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_page = {
            executor.submit(scrape_page, page, proxy=proxy): page
            for page in range(start_page, start_page + num_pages)
        }

        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                records = future.result()
                all_records.extend(records)
                time.sleep(delay)
            except Exception as exc:
                logging.error(f"第{page}页发生异常: {exc}")

    return all_records


def scrape_details(all_records: List[Dict], max_workers: int = 3, delay: float = 2.0, proxy: str = None) -> None:
    """
    使用多线程爬取所有记录的详情页，并更新记录
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_record = {
            executor.submit(scrape_detail, record, proxy=proxy): record
            for record in all_records
        }

        for future in as_completed(future_to_record):
            record = future_to_record[future]
            try:
                detail_data = future.result()
                record.update(detail_data)
                time.sleep(delay)
            except Exception as exc:
                logging.error(f"记录 {record['ID']} 详情爬取异常: {exc}")


def export_to_excel(records: List[Dict], filename: str = "companies_data.xlsx"):
    """
    将记录导出到Excel
    """
    if not records:
        logging.warning("没有记录可导出")
        print("没有记录可导出")
        return

    df = pd.DataFrame(records)
    df.to_excel(filename, index=False, engine='openpyxl')
    logging.info(f"导出{len(records)}条记录到{filename}")
    print(f"导出{len(records)}条记录到{filename}")


# 示例用法
if __name__ == "__main__":
    # 安装所需依赖:
    # pip install selenium pandas openpyxl beautifulsoup4 fake-useragent

    # 配置 ChromeDriver 路径（如果不在PATH中）
    # webdriver.Chrome(executable_path='/path/to/chromedriver')

    # 配置代理（可选，例如 'http://your_proxy_ip:port'）
    PROXY = None  # 或 'http://123.45.67.89:8080'

    START_PAGE = 1
    NUM_PAGES = 5
    THREADS = 3  # 减少线程数，避免过快请求
    OUTPUT_FILE = "active_companies_with_details.xlsx"

    print(f"开始从第{START_PAGE}页爬取{NUM_PAGES}页列表，使用{THREADS}个线程（Selenium模式）...")
    records = scrape_multiple_pages(START_PAGE, NUM_PAGES, max_workers=THREADS, proxy=PROXY)

    print("开始爬取详情页...")
    scrape_details(records, max_workers=THREADS, proxy=PROXY)

    export_to_excel(records, OUTPUT_FILE)
    print("爬取完成！")