import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from time import sleep
import threading
from queue import Queue
import re
import ast
import pickle

class func:
    def __init__(self):
        pass

    @staticmethod
    def get_elem(driver, elem, full_info_elem = None, elem_type = ''):
        if elem_type == 'prod_link':
            pl = driver.find_elements(By.CSS_SELECTOR, elem)
            output = [i.get_attribute('href') for i in pl]
        elif elem_type == 'cate':
            cate = driver.find_elements(By.CSS_SELECTOR, elem)
            output = [i.text for i in cate]
        elif elem_type == 'img':
            img_elem = driver.find_element(By.CSS_SELECTOR, elem)
            output = img_elem.find_element(By.TAG_NAME, 'img').get_attribute('srcset').split(' ')[0]
        elif elem_type == 'discount' or elem_type == 'price' or elem_type == 'sale_q' or elem_type == 'rating':
            output = driver.find_element(By.CSS_SELECTOR, elem).text
        elif elem_type == 'info_elems':
            info_elems = driver.find_elements(By.CSS_SELECTOR, elem)
            title_elem, detail_info_elem, describe_elem = full_info_elem[0], full_info_elem[1], full_info_elem[2]
            for i in info_elems:
                info, describe, seller, seller_star, seller_reviews_quantity, seller_follow = None, None, None, None, None, None
                try:
                    title = i.find_element(By.CSS_SELECTOR, title_elem)
                    title = title.text
                except:
                    title = None
                if title == 'Thông tin chi tiết':
                    try:
                        info_row = i.find_elements(By.CSS_SELECTOR, detail_info_elem)
                        info = [i.text.split('\n') for i in info_row]
                    except Exception as e:
                        print(f'info except: {threading.current_thread().name} - {type(e).__name__}')
                        info = None
                        print('detail_info nan')
                elif title == 'Mô tả sản phẩm':
                    try:
                        describe = i.find_element(By.CSS_SELECTOR, describe_elem).text
                    except Exception as e:
                        print(f'describe except: {threading.current_thread().name} - {type(e).__name__}')
                        describe = None
                        print('describe nan')
                elif title == 'Thông tin nhà bán':
                    try:
                        seller = i.find_element(By.CSS_SELECTOR, '.seller-name').text.split(' ')[0]
                    except Exception as e:
                        print(f'seller except: {threading.current_thread().name} - {type(e).__name__}')
                        seller = None
                        print('seller nan')
                    try:
                        seller_evaluation_elems = i.find_element(By.CSS_SELECTOR, '.item.review')
                    except Exception as e:
                        print(f'seller eval except: {threading.current_thread().name} - {type(e).__name__}')
                        seller_evaluation_elems = None
                        print('seller_evaluation nan')
                    try:
                        seller_star = seller_evaluation_elems.find_element(By.CSS_SELECTOR, '.title').text
                    except Exception as e:
                        print(f'seller star except: {threading.current_thread().name} - {type(e).__name__}')
                        seller_star = None
                        print('seller_star nan')
                    try:
                        seller_reviews_quantity = seller_evaluation_elems.find_element(By.CSS_SELECTOR, '.sub-title').text
                    except Exception as e:
                        print(f'seller review except: {threading.current_thread().name} - {type(e).__name__}')
                        seller_reviews_quantity = None
                        print('seller_reviews_quantity nan') 
                    try:
                        seller_follow = i.find_element(By.CSS_SELECTOR, '.item.normal .title').text
                    except Exception as e:
                        print(f'seller follow except: {threading.current_thread().name} - {type(e).__name__}')
                        seller_follow = None
                        print('seller_follow nan')
            output = (info, describe, seller, seller_star, seller_reviews_quantity, seller_follow)
        else:
            print('no output')
        return output
    
    @staticmethod
    def wait(driver, time, elem):
        wait = WebDriverWait(driver, time)
        elem_to_wait = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, elem)))
        return elem_to_wait
    
    @staticmethod
    def scroll(driver, scroll_iters = 10, scroll_amount = 300, scroll_interval = 0.2):
        try:
            for _ in range(scroll_iters):
                driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_amount)
                sleep(scroll_interval)
        except Exception as e:
            print(f'scroll except: {threading.current_thread().name} - {type(e).__name__}')
            sleep(10)
            func.scroll(driver, scroll_iters = 10, scroll_amount = 300, scroll_interval = 0.2)
            print(f'Try to re-scroll sucessfully')


    @staticmethod
    def load_multi_page(driver, n, link = str):
        driver.maximize_window()
        link = f'{link}?page={n}'
        driver.get(link)
        sleep(3)
    @staticmethod
    def get_data(driver, que,
                prod_link_elem, category_bar_elem, image_elem, 
                price_elem, discount_elem,
                sales_quantity_elem, rating_elem, 
                info_elem, detail_info_elem, 
                describe_elem,
                extend_page_elem,
                title_elem,
                preventive_prod_link_elem):   
             
        func.scroll(driver, 15)
        try:
            func.wait(driver, 30, prod_link_elem)
            pl = func.get_elem(driver, prod_link_elem, elem_type = 'prod_link')
            print(f'{threading.current_thread().name} - Take Product links succesfully')
        except Exception as e:
            print(f'{threading.current_thread().name} - First Product link not exist')
            try:
                func.wait(driver, 30, preventive_prod_link_elem)
                pl = func.get_elem(driver, preventive_prod_link_elem, elem_type = 'prod_link')
                print(f'{threading.current_thread().name} - Take prevent Product link succesfully')
            except Exception as e:
                print(f'{threading.current_thread().name} - Prevent Product link not exist also')
                pl = []
        page_features = []
        for i, prod_link in enumerate(pl):
            try:
                driver.get(prod_link)
            except:
                print(f'{threading.current_thread().name} get prod_link unsuccessful. Try to get again ...')
                try:
                    driver.get(prod_link)
                    print(f'{threading.current_thread().name} Try to get again successfully')
                except:
                    print(f'{threading.current_thread().name} Cant get prod_link, get next link')
                    driver.get(pl[i + 1])
                    print(f'{threading.current_thread().name} Get next link successfully')
                    
            sleep(2)
            driver.maximize_window()

            #expandpage
            func.scroll(driver, 15, 300, 0.2)
            try:
                elem_to_wait = func.wait(driver, 10, extend_page_elem)
                elem_to_wait.click()
            except ElementClickInterceptedException:
                print(f'click except: {threading.current_thread().name}')
                try:
                    func.scroll(driver, 2)
                    elem_to_wait.click()
                except Exception as e:
                    print(f'Cant not click: {threading.current_thread().name} - {type(e).__name__}')
            except TimeoutException:
                print(f'Expand page not exist')
            #cate
            try:
                func.wait(driver, 2, category_bar_elem)
                cate = func.get_elem(driver, category_bar_elem, elem_type = 'cate')
            except Exception as e:
                print(f'cate except: {threading.current_thread().name} - {type(e).__name__}')
                cate = None
                print('cate nan')
            #img
            try:
                func.wait(driver, 2, image_elem)
                img = func.get_elem(driver, image_elem, elem_type = 'img')
            except Exception as e:
                print(f'img except: {threading.current_thread().name} - {type(e).__name__}')
                img = None
                print('img nan')
            #price
            try:
                func.wait(driver, 2, price_elem)
                price = func.get_elem(driver, price_elem, elem_type = 'price')
            except Exception as e:
                print(f'price except: {threading.current_thread().name} - {type(e).__name__}')
                price = None
                print('price nan')
            #discount
            try:
                func.wait(driver, 2, discount_elem)
                discount = func.get_elem(driver, discount_elem, elem_type = 'discount')
            except Exception as e:
                print(f'discount except: {threading.current_thread().name} - {type(e).__name__}')
                discount = None
                print('discount nan')
            #rating
            try:
                func.wait(driver, 2, rating_elem)
                rating = func.get_elem(driver, rating_elem, elem_type = 'rating')
            except Exception as e:
                print(f'rating except: {threading.current_thread().name} - {type(e).__name__}')
                rating = None
                print('rating nan')
            #sales quant
            try:
                func.wait(driver, 2, sales_quantity_elem)
                sale_q = func.get_elem(driver, sales_quantity_elem, elem_type = 'sale_q')
            except Exception as e:
                print(f'sale_q except: {threading.current_thread().name} - {type(e).__name__}')
                sale_q = None
                print('sale_q nan')
            #full_info
                
            info, describe, seller, seller_star, seller_reviews_quantity, seller_follow = func.get_elem(driver, 
                                                                                                        info_elem, 
                                                                                                        (title_elem, detail_info_elem, describe_elem), 
                                                                                                        elem_type = 'info_elems')
            features = [prod_link, cate, img, price, discount, sale_q, rating, info, describe, seller, seller_star, seller_reviews_quantity, seller_follow]
            page_features.append(features)
        que.put(page_features)


    @staticmethod
    def wrangling(col, delimiter = None):
        if col.name == 'product_link'\
                or col.name == 'image'\
                    or col.name == 'describe'\
                        or col.name == 'seller'\
                            or col.name == 'seller_star':
            result = col

        elif col.name == 'category':
            if isinstance(col[0], str):
                col = [ast.literal_eval(i) for i in col]
                col = [i[0].split(delimiter) for i in col]
            else:
                col = [i[0].split(delimiter) for i in col]
            name = [i[-1] for i in col]
            detail_cate = [i[-2] for i in col]
            large_cate = [i[-3] for i in col]
            result = pd.DataFrame({'name': name, 'detail_cate': detail_cate, 'large_cate': large_cate})

        elif col.name == 'price':
            result = col.apply(lambda x: int(re.sub(r'[^0-9]', '', x) if isinstance(x, str) else x))

        elif col.name == 'discount':
            result = pd.Series([float(i.replace('%', ''))/ 100 if isinstance(i, str) else i for i in col], name = col.name)

        elif col.name == 'sale_quantity':
            result = col.apply(lambda x: float(re.sub(r'[^0-9]', '', x) if not pd.isna(x) else None))

        elif col.name == 'rating':
            rating_star = []
            rating_quantity = []
            for i in col:
                if not isinstance(i, float):
                    rs, rq = i.split(delimiter)
                    rs = float(re.sub(r'[^0-9]', '', rs)) / 10
                    rq = int(re.sub(r'[^0-9]', '', rq))
                rating_star.append(rs)
                rating_quantity.append(rq)
            result = pd.DataFrame({'rating_star': rating_star, 'rating_quantity': rating_quantity})

        elif col.name == 'info':
            if isinstance(col[0], str):
                col = [ast.literal_eval(i) if isinstance(i, str) else i for i in col]
            else:
                col = col
            col_name = [v[0] for i in col for v in i]
            col_name = set(col_name)
            di = {i: [] for i in col_name}
            for i in col:
                info_i = []
                for v in i:
                    info_i.append(v[0])
                lack = [i for i in di.keys() if i not in info_i]
                for l in lack:
                    i.append([l, None])
            for i in col:
                for v in i:
                    try:
                        di[v[0]].append(v[1])
                    except:
                        di[v[0]].append(None)

            result = pd.DataFrame(di)

        elif col.name == 'seller_reviews_quantity' or col.name == 'seller_follow':
            result = []
            for i in col:
                try:
                    cleaned_str = re.sub(r'[^\d.ktr]', '', i)
                    cleaned_str = cleaned_str.replace('k', '000').replace('tr', '000000')
                    i = float(cleaned_str)
                except:
                    i = None
                result.append(i)
            result = pd.Series(result, name = col.name)

        return result.reset_index(drop = True)


class TikiCrawler(func):
    def __init__(self, root_link, n_browers, 
                 prod_link_elem, category_bar_elem, image_elem, 
                 price_elem, discount_elem,
                 sales_quantity_elem, rating_elem, 
                 info_elem, detail_info_elem, 
                 describe_elem,
                 extend_page_elem,
                 title_elem,
                 preventive_prod_link_elem,
                 all_data = None,
                 wrangled_data = None):
        self.root_link = root_link
        self.n_browers = n_browers
        self.idx_page = [i for i in range(1, n_browers + 1)]
        self.que = Queue()
        self.prod_link_elem = prod_link_elem
        self.preventive_prod_link_elem = preventive_prod_link_elem
        self.category_bar_elem = category_bar_elem
        self.image_elem = image_elem
        self.price_elem = price_elem
        self.discount_elem = discount_elem
        self.sales_quantity_elem = sales_quantity_elem
        self.rating_elem = rating_elem
        self.info_elem = info_elem
        self.detail_info_elem = detail_info_elem
        self.describe_elem = describe_elem
        self.extend_page_elem = extend_page_elem
        self.title_elem = title_elem
        self.all_data = all_data
        self.wrangled_data = wrangled_data
    
    def open_drivers(self):
        self.drivers = [webdriver.Chrome() for _ in range(self.n_browers)]

    def load_multi_browers(self):
        for driver, page in zip(self.drivers, self.idx_page):
            t = threading.Thread(target = func.load_multi_page, args = (driver, page, self.root_link))
            t.start()

    def run(self):
        threads = []
        for driver in self.drivers:
            print('--Running--')
            t = threading.Thread(target = func.get_data, 
                                 args = (driver, self.que, self.prod_link_elem, 
                                         self.category_bar_elem, self.image_elem, 
                                         self.price_elem, self.discount_elem,
                                         self.sales_quantity_elem, self.rating_elem, 
                                         self.info_elem, self.detail_info_elem, 
                                         self.describe_elem, self.extend_page_elem,
                                         self.title_elem, self.preventive_prod_link_elem))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        results = []
        while not self.que.empty():
            results.extend(self.que.get())
        return results
    
    def crawl_multipage(self, page_crawl = 3):
        self.all_data = pd.DataFrame()
        while self.idx_page[0] < page_crawl:
            self.load_multi_browers()
            sleep(5)
            all_features = self.run()
            page_df = pd.DataFrame(
                all_features,
                columns = ['product_link', 'category', 'image', 'price', 
                           'discount', 'sale_quantity', 'rating', 
                           'info', 
                           'describe', 'seller', 'seller_star', 
                           'seller_reviews_quantity', 'seller_follow']
            )
            self.all_data = pd.concat([self.all_data, page_df], axis = 0)
            self.idx_page = [i + self.n_browers for i in self.idx_page]
        
    def wrangling_data(self, delimiter = None):
        data = []
        for col in self.all_data.columns:
            part = func.wrangling(self.all_data[col], delimiter)
            data.append(part)
        self.wrangled_data = pd.concat(data, axis = 1)

    def sub_crawler(self, sub_link_elem, preventive_sub_link_elem):
        temp_drive = webdriver.Chrome()
        temp_drive.get(self.root_link)
        try:
            func.wait(temp_drive, 10, sub_link_elem)
            sub_link_elem = temp_drive.find_elements(By.CSS_SELECTOR, sub_link_elem)
        except:
            func.wait(temp_drive, 10, preventive_sub_link_elem)
            sub_link_elem = temp_drive.find_elements(By.CSS_SELECTOR, preventive_sub_link_elem)
        info = [(i.text, i.get_attribute('href')) for i in sub_link_elem]
        sub_crawler = {}
        for name, link in info:
            sub_crawler[name] = TikiCrawler(
                link,
                self.n_browers,
                self.prod_link_elem, 
                self.category_bar_elem, self.image_elem, 
                self.price_elem, self.discount_elem,
                self.sales_quantity_elem, self.rating_elem, 
                self.info_elem, self.detail_info_elem, 
                self.describe_elem, self.extend_page_elem,
                self.title_elem, self.preventive_prod_link_elem
            )
        temp_drive.close()
        return sub_crawler
    
    def close(self):
        for driver in self.drivers:
            driver.close()


    def save(self, pickle_file_path):
        save_dict = {k: v  for k, v in self.__dict__.items() if k not in ['que', 'drivers', 'idx_page']}
        with open(pickle_file_path, 'wb') as file:
            pickle.dump(save_dict, file)

    @classmethod
    def load(cls, pickle_file_path):
        with open(pickle_file_path, 'rb') as file:
            data_dict = pickle.load(file)
        return cls(**data_dict)
