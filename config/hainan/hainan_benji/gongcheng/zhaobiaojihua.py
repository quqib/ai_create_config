configure = {
    "name": "海南省公共资源交易平台-工程建设-招标计划",
    "host": "ggzy.hainan.gov.cn",
    "source_site": "海南省公共资源交易平台",
    "industry": "工程建设",
    "notice_type": "招标计划",
    "org_id": "4601213",
    "page_url": "https://ggzy.hainan.gov.cn/ggzyjy/jyxx/jyxx_list.html",
    "list": {
        "mode": "REQUESTS",
        "method": "POST",
        "isdump": True,
        "headers": {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://ggzy.hainan.gov.cn",
            "Referer": "https://ggzy.hainan.gov.cn/ggzyjy/jyxx/jyxx_list.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        },
        "fields": {
            "title": {"type": "jsonpath", "value": "$.result.records[*].titlenew"},
            "url": {"type": "jsonpath", "value": "$.result.records[*].linkurl", "prepath": True},
            "entrance_url": {"type": "jsonpath", "value": "$.result.records[*].linkurl", "prepath": True},
            "publish_time": {"type": "jsonpath", "value": "$.result.records[*].webdate", "format": "date"}
        }
    },
    "detail": {
        "mode": "REQUESTS",
        "method": "GET",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"},
        "attachment": {
            "enable": True,
            "fields": {
                "url": {"type": "xpath",
                        "value": "//a[@onclick and contains(@onclick, 'downloadztbattach')]/@onclick",
                        "regex": "'(/[^']+)",
                        "encrypt": [{"type": "replace", "origin": "downloadztbattach\?attachGuid",
                                     "dest": "ztbAttachDownloadAction.action?cmd=getContent&attachGuid"}],
                        "candidate": {
                            "type": "xpath",
                            "value": "//a[@href and contains(@href, 'gpx-public-file')]/@href",
                        },
                        "prepath": True,
                        "isnull": True
                        },
                "name": {"type": "xpath",
                         "value": "//a[@href and contains(@href, 'gpx-public-file')]/text() | //a[@onclick and contains(@onclick, 'downloadztbattach')]/@title",
                         "isnull": True,
                         }
            },
            "captcha": {
                "enable": True,
                "startcheck": "downloadztbattach",
                "steps": [
                    {
                        "name": "get_image",
                        "method": "POST",
                        "isdump": False,
                        "issave": False,
                        "url": "https://ggzy.hainan.gov.cn/EpointWebBuilder/rest/frontAppNotNeedLoginAction/getVerificationCodeM@$params={\"width\":\"100\",\"height\":\"40\",\"codeNum\":\"4\",\"interferenceLine\":\"1\",\"codeGuid\":\"\"}",
                        "headers": {
                            "Accept": "application/json, text/javascript, */*;",
                            "Accept-Language": "zh-CN,zh;q=0.9",
                            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "Origin": "https://ggzy.hainan.gov.cn/",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
                        },
                        "fields": {
                            "verificationCodeGuid": {
                                "type": "jsonpath",
                                "value": "$.custom.verificationCodeGuid",
                            },
                            "img_str": {
                                "type": "jsonpath",
                                "regex": ',(.+)',
                                "value": "$.custom.imgCode",
                            },
                        },
                        "captcha_config": {
                            "type": "abc_num",
                            "length": 4,
                            "iscase": False
                        },
                        "response_type": "json"
                    },
                    {
                        "name": "get_file",
                        "method": "GET",
                        "url": "${list_url}&verificationCode=${captcha_code}&verificationGuid=${verificationCodeGuid}",
                        "issave": False,
                        "isredirect": True,
                        "check_fail": "验证码验证失败",
                        "headers": {
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                            "accept-encoding": "gzip, deflate, br, zstd",
                            "Accept-Language": "zh-CN,zh;q=0.9",
                            "Origin": "https://ggzy.hainan.gov.cn/",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
                        },
                        "response_type": "file"
                    }
                ]
            }
        },
        "fields": {
            "content": {"type": "xpath", "value": "//div[@class='main-content']"},
            "title": {"type": "xpath", "value": "//h3[@class='infotitle']/text()", "isnull": True},
            "publish_time": {"type": "xpath", "value": "//div[@class='article-sources']/textall()",
                             "regex": "(?:发布时间|信息时间|发布日期)\\s*[:：]*\\s*(\\d{4}-\\d{2}-\\d{2})",
                             "format": "date", "isnull": True},
            "project_code": {"type": "xpath", "value": "//div[@class='main-content']/textall()",
                             "regex": "(?:项目编号|项目编码|项目代码|采购编号|招标编号)\\s*[：:]*\\s*([A-Za-z0-9\\-]+)",
                             "isbalance": True, "isclean": True, "isnull": True}
        }
    },
    "pagination": {
        "enable": True,
        "url": "https://ggzy.hainan.gov.cn/inteligentsearch/rest/esinteligentsearch/getFullTextDataNewM@$token=&pn=${page_param}&rn=10&sdt=&edt=&wd=%20&inc_wd=&exc_wd=&fields=title&cnum=001&sort={\"webdate\":\"0\"}&ssort=title&cl=200&terminal=&condition=@json:[{\"fieldName\":\"xiaquncode\",\"equal\":\"460000\",\"notEqual\":null,\"equalList\":null,\"notEqualList\":null,\"isLike\":true,\"likeType\":2},{\"fieldName\":\"categorynum\",\"equal\":\"003001001\",\"notEqual\":null,\"equalList\":null,\"notEqualList\":null,\"isLike\":true,\"likeType\":2}]&highlights=title&noParticiple=1&searchRange=@json:[]&isBusiness=1",
        "headers": {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://ggzy.hainan.gov.cn",
            "Referer": "https://ggzy.hainan.gov.cn/ggzyjy/jyxx/jyxx_list.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        },
        "page_param": {
            "current": 1,
            "start": 1,
            "step": 10,
            "offset": 0,
            "per_num": 10,
            "count": {"type": "jsonpath", "value": "$.result.totalcount"}
        }
    }
}

entrance_url = "https://ggzy.hainan.gov.cn/inteligentsearch/rest/esinteligentsearch/getFullTextDataNewM@$token=&pn=0&rn=10&sdt=&edt=&wd=%20&inc_wd=&exc_wd=&fields=title&cnum=001&sort={\"webdate\":\"0\"}&ssort=title&cl=200&terminal=&condition=@json:[{\"fieldName\":\"xiaquncode\",\"equal\":\"460000\",\"notEqual\":null,\"equalList\":null,\"notEqualList\":null,\"isLike\":true,\"likeType\":2},{\"fieldName\":\"categorynum\",\"equal\":\"003001001\",\"notEqual\":null,\"equalList\":null,\"notEqualList\":null,\"isLike\":true,\"likeType\":2}]&highlights=title&noParticiple=1&searchRange=@json:[]&isBusiness=1"
