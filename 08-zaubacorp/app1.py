import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict
from fake_useragent import UserAgent
import logging
import re
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
from openpyxl import load_workbook

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


def get_proxy_list() -> List[str]:
    """
    返回代理池（需自行配置）
    - 返回值：包含代理地址的列表，如 ['http://proxy1:port', 'http://proxy2:port']
    - 说明：代理用于绕过IP封禁。建议使用付费代理（如BrightData、Oxylabs）以确保稳定性。
    - 注意：若无代理，列表包含None以禁用代理功能。免费代理可能不稳定。
    """
    return [
        # 'http://proxy1:port',  # 示例：替换为实际代理地址
        # 'http://proxy2:port',
        None  # 无代理占位符
    ]


def setup_selenium_options(proxy: str = None) -> Options:
    """设置Selenium选项"""
    options = Options()
    options.add_argument(f"user-agent={get_random_user_agent()}")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    return options


def scrape_page(page_num: int, base_url: str = "https://www.zaubacorp.com", retries: int = 3, proxy: str = None) -> \
List[Dict]:
    """
    爬取单页列表，优先使用requests，失败则用Selenium
    """
    url = f"{base_url}/companies-list/status-Active/p-{page_num}-company.html"
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }
    cookies = {}
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    records = []

    # 尝试使用requests
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, cookies=cookies, proxies=proxies, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            if "captcha" in response.text.lower() or "access denied" in response.text.lower():
                logging.warning(f"第{page_num}页（requests）检测到CAPTCHA或访问被拒绝")
                break

            table = soup.find('table')
            if not table:
                logging.warning(f"第{page_num}页（requests）未找到表格")
                break

            rows = table.find_all('tr')[1:]
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

            logging.info(f"第{page_num}页（requests）爬取到{len(records)}条记录")
            return records

        except requests.RequestException as e:
            logging.error(f"第{page_num}页（requests）第{attempt + 1}次尝试失败: {e}")
            if attempt == retries - 1:
                break
            time.sleep(2 ** attempt)

    # 如果requests失败，尝试Selenium
    logging.info(f"第{page_num}页切换到Selenium模式")
    for attempt in range(retries):
        driver = None
        try:
            options = setup_selenium_options(proxy)
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            if "captcha" in driver.page_source.lower() or "access denied" in driver.page_source.lower():
                logging.warning(f"第{page_num}页（Selenium）检测到CAPTCHA或访问被拒绝")
                return records

            table = soup.find('table')
            if not table:
                logging.warning(f"第{page_num}页（Selenium）未找到表格")
                return records

            rows = table.find_all('tr')[1:]
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

            logging.info(f"第{page_num}页（Selenium）爬取到{len(records)}条记录")
            return records

        except Exception as e:
            logging.error(f"第{page_num}页（Selenium）第{attempt + 1}次尝试失败: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return records

        finally:
            if driver:
                driver.quit()


def scrape_detail(record: Dict, retries: int = 3, proxy: str = None) -> Dict:
    """
    爬取公司详情页，优先使用requests，失败则用Selenium
    优化：改进Contact Details解析，添加调试信息
    """
    company_id = record['ID']
    company_name = record['公司名称'].replace(' ', '-').upper()
    detail_url = f"https://www.zaubacorp.com/{company_name}-{company_id}"
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
    }
    cookies = {}
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    detail_data = {}

    # 尝试使用requests
    for attempt in range(retries):
        try:
            response = requests.get(detail_url, headers=headers, cookies=cookies, proxies=proxies, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            if "captcha" in response.text.lower() or "access denied" in response.text.lower():
                logging.warning(f"详情页 {detail_url}（requests）检测到CAPTCHA或访问被拒绝")
                break

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
            else:
                logging.warning(f"详情页 {detail_url}（requests）未找到Basic Information表格")

            # 优化Contact Details解析
            contact_section = soup.find(string=re.compile("Contact Details", re.I))
            if contact_section:
                # 查找后续的p、div或任何包含Email的元素
                contact_elem = contact_section.find_next(['p', 'div', 'span'])
                if contact_elem:
                    contact_text = contact_elem.get_text(strip=True)
                    # 更宽松的正则，匹配Email ID
                    email_match = re.search(r'(?:Email ID|Email|E-mail)\s*[:=]?\s*([\w\.-]+@[\w\.-]+)', contact_text,
                                            re.I)
                    website_match = re.search(r'(?:Website|Web)\s*[:=]?\s*(\S+)', contact_text, re.I)
                    if email_match:
                        detail_data['Email'] = email_match.group(1)
                        logging.info(f"详情页 {detail_url}（requests）提取Email: {detail_data['Email']}")
                    else:
                        detail_data['Email'] = 'Not Found'
                        logging.warning(f"详情页 {detail_url}（requests）未找到Email ID")
                    detail_data['Website'] = website_match.group(1) if website_match else 'Not Available'
                else:
                    detail_data['Email'] = 'Not Found'
                    detail_data['Website'] = 'Not Available'
                    logging.warning(f"详情页 {detail_url}（requests）未找到Contact Details内容")
            else:
                detail_data['Email'] = 'Not Found'
                detail_data['Website'] = 'Not Available'
                logging.warning(f"详情页 {detail_url}（requests）未找到Contact Details部分")

            logging.info(f"详情页 {detail_url}（requests）提取成功")
            return detail_data

        except requests.RequestException as e:
            logging.error(f"详情页 {detail_url}（requests）第{attempt + 1}次尝试失败: {e}")
            if attempt == retries - 1:
                break
            time.sleep(2 ** attempt)

    # 如果requests失败，尝试Selenium
    logging.info(f"详情页 {detail_url} 切换到Selenium模式")
    for attempt in range(retries):
        driver = None
        try:
            options = setup_selenium_options(proxy)
            driver = webdriver.Chrome(options=options)
            driver.get(detail_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            if "captcha" in driver.page_source.lower() or "access denied" in driver.page_source.lower():
                logging.warning(f"详情页 {detail_url}（Selenium）检测到CAPTCHA或访问被拒绝")
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
            else:
                logging.warning(f"详情页 {detail_url}（Selenium）未找到Basic Information表格")

            # 优化Contact Details解析
            contact_section = soup.find(string=re.compile("Contact Details", re.I))
            if contact_section:
                contact_elem = contact_section.find_next(['p', 'div', 'span'])
                if contact_elem:
                    contact_text = contact_elem.get_text(strip=True)
                    email_match = re.search(r'(?:Email ID|Email|E-mail)\s*[:=]?\s*([\w\.-]+@[\w\.-]+)', contact_text,
                                            re.I)
                    website_match = re.search(r'(?:Website|Web)\s*[:=]?\s*(\S+)', contact_text, re.I)
                    if email_match:
                        detail_data['Email'] = email_match.group(1)
                        logging.info(f"详情页 {detail_url}（Selenium）提取Email: {detail_data['Email']}")
                    else:
                        detail_data['Email'] = 'Not Found'
                        logging.warning(f"详情页 {detail_url}（Selenium）未找到Email ID")
                    detail_data['Website'] = website_match.group(1) if website_match else 'Not Available'
                else:
                    detail_data['Email'] = 'Not Found'
                    detail_data['Website'] = 'Not Available'
                    logging.warning(f"详情页 {detail_url}（Selenium）未找到Contact Details内容")
            else:
                detail_data['Email'] = 'Not Found'
                detail_data['Website'] = 'Not Available'
                logging.warning(f"详情页 {detail_url}（Selenium）未找到Contact Details部分")

            logging.info(f"详情页 {detail_url}（Selenium）提取成功")
            return detail_data

        except Exception as e:
            logging.error(f"详情页 {detail_url}（Selenium）第{attempt + 1}次尝试失败: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return detail_data

        finally:
            if driver:
                driver.quit()


def save_checkpoint(records: List[Dict], page_num: int, checkpoint_file: str = "checkpoint.json"):
    """保存检查点"""
    checkpoint_data = {
        'page_num': page_num,
        'records': records
    }
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, ensure_ascii=False)
    logging.info(f"保存检查点到 {checkpoint_file}，当前页: {page_num}")


def load_checkpoint(checkpoint_file: str = "checkpoint.json") -> tuple[List[Dict], int]:
    """加载检查点"""
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        logging.info(f"从 {checkpoint_file} 加载检查点，恢复到页 {checkpoint_data['page_num']}")
        return checkpoint_data['records'], checkpoint_data['page_num']
    return [], 0


def append_to_excel(records: List[Dict], filename: str):
    """增量追加记录到Excel"""
    if not records:
        logging.info(f"无记录可追加到 {filename}")
        return

    df = pd.DataFrame(records)
    if os.path.exists(filename):
        book = load_workbook(filename)
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            writer.book = book
            startrow = book.active.max_row
            df.to_excel(writer, index=False, startrow=startrow, header=False if startrow > 1 else True)
    else:
        df.to_excel(filename, index=False, engine='openpyxl')

    logging.info(f"追加{len(records)}条记录到 {filename}")


def scrape_multiple_pages(start_page: int, num_pages: int, max_workers: int = 3, delay: float = 2.0,
                          proxy_list: List[str] = None, checkpoint_file: str = "checkpoint.json",
                          filename_prefix: str = "companies_data") -> List[Dict]:
    """
    使用多线程爬取多页列表，增量保存
    """
    all_records = []
    proxy_list = proxy_list or [None]
    proxy_index = 0

    checkpoint_records, last_page = load_checkpoint(checkpoint_file)
    all_records.extend(checkpoint_records)
    start_page = max(start_page, last_page + 1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xlsx"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_page = {
            executor.submit(scrape_page, page, proxy=proxy_list[proxy_index % len(proxy_list)]): page
            for page in range(start_page, start_page + num_pages)
        }

        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                records = future.result()
                if records:
                    scrape_details(records, max_workers=max_workers, delay=delay,
                                   proxy=proxy_list[proxy_index % len(proxy_list)])
                    append_to_excel(records, filename)
                    all_records.extend(records)
                    save_checkpoint(all_records, page, checkpoint_file)
                proxy_index += 1
                time.sleep(delay)
            except Exception as exc:
                logging.error(f"第{page}页发生异常: {exc}")

    return all_records


def scrape_details(records: List[Dict], max_workers: int = 3, delay: float = 2.0, proxy: str = None) -> None:
    """
    使用多线程爬取所有记录的详情页
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_record = {
            executor.submit(scrape_detail, record, proxy=proxy): record
            for record in records
        }

        for future in as_completed(future_to_record):
            record = future_to_record[future]
            try:
                detail_data = future.result()
                record.update(detail_data)
                time.sleep(delay)
            except Exception as exc:
                logging.error(f"记录 {record['ID']} 详情爬取异常: {exc}")


# 示例用法
if __name__ == "__main__":
    # 安装所需依赖:
    # pip install requests selenium pandas openpyxl beautifulsoup4 fake-useragent

    # 配置 ChromeDriver 路径（如果不在PATH中）
    # webdriver.Chrome(executable_path='/path/to/chromedriver')

    # 配置参数
    START_PAGE = 1
    """
    开始页码
    - 作用：指定从第几页开始爬取（网站共约58,113页）。
    - 默认值：1（从第一页开始）。
    - 注意：如果存在检查点文件（checkpoint.json），会自动从最后爬取的页面继续。
    - 建议：测试时设为1，大规模爬取可根据需要调整。
    """

    NUM_PAGES = 1
    """
    要爬取的页面数量
    - 作用：控制爬取的总页数（每页约30条记录）。
    - 默认值：5（测试用，约150条记录）。
    - 注意：58,113页总计约174万条记录，建议分批爬取（如每批500页）。
    - 建议：小批量测试设为1-10，大规模爬取需配合代理和检查点。
    """

    THREADS = 3
    """
    线程数
    - 作用：控制并行爬取的线程数量（列表页和详情页均适用）。
    - 默认值：3（平衡性能和稳定性）。
    - 注意：Selenium耗资源，线程过多可能导致内存/CPU瓶颈。建议3-5，视机器性能调整。
    - 建议：低配机器设为1-2，高配机器可增至5-10，配合代理避免封禁。
    """

    OUTPUT_FILE_PREFIX = "active_companies_with_details"
    """
    输出Excel文件名前缀
    - 作用：指定生成Excel文件名的前缀，自动附加时间戳（格式：prefix_YYYYMMDD_HHMMSS.xlsx）。
    - 默认值：active_companies_with_details
    - 示例：active_companies_with_details_20250923_161530.xlsx
    - 注意：确保文件名合法，避免包含特殊字符。
    """

    PROXY_LIST = get_proxy_list()
    """
    代理列表
    - 作用：提供代理地址列表，循环使用以绕过IP封禁。
    - 默认值：调用get_proxy_list()，默认包含None（无代理）。
    - 注意：需在get_proxy_list()中配置有效代理（如BrightData、Oxylabs）。免费代理可能不稳定。
    - 建议：测试时可设为[None]，生产环境配置多个高质量代理。
    """

    CHECKPOINT_FILE = "checkpoint.json"
    """
    检查点文件名
    - 作用：保存已爬取的记录和页码，中断后可恢复。
    - 默认值：checkpoint.json
    - 注意：文件存储在脚本运行目录，记录所有数据和最后页码。建议定期备份。
    - 建议：保持默认值，或按任务命名（如checkpoint_20250923.json）。
    """

    print(f"开始从第{START_PAGE}页爬取{NUM_PAGES}页列表，使用{THREADS}个线程...")
    records = scrape_multiple_pages(
        START_PAGE,
        NUM_PAGES,
        max_workers=THREADS,
        proxy_list=PROXY_LIST,
        checkpoint_file=CHECKPOINT_FILE,
        filename_prefix=OUTPUT_FILE_PREFIX
    )
    print("爬取完成！")