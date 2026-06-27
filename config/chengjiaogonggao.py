configure = {
    "name": "温州市公共资源交易中心-交易信息-苍南县-产权交易-成交公告",
    "org_id": "3304976",
    "page_url": "https://ggzyjy-eweb.wenzhou.gov.cn/col/col1229666963/index.html",
    "host": "ggzyjy-eweb.wenzhou.gov.cn",
    "source_site": "温州市公共资源交易中心",
    "industry": "产权交易",
    "notice_type": "成交公告",
    "list": {
        "mode": "REQUESTS",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        },
        "captcha": {
            "enable": True,
            "steps": [
                {
                    "name": "get_token",
                    "method": "GET",
                    "url": "https://ggzyjy-eweb.wenzhou.gov.cn/col/col1229666963/index.html",
                    "issave": False,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
                    },
                    "fields": {
                        "tplSetId": {
                            "type": "regex",
                            "value": "'tplSetId':\\s*'(.*?)'"
                        }
                    }
                },
                {
                    "name": "get_list",
                    "method": "GET",
                    "url": "${list_url}",
                    "issave": True,
                    "headers": {
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Host": "ggzyjy-eweb.wenzhou.gov.cn",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    "response_type": "list"
                }
            ]
        },
        "fields": {
            "title": {
                "type": "jsonpath",
                "value": "$.data.html",
                "xpath": "//div[contains(@class,'page-content')]//li//a[@href and @class='fl']/text()"
            },
            "url": {
                "type": "jsonpath",
                "value": "$.data.html",
                "xpath": "//div[contains(@class,'page-content')]//li//a[@href and @class='fl']/@href",
                "prepath": True
            },
            "entrance_url": {
                "type": "jsonpath",
                "value": "$.data.html",
                "xpath": "//div[contains(@class,'page-content')]//li//a[@href and @class='fl']/@href",
                "prepath": True
            },
            "publish_time": {
                "type": "jsonpath",
                "value": "$.data.html",
                "xpath": "//div[contains(@class,'page-content')]//li//span[@class='fr']/text()",
                "regex": "(\\d+-\\d+-\\d+)",
                "format": "date"
            }
        }
    },
    "detail": {
        "mode": "REQUESTS",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"
        },
        "fields": {
            "content": {
                "type": "xpath",
                "value": "//div[contains(@class,'container')]//div[@class='ewb-article']",
            },
            "title": {
                "type": "xpath",
                "value": "//div[contains(@class,'container')]//div[@class='ewb-article']/h3/text()",
            },
            "publish_time": {
                "type": "xpath",
                "value": "//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-source']/textall()",
                "regex": "(?:发布时间|信息时间|发布日期|时间发布|发稿时间|日期)\\s*[:：]*\\s*(\\d+-\\d+-\\d+)",
                "format": "date",
            },
            "project_code": {
                "type": "xpath",
                "value": "//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']/textall()",
                "isbalance": True,
                "isclean": True,
                "regex": "(?:项目编号|项目编码|项目代码|采购编号|招标编号|招标代码|采购任务编号|工程编码|工程编号|公示编号)\\s*[:：]*\\s*[\\(【\\[（]*([a-zA-Z0-9\\(\\)（）\\[\\]【】/\\-_年第号\\s]{4,}[a-zA-Z0-9\\)）\\]】\\-_号]{2,})(?![a-zA-Z0-9\\)）\\]】\\-_号])",
                "isnull": True
            }
        },
        "attachment": {
            "enable": True,
            "mode": "REQUESTS",
            "isverify": False,
            "fields": {
                "url": {
                    "type": "xpath",
                    "value": "//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//img[@src and not(contains(@src,'data:image/')) and not(contains(@src,'file:'))]/@src|//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//a[@href and normalize-space(.) != '' and (contains(@href,'.xls') or contains(@href,'.doc')  or contains(@href,'.pdf') or contains(@href,'.rar')  or contains(@href,'.zip') or contains(@href,'.jpg') or contains(@href,'.png') or contains(text(),'.xls') or contains(text(),'.doc')  or contains(text(),'.pdf') or contains(text(),'.rar')  or contains(text(),'.zip') or contains(text(),'.jpg') or contains(text(),'.png'))]/@href|//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//a[@class='fujian' and @href  and normalize-space(.) != '']/@href|//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//*[@class='attachlist' or @id='attachlist']//a[@href and @title]/@href",
                    "encrypt": [
                        {"type": "replace", "origin": "downloadztbattach\?",
                         "dest": "ztbAttachDownloadAction.action?cmd=getContent&"}],
                    "prepath": True,
                    "candidate": {
                        "type": "xpath",
                        "value": "//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//a[@id='pdfshow' and normalize-space(.) != '' and @data-value]/@data-value",
                        "encrypt": [
                            {"type": "replace", "origin": "downloadztbattach\?",
                             "dest": "ztbAttachDownloadAction.action?cmd=getContent&"}],
                        "prepath": True,
                    },
                    "isnull": True
                },
                "name": {
                    "type": "xpath",
                    "value": "//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//img[@src and not(contains(@src,'data:image/')) and not(contains(@src,'file:'))]/@src|//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//a[@href and normalize-space(.) != '' and (contains(@href,'.xls') or contains(@href,'.doc')  or contains(@href,'.pdf') or contains(@href,'.rar')  or contains(@href,'.zip') or contains(@href,'.jpg') or contains(@href,'.png') or contains(text(),'.xls') or contains(text(),'.doc')  or contains(text(),'.pdf') or contains(text(),'.rar')  or contains(text(),'.zip') or contains(text(),'.jpg') or contains(text(),'.png'))]/text()|//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//a[@class='fujian' and @href  and normalize-space(.) != '']/text()|//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//*[@class='attachlist' or @id='attachlist']//a[@href and @title]/text()|//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//a[@href and normalize-space(.) != '' and (contains(@href,'.xls') or contains(@href,'.doc')  or contains(@href,'.pdf') or contains(@href,'.rar')  or contains(@href,'.zip') or contains(@href,'.jpg') or contains(@href,'.png') or contains(text(),'.xls') or contains(text(),'.doc')  or contains(text(),'.pdf') or contains(text(),'.rar')  or contains(text(),'.zip') or contains(text(),'.jpg') or contains(text(),'.png')) and strong]/strong/text()",
                    "candidate": {
                        "type": "xpath",
                        "value": "//div[contains(@class,'container')]//div[@class='ewb-article']//div[@class='ewb-article-content']//a[@id='pdfshow' and normalize-space(.) != '' and @data-value]/text()",
                    },
                    "isnull": True
                }
            }
        }
    },
    "pagination": {
        "url": "https://ggzyjy-eweb.wenzhou.gov.cn/api-gateway/jpaas-publish-server/front/page/build/unit?webId=3819&pageId=1229666963&parseType=bulidstatic&pageType=column&tagId=%E8%B5%84%E6%96%99list&tplSetId=${tplSetId}&paramJson=%7B%22pageNo%22%3A${page_param}%2C%22pageSize%22%3A10%7D",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        },
        "enable": True,
        "page_param": {
            "current": 1,
            "start": 1,
            "step": 1,
            "count": {
                "type": "jsonpath",
                "value": "$.data.html",
                "regex": "count=\\s*\"(\\d+)\"\\s*"
            },
            "per_num": 10
        }
    }
}

entrance_url = "https://ggzyjy-eweb.wenzhou.gov.cn/api-gateway/jpaas-publish-server/front/page/build/unit?webId=3819&pageId=1229666963&parseType=bulidstatic&pageType=column&tagId=%E8%B5%84%E6%96%99list&tplSetId=${tplSetId}&paramJson=%7B%22pageNo%22%3A1%2C%22pageSize%22%3A10%7D"
