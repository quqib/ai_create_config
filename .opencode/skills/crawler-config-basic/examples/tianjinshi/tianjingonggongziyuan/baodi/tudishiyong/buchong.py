configure = {
    "name": "天津市公共资源交易平台-宝坻区-交易信息-工程建设-补充公告",
    "org_id": "1201895",
    "page_url": "http://180.213.33.140:8081/jyxx.jhtml",
    "host": "180.213.33.140",
    "source_site": "天津市公共资源交易平台",
    "industry": "工程建设",
    "notice_type": "补充公告",
    "list": {
        "mode": "REQUESTS",
        "method": "POST",
        "headers": {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "http://180.213.33.140:8081",
            "Referer": "http://180.213.33.140:8081/jyxx.jhtml",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        },
        "fields": {
            "title": {
                "type": "jsonpath",
                "value": "$.content[*].title",
            },
            "url": {
                "type": "jsonpath",
                "value": "$.content[*].url",
                "prepath": True,
            },
            "entrance_url": {
                "type": "jsonpath",
                "value": "$.content[*].url",
                "prepath": True,
            },
            "publish_time": {
                "type": "jsonpath",
                "value": "$.content[*].releaseTime",
                "istimestamp": True,
                "format": "date"
            }
        },
    },
    "detail": {
        "mode": "REQUESTS",
        "method": "GET",
        "headers": {
            "Accept": "application/json, text/javascript, */*; q=0.01",

            "Content-Type": "application/json;charset=UTF-8",

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",

        },
        "attachment": {
            "enable": True,
            "mode": "REQUESTS",
            "fields": {
                "url": {
                    "type": "xpath",
                    "value": "//a[@href and (contains(@href, 'fileupload') or contains(@href, 'downEnId'))]/@href",
                    "prepath": True,
                    "isnull": True
                },
                "name": {
                    "type": "xpath",
                    "value": "//a[@href and (contains(@href, 'fileupload') or contains(@href, 'downEnId'))]/@href",
                    "isnull": True
                }
            },
            "isverify": False
        },

        "fields": {
            "content": {
                "type": "xpath",
                "value": "//div[@class='detail-body']"
            },
            "title": {
                "type": "xpath",
                "value": "//h1[@class='detail-title']/text()",
                "isnull": True
            },
            "publish_time": {
                "type": "xpath",
                "value": "//p[@class='detail-meta']/textall()",
                "regex": "(?:发布时间|信息时间|发布日期)\\s*[:：]*\\s*(\\d+-\\d+-\\d+)",
                "format": "date",
                "isnull": True
            },
            "project_code": {
                "type": "xpath",
                "value": "//div[@class='detail-body']/textall()",
                "isbalance": True,
                "isclean": True,
                "regex": "(?:项目编号|项目编码|项目代码|采购编号|招标编号)\\s*[:：]*\\s*[\\(【\\[（]*([a-zA-Z0-9\\(\\)（）\\[\\]【】\\-_年第号\\s]{4,}[a-zA-Z0-9\\)）\\]】\\-_号]{2,})(?![a-zA-Z0-9\\)）\\]】\\-_号])",
                "isnull": True
            }
        }
    },

    "pagination": {
        "url": 'http://180.213.33.140:8081/content/pageContentM@$pageNo=${page_param}&count=10&orderBy=27&isNew=true&title=&projectType=&areaNo=宝坻区&inDate=&tenderProjectCode=&channelIds=@json:["82328"]&timeBegin=&timeEnd',
        "headers": {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "http://180.213.33.140:8081",
            "Referer": "http://180.213.33.140:8081/jyxx.jhtml",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        },
        "enable": True,
        "page_param": {
            "current": 1,
            "start": 1,
            "step": 1,
            "count": {
                "type": "jsonpath",
                "value": '$.totalElements',
            },
            "per_num": 10
        }
    }
}

entrance_url = 'http://180.213.33.140:8081/content/pageContentM@$pageNo=1&count=10&orderBy=27&isNew=true&title=&projectType=&areaNo=宝坻区&inDate=&tenderProjectCode=&channelIds=@json:["82328"]&timeBegin=&timeEnd'
