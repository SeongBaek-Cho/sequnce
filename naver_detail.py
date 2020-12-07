# -*- encoding: utf-8 -*-
import sys
import time
from container import naver_detail_connector # /GenqCrawler/container/connector.py
from bs4 import BeautifulSoup
import requests

def abstarct_parser(abstarct) :
    return " ".join(abstarct.split())

naver_connector = naver_detail_connector
lists = naver_connector.paper_query_list(1000)
naver_connector.wait_query_add(lists)
# for idx in range(len(lists)) :
#     conn.query_update_reset(lists[idx][0],lists[idx][2])
error_count = 0
for idx in range(len(lists)) :
    if error_count > 4 :
        naver_connector.query_update_reset(lists[idx][0],lists[idx][2])
        continue
    try :
        items = {'paper_id':lists[idx][0],'job_url':lists[idx][1],'status':lists[idx][2],'title':'','author':'','reference_text':'','reference_url':'','reference_year':'','reference_page':'','doi':'','doi_url':'','abstract':''}
        print(items['paper_id'] , items['job_url'], items['status'])
        req = requests.get(items['job_url'])
        time.sleep(5)
        soup_html = BeautifulSoup(req.text, 'html.parser')
        # Error Check
        try :
            error_text = soup_html.find('strong',class_='ui_errorview_tit').text
            if '서비스가 종료된 자료입니다' in error_text :
                naver_connector.paper_service_exit(items['paper_id'])
                continue
            error_text = soup_html.find('strong','ui_errorview_tit').text
            if '페이지를 표시할 수 없습니다' in error_text :
                naver_connector.query_update_reset(items['paper_id'],items['status'])
                continue
        except Exception as e :
            print(items['paper_id']," not Error")
        # Title, Author, Reference, DOI scraping
        items['title'] = soup_html.find('h4',id="articleData").text
        ul_list = soup_html.find('dl',class_='ui_listdetail_list')
        dt_list = ul_list.find_all('dt','ui_listdetail_item_tit')
        dd_list = ul_list.find_all('dd','ui_listdetail_item_info')
        for e_idx in range(len(dt_list)) :
            tit = dt_list[e_idx].text
            if '저자' in tit :
                try :
                    items['author'] = dd_list[e_idx].text
                except Exception as e :
                    print('저자 Excpetion :',e)
                    continue
            elif '학술지정보' in tit :
                try :
                    dd_a = dd_list[e_idx].select('ul > li.ui_listdetail_box_item > a.ui_listdetail_txt')[0]
                    dd_b = dd_list[e_idx].select('ul > li.ui_listdetail_box_item > div#journal_year > div > input#select_filed')[0]
                    dd_c = dd_list[e_idx].select('ul > li.ui_listdetail_box_item > div#journal_issue_vol > div > input#select_filed')[0]
                    items['reference_text'] = dd_a.text
                    items['reference_url'] = 'https://academic.naver.com' + dd_a['href']
                    items['reference_year'] = dd_b['value']
                    items['reference_page'] = dd_c['value']
                except Exception as e :
                    print("학술지정보 Exception :",e)
                    continue
            elif 'DOI' in tit :
                try :
                    dd_a = dd_list[e_idx].select('a')[0]
                    items['doi'] = dd_a.text
                    items['doi_url'] = dd_a['href']
                except Exception as e :
                    print('DOI Exception :',e)
                    continue
        # abstract scraping
        abstract_div = soup_html.select('div#div_abstract')
        for e_idx in range(len(abstract_div)) :
            if not None in abstract_div[e_idx].select("h5.ui_enddetail_tit")[0] :
                h5_tit = abstract_div[e_idx].select("h5.ui_enddetail_tit")[0].text
                if '초록' in h5_tit :
                    if not None in abstract_div[e_idx].select("p.ui_enddetail_txt")[0] :
                        items['abstract'] = abstract_div[e_idx].select("p.ui_enddetail_txt")[0].text
                        if items['abstract'] :
                            items['abstract'] = abstarct_parser(items['abstract'])
        naver_connector.paper_data_update(items)
    except Exception as d :
        print("Throw Exception ",d)
        error_count+=1
        naver_connector.paper_data_error(items['paper_id'])
        continue