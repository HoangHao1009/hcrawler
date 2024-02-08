# hcrawler
Crawl Tiki web data using selenium
A easy-used tool to crawl data from Tiki - you just need put a link of category you'd like to crawl.

### Library installation

```python
git clone https://github.com/HoangHao1009/hcrawler
cd hcrawler
pip install -e .
```

### Usage

#### 1. Set parameters for crawler
```python
from hcrawler import module

#category link crawler'll take
#example for book, it may be large category: dien-thoai-may-tinh-bang, thoi-trang-nu, ...
#or small category: sach-van-hoc, sach-kinh-te,..
root_link = 'https://tiki.vn/sach-truyen-tieng-viet/c316' 
#Numbers of chrome drivers will open for crawl
n_browers = 5
#CSS SELECTOR for elements (those behind are collected in Feb-4-2024)
prod_link_elem = '.style__ProductLink-sc-1axza32-2.ezgRFw.product-item'
category_bar_elem = '.breadcrumb'
image_elem = '.image-frame'
price_elem = '.product-price__current-price'
discount_elem = '.product-price__discount-rate'
sales_quantity_elem = '.styles__StyledQuantitySold-sc-1swui9f-3.bExXAB'
rating_elem = '.styles__StyledReview-sc-1swui9f-1.dXPbue'
info_elem = '.WidgetTitle__WidgetContainerStyled-sc-1ikmn8z-0.iHMNqO'
detail_info_elem = '.WidgetTitle__WidgetContentStyled-sc-1ikmn8z-2.jMQTPW'
describe_elem = '.style__Wrapper-sc-13sel60-0.dGqjau.content'
extend_page_elem = '.btn-more'
title_elem = '.WidgetTitle__WidgetTitleStyled-sc-1ikmn8z-1.eaKcuo'
#sub_link_elem will be used for crawl detail category in root_link you put
sub_link_elem = '.styles__TreeItemStyled-sc-1uq9a9i-2.ThXqv a'

#you can put extra preventive CSS elements if prod_link_elem or sub_link_elem isn't valid
preventive_prod_link_elem = '.style__ProductLink-sc-139nb47-2.cKoUly.product-item'
preventive_sub_link_elem = '.item.item--category'
```

#### 2. Initialize crawler

```python
crawler = module.TikiCrawler(root_link, n_browers, 
                             prod_link_elem, category_bar_elem, image_elem, 
                             price_elem, discount_elem,
                             sales_quantity_elem, rating_elem,
                             info_elem, detail_info_elem,
                             describe_elem,
                             extend_page_elem,
                             title_elem, preventive_prod_link_elem)
```

#### 3. Crawling

##### 3.1. If you just want to crawl root_link
```python
crawler.crawl_multipage(50)
#save data you've crawled
crawler.save('Tikibook50crawler.pickle')
```

##### 3.2. If you want to crawl detail category in root_link
```python
#initialize subcrawler: you need to put a Crawler that have already set up
module.SubCrawler.get_crawlers(crawler, sub_link_elem, preventive_sub_link_elem)

#you can take a subcrawler you want in
subcrawlers = module.SubCrawler.crawlers -> a list of subcrawlers
#enter to crawler you want with .name and crawl with .core
#example
for crawler in subcrawlers:
  if crawler.name == 'Sách văn học':
    crawler.core.crawl_multipage(50)
#or you can crawl by all crawlers
module.SubCrawler.super_crawling(50)
```

#### 4. Take data
```python
#If you want to load from .pickle
crawler = module.TikiCrawler.load('file_path.pickle')

#select raw data you crawl in all_data attribute
data = crawler.all_data

#if you'd like to use auto wrangling data
crawler.wrangling_data(delimeter = '\n')
#take it
wrangled_data = crawler.wrangled_data
```

### Notice
- At now, hcrawler just crawl: product link, category, image, price, discount, sale quantity, rating, info, describe, seller, seller_star, seller_reviews_quantity, seller_follow. Another features crawling may be updated in future version.
- The core of hcrawler is selenium, so make sure you've set up Chrome Webdriver which is matched with your current Chrome version to use it.
- Select n_browsers suitable which your device (more browser - more faster but need more stronger device, interner connection, ...).
- If it can't crawl some info (which is print out if nan), check for element CSS_SELECTOR. Which elements I use in example is effective in Feb-4-2024, but it maybe change in future.

