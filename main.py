from base import *


# from config.chengjiaogonggao import *
from result.hainan.caigougonggao import *





logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler('new_spider.log', encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

task_params = {
    "task_id": "123456789987654321",
    "parent_task_id": "",
    "task_level": 1,
    "task_type": "list",
    "node_ip": "127.0.0.1",
    "crawler_type": "",
    "page_id": "123",
    "org_name": "",
    "review_name": "",
    "county_code": "",
    "addr_id": "",
    "org_id": "",
    "url": entrance_url,
    "file_level": "1",
    "begin_date": "",
    "is_full": 1,
    "current_page": -1,
    "is_turn": 1,
    "configure": configure,
    "entrance_url": entrance_url,
}

spider = NewCommonSpider(logger=logger)
spider_result = spider.run(task_params)
print(spider_result)
print(spider_result.get('task_status'))
if spider_result.get('task_status') == "FAILED":
    sys.exit(1)
time.sleep(3)
# for item in spider_result.get('payload', {}).get('data', {}).get('url_info', [])[::3]:
for item in spider_result.get('payload', {}).get('data', {}).get('url_info', []):
    entrance_url = item.get('entrance_url')
    task_params = {
        "task_id": "1234567899833337654321",
        "parent_task_id": spider_result.get('task_id'),
        "task_level": 1,
        "task_type": "detail",
        "node_ip": "127.0.0.1",
        "crawler_type": "",
        "page_id": "123",
        "org_name": "",
        "review_name": "",
        "county_code": "",
        "begin_date": item.get('publish_time'),
        'extra_info': json.dumps({k: v for k, v in item.items() if k not in ['url', 'entrance_url', 'trace_index']}),
        "addr_id": "",
        "org_id": "",
        "url": entrance_url,
        "configure": configure,
        "entrance_url": entrance_url,
    }
    detail_spider_result = spider.run(task_params)
    print(detail_spider_result)
    print(detail_spider_result.get('task_status'))
    if detail_spider_result.get('task_status') == "FAILED":
        sys.exit(1)
    time.sleep(3)

# exit()
# if len(spider_result.get('payload', {}).get('data', {}).get('sub_info', [])) >= 2:
if len(spider_result.get('payload', {}).get('data', {}).get('sub_info', [])) >= 1:
    sub_list = spider_result.get('payload', {}).get('data', {}).get('sub_info', [])
    middle_final_list = [sub_list[int((len(sub_list) - 1) / 2)], sub_list[len(sub_list) - 1]]
    for sub_list_item in middle_final_list:
        entrance_url = sub_list_item.get('entrance_url')
        task_params = {
            "task_id": "123456789987654321",
            "parent_task_id": "",
            "task_level": 1,
            "task_type": "list",
            "node_ip": "127.0.0.1",
            "crawler_type": "",
            "page_id": "123",
            "org_name": "",
            "review_name": "",
            "county_code": "",
            "addr_id": "",
            "org_id": "",
            "url": entrance_url,
            "file_level": "1",
            "begin_date": "",
            "is_full": 0,
            "current_page": int(sub_list_item.get("current_page", -1)),
            "is_turn": 1,
            "configure": configure,
            "entrance_url": entrance_url,
        }
        sub_spider_result = spider.run(task_params)
        print(sub_spider_result)
        print(sub_spider_result.get('task_status'))
        if sub_spider_result.get('task_status') == "FAILED":
            sys.exit(1)
        time.sleep(3)
        for item in sub_spider_result.get('payload', {}).get('data', {}).get('url_info', [])[::3]:
        # for item in sub_spider_result.get('payload', {}).get('data', {}).get('url_info', []):
            entrance_url = item.get('entrance_url')
            task_params = {
                "task_id": "1234567899833337654321",
                "parent_task_id": sub_spider_result.get('task_id'),
                "task_level": 1,
                "task_type": "detail",
                "node_ip": "127.0.0.1",
                "crawler_type": "",
                "page_id": "123",
                "org_name": "",
                "review_name": "",
                "county_code": "",
                "begin_date": item.get('publish_time'),
                'extra_info': json.dumps(
                    {k: v for k, v in item.items() if k not in ['url', 'entrance_url', 'trace_index']}),
                "addr_id": "",
                "org_id": "",
                "url": entrance_url,
                "configure": configure,
                "entrance_url": entrance_url,
            }
            sub_detail_spider_result = spider.run(task_params)
            print(sub_detail_spider_result)
            print(sub_detail_spider_result.get('task_status'))
            if sub_detail_spider_result.get('task_status') == "FAILED":
                sys.exit(1)
            time.sleep(3)

print(json.dumps(configure, ensure_ascii=False))
