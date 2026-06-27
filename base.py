import sys
import traceback
import ddddocr
from minio import Minio
import os
import json
import time
import random
import string
from datetime import datetime
import logging
import requests
import json
import copy
import re
from datetime import datetime
from urllib.parse import parse_qs, unquote, urlparse,urljoin,quote
from typing import Dict, Any, List
from playwright.sync_api import sync_playwright,ViewportSize, TimeoutError as PlaywrightTimeoutError
from jsonpath_ng import parse as jsonpath_parse
import hashlib
import hmac
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, PKCS1_OAEP
import cv2
import numpy as np
from urllib3.exceptions import IncompleteRead
import jsonpath


class NewCommonSpider:
    def __init__(self,logger):
        self.logger=logger
        self.playwright = None
        self.browser = None
        self.context = None
        self.timeout = 60
        self.retry_times = 3
        # 临时文件目录
        self.temp_dir = "spider_temp"
        self.attachment_temp_dir = 'attachments_temp'
        self.task_id = None
        self.max_attachment_size = 20971520



    def init_params(self):
        self.task_id = None
        self.playwright = None
        self.browser = None
        self.context = None

        if not os.path.exists(self.attachment_temp_dir):
            os.makedirs(self.attachment_temp_dir, exist_ok=True)
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)

        self.random_user_agent=self.generate_user_agent()

    @staticmethod
    def generate_user_agent() -> str:
        """
        随机生成高真实度 User-Agent
        包含：Chrome / Edge / Firefox
        版本号丰富，系统为 Win10 / Win11
        """
        # 系统平台
        os_platforms = [
            "Windows NT 10.0; Win64; x64",
            "Windows NT 11.0; Win64; x64"
        ]

        # Chrome 版本（超多真实版本）
        chrome_versions = [
            "134.0.0.0", "133.0.0.0", "132.0.0.0", "131.0.0.0",
            "130.0.0.0", "129.0.0.0", "128.0.0.0", "127.0.0.0",
            "126.0.0.0", "125.0.0.0", "124.0.0.0", "123.0.0.0",
            "122.0.0.0", "121.0.0.0", "120.0.0.0", "119.0.0.0",
            "118.0.0.0", "117.0.0.0", "116.0.0.0", "115.0.0.0",
            "114.0.0.0", "113.0.0.0", "112.0.0.0", "111.0.0.0",
        ]

        # Edge 版本（和 Chrome 内核同步，真实可用）
        edge_versions = [
            "134.0.0.0", "133.0.0.0", "132.0.0.0", "131.0.0.0",
            "130.0.0.0", "129.0.0.0", "128.0.0.0", "127.0.0.0",
            "126.0.0.0", "125.0.0.0", "124.0.0.0", "123.0.0.0",
            "122.0.0.0", "121.0.0.0", "120.0.0.0", "119.0.0.0",
            "118.0.0.0", "117.0.0.0", "116.0.0.0", "115.0.0.0",
        ]

        # Firefox 版本
        firefox_versions = [
            "125.0", "126.0", "127.0", "128.0", "129.0",
            "130.0", "131.0", "132.0", "133.0", "134.0",
            "124.0", "123.0", "122.0", "121.0", "120.0",
            "119.0", "118.0", "117.0", "116.0", "115.0",
        ]

        os = random.choice(os_platforms)
        browser = random.choice(["chrome", "edge", "firefox"])

        if browser == "chrome":
            chrome_ver = random.choice(chrome_versions)
            return (f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{chrome_ver} Safari/537.36")

        elif browser == "edge":
            edge_ver = random.choice(edge_versions)
            return (f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) "
                    f"Chrome/{edge_ver} Safari/537.36 Edg/{edge_ver}")

        else:  # firefox
            ff_ver = random.choice(firefox_versions)
            return (f"Mozilla/5.0 ({os}; rv:{ff_ver}) "
                    f"Gecko/20100101 Firefox/{ff_ver}")

    def get_task_result(self, spider_status, data, task_params):
        """获取任务结果"""
        task_result={
            "task_id": task_params.get("task_id",''),
            "task_type": task_params.get("task_type",''),
            "parent_task_id": task_params.get("parent_task_id",''),
            "task_conf_id":task_params.get("task_conf_id",''),
            "task_level": task_params.get("task_level",''),
            "task_status": spider_status,
            "begin_date": task_params.get("begin_date",''),
            "page_id": task_params.get("page_id",''),
            "node_id": task_params.get("node_id", ''),
            "node_ip": task_params.get("node_ip",''),
            "crawler_type": task_params.get("crawler_type",''),
            "payload": data,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if task_params.get("data_id",''):
            task_result.update({"data_id":task_params.get("data_id",'')})
        return task_result

    def run(self, task_params):
        """运行新版通用爬虫"""
        spider_status = "FAILED"
        result={}
        try:
            self.init_params()
            self.task_id = task_params.get("task_id", "")
            config = json.loads(task_params.get("configure", "{}")) if isinstance(task_params.get("configure", "{}"), str) else task_params.get("configure", {})
            self.config_data_name=config.get("name", "")
            entrance_url = task_params.get("entrance_url", "")
            source_site = config.get("source_site", "")

            if not config or not entrance_url or not source_site:
                self.logger.error(f"【{self.task_id}】缺少爬虫配置或入口URL")
                return self.get_task_result(spider_status, data=result, task_params=task_params)

            ##根据任务获取任务类型
            task_type = task_params.get("task_type", "")
            if not task_type:
                self.logger.error(f"【{self.task_id}】缺少任务类型")
                return self.get_task_result(spider_status, data=result, task_params=task_params)
            if task_type.lower() == "list":
                spider_status, result = self._run_list_request(entrance_url, config, task_params)
                return self.get_task_result(spider_status, data=result, task_params=task_params)
            elif task_type.lower() == "detail":
                spider_status, result = self._run_detail_request(entrance_url, config, task_params)
                return self.get_task_result(spider_status, data=result, task_params=task_params)
            else:
                self.logger.error(f"【{self.task_id}】不支持的任务类型: {task_type}")
                return self.get_task_result(spider_status, data=result, task_params=task_params)
        except Exception as e:
            self.logger.error(f"【{self.__class__.__name__}】运行爬虫失败: {e}")
            traceback.print_exc()
            return self.get_task_result(spider_status, data=result, task_params=task_params)
        finally:
            # 关闭 Playwright 浏览器上下文
            if self.context:
                self.context.close()
                self.context = None
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None

    def _generate_unique_filename(self, url, ext):
        """生成唯一文件名：task_id + URL哈希 + 后缀"""
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        return f"{self.task_id}_{url_hash}.{ext}"

    def _build_fingerprint_init_script(self):
        # 全部固定为确定值，无外部依赖
        payload = {
            "webdriver": False,  # 禁用自动化检测
            "language": "zh-CN",  # 语言
            "platform": "Win32",  # 系统平台
            "hardwareConcurrency": 8,  # CPU 线程数
            "deviceMemory": 8,  # 运行内存 GB
            "colorDepth": 24,  # 颜色深度
            "screenResolution": [1920, 1080],  # 屏幕分辨率
            "availableScreenResolution": [1920, 1040],  # 可用分辨率
            "maxTouchPoints": 0,  # 无触屏
            "plugins": [  # 固定插件列表
                ["Chrome PDF Viewer", "Portable Document Format", [
                    ["application/pdf", "pdf"],
                    ["application/x-google-chrome-pdf", "pdf"]
                ]]
            ],
            "webglVendor": "Google Inc. (Intel)",
            "webglRenderer": "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)"
        }

        payload_json = json.dumps(payload, ensure_ascii=False)

        return f"""
    (() => {{
      const fp = {payload_json};

      const defineGetter = (obj, prop, value) => {{
        try {{
          Object.defineProperty(obj, prop, {{
            get: () => value,
            configurable: true,
          }});
        }} catch (e) {{}}
      }};

      if (typeof fp.webdriver === "boolean") defineGetter(navigator, "webdriver", fp.webdriver);
      if (typeof fp.platform === "string") defineGetter(navigator, "platform", fp.platform);
      if (typeof fp.hardwareConcurrency === "number") defineGetter(navigator, "hardwareConcurrency", fp.hardwareConcurrency);
      if (typeof fp.deviceMemory === "number") defineGetter(navigator, "deviceMemory", fp.deviceMemory);
      if (typeof fp.maxTouchPoints === "number") defineGetter(navigator, "maxTouchPoints", fp.maxTouchPoints);

      if (typeof fp.language === "string" && fp.language) {{
        defineGetter(navigator, "language", fp.language);
        const base = String(fp.language).split("-")[0];
        const langs = [fp.language, base, "en"].filter((v, i, a) => v && a.indexOf(v) === i);
        defineGetter(navigator, "languages", langs);
      }}

      if (Array.isArray(fp.availableScreenResolution) && fp.availableScreenResolution.length === 2) {{
        try {{
          Object.defineProperty(screen, "availWidth", {{
            get: () => fp.availableScreenResolution[0],
            configurable: true,
          }});
          Object.defineProperty(screen, "availHeight", {{
            get: () => fp.availableScreenResolution[1],
            configurable: true,
          }});
        }} catch (e) {{}}
      }}

      if (typeof fp.colorDepth === "number") {{
        try {{
          Object.defineProperty(screen, "colorDepth", {{
            get: () => fp.colorDepth,
            configurable: true,
          }});
          Object.defineProperty(screen, "pixelDepth", {{
            get: () => fp.colorDepth,
            configurable: true,
          }});
        }} catch (e) {{}}
      }}

      const pluginData = Array.isArray(fp.plugins) ? fp.plugins : [];
      if (pluginData.length) {{
        const makeMimeType = (type, suffixes, description, enabledPlugin) => ({{
          type,
          suffixes,
          description,
          enabledPlugin,
        }});

        const makePlugin = (name, description, mimeData) => {{
          const plugin = {{
            name,
            description: description || "",
            filename: "internal-pdf-viewer",
            length: Array.isArray(mimeData) ? mimeData.length : 0,
          }};
          (mimeData || []).forEach((mt, i) => {{
            plugin[i] = mt;
          }});
          plugin.item = function (index) {{ return this[index]; }};
          plugin.namedItem = function (_name) {{ return null; }};
          return plugin;
        }};

        const pluginArray = [];
        pluginData.forEach((p) => {{
          if (!Array.isArray(p) || p.length < 3) return;
          const name = String(p[0] || "");
          const desc = String(p[1] || "");
          const mimes = Array.isArray(p[2]) ? p[2] : [];
          const mimeData = mimes
            .map((m) => {{
              if (!Array.isArray(m) || m.length < 2) return null;
              return makeMimeType(String(m[0]), String(m[1]), desc, null);
            }})
            .filter(Boolean);
          if (name) pluginArray.push(makePlugin(name, desc, mimeData));
        }});

        pluginArray.refresh = function () {{ }};
        pluginArray.item = function (index) {{ return this[index]; }};
        pluginArray.namedItem = function (name) {{ return this.find((p) => p.name === name) || null; }};

        defineGetter(navigator, "plugins", pluginArray);

        const mimeTypes = [];
        pluginArray.forEach((pl) => {{
          for (let i = 0; i < pl.length; i++) {{
            const mt = pl[i];
            if (!mt || !mt.type) continue;
            try {{ mt.enabledPlugin = pl; }} catch (e) {{}}
            mimeTypes.push(mt);
          }}
        }});
        mimeTypes.item = function (index) {{ return this[index]; }};
        mimeTypes.namedItem = function (name) {{ return this.find((m) => m.type === name) || null; }};
        defineGetter(navigator, "mimeTypes", mimeTypes);
      }}

      if (typeof fp.webglVendor === "string" && typeof fp.webglRenderer === "string") {{
        const overrideWebGL = (proto) => {{
          if (!proto || !proto.getParameter) return;
          const getParameter = proto.getParameter;
          proto.getParameter = function (parameter) {{
            if (parameter === 37445) return fp.webglVendor;
            if (parameter === 37446) return fp.webglRenderer;
            return getParameter.apply(this, [parameter]);
          }};
        }};

        if (typeof WebGLRenderingContext !== "undefined") overrideWebGL(WebGLRenderingContext.prototype);
        if (typeof WebGL2RenderingContext !== "undefined") overrideWebGL(WebGL2RenderingContext.prototype);
      }}

      if (!window.chrome) {{
        window.chrome = {{ runtime: {{}}, loadTimes: function () {{}}, csi: function () {{}}, app: {{}} }};
      }}

      if (window.Notification) {{
        Object.defineProperty(window.Notification, "permission", {{
          get: () => "default",
          configurable: true,
        }});
      }}

      if (navigator.permissions && navigator.permissions.query) {{
        const originalQuery = navigator.permissions.query;
        navigator.permissions.query = function (parameters) {{
          if (parameters && parameters.name === "notifications") {{
            return Promise.resolve({{ state: "prompt", onchange: null }});
          }}
          return originalQuery.apply(this, arguments);
        }};
      }}
    }})();
    """.strip()

    def download_attachments_auto(self, page, iframe, click_info):
        """
        # ======================
        # 点击通用下载逻辑：自动适配 iframe / 非 iframe 内的附件
        # ======================
        :param page:
        :param iframe:
        :param click_info:
        :return:
        """
        all_download_links = []
        file_elems = None
        real_download_url = None  # 真实下载地址（非blob）

        attachment_selector = click_info.get('value', '')
        is_null = click_info.get('isnull', False)
        if not attachment_selector:
            raise ValueError("点击下载提取规则为空")

        # --------------------------
        # 监听网络响应 → 抓真实URL（核心优化）
        # --------------------------
        def catch_response(response):
            nonlocal real_download_url
            try:
                # 过滤下载请求（根据文件类型/下载关键字）
                content_types = [
                    'application/octet-stream',
                    'application/pdf',
                    'application/zip',
                    'application/vnd',
                    'audio/',
                    'video/',
                    'text/csv',
                    'excel', 'word'
                ]
                if any(ct in response.headers.get('content-type', '') for ct in content_types):
                    real_download_url = response.url
            except:
                pass

        page.on("response", catch_response)

        try:
            if iframe:
                file_elems = iframe.locator(attachment_selector)
            else:
                file_elems = page.locator(attachment_selector)
            total = file_elems.count()
            if total > 0:
                self.logger.info(f"✅ 寻找附件，共找到 {total} 个文件")
        except:
            if not is_null:
                raise ValueError("点击下载提取结果为空")
            total = 0
        if file_elems:
            for i in range(total):
                self.logger.info(f"--- 正在处理第 {i + 1} 个文件 ---")
                real_download_url = None  # 每次重置
                try:
                    with page.expect_download(timeout=10000) as download_info:
                        file_elems.nth(i).click()

                    download = download_info.value
                    name = download.suggested_filename
                    blob_url = download.url

                    url = real_download_url if real_download_url else blob_url

                    all_download_links.append({
                        "name": name,
                        "url": url
                    })
                    self.logger.info(f"文件名：{name}")
                    self.logger.info(f"下载链接：{url}")

                except Exception as e:
                    self.logger.info(f"❌ 第 {i + 1} 个文件下载失败：{str(e)}")

        return all_download_links

    def get_nested_frame(self, page, iframe_xpath_list):
        """
        自动进入多层 iframe
        :param page: playwright page 对象
        :param iframe_xpath_list: iframe 路径列表，例如 ["//iframe[@id='iframe']", "//iframe[@id='project-page']"]
        :return: 最终的 FrameLocator
        """
        if not iframe_xpath_list:
            return None

        frame = page
        try:
            for xpath in iframe_xpath_list:
                # 逐层进入 iframe
                frame = frame.frame_locator(xpath)
                print(frame)

                # 关键：检查这一层 iframe 是否真的存在
                # 如果不存在，直接返回 None
                if not frame.locator("html").count():
                    return None

            return frame  # 全部层级都找到，返回最终 frame

        except Exception as e:
            raise ValueError(str(e))


    def replace_exec_in_headers(self,headers):
        """
        从 $exec(...) 字符串中提取代码并执行，返回结果
        带完整异常处理，不会崩溃
        """
        # 1. 正则提取 $exec( 内部的代码
        exec_pattern = re.compile(r'^\$exec\(([\s\S]*?)\)$')
        global_vars={}
        for key, value in headers.items():
            if not isinstance(value, str):
                continue
            match = exec_pattern.fullmatch(value.strip())

            if not match:
                continue
            try:
                local_vars = {}
                # 提取代码
                code_str = self.render(match.group(1).strip(),global_vars)
                if not code_str:
                    self.logger.error(f"【{self.task_id}】异常：$exec 内部代码为空")
                    return headers

                # 2. 执行提取到的代码
                exec(code_str, globals(), local_vars)

                # 3. 获取结果变量
                if "result" in local_vars:
                    global_vars.update({"result": local_vars["result"]})
                    headers.update({key: global_vars["result"]})
                elif key in local_vars:
                    global_vars.update({key: local_vars[key]})
                    headers.update({key: global_vars[key]})
                else:
                    self.logger.error(f"【{self.task_id}】异常：代码中未定义 result 变量")
                    return headers

            except SyntaxError as e:
                self.logger.error(f"【{self.task_id}】语法异常：{str(e)}")
                return headers
            except Exception as e:
                self.logger.error(f"【{self.task_id}】执行异常：{str(e)}")
                return headers
        return headers


    def _request(self, request_config, url, data=None,is_save=True,session=None,is_return_content=False):
        """
        通用请求方法，支持 Requests 和 Playwright
        :param request_config: list/detail 中的请求配置（包含mode/method/headers等）
        :param url: 请求URL
        :param data: POST请求数据
        :param is_save: 是否固证
        :param session: 会话对象
        :param is_return_content: 是否返回二进制流
        :return: 响应内容（文本/页面对象）
        """
        mode = request_config.get("mode", "REQUESTS").upper()
        method = request_config.get("method", "GET").upper()
        headers = copy.deepcopy(request_config.get("headers", {}))
        is_dumps=request_config.get("isdump", True)
        is_redirect = request_config.get("isredirect", True)
        is_verify = request_config.get("isverify", True)
        iframe_selectors=request_config.get("iframe", [])
        attach_click_info=request_config.get("attachment", {}).get("click", {})
        check_404_page = request_config.get("404", '')
        formdata = request_config.get("formdata", [])
        check_selenium_list = request_config.get("checkselenium", [])
        form_data=None

        resp_headers_params = request_config.get("respheaders", [])

        # 随机选择UA
        if "user-agent" in headers:
            headers["user-agent"] = self.generate_user_agent()
        else:
            headers["User-Agent"] = self.generate_user_agent()
        proxy_dict = None
        file_url = None
        spider_status = "FAILED"
        content = None
        selenium_iframe=None
        attach_info_list=[]
        if formdata and data:
            if not form_data:
                form_data = {}
            for formdata_item in formdata:
                if formdata_item in data:
                    form_data[formdata_item]=(None, data[formdata_item])
                    data.pop(formdata_item, None)
        for check_selenium_item in check_selenium_list:
            if check_selenium_item in url:
                mode ='SELENIUM'
                break

        try:
            headers = self.replace_exec_in_headers(headers)
            # Requests 静态请求
            if mode == "REQUESTS":
                for retry_num in range(self.retry_times):
                    proxy_dict={'http': 'http://t14306903178173:wp12345@j708.kdltps.com:15818/', 'https': 'http://t14306903178173:wp12345@j708.kdltps.com:15818/'}
                    try:
                        if method == "GET":
                            if session:
                                resp = session.get(url, headers=headers,proxies=proxy_dict, timeout=self.timeout,
                                                    verify=is_verify,allow_redirects=is_redirect,stream=is_return_content)
                            else:
                                resp = requests.get(url, headers=headers, proxies=proxy_dict, timeout=self.timeout,verify=is_verify,allow_redirects=is_redirect,stream=is_return_content)
                        elif method == "POST":
                            tmp_post_data = json.dumps(data) if is_dumps else data

                            if session:
                                resp = session.post(url, headers=headers, data=tmp_post_data, files=form_data, proxies=proxy_dict,
                                                     timeout=self.timeout, verify=is_verify, allow_redirects=is_redirect,stream=is_return_content)
                            else:
                                resp = requests.post(url, headers=headers, data=tmp_post_data, files=form_data,
                                                         proxies=proxy_dict,
                                                         timeout=self.timeout, verify=is_verify,
                                                         allow_redirects=is_redirect,stream=is_return_content)
                        else:
                            self.logger.error(f"【{self.task_id}】不支持的请求方法: {method}")
                            return file_url, None,None,attach_info_list
                        if int(resp.status_code) != 200:
                            if int(resp.status_code) == 404:
                                self.logger.error(
                                    f"【{self.task_id}】Requests请求链接失效：{url}")
                                spider_status = "NOT_FIND"
                                continue
                            print(resp.status_code)
                            if str(resp.status_code).startswith('3'):
                                self.logger.error(
                                    f"【{self.task_id}】Requests请求链接发生跳转：{url}")
                                spider_status = "FAILED"
                                break
                            raise ValueError("请求状态码不正确")
                        if not is_return_content:
                            resp.encoding = resp.apparent_encoding or "utf-8"
                        if is_return_content:
                            temp_download_content =b''
                            downloaded_size= 0
                            exceed_limit =False
                            for chunk in resp.iter_content(chunk_size=8192):
                                if chunk:
                                    downloaded_size += len(chunk)
                                    if downloaded_size > self.max_attachment_size:
                                        self.logger.info(
                                            f"【{self.task_id}】下载大小 {self.max_attachment_size / 1024 / 1024:.2f}MB 超过限制，停止下载")
                                        exceed_limit = True
                                        break  # 只退出循环
                                    temp_download_content+=chunk
                            if exceed_limit:
                                content = b''
                                spider_status = "OUTlIMIT"
                                break
                            content = temp_download_content
                            attach_info_list=[{"attach_ext":self.get_file_type_by_headers(resp.headers)}]
                        else:
                            content = resp.text
                            if check_404_page and check_404_page in content:
                                self.logger.error(
                                    f"【{self.task_id}】Requests请求响应存在404标识：{url}")
                                spider_status = "NOT_FIND"
                                break

                        #出现响应头获取信息
                        headers_resp_dict={}
                        for headers_item in resp_headers_params:
                            if headers_item.lower()=='set-cookie':
                                cookies_dict = resp.cookies.get_dict()
                                if cookies_dict:
                                    self.logger.error(
                                        f"【{self.task_id}】Requests请求响应获取到Cookies：{json.dumps(cookies_dict)}")
                                    headers_resp_dict.update(cookies_dict)
                            else:
                                resp_param=resp.headers.get(headers_item, '')
                                if resp_param:
                                    self.logger.error(
                                        f"【{self.task_id}】Requests请求响应获取到{headers_item}：{resp_param}")
                                    headers_resp_dict.update({headers_item:resp_param})
                        if headers_resp_dict:
                            if not attach_info_list:
                                attach_info_list.append({})
                            attach_info_list[0].update(headers_resp_dict)


                        content_type = resp.headers.get('Content-Type', '').lower()
                        # 文件类型
                        file_types = [
                            'pdf', 'msword', 'excel', 'zip', 'rar', 'octet-stream',
                            'image/', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'
                        ]
                        if not is_return_content:
                            for t in file_types:
                                if t in content_type:
                                    content = f"{url} is a file requests"  # 文件请求
                        # 保存HTML文件
                        if is_save:
                            filename = self._generate_unique_filename(url, "html")
                            if not os.path.exists(os.path.join(self.temp_dir,self.config_data_name)):
                                os.mkdir(os.path.join(self.temp_dir,self.config_data_name))
                            local_path = os.path.join(os.path.join(self.temp_dir,self.config_data_name), filename)
                            with open(local_path, "w", encoding="utf-8") as f:
                                f.write(content)
                            file_url = local_path
                        spider_status = "SUCCESS"
                        break
                    except Exception as e:
                        self.logger.error(
                            f"【{self.task_id}】Requests请求失败(重试 {retry_num + 1}/{self.retry_times}): {e}")
                        spider_status = "FAILED"
                        time.sleep(2)
            # Playwright 模拟浏览器
            elif mode == "SELENIUM":  # 配置中写的SELENIUM，实际用Playwright
                for retry_num in range(self.retry_times):
                    try:
                        proxy_dict={'server': 'j708.kdltps.com:15818', 'username': 't14306903178173', 'password': 'wp12345'}
                        if not self.playwright:
                            # 固定常量配置
                            context_kwargs = {
                                "ignore_https_errors": True,
                                "locale": "zh-CN",
                                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                                "timezone_id": "Asia/Shanghai",
                                "viewport": ViewportSize(width=1920, height=1080),
                                "screen": {"width": 1920, "height": 1080}
                            }
                            self.playwright = sync_playwright().start()
                            self.browser = self.playwright.chromium.launch(headless=True)
                            self.context = self.browser.new_context(proxy=proxy_dict,**context_kwargs)
                            self.context.add_init_script(script=self._build_fingerprint_init_script())
                        page = self.context.new_page()
                        page.set_extra_http_headers(headers)
                        response=page.goto(url, timeout=self.timeout * 1000)
                        if iframe_selectors:
                            page.wait_for_load_state("networkidle", timeout=self.timeout * 1000)
                            selenium_iframe = self.get_nested_frame(page, iframe_selectors)
                        else:
                            page.wait_for_load_state("load")

                        page.evaluate("""
                                              () => {
                                                  // 自动滚动到页面底部，触发懒加载
                                                  window.scrollTo({
                                                      top: document.documentElement.scrollHeight || document.body.scrollHeight,
                                                      behavior: 'smooth'
                                                  });
                                              }
                                              """)

                        time.sleep(random.uniform(2,4))  # 等待加载
                        if response:
                            if int(response.status)!=200:
                                if int(response.status) == 404:
                                    self.logger.error(
                                        f"【{self.task_id}】Playwright请求链接失效：{url}")
                                    spider_status = "NOT_FIND"
                                    continue
                                raise ValueError("请求状态码不正确")
                        else:
                            raise ValueError("Playwright未获取到HTTP响应")

                        content = page.content()
                        content_disposition = response.headers.get("content-disposition", "").lower()
                        content_type = response.headers.get("content-type", "").lower()

                        # 判断条件：强制下载 或 不是普通网页类型
                        if "attachment" in content_disposition:
                            content = f"{url} is a file requests"  # 文件请求
                        else:
                            # 普通网页类型，排除掉
                            web_types = {"text/html", "application/xhtml+xml", "text/plain"}
                            if not any(t in content_type for t in web_types):
                                content = f"{url} is a file requests"  # 文件请求

                        # 截长图
                        if is_save:
                            if not os.path.exists(os.path.join(self.temp_dir,self.config_data_name)):
                                os.mkdir(os.path.join(self.temp_dir,self.config_data_name))
                            filename = self._generate_unique_filename(url, "png")
                            local_path = os.path.join(os.path.join(self.temp_dir,self.config_data_name), filename)
                            page.screenshot(path=local_path, full_page=True)
                            if selenium_iframe:
                                content=selenium_iframe.locator("html").inner_html()
                            if attach_click_info:
                                attach_info_list=self.download_attachments_auto(page,selenium_iframe,attach_click_info)
                            file_url = local_path
                        if check_404_page and check_404_page in content:
                            self.logger.error(
                                f"【{self.task_id}】Playwright请求响应存在404标识：{url}")
                            spider_status = "NOT_FIND"
                            break
                        spider_status = "SUCCESS"
                        break
                    except Exception as e:
                        traceback.print_exc()
                        self.logger.error(
                            f"【{self.task_id}】Playwright请求失败(重试 {retry_num + 1}/{self.retry_times}): {e}")
                        spider_status = "FAILED"
                        time.sleep(2)
                    finally:
                        # 关闭 Playwright 浏览器上下文
                        if self.context:
                            self.context.close()
                            self.context = None
                        if self.browser:
                            self.browser.close()
                            self.browser = None
                        if self.playwright:
                            self.playwright.stop()
                            self.playwright = None
            else:
                raise ValueError(f"不支持的请求模式: {mode}")
            return spider_status, file_url, content,attach_info_list

        except Exception as e:
            self.logger.error(f"【{self.task_id}】{mode}请求失败 {url}: {e}")
            return spider_status, file_url, None,attach_info_list

    def parse_entrance_url_payload(self, entrance_url: str, method='GET') -> tuple:
        """
        解析入口URL中的负载数据为JSON字符串
        假设URL格式为：https://example.com?param1=value1&param2=value2&...
        负载数据部分为：param1=value1&param2=value2&...
        """
        # 定义分隔符
        separator = "M@$"
        base_url = entrance_url

        try:
            # 1. 检查并提取M@$后的负载数据
            if separator not in entrance_url or method.upper() != "POST":
                return base_url, {}

            # 分割字符串，取M@$之后的部分（负载数据）
            base_url = entrance_url.split(separator)[0]
            payload_str = entrance_url.split(separator)[1]
            if not payload_str.strip():  # 负载数据为空的情况
                return base_url, {}

            # 2. 解析URL参数格式的负载数据（处理中文/特殊字符解码）
            # parse_qs会把值解析为列表（兼容多值参数，如a=1&a=2）
            payload_dict = parse_qs(unquote(payload_str), keep_blank_values=True)

            # 3. 简化字典：将列表值转为单个值（若只有一个值），更符合JSON常用格式
            simplified_dict = {}

            # 递归遍历字典/列表，替换字符串为 Python 类型
            def convert_types(obj):
                # 如果是字典，遍历每个 key:value
                if isinstance(obj, dict):
                    return {key: convert_types(value) for key, value in obj.items()}

                # 如果是列表，遍历每个元素
                elif isinstance(obj, list):
                    return [convert_types(item) for item in obj]

                # 字符串替换核心逻辑
                elif obj == "true":
                    return True
                elif obj == "false":
                    return False
                elif obj == "null":
                    return None

                # 其他值原样返回
                else:
                    return obj
            for key, values in payload_dict.items():
                # parse_qs 会返回列表，取第一个值
                val = values[0].strip() if values else ""
                # 2. 核心规则：以 { 开头、} 结尾 → 解析成列表/字典
                if val.startswith("@json:"):
                    real_val = val[6:]  # 去掉大括号
                    try:
                        simplified_dict[key] = convert_types(json.loads(real_val))
                    except:
                        simplified_dict[key] = convert_types(val)
                elif val.startswith("@plus:"):
                    simplified_dict[key] = convert_types(val[6:].replace(" ","+"))
                else:
                    # 普通值 → 直接保留字符串
                    simplified_dict[key] = convert_types(val)

            print(base_url, simplified_dict)
            # 4. 转换为JSON字符串
            return base_url, simplified_dict

        except Exception as e:
            # 捕获所有异常，避免程序崩溃，返回空JSON
            self.logger.error(f"【parse_entrance_url_payload】解析失败：{str(e)}")
            return base_url, {}

    @staticmethod
    def timestamp_to_str(timestamp):
        """
        自动识别秒/毫秒时间戳，转换成标准日期字符串
        :param timestamp: 整数或字符串形式的时间戳
        :return: 格式化日期字符串，如 2026-04-26 15:29:41
        """
        try:
            # 转成数字
            ts = int(timestamp)

            # 自动判断是毫秒（13位）还是秒（10位）
            if ts > 1e12:  # 毫秒时间戳
                ts = ts / 1000

            # 转换为本地日期时间
            dt = datetime.fromtimestamp(ts)

            # 格式化输出（你可以自己改格式）
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp

    @staticmethod
    def compare_yyyymmdd_safe(date1: str, date2: str) -> int:
        """
        安全比较两个YYYYMmdd格式日期的大小（包含格式校验）
        返回值同方法1，格式非法时抛出ValueError
        """
        # 定义日期格式：%Y是4位年，%m是2位月，%d是2位日
        fmt = "%Y%m%d"
        try:
            # 解析为datetime对象
            dt1 = datetime.strptime(date1, fmt)
            dt2 = datetime.strptime(date2, fmt)
        except ValueError as e:
            raise ValueError(f"日期格式非法：{e}")

        # 比较datetime对象
        if dt1 > dt2:
            return 1
        elif dt1 < dt2:
            return -1
        else:
            return 0

    @staticmethod
    def is_yyyymmdd(date_str: str) -> bool:
        """
        判断字符串是否为 yyyymmdd 格式（严格校验：长度8位 + 合法日期）
        :param s: 待判断的字符串
        :return: True / False
        """
        # 第一步：必须是8位纯数字
        if not isinstance(date_str, str) or len(date_str) != 8 or not date_str.isdigit():
            return False

        # 第二步：尝试按 yyyymmdd 解析，能解析成功就是合法日期
        try:
            datetime.strptime(date_str, "%Y%m%d")
            return True
        except ValueError:
            # 解析失败（比如 20250230、20241331）
            return False

    @staticmethod
    def extract_date_to_yyyymmdd(input_str: str) -> str:
        """
        提取字符串中的日期部分（支持纯日期/日期+时间格式），转为 yyyyMMdd 格式
        非日期字符串返回原字符串

        支持的输入示例：
        - 纯日期：2026-03-16、2026/03/16、2026.03.16、2026年03月16日
        - 日期+时间：2026-03-16 14:30:59、2026/03/16 08:00、2026.03.16 23:59:59.999
        - 不规则格式：2026-3-6 9:5、2026/3/6 10:05:01

        参数:
            input_str: 输入的字符串（日期/日期+时间/非日期）

        返回:
            提取日期后转为 yyyyMMdd 格式的字符串，或原字符串
        """
        # 第一步：去除首尾空格，统一处理
        input_clean = input_str.strip()
        if not input_clean:  # 空字符串直接返回
            return ""

        # 第二步：定义支持的日期（含时间）格式模板（按优先级排序）
        # 先匹配带时间的格式，再匹配纯日期格式
        date_time_formats = [
            # 日期+时间（含秒/毫秒）
            "%Y-%m-%d %H:%M:%S.%f",  # 2026-03-16 14:30:59.123
            "%Y-%m-%d %H:%M:%S",  # 2026-03-16 14:30:59
            "%Y-%m-%d %H:%M",  # 2026-03-16 14:30
            "%Y/%m/%d %H:%M:%S.%f",  # 2026/03/16 14:30:59.123
            "%Y/%m/%d %H:%M:%S",  # 2026/03/16 14:30:59
            "%Y/%m/%d %H:%M",  # 2026/03/16 14:30
            "%Y.%m.%d %H:%M:%S",  # 2026.03.16 14:30:59
            "%Y.%m.%d %H:%M",  # 2026.03.16 14:30
            "%Y年%m月%d日 %H:%M:%S",  # 2026年03月16日 14:30:59
            "%Y年%m月%d日 %H:%M",  # 2026年03月16日 14:30
            # 纯日期
            "%Y-%m-%d",  # 2026-03-16
            "%Y/%m/%d",  # 2026/03/16
            "%Y.%m.%d",  # 2026.03.16
            "%Y年%m月%d日",  # 2026年03月16日



            "%Y年%m月%d"  # 2026年03月16
        ]

        # 第三步：尝试用datetime解析（优先匹配完整格式）
        for fmt in date_time_formats:
            try:
                date_obj = datetime.strptime(input_clean, fmt)
                return date_obj.strftime("%Y%m%d")  # 转为yyyyMMdd
            except ValueError:
                continue

        # 所有情况都不匹配，返回原字符串
        return input_str

    @staticmethod
    def clean_unbalanced_brackets(s: str) -> str:
        """
            满足终极需求：
            1. 遇到不匹配的右括号 → 删除该括号及前面不匹配的左括号 + 后面所有内容
            2. 遍历完有未闭合的左括号 → 删除第一个未闭合左括号及后面所有内容
            支持：() [] {} 【】 （）
            """
        bracket_map = {
            ')': '(',
            ']': '[',
            '}': '{',
            '）': '（',
            '】': '【'
        }
        left_brackets = set(bracket_map.values())
        stack = []  # 存储左括号的索引

        for idx, char in enumerate(s):
            # 左括号：记录位置
            if char in left_brackets:
                stack.append(idx)

            # 右括号：检查匹配
            elif char in bracket_map:
                # 能匹配：弹出栈顶
                if stack and s[stack[-1]] == bracket_map[char]:
                    stack.pop()
                # 不能匹配：直接截断到【错误左括号的前面】
                else:
                    if stack:
                        return s[:stack[-1]]
                    else:
                        return s[:idx]

        # 遍历完还有未闭合的左括号：截断到第一个未闭合括号前面
        if stack:
            return s[:stack[0]]

        # 完全正常
        return s

    @staticmethod
    def render(s, ctx):
        """
            递归循环替换 ${key} 格式的变量，直到没有可替换内容为止
            支持嵌套：${a} 中包含 ${b} 也能完全替换
            """
        if not isinstance(s, str):
            return s

        pattern = re.compile(r"\$\{([\w-]+)\}")
        max_loop = 10  # 防止死循环，设置最大替换次数
        current = s

        for _ in range(max_loop):
            # 查找所有 ${key}
            keys = pattern.findall(current)
            if not keys:
                break  # 没有可替换变量，退出

            # 替换一次
            current = pattern.sub(lambda m: ctx.get(m.group(1), m.group(0)), current)

        return current

    @staticmethod
    def classfy_ocr(img_bytes, captcha_type, captcha_length=4,small_img_bytes=None,gap_y=0,img_height=None,img_width=None):
        ocr = ddddocr.DdddOcr(show_ad=False)
        if captcha_type.lower() == "abc_num":
            with open("captcha.jpg", "wb") as f:
                f.write(img_bytes)
            return ocr.classification(img_bytes)
        if captcha_type.lower() == "math":
            with open("captcha.jpg", "wb") as f:
                f.write(img_bytes)
            res = ocr.classification(img_bytes)
            # 清洗识别结果，只保留数字、×、=、?
            clean_expr = re.sub(r'[^0-9×=+-?]', '', res)
            print(f"识别到的算式: {clean_expr}")
            if clean_expr.endswith('2'):
                clean_expr = clean_expr[:-1]

            if not re.search('[\×\+\-x\÷]', clean_expr):
                clean_expr = clean_expr[:2] + '-' + clean_expr[2:]

            print(f"处理后的算式: {clean_expr}")

            # 解析并计算
            try:
                # 将×替换为*，去掉=?，然后用eval计算
                calc_expr = clean_expr.replace('×', '*').replace('=?', '')
                result = eval(calc_expr)
                print(f"计算结果: {result}")
                return result
            except Exception as e:
                print(f"计算错误: {e}")
                return None

        if captcha_type.lower() == "multi_slide":
            # 解析并计算
            try:
                # ====================== 1. 从二进制流读取图片 ======================
                bg_np = np.frombuffer(img_bytes, np.uint8)
                bg = cv2.imdecode(bg_np, cv2.IMREAD_GRAYSCALE)  # 背景灰度图

                slider_np = np.frombuffer(small_img_bytes, np.uint8)
                slider = cv2.imdecode(slider_np, cv2.IMREAD_GRAYSCALE)  # 滑块灰度图

                # ====================== 2. 滑块预处理（去白色/透明背景） ======================
                # 阈值处理：把背景变成纯黑，只保留滑块主体
                _, slider_mask = cv2.threshold(slider, 240, 255, cv2.THRESH_BINARY_INV)
                slider = cv2.bitwise_and(slider, slider, mask=slider_mask)

                # ====================== 3. 关键：只在 Y 坐标附近搜索（你已提供gap_y） ======================
                slider_h = slider.shape[0]
                bg_h, bg_w = bg.shape[:2]

                # 截取背景图中 缺口Y 上下一小条区域（极大提升准确率和速度）
                y_start = max(0, gap_y - 5)  # 往上留5像素容错
                y_end = min(bg_h, gap_y + slider_h + 5)  # 往下覆盖滑块高度
                bg_roi = bg[y_start:y_end, :]

                # ====================== 4. 模板匹配（最准算法） ======================
                result = cv2.matchTemplate(bg_roi, slider, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                # ====================== 5. 最终 X 坐标 ======================
                gap_x = max_loc[0]
                return gap_x
            except Exception as e:
                print(f"识别错误: {e}")
                return None
        if captcha_type.lower() == "block_puzzle":
            # 解析并计算
            try:
                bg_np = np.frombuffer(img_bytes, np.uint8)
                bg_img = cv2.imdecode(bg_np, cv2.IMREAD_COLOR)
                if bg_img is None:
                    raise ValueError("背景图解析失败")

                # 缺口拼图块
                gap_np = np.frombuffer(small_img_bytes, np.uint8)
                gap_img = cv2.imdecode(gap_np, cv2.IMREAD_COLOR)
                if gap_img is None:
                    raise ValueError("缺口图解析失败")
                gap_h, gap_w = gap_img.shape[:2]

                # ---------------------- 2. 灰度 + 边缘预处理 ----------------------
                bg_gray = cv2.cvtColor(bg_img, cv2.COLOR_BGR2GRAY)
                gap_gray = cv2.cvtColor(gap_img, cv2.COLOR_BGR2GRAY)

                # 边缘检测，弱化颜色影响，强化形状匹配
                bg_edges = cv2.Canny(bg_gray, 50, 150)
                gap_edges = cv2.Canny(gap_gray, 50, 150)

                # ---------------------- 3. 模板匹配找缺口位置 ----------------------
                # 使用 CCOEFF_NORMED 匹配，适合边缘图
                result = cv2.matchTemplate(bg_edges, gap_edges, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                # 缺口在背景图上的左上角坐标
                gap_x, gap_y = max_loc
                gap_center_x = gap_x + gap_w // 2  # 缺口中心x坐标

                # 找拼图滑块的初始位置（这里假设滑块在左侧边缘，你可以根据实际场景修改）
                # 这里用缺口图的左边缘作为滑块初始位置，或者你可以自己指定
                slider_initial_x = 0 + gap_w // 2  # 滑块初始中心x（示例：左侧对齐）

                # ---------------------- 4. 计算需要滑动的距离 ----------------------
                slide_distance = gap_center_x - slider_initial_x  # 水平滑动距离

                return slide_distance
            except Exception as e:
                print(f"识别错误: {e}")
                return None

    @staticmethod
    def base64_to_bytes(base64_str):
        if not base64_str:
            return None
        # 移除base64头部标识
        if "," in base64_str:
            base64_str = base64_str.split(",")[-1]
        # base64 转 字节
        img_bytes = base64.b64decode(base64_str)
        return img_bytes

    def captcha_validate(self, captcha_config, ctx=None, session=None):
        spider_status, trace_url, content, attach_info_list = "FAILED", None, None, []
        if not captcha_config.get("enable", True):
            return spider_status, trace_url, content, attach_info_list
        self.logger.info(f"【{self.task_id}】【captcha】开始自动处理验证码")
        steps = captcha_config.get("steps", [])
        for _ in range(5):
            temp_ctx = {}
            if ctx:
                temp_ctx = copy.deepcopy(ctx)
            for step in steps:
                temp_step = copy.deepcopy(step)
                url = self.render(temp_step.get("url", ""), temp_ctx)
                method = temp_step.get("method", "get").lower()
                temp_step['headers'].update({k: self.render(value, temp_ctx) for k, value in temp_step.get("headers", {}).items()})
                base_url, data = self.parse_entrance_url_payload(url, method)
                is_save = temp_step.get("issave", True)
                is_return_content = temp_step.get("response_type", 'json') == 'image' or temp_step.get("response_type", 'json') == 'file'
                # 发送请求
                self.logger.info(f"【{self.task_id}】【captcha】进入【{temp_step.get('name','')}】请求：{base_url}")
                req_status, trace_url, content, attach_info_list = self._request(temp_step, base_url, data, is_save=is_save,
                                                                                 session=session,is_return_content=is_return_content)
                if req_status == "FAILED":
                    spider_status = "FAILED"
                    self.logger.error(f"【{self.task_id}】【captcha】请求出错：{base_url}")
                    return spider_status,trace_url, content,attach_info_list
                if req_status == "NOT_FIND":
                    spider_status = "FAILED"
                    self.logger.error(f"【{self.task_id}】【captcha】请求不存在：{base_url}")
                    return spider_status, trace_url, content, attach_info_list
                spider_status = req_status
                if attach_info_list:
                    temp_ctx.update(attach_info_list[0])
                # # 如果是图片二进制流
                if temp_step.get("response_type", 'json') == 'image':
                    temp_ctx['img_str'] = base64.b64encode(content).decode()
                if not isinstance(content, bytes):
                    extract_dict = self._extract_fields(content, temp_step.get('fields', {}),base_url=base_url)[-1]
                    if temp_step.get('fields', {}) and not extract_dict:
                        spider_status = "FAILED"
                        self.logger.error(f"【{self.task_id}】【captcha】 提取字段失败")
                        break
                    if extract_dict:
                        temp_ctx.update(extract_dict[0])
                if "img_str" in temp_ctx:
                    img_bytes = self.base64_to_bytes(temp_ctx["img_str"])
                    small_img_bytes = self.base64_to_bytes(temp_ctx.get("small_img_str", None))
                    code = self.classfy_ocr(img_bytes, captcha_type=temp_step.get('captcha_config', {}).get('type', 'abc_num'),small_img_bytes=small_img_bytes,gap_y=int(temp_ctx.get('y_pos','0')))
                    if not isinstance(code, dict):
                        temp_ctx["captcha_code"] = str(code)
                    else:
                        temp_ctx["captcha_code"] = str(code)
                        temp_ctx.update(code)
                    if "encrypt" in step:
                        tmp_encrypt_code = ""
                        for encrypt_item in step.get("encrypt", []):
                            copy_encrypt_item = copy.deepcopy(encrypt_item)
                            tmp_encrypt_code = self.render(copy_encrypt_item.get('value', tmp_encrypt_code), temp_ctx)
                            copy_encrypt_item = {k: self.render(value, temp_ctx) for k, value in copy_encrypt_item.items()}
                            tmp_encrypt_code = self.common_encrypt(tmp_encrypt_code, copy_encrypt_item)

                        temp_ctx["captcha_code"] = tmp_encrypt_code
                    temp_ctx.pop("img_str", None)
                    self.logger.info(f"【{self.task_id}】验证码识别结果：{code}")
                if "check_success" in temp_step:
                    temp_content = content
                    if isinstance(temp_content, bytes):
                        temp_content = temp_content.decode(errors="ignore")
                    resp_txt = json.dumps(temp_content) if isinstance(temp_content, dict) else temp_content
                    if temp_step.get("check_success", '') in resp_txt:
                        spider_status = "SUCCESS"
                        self.logger.info(f"【{self.task_id}】【captcha】验证结果成功")
                    else:
                        spider_status = "FAILED"
                        self.logger.error(f"【{self.task_id}】【captcha】验证结果失败：{temp_content}")
                        break
                if "check_fail" in temp_step:
                    temp_content = content
                    if isinstance(temp_content, bytes):
                        temp_content = temp_content.decode(errors="ignore")
                    resp_txt = json.dumps(temp_content) if isinstance(temp_content, dict) else temp_content
                    if temp_step.get("check_fail", '') in resp_txt:
                        spider_status = "FAILED"
                        self.logger.error(f"【{self.task_id}】【captcha】验证结果失败：{temp_content}")
                        break
                time.sleep(2)
            if spider_status=="SUCCESS" or spider_status =='OUTlIMIT':
                break
        return spider_status, trace_url, content, attach_info_list


    @staticmethod
    def md5_encrypt(text: str, salt: str = "") -> str:
        """
        MD5 加密（不可逆哈希）
        :param text: 要加密的字符串
        :param salt: 盐值（可选）
        :return: 32位小写MD5字符串
        """
        # 1. 拼接原文 + 盐值，并编码为 bytes（必须转bytes才能加密）
        data = (text + salt).encode("utf-8")
        # 2. 执行MD5哈希计算
        md5_result = hashlib.md5(data)
        # 3. 转换为16进制字符串返回
        return md5_result.hexdigest()

    @staticmethod
    def sha_encrypt(text: str, algorithm: str = "sha256", salt: str = "") -> str:
        """
        SHA 系列加密
        :param text: 原文
        :param algorithm: 算法：sha1 / sha256 / sha512
        :param salt: 盐值
        :return: 哈希结果
        """
        # 拼接原文并转bytes
        data = (text + salt).encode("utf-8")
        # 动态获取哈希对象
        hash_obj = getattr(hashlib, algorithm)(data)
        return hash_obj.hexdigest()

    @staticmethod
    def hmac_sha256(text: str, key: str) -> str:
        """
        HMAC-SHA256 带密钥加密（防篡改，接口sign专用）
        :param text: 要签名的字符串
        :param key: 密钥（后端给的固定字符串）
        :return: 签名字符串
        """
        # 原文转bytes
        msg = text.encode("utf-8")
        # 密钥转bytes
        key = key.encode("utf-8")

        # 执行HMAC加密
        hmac_obj = hmac.new(key, msg, hashlib.sha256)
        return hmac_obj.hexdigest()

    @staticmethod
    def base64_encode(text,encode_type='utf-8'):
        """
        Base64编码
        :param text: 原文
        :return:
        """
        return base64.b64encode(text.encode(encode_type)).decode()

    @staticmethod
    def base64_decode(text,encode_type='utf-8'):
        """
        Base64解码
        :param text: 原文
        :return:
        """
        return base64.b64decode(text).decode(encode_type)

    @staticmethod
    def url_encode(text):
        """
        URL编码（处理中文&特殊字符）
        :param text: 原文
        :return:
        """
        return quote(text)

    @staticmethod
    def url_decode(text):
        """
        URL解码
        :param text: 原文
        :return:
        """
        return unquote(text)

    @staticmethod
    def replace_str(text, src_str, dest_str):
        """
        字符串子字符串替换
        :param text: 原文
        :param src_str: 原子字符串
        :param dest_str: 目标子字符串
        :return:
        """
        return re.sub(src_str, dest_str, text)

    @staticmethod
    def truncate_str(text, start_index, end_index):
        """
        截断字符串
        :param text: 原文
        :param start_index: 起始索引
        :param end_index: 目标索引
        :return:
        """
        if not start_index:
            start_index = 0
        if not end_index:
            end_index = len(text)
        # 边界容错：防止索引越界、负数
        start_index = max(0, start_index)
        end_index = min(len(text), end_index)
        return text[start_index:end_index]

    @staticmethod
    def aes_encrypt(data: str, key: str, mode, iv='', padding='pkcs5') -> str:
        """
        AES 加密
        :param data: 明文字符串
        :param key: 密钥字符串（16/24/32位）
        :param iv: 偏移量，ECB模式填空串
        :param mode: 模式 AES.MODE_CBC / AES.MODE_ECB
        :param padding: 填充方式 PKCS7Padding / PKCS5Padding
        :return: base64 密文
        """
        # 字符串转字节
        key_bytes = key.encode("utf-8")
        iv_bytes = iv.encode("utf-8")
        data_bytes = data.encode("utf-8")

        # 初始化加密器
        if mode == AES.MODE_ECB:
            cipher = AES.new(key_bytes, mode)
        else:
            cipher = AES.new(key_bytes, mode, iv_bytes)

        # 填充 + 加密 + base64
        pad_data = pad(data_bytes, AES.block_size, style=padding)
        encrypt_bytes = cipher.encrypt(pad_data)
        return base64.b64encode(encrypt_bytes).decode("utf-8")

    @staticmethod
    def aes_decrypt(cipher_data: str, key: str, mode, iv='', padding='pkcs5') -> str:
        """
        AES 解密
        :param cipher_data: base64 密文字符串
        :param key: 密钥字符串
        :param iv: 偏移量，ECB模式填空串
        :param mode: 模式 AES.MODE_CBC / AES.MODE_ECB
        :param padding: 填充方式
        :return: 明文字符串
        """
        key_bytes = key.encode("utf-8")
        iv_bytes = iv.encode("utf-8")

        # base64 解码
        encrypt_bytes = base64.b64decode(cipher_data)

        # 初始化解密器
        if mode == AES.MODE_ECB:
            cipher = AES.new(key_bytes, mode)
        else:
            cipher = AES.new(key_bytes, mode, iv_bytes)

        # 解密 + 去填充
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        origin_bytes = unpad(decrypt_bytes, AES.block_size, style=padding)
        return origin_bytes.decode("utf-8")

    @staticmethod
    def rsa_encrypt(data: str, pub_key_content: str, padding="PKCS1v15") -> str:
        """
        RSA 公钥加密
        :param data: 明文字符串
        :param pub_key_content: RSA公钥完整字符串
        :param padding: 填充模式 PKCS1v15 / OAEP
        :return: base64 密文
        """
        # 导入公钥
        pub_key = RSA.import_key(pub_key_content)
        # 选择填充模式
        if padding.upper() == "OAEP":
            cipher = PKCS1_OAEP.new(pub_key)
        else:
            cipher = PKCS1_v1_5.new(pub_key)
        # 加密 + base64
        encrypt_bytes = cipher.encrypt(data.encode("utf-8"))
        return base64.b64encode(encrypt_bytes).decode("utf-8")

    @staticmethod
    def rsa_decrypt(cipher_data: str, pri_key_content: str, padding="PKCS1v15") -> str:
        """
        RSA 私钥解密
        :param cipher_data: base64 密文字符串
        :param pri_key_content: RSA私钥完整字符串
        :param padding: 填充模式 PKCS1v15 / OAEP
        :return: 明文字符串
        """
        # 导入私钥
        pri_key = RSA.import_key(pri_key_content)
        # base64解码
        encrypt_bytes = base64.b64decode(cipher_data)
        # 选择填充解密
        if padding.upper() == "OAEP":
            cipher = PKCS1_OAEP.new(pri_key)
            decrypt_bytes = cipher.decrypt(encrypt_bytes)
        else:
            cipher = PKCS1_v1_5.new(pri_key)
            decrypt_bytes = cipher.decrypt(encrypt_bytes, sentinel=b"")

        return decrypt_bytes.decode("utf-8")

    def common_encrypt(self, text, encrypt_dict):
        encrypt_type = encrypt_dict.get('type', '').lower()
        """
        {
                    "type":"aes",
                    "key":"qnbyzzwmdgghmcnm",
                    "mode":"ecb",
                    "padding":"pkcs7"

                }
        """
        if encrypt_type == 'md5':
            return self.md5_encrypt(text, encrypt_dict.get('salt', ''))
        elif encrypt_type == 'sha':
            return self.sha_encrypt(text, encrypt_dict.get('algorithm', ''), encrypt_dict.get('salt', ''))
        elif encrypt_type == 'hmac':
            return self.hmac_sha256(text, encrypt_dict.get('key', ''))
        elif encrypt_type == 'base64':
            return self.base64_encode(text,encrypt_dict.get("encode",'utf-8'))
        elif encrypt_type == 'url':
            return self.url_encode(text)
        elif encrypt_type == 'replace':
            return self.replace_str(text, encrypt_dict.get('origin', ''), encrypt_dict.get('dest', ''))
        elif encrypt_type == 'truncate':
            return self.truncate_str(text, encrypt_dict.get('start', 0), encrypt_dict.get('end', len(text)))
        elif encrypt_type == 'aes':
            mode = encrypt_dict.get('mode', 'cbc').lower()
            if mode == 'cbc':
                mode = AES.MODE_CBC
            elif mode == 'ecb':
                mode = AES.MODE_ECB
            elif mode == "gcm":
                mode = AES.MODE_GCM
            elif mode == "ctr":
                mode = AES.MODE_CTR
            else:
                mode = AES.MODE_CBC
            return self.aes_encrypt(text, encrypt_dict.get('key', ''), mode, encrypt_dict.get('iv', ''),
                                    encrypt_dict.get('padding', ''))
        elif encrypt_type == 'rsa':
            return self.rsa_encrypt(text, encrypt_dict.get('pub_key', 0), encrypt_dict.get('padding', 0))
        else:
            return text

    def common_decrypt(self, text, decrypt_dict):
        decrypt_type = decrypt_dict.get('type', '').lower()
        """
        {
                    "type":"aes",
                    "key":"qnbyzzwmdgghmcnm",
                    "mode":"ecb",
                    "padding":"pkcs7"

                }
        """
        if decrypt_type == 'base64':
            return self.base64_decode(text,decrypt_dict.get("encode",'utf-8'))
        elif decrypt_type == 'url':
            return self.url_decode(text)
        elif decrypt_type == 'replace':
            return self.replace_str(text, decrypt_dict.get('origin', ''), decrypt_dict.get('dest', ''))
        elif decrypt_type == 'truncate':
            return self.truncate_str(text, decrypt_dict.get('start', 0), decrypt_dict.get('end', len(text)))
        elif decrypt_type == 'aes':
            mode = decrypt_dict.get('mode', 'cbc').lower()
            if mode == 'cbc':
                mode = AES.MODE_CBC
            elif mode == 'ecb':
                mode = AES.MODE_ECB
            elif mode == "gcm":
                mode = AES.MODE_GCM
            elif mode == "ctr":
                mode = AES.MODE_CTR
            else:
                mode = AES.MODE_CBC
            return self.aes_decrypt(text, decrypt_dict.get('key', ''), mode, decrypt_dict.get('iv', ''),
                                    decrypt_dict.get('padding', ''))
        elif decrypt_type == 'rsa':
            return self.rsa_decrypt(text, decrypt_dict.get('pri_key', 0), decrypt_dict.get('padding', 0))
        else:
            return text

    def build_final_url(self, rule_list):
        """
        根据规则列表自动生成最终URL
        兼容旧格式：[条件, 真URL, 假URL]
        支持新格式（多层if-elif-else）：[[条件1, URL1], [条件2, URL2], ..., 默认URL]
        :param rule_list: 规则列表
        :return: 最终生成的URL
        """
        # ======================
        # 旧格式：单层判断（完全兼容原来逻辑）
        # ======================
        if len(rule_list) == 3 and not isinstance(rule_list[0], (list, tuple)):
            condition = rule_list[0]
            url_true = rule_list[1]
            url_false = rule_list[2]

            try:
                check_result = eval(condition)
            except Exception as e:
                raise ValueError(f"判断表达式执行失败: {condition}") from e

            return url_true if check_result else url_false

        # ======================
        # 新格式：多层 if-elif-else
        # ======================
        if not rule_list:
            raise ValueError("规则列表不能为空")

        # 最后一项是默认URL，前面是所有条件
        default_url = rule_list[-1]
        condition_rules = rule_list[:-1]

        # 逐条匹配，满足即返回
        for idx, rule in enumerate(condition_rules):
            if not isinstance(rule, (list, tuple)) or len(rule) != 2:
                raise ValueError(f"第{idx + 1}条规则格式错误，必须为 [条件, URL]")

            cond, url = rule
            try:
                is_match = eval(cond)
            except Exception as e:
                raise ValueError(f"第{idx + 1}条条件执行失败: {cond}") from e

            if is_match:
                return url

        # 所有条件不满足 → 返回默认URL
        return default_url

    def _extract_fields(self, content, fields_config, begin_date: str = None, base_url: str = None):
        """
        通用字段提取（支持多结果返回）
        :param content: 待提取内容（HTML/JSON字符串）
        :param fields_config: 字段提取配置
        :param begin_date: 开始日期（YYYYMMDD格式），用于日期范围校验
        :return: 列表，每个元素是包含各字段解析结果的字典
        """
        # 首先提取所有字段的结果
        field_results = {}
        remove_index_list = []
        extract_status = "FAILED"

        temp_results = []

        const_field_list_dict={}

        multi_field_list_dict = {}

        for field_name, field_cfg in fields_config.items():
            # 空配置直接返回失败结果
            if not field_cfg or not field_cfg.get("value"):
                extract_status = "FAILED"
                self.logger.error(f"【{self.task_id}】字段 {field_name} 不存在提取规则")
                return extract_status, None

            extract_type = field_cfg.get("type", "xpath").lower()
            extract_expr = field_cfg.get("value")
            is_null = field_cfg.get("isnull", False)
            result = []

            try:
                from lxml import etree
                # XPath提取（HTML）
                if extract_type == "xpath":
                    html = etree.HTML(content)
                    ##判断xpath表达式里是否存在textall()
                    if extract_expr.strip().endswith("textall()"):
                        COMMENT_REG = re.compile(r'<!--[\s\S]*?-->', re.MULTILINE)
                        content = COMMENT_REG.sub('', content)
                        html = etree.HTML(content)
                        extract_expr = extract_expr.strip().rstrip('textall()').rstrip('/')
                        target_nodes = html.xpath(extract_expr)
                        clean_text_list = []
                        NEWLINE_TAGS = {'p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr'}
                        for node in target_nodes:
                            # 提取当前节点下所有子孙文本节点（解决文本分割问题）
                            if isinstance(node, etree._Element):
                                parts = []

                                def traverse(node):
                                    # 不是元素节点跳过
                                    if not isinstance(node, etree._Element):
                                        return

                                    # 提取自身文本
                                    if node.text:
                                        txt = node.text.strip()
                                        if txt:
                                            parts.append(txt)

                                    # 遍历子节点
                                    for child in node:
                                        # 安全获取标签名
                                        tag = child.tag if isinstance(child.tag, str) else ''

                                        # 如果是块级标签，插入换行
                                        if tag in NEWLINE_TAGS:
                                            parts.append('\n')

                                        # 递归提取
                                        traverse(child)

                                    # 提取尾部文本
                                    if node.tail:
                                        txt = node.tail.strip()
                                        if txt:
                                            parts.append(txt)

                                traverse(node)
                                # 拼接
                                combined_text = ''.join(
                                    [part for part in parts if part])
                                # # 合并连续空格/换行，最终清理
                                # clean_text = re.sub(r'\s+', ' ', combined_text)
                                # clean_text_list.append(clean_text)
                                clean_text_list.append(combined_text)
                        elements = clean_text_list
                    else:
                        elements = html.xpath(extract_expr)

                    if elements:
                        result = [etree.tostring(e, encoding="utf-8").decode("utf-8").strip() if isinstance(e,
                                                                                                            etree._Element) else str(
                            e).strip() for e in elements]

                # JSONPath提取
                elif extract_type == "jsonpath":
                    json_data = json.loads(content) if isinstance(content, str) else content
                    # jsonpath_expr = jsonpath_parse(extract_expr)
                    # elements = [match.value for match in jsonpath_expr.find(json_data)]
                    elements = jsonpath.jsonpath(json_data, extract_expr)
                    if not elements:
                        elements =[]
                    if elements:
                        result = [str(e).strip() if e or isinstance(e,int) else "" for e in elements]


                # 正则提取
                elif extract_type == "regex":
                    matches = re.findall(extract_expr, content, re.S)
                    if matches:
                        # 处理分组匹配
                        if isinstance(matches[0], tuple):
                            result = [m[0] for m in matches if m[0]]
                        else:
                            result = [m for m in matches if m]

                elif extract_type == "const":
                    const_field_list_dict.update({field_name:extract_expr})
                    continue
                for cfg_key in field_cfg.keys():
                    ##结果继续xpath
                    if cfg_key == "xpath" and field_cfg.get("xpath", '') and result:
                        formatted = []
                        for item in result:
                            if not item or not item.strip():
                                formatted.append("")
                                continue
                            html = etree.HTML(item)
                            xpath_extract_expr = field_cfg.get("xpath", '')
                            if xpath_extract_expr.strip().endswith("textall()"):
                                COMMENT_REG = re.compile(r'<!--[\s\S]*?-->', re.MULTILINE)
                                item = COMMENT_REG.sub('', item)
                                html = etree.HTML(item)
                                xpath_extract_expr = xpath_extract_expr.strip().rstrip('textall()').rstrip('/')
                                target_nodes = html.xpath(xpath_extract_expr)
                                clean_text_list = []
                                NEWLINE_TAGS = {'p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr'}
                                for node in target_nodes:
                                    # 提取当前节点下所有子孙文本节点（解决文本分割问题）
                                    if isinstance(node, etree._Element):
                                        parts = []

                                        def traverse(node):
                                            # 不是元素节点跳过
                                            if not isinstance(node, etree._Element):
                                                return

                                            # 提取自身文本
                                            if node.text:
                                                txt = node.text.strip()
                                                if txt:
                                                    parts.append(txt)

                                            # 遍历子节点
                                            for child in node:
                                                # 安全获取标签名
                                                tag = child.tag if isinstance(child.tag, str) else ''

                                                # 如果是块级标签，插入换行
                                                if tag in NEWLINE_TAGS:
                                                    parts.append('\n')

                                                # 递归提取
                                                traverse(child)

                                            # 提取尾部文本
                                            if node.tail:
                                                txt = node.tail.strip()
                                                if txt:
                                                    parts.append(txt)

                                        traverse(node)
                                        # 拼接
                                        combined_text = ''.join(
                                            [part for part in parts if part])
                                        # # 合并连续空格/换行，最终清理
                                        # clean_text = re.sub(r'\s+', ' ', combined_text)
                                        # clean_text_list.append(clean_text)
                                        clean_text_list.append(combined_text)
                                elements = clean_text_list
                            else:
                                elements = html.xpath(xpath_extract_expr)

                            if elements:
                                formatted.extend(
                                    [etree.tostring(e, encoding="utf-8").decode("utf-8").strip() if isinstance(e,
                                                                                                               etree._Element) else str(
                                        e).strip() for e in elements])
                        result = formatted

                    ##继续jsonpath
                    if cfg_key == "jsonpath" and field_cfg.get("jsonpath", '') and result:
                        formatted = []
                        for item in result:
                            json_data = json.loads(item) if isinstance(item, str) else item
                            # jsonpath_expr = jsonpath_parse(field_cfg.get("jsonpath", ''))
                            # elements = [match.value for match in jsonpath_expr.find(json_data)]

                            elements = jsonpath.jsonpath(json_data, field_cfg.get("jsonpath", ''))
                            if not elements:
                                elements = []
                            if elements:
                                formatted.extend([str(e).strip() if e or isinstance(e,int) else "" for e in elements])
                        result = formatted

                    # 解密
                    if cfg_key == "decrypt" and field_cfg.get('decrypt', []) and result:
                        formatted = []
                        for item in result:
                            for decrypt_item in field_cfg.get('decrypt', []):
                                item = self.common_decrypt(item, decrypt_item)
                            formatted.append(item)
                        result = formatted

                    ##正则处理
                    if cfg_key == "regex" and field_cfg.get("regex", '') and result:
                        formatted = []
                        for item in result:
                            match_pat = re.search(field_cfg.get("regex", ''), item, re.S)
                            if match_pat:
                                formatted.append(match_pat.group(1))
                            else:
                                formatted.append("")
                        result = formatted

                    # 加密
                    if cfg_key == "encrypt" and field_cfg.get('encrypt', []) and result:
                        formatted = []
                        for item in result:
                            for encrypt_item in field_cfg.get('encrypt', []):
                                item = self.common_encrypt(item, encrypt_item)
                            formatted.append(item)
                        result = formatted

                ##提取额外变量
                if field_cfg.get("extra", {}):
                    temp_extract_status, temp_results = self._extract_fields(content, field_cfg.get("extra", {}),
                                                                             base_url=base_url)

                ##判断真假
                if field_cfg.get("ifelse", []) and result:
                    formatted = []

                    if temp_results:
                        for item, temp_item in zip(result, temp_results):
                            field_condition = []
                            for condition_item in field_cfg.get("ifelse", []):
                                if isinstance(condition_item,(list)):
                                    sub_field_condition=[]
                                    for sub_condition_item in condition_item:
                                        sub_formatted_item = sub_condition_item.replace("${url}", str(item))
                                        sub_field_condition.append(self.render(sub_formatted_item, temp_item))
                                    field_condition.append(sub_field_condition)
                                else:
                                    formatted_item = condition_item.replace("${url}", str(item))
                                    field_condition.append(self.render(formatted_item, temp_item))
                            formatted.append(self.build_final_url(field_condition))
                    else:
                        for item in result:
                            field_condition = []
                            for condition_item in field_cfg.get("ifelse", []):
                                formatted_item = condition_item.replace("${url}", str(item))
                                field_condition.append(formatted_item)
                            formatted.append(self.build_final_url(field_condition))

                    result = formatted

                if field_cfg.get("isbalance", False) and result:
                    formatted = []
                    for item in result:
                        check_item = self.clean_unbalanced_brackets(item)
                        if check_item:
                            formatted.append(check_item)
                    result = formatted

                if field_cfg.get("isclean", False) and result:
                    formatted = []
                    for item in result:
                        clean_item = re.sub(r'\s+', '', item)
                        if clean_item:
                            formatted.append(clean_item.strip('-'))
                    result = formatted

                # 时间戳转化
                if field_cfg.get("istimestamp", False) and result:
                    formatted = []
                    for item in result:
                        formatted_item = self.timestamp_to_str(item)
                        if formatted_item:
                            formatted.append(formatted_item)
                    result = formatted

                # 日期格式化
                if field_cfg.get("format") == "date" and result:
                    formatted = []
                    is_default = False
                    if len(set(result)) >=2:
                        is_default = True
                    for item in result:
                        formatted_item = self.extract_date_to_yyyymmdd(item)
                        if formatted_item and self.is_yyyymmdd(formatted_item):
                            formatted.append(formatted_item)
                            if begin_date and self.compare_yyyymmdd_safe(formatted_item, begin_date) < 0:
                                remove_index_list.append(1)
                            else:
                                remove_index_list.append(0)
                        elif is_default:
                            formatted.append("")
                            remove_index_list.append(1)
                    result = formatted

                # 补全链接
                if field_cfg.get("base", '') and result:
                    formatted = []
                    for item in result:
                        formatted_item = item.strip('.').strip('/')
                        if formatted_item.startswith("http://") or formatted_item.startswith("https://"):
                            formatted.append(formatted_item)
                            continue
                        formatted.append(field_cfg.get("base") + formatted_item)
                    result = formatted

                # 替换链接
                if field_cfg.get("replace", '') and result:
                    formatted = []
                    if temp_results:
                        for item, temp_item in zip(result, temp_results):
                            formatted_item = field_cfg.get("replace").replace("${url}", str(item))
                            formatted.append(self.render(formatted_item, temp_item))
                    else:
                        for item in result:
                            formatted_item = item
                            formatted.append(field_cfg.get("replace").replace("${url}", str(formatted_item)))
                    result = formatted

                # 补全前缀路径
                if field_cfg.get("prepath", False) and result:
                    formatted = []
                    for item in result:
                        if item.startswith("http://") or item.startswith("https://"):
                            formatted.append(item)
                            continue
                        formatted.append(urljoin(base_url, item))
                    result = formatted


                if field_cfg.get("request", {}) and result:
                    formatted = []
                    for item in result:
                        self.logger.info(f"【{self.task_id}】字段 {field_name} 进入单独请求：{item}")
                        temp_spider_status, temp_trace_url, temp_content, temp_attach_info_list=self._request(field_cfg.get("request",{}),item)
                        if temp_spider_status=='SUCCESS':
                            formatted.append(temp_content)
                    result = formatted

                if field_cfg.get("ismulti", False) and result:
                    self.logger.info(f"【{self.task_id}】字段 {field_name} 提取成功,设置多值")
                    multi_field_list_dict.update({field_name:result[0]})
                    continue


            except Exception as e:
                self.logger.error(f"【{self.task_id}】字段 {field_name} 提取失败 [{extract_expr}]: {str(e)}")
                if field_cfg.get("candidate",{}):
                    candidate_extract_status, candidate_output=self._extract_fields(content, {field_name:field_cfg.get("candidate",{})},  begin_date,base_url)
                    if candidate_extract_status=='SUCCESS' and candidate_output:
                        self.logger.info(f"【{self.task_id}】字段 {field_name} 候选提取成功")
                        field_results[field_name] = [candidate_item[field_name] for candidate_item in candidate_output]
                        continue
                extract_status = "FAILED"
                return extract_status, None
            if not result:
                self.logger.error(f"【{self.task_id}】字段 {field_name} 提取为空 [{extract_expr}]")
                if field_cfg.get("candidate",{}):
                    candidate_extract_status, candidate_output=self._extract_fields(content, {field_name:field_cfg.get("candidate",{})},  begin_date,base_url)
                    if candidate_extract_status=='SUCCESS' and candidate_output:
                        self.logger.info(f"【{self.task_id}】字段 {field_name} 候选提取成功")
                        field_results[field_name] = [candidate_item[field_name] for candidate_item in candidate_output]
                        continue
                if not is_null:
                    extract_status = "FAILED"
                    return extract_status, None
                continue
            field_results[field_name] = result

        if not field_results:
            extract_status = "NO_RESULT"
            return extract_status, []

        # 判断各解析字段数量是否相同
        field_lengths = [len(results) for results in field_results.values()]
        if len(set(field_lengths)) > 1:
            self.logger.error(f"【{self.task_id}】字段提取结果数量不一致: {field_lengths}")
            extract_status = "FAILED"
            return extract_status, None

        # 构建列表形式的输出
        output = []
        for i in range(field_lengths[0]):
            item = {}
            for field_name, results in field_results.items():
                # 如果该字段有对应位置的结果，使用结果，否则使用空字符串
                if i < len(results):
                    item[field_name] = results[i]
                else:
                    item[field_name] = ""
            item['trace_index'] = i
            if remove_index_list and remove_index_list[i]:
                continue
            for const_name,const_value in  const_field_list_dict.items():
                item[const_name]=const_value
            for multi_name,multi_value in  multi_field_list_dict.items():
                item[multi_name]=multi_value
            output.append(item)
            extract_status = "SUCCESS"
        if not output:
            self.logger.info(f"【{self.task_id}】字段过滤后为空")
            extract_status = "NO_RESULT"
        return extract_status, output

    @staticmethod
    def handle_calc(origin_str: str) -> str:
        """
        处理字符串中的 @calc:{} 计算表达式
        匹配 @calc:{表达式} 格式，提取表达式并运算，无匹配则原样返回
        :param origin_str: 原始待处理字符串
        :return: 处理后的新字符串
        """
        # 正则匹配规则：匹配 @calc:{任意内容}，非贪婪提取大括号内的运算表达式
        pattern = re.compile(r'@calc:\{(.+?)\}')

        def calc_match(match):
            """
            正则匹配回调函数，执行表达式计算
            :param match: 正则匹配对象
            :return: 计算结果字符串，异常则返回原匹配内容
            """
            # 获取大括号内的数学表达式
            expr = match.group(1)
            try:
                # 执行数学运算并转为字符串
                return str(eval(expr))
            except Exception:
                # 表达式错误/运算异常，保留原内容不做修改
                return match.group(0)

        # 全局替换所有匹配到的计算表达式
        return pattern.sub(calc_match, origin_str)

    def _generate_sub_list_tasks(self, pagination_config, content, is_full, current_page,temp_time_ctx=None):
        """
        生成子list任务元信息（不执行）
        :param pagination_config: 分页配置
        :param content: 入口页响应内容
        :param is_full: 是否全量
        :param current_page: 当前页码
        :param temp_time_ctx: 临时替换变量字典
        :return: 子list任务列表
        """
        pagination = pagination_config
        url_template = pagination.get("url", "")
        extract_status = "FAILED"
        if not pagination.get("enable", False):
            extract_status = "NO_RESULT"
            return extract_status, []
        if not url_template:
            return extract_status, []
        if not temp_time_ctx:
            copy_temp_time_ctx={}
        else:
            copy_temp_time_ctx = copy.deepcopy(temp_time_ctx)

        # 解析分页配置
        page_param = pagination.get("page_param", {})
        max_page = int(pagination.get("max_page",100000))
        start_page = page_param.get("start", 0)
        p_current = int(page_param.get("current", 0))
        per_num = int(page_param.get("per_num", 10))
        step_num = int(page_param.get("step", 1))
        offset_num = int(page_param.get("offset", 0))

        extra_param_setting=pagination.get("extra", {})

        # 提取总页数/总条数
        total_page = None
        total_count = None
        is_extract_next = None

        # 提取总页码
        if page_param.get("total"):
            extract_status, total_page_str = self._extract_fields(content, {"total": page_param["total"]})
            if extract_status == "FAILED":
                return extract_status, []
            total_page = int(total_page_str[0]["total"]) if (
                        total_page_str and total_page_str[0].get("total")) else 0
            print('total_page', total_page)

        # 提取总条数
        if page_param.get("count"):
            extract_status, total_count_str = self._extract_fields(content, {"count": page_param["count"]})
            if extract_status == "FAILED":
                return extract_status, []
            total_count = int(total_count_str[0]["count"]) if (
                        total_count_str and total_count_str[0].get("count")) else 0
            print('total_count', total_count)

        # 提取下一页
        if page_param.get("next"):
            extract_status, is_next_str = self._extract_fields(content, {"next": page_param["next"]})
            if is_next_str:
                is_extract_next = True
            else:
                is_extract_next = False
            print('is_extract_next', is_extract_next)

        if extra_param_setting:
            extract_status, page_extra_params = self._extract_fields(content, extra_param_setting)
            if extract_status == "FAILED":
                return extract_status, []
            copy_temp_time_ctx.update(page_extra_params[0])

        # 计算最终总页数
        if total_count == 0 or total_page==0:
            extract_status = "NO_DATA"
            return extract_status, []
        if total_count and not total_page:
            total_page = (total_count + per_num - 1) // per_num
        if not total_page and is_extract_next is None:
            extract_status = "FAILED"
            return extract_status, []
        if is_extract_next:
            print("p_current",p_current)
            total_page = p_current + 2 -start_page if p_current >= current_page else current_page + 2 -start_page
        elif is_extract_next is False:
            total_page = p_current+1  -start_page if p_current >= current_page else current_page +1   -start_page
        print('total_page', total_page)
        final_total = start_page + total_page
        max_page = start_page +max_page
        next_page = p_current + 1
        if current_page > p_current:
            next_page = current_page + 1
        if not is_full:
            final_total = next_page + 1
        print('next_page', next_page)

        print('final_total', final_total)


        final_total = min(start_page + total_page, final_total, max_page)

        print('final_total', final_total)


        # 生成子任务
        sub_tasks = []
        for page in range(next_page, final_total):
            sub_url = self.handle_calc(url_template.replace("${page_param}", str(page*step_num+offset_num)))
            sub_tasks.append({
                "entrance_url": self.render(sub_url,copy_temp_time_ctx) if copy_temp_time_ctx else sub_url,
                "current_page": page,
                "is_turn": 1 if not is_full or is_extract_next else 0,
            })
        extract_status = "SUCCESS"
        return extract_status, sub_tasks

    def get_next_month(self,date_str):
        # 解析为 datetime
        dt = datetime.strptime(date_str, "%Y%m%d")

        # 计算下一个月（纯 datetime 实现）
        if dt.month == 12:
            next_month = datetime(dt.year + 1, 1, dt.day, dt.hour, dt.minute, dt.second)
        else:
            next_month = datetime(dt.year, dt.month + 1, dt.day, dt.hour, dt.minute, dt.second)

        # 格式化输出
        return next_month.strftime("%Y%m%d")

    def _run_list_request(self, entrance_url, config, task_params):
        """执行列表接口请求"""
        spider_status = "FAILED"
        sub_tasks = []
        if not entrance_url:
            self.logger.error(f"【{self.task_id}】缺少列表接口URL")
            return spider_status, None
        temp_time_ctx = {}
        time_sub_tasks = [] ##时间查询子任务
        temp_entrance_url = entrance_url
        begin_date = self.extract_date_to_yyyymmdd(task_params.get("begin_date", ''))
        temp_starttime_pat = re.search('\$\{(starttime@[^}]+)\}',entrance_url)
        temp_endtime_pat = re.search('\$\{(endtime@[^}]+)\}', entrance_url)
        # start_date_str, end_date_str = '20100101','20100201'
        start_date_str, end_date_str = '20260523','20260623'
        if begin_date:
            start_date_str = begin_date
            end_date_str = self.get_next_month(start_date_str)
        if temp_starttime_pat:
            temp_starttime=temp_starttime_pat.group(1)
            starttime_field_name,starttime_attr_name,starttime_attr_value = temp_starttime.split("@")
            url_start_time = ''
            if starttime_attr_name == 'time' and starttime_attr_value:
                url_start_time = datetime.strptime(start_date_str, "%Y%m%d").strftime(starttime_attr_value)
            elif starttime_attr_name == 'value' and starttime_attr_value:
                url_start_time = starttime_attr_value
            elif starttime_attr_name == 'timestamp' and starttime_attr_value:
                if int(starttime_attr_value) == 13:
                    url_start_time = str(int(datetime.strptime(start_date_str, "%Y%m%d").timestamp() * 1000))
                if int(starttime_attr_value) == 13:
                    url_start_time = str(int(datetime.strptime(start_date_str, "%Y%m%d").timestamp()))
            elif starttime_attr_name == 'curtime' and starttime_attr_value:
                url_start_time = datetime.now().strftime(starttime_attr_value)
            elif starttime_attr_name == 'curtimestamp' and starttime_attr_value:
                target_dt = datetime.now()
                if int(starttime_attr_value) == 13:
                    url_start_time = str(int(target_dt.timestamp() * 1000))  # 13位毫秒
                else:
                    url_start_time = str(int(target_dt.timestamp()))
            if url_start_time:
                entrance_url = entrance_url.replace("${"+temp_starttime+"}",url_start_time)
                temp_time_ctx.update({"starttime": "${starttime@value@"+url_start_time+"}"})
        if temp_endtime_pat:
            temp_endtime = temp_endtime_pat.group(1)
            endtime_field_name, endtime_attr_name, endtime_attr_value = temp_endtime.split("@")
            url_end_time=''
            if endtime_attr_name == 'time' and endtime_attr_value:
                url_end_time = datetime.strptime(end_date_str, "%Y%m%d").strftime(endtime_attr_value)
            elif endtime_attr_name == 'value' and endtime_attr_value:
                url_end_time = endtime_attr_value
            elif endtime_attr_name == 'timestamp' and endtime_attr_value:
                if int(endtime_attr_value) == 13:
                    url_end_time = str(int(datetime.strptime(end_date_str, "%Y%m%d").timestamp() * 1000))
                if int(endtime_attr_value) == 13:
                    url_end_time = str(int(datetime.strptime(end_date_str, "%Y%m%d").timestamp()))
            elif endtime_attr_name == 'curtime' and endtime_attr_value:
                url_end_time = datetime.now().strftime(endtime_attr_value)
            elif endtime_attr_name == 'curtimestamp' and endtime_attr_value:
                target_dt = datetime.now()
                if int(endtime_attr_value) == 13:
                    url_end_time = str(int(target_dt.timestamp() * 1000))  # 13位毫秒
                else:
                    url_end_time = str(int(target_dt.timestamp()))
            if url_end_time:
                entrance_url = entrance_url.replace("${" + temp_endtime + "}", url_end_time)
                temp_time_ctx.update({"endtime": "${endtime@value@"+url_end_time+"}"})

        if temp_starttime_pat or temp_endtime_pat:
            current_date=datetime.now().strftime("%Y%m%d")
            while self.compare_yyyymmdd_safe(start_date_str,current_date)<0 and self.compare_yyyymmdd_safe(end_date_str,current_date)<0:
                is_sub_time_task = False
                next_temp_entrance_url =temp_entrance_url
                if temp_starttime_pat:
                    start_date_str=self.get_next_month(start_date_str)
                    url_start_time = ''
                    if starttime_attr_name == 'time' and starttime_attr_value:
                        url_start_time = datetime.strptime(start_date_str, "%Y%m%d").strftime(starttime_attr_value)
                    elif starttime_attr_name == 'timestamp' and starttime_attr_value:
                        if int(starttime_attr_value) == 13:
                            url_start_time = str(int(datetime.strptime(start_date_str, "%Y%m%d").timestamp() * 1000))
                        if int(starttime_attr_value) == 13:
                            url_start_time = str(int(datetime.strptime(start_date_str, "%Y%m%d").timestamp()))
                    if url_start_time:
                        next_temp_entrance_url =next_temp_entrance_url.replace("${" + temp_starttime + "}", "${starttime@value@" + url_start_time + "}")
                        is_sub_time_task = True
                if temp_endtime_pat:
                    end_date_str = self.get_next_month(end_date_str)
                    url_end_time = ''
                    today = datetime.now().date()
                    end_date = datetime.strptime(end_date_str, "%Y%m%d").date()
                    if endtime_attr_name == 'time' and endtime_attr_value:
                        if end_date >= today:
                            url_end_time = datetime.now().strftime(
                                endtime_attr_value)
                        else:
                            url_end_time = datetime.strptime(end_date_str, "%Y%m%d").strftime(endtime_attr_value)
                    elif endtime_attr_name == 'timestamp' and endtime_attr_value:
                        if end_date >= today:
                            target_dt = datetime.now()
                        else:
                            target_dt = datetime.strptime(end_date_str, "%Y%m%d")
                        if int(endtime_attr_value) == 13:
                            url_end_time = str(int(target_dt.timestamp() * 1000))
                        if int(endtime_attr_value) == 13:
                            url_end_time = str(int(target_dt.timestamp()))
                    if url_end_time:
                        next_temp_entrance_url = next_temp_entrance_url.replace("${" + temp_endtime + "}", "${endtime@value@" + url_end_time + "}")
                        is_sub_time_task = True
                if is_sub_time_task:
                    # print('1111111111111111111111111111111111')
                    time_sub_tasks.append({
                        "entrance_url": next_temp_entrance_url,
                        "current_page": -1,
                        "is_turn": 1,
                    })


        self.logger.info(f"【{self.task_id}】开始执行List任务 | 入口URL: {entrance_url}")
        list_config = config.get("list", {})

        base_url, payload = self.parse_entrance_url_payload(entrance_url,list_config.get('method','GET'))
        # 1. 请求并保存结果
        is_list_start = False
        if not list_config.get("captcha", {}).get('startcheck', ''):
            is_list_start = True
        elif list_config.get("captcha", {}).get('startcheck', '') in entrance_url:
            is_list_start = True
        if is_list_start and list_config.get("captcha", {}) and list_config.get("captcha", {}).get("enable", True):
            session = requests.Session()
            ctx = {"list_url": entrance_url}
            spider_status, trace_url, content, attach_info_list = self.captcha_validate(list_config.get("captcha", {}),
                                                                                     ctx=ctx, session=session)
            if session:
                session.close()

            if spider_status =='OUTlIMIT':
                spider_status = 'SUCCESS'
        else:
            spider_status, trace_url, content, attach_info_list = self._request(list_config, base_url, payload)
        if spider_status == "FAILED" or not content:
            self.logger.error(f"【{self.task_id}】【list】请求入口页失败")
            spider_status = "FAILED"
            return spider_status, None
        if spider_status == "NOT_FIND":
            return spider_status, None

        decrypt_config = list_config.get("decrypt", [])
        for decrypt_dict in decrypt_config:
            content = self.common_decrypt(content, decrypt_dict)
        encrypt_config = list_config.get("encrypt", [])
        for encrypt_dict in encrypt_config:
            content = self.common_encrypt(content, encrypt_dict)

        # 2. 生成子list任务
        pagination_config = copy.deepcopy(config.get("pagination", {}))
        is_turn = int(task_params.get("is_turn", 1))
        is_full = int(task_params.get("is_full", 1))
        current_page = int(task_params.get("current_page", -1))
        ##列表可能存在get变post请求，不返回页码，需要增加一轮请求，获取页码
        if list_config.get('page', {}) and (is_turn or is_full):
            base_page_url, page_payload = self.parse_entrance_url_payload(list_config.get('page', {}).get('url',
                                                                                                          ''),
                                                                          list_config.get('page', {}).get('method',
                                                                                                          'GET'))
            page_spider_status, page_trace_url, page_content, page_attach_info_list = self._request(
                list_config.get('page', {}), base_page_url, page_payload, is_save=False)
            if page_spider_status == "FAILED" or not page_content:
                self.logger.error(f"【{self.task_id}】【list】请求获取页码失败")
                spider_status="FAILED"
                return spider_status, None
            decrypt_config = list_config.get('page', {}).get("decrypt", [])
            for decrypt_dict in decrypt_config:
                page_content = self.common_decrypt(page_content, decrypt_dict)
            encrypt_config = list_config.get('page', {}).get("encrypt", [])
            for encrypt_dict in encrypt_config:
                page_content = self.common_encrypt(page_content, encrypt_dict)
        else:
            page_content = content
        if is_turn:
            extract_status, sub_tasks = self._generate_sub_list_tasks(pagination_config, page_content, is_full,
                                                                      current_page, temp_time_ctx= temp_time_ctx)
            if extract_status == "FAILED":
                return extract_status, None

            if extract_status =='NO_DATA':
                self.logger.info(f"【{self.task_id}】【list】获取到记录总量为空")
                spider_status = "NO_RESULT"
                if time_sub_tasks:
                    crawler_result = {
                        "data": {
                            "trace": trace_url,
                            "url_info": [],
                            "sub_info": time_sub_tasks,
                        }
                    }
                    spider_status = "SUCCESS"
                    return spider_status, crawler_result
                return spider_status, {"data": {"trace": trace_url}}


        # 3. 动态提取字段
        fields_config = list_config.get("fields", {})
        extract_status, field_results = self._extract_fields(content, fields_config, base_url=base_url)
        if extract_status == "FAILED" or field_results is None:
            self.logger.error(f"【{self.task_id}】【list】字段提取失败")
            spider_status = "FAILED"
            return spider_status, {"data": {"trace": trace_url}}
        if extract_status == "NO_RESULT" or not field_results:
            self.logger.info(f"【{self.task_id}】【list】字段提取为空")
            spider_status = "NO_RESULT"
            return spider_status, {"data": {"trace": trace_url}}

        spider_status = "SUCCESS"
        self.logger.info(f"【{self.task_id}】完成执行List任务 | 入口URL: {entrance_url}")
        # 4.构造子任务结果
        if time_sub_tasks:
            sub_tasks.extend(time_sub_tasks)
        crawler_result = {
            "data": {
                "trace": trace_url,
                "url_info": field_results,
                "sub_info": sub_tasks,
            }
        }

        return spider_status, crawler_result

    @staticmethod
    def _extract_ext(file_str: str) -> str:
        """内部辅助函数：从字符串（URL/文件名）中提取扩展名"""
        if not file_str or not isinstance(file_str, str):
            return ""

        # 步骤1：处理URL - 提取路径部分并解码
        parsed_url = urlparse(file_str)
        ##如果url存在查询参数
        # if parsed_url.netloc and parsed_url.query:
        #     return ""
        file_path = parsed_url.path if parsed_url.path else file_str

        # 步骤2：解码URL编码字符（如%20、中文编码）
        decoded_path = unquote(file_path)

        # 步骤3：提取文件名（兼容Windows/Linux路径分隔符）
        file_name = os.path.basename(decoded_path).strip()

        # 步骤4：提取扩展名（支持多扩展名，排除隐藏文件/末尾点）
        if "." not in file_name or file_name.startswith("."):
            return ""

        # 步骤5：定义需要优先匹配的多后缀扩展名（按长度从长到短排序）
        multi_extensions = [
                "tar.gz", "tar.bz2", "tar.xz", "zip.gz", "rar.gz",
                "docx", "xlsx", "pptx", "pdf", "csv", "json", "xml",
                "jpg", "png", "gif", "mp4", "mp3", "txt", "log"
        ]

        # 步骤6：优先匹配多后缀
        for ext in multi_extensions:
            ext_with_dot = f".{ext}"
            if file_name.endswith(ext_with_dot):
                return ext

        # 步骤7：匹配单后缀（处理未在multi_extensions中的自定义后缀）
        # 分割文件名和后缀（os.path.splitext会拆分最后一个.）
        _, ext = os.path.splitext(file_name)
        if ext and re.search("\.[a-zA-Z0-9]+$",ext):
            if ext.lower() not in [".html",".aspx",".jsp",'.htm','.jhtml',".do",".action"]:
                return ext.lstrip(".")  # 去掉前缀的.，返回纯后缀

        # 无后缀的情况
        return ""

    def _download_attachment_file(self,attachment_name, attachment_url,attachment_ext,request_config):
        download_status = "FAILED"
        attachments_item={}
        proxy_dict=None
        download_mode=request_config.get("mode", "REQUESTS").upper()
        headers = request_config.get("headers", {})
        is_redirect = request_config.get("isredirect", True)
        is_verify = request_config.get("isverify", True)
        if not headers:
            headers= {}
        if "user-agent" in headers:
            headers["user-agent"] = self.random_user_agent
        else:
            headers["User-Agent"] = self.random_user_agent
        for retry_num in range(self.retry_times):
            if download_mode == 'REQUESTS':
                proxy_dict = {'http': 'http://t14306903178173:wp12345@j708.kdltps.com:15818/', 'https': 'http://t14306903178173:wp12345@j708.kdltps.com:15818/'}
                local_path=None
                try:
                    resp = requests.get(attachment_url, headers=headers,timeout=self.timeout, stream=True,proxies=proxy_dict,verify=is_verify,allow_redirects=is_redirect)
                    if int(resp.status_code) != 200:
                        if int(resp.status_code) == 404:
                            self.logger.error(
                                f"【{self.task_id}】【detail】附件文件【{attachment_name}】链接失效：{attachment_url}")
                            download_status = "SUCCESS"
                            attachments_item = {
                                "url": attachment_url,
                                "file_name": attachment_name,
                            }
                            break
                        print(resp.status_code)
                        raise ValueError("请求状态码不正确")
                    if not attachment_ext:
                        attachment_ext = self.get_file_type_by_headers(resp.headers)
                        if not attachment_ext:
                            attachments_item = {
                                "url": attachment_url,
                                "file_name": attachment_name,
                            }
                            self.logger.info(
                                f"【{self.task_id}】【detail】【{attachment_name}】 未提取到附件文件类型 URL: {attachment_url}")
                            download_status = "SUCCESS"
                            break
                    # 保存附件
                    filename = self._generate_unique_filename(attachment_url, attachment_ext)
                    if not os.path.exists(os.path.join(self.attachment_temp_dir, self.config_data_name)):
                        os.mkdir(os.path.join(self.attachment_temp_dir, self.config_data_name))
                    local_path = os.path.join(os.path.join(self.attachment_temp_dir, self.config_data_name), filename)
                    # 下载时添加大小限制
                    downloaded_size = 0
                    exceed_limit = False
                    with open(local_path, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            if chunk:
                                downloaded_size += len(chunk)
                                if downloaded_size > self.max_attachment_size:
                                    self.logger.info(
                                        f"【{self.task_id}】附件下载大小 {self.max_attachment_size / 1024 / 1024:.2f}MB 超过限制，停止下载")
                                    exceed_limit = True
                                    break  # 只退出循环，不删文件
                                f.write(chunk)
                    if exceed_limit and os.path.exists(local_path):
                        os.remove(local_path)
                        attachments_item = {
                            "url": attachment_url,
                            "file_name": attachment_name,
                        }
                        download_status = "SUCCESS"
                        break
                    file_url = local_path
                    attachments_item={
                        "file": file_url,
                        "url": attachment_url,
                        "file_name": attachment_name,
                    }
                    self.logger.info(
                        f"【{self.task_id}】【detail】【{attachment_name}】附件处理完成 | 本地路径: {local_path} | URL: {attachment_url}")
                    download_status = "SUCCESS"
                    break
                except IncompleteRead as e:
                    self.logger.error(f"【{self.task_id}】下载文件时出现错误: {str(e)}")
                    # 清理临时文件
                    if local_path and os.path.exists(local_path):
                        os.remove(local_path)
                    attachments_item = {
                        "url": attachment_url,
                        "file_name": attachment_name,
                    }
                    download_status = "SUCCESS"
                    continue
                except Exception as e:
                    self.logger.error(
                        f"【{self.task_id}】【detail】【{attachment_name}】附件处理失败 | URL: {attachment_url} | (重试 {retry_num + 1}/{self.retry_times})错误信息: {str(e)}")
                    download_status = "FAILED"
                    time.sleep(2)
            elif download_mode == "SELENIUM":  # 配置中写的SELENIUM，实际用Playwright
                try:
                    # proxy_dict = {'server': 'j708.kdltps.com:15818', 'username': 't14306903178173',
                    #               'password': 'wp12345'}
                    if not self.playwright:
                        # 固定常量配置
                        context_kwargs = {
                            "ignore_https_errors": True,
                            "locale": "zh-CN",
                            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                            "timezone_id": "Asia/Shanghai",
                            "viewport": ViewportSize(width=1920, height=1080),
                            "screen": {"width": 1920, "height": 1080}
                        }
                        self.playwright = sync_playwright().start()
                        self.browser = self.playwright.chromium.launch(headless=True, args=[
                            # 核心：禁用PDF预览器
                            "--disable-pdf-extension",
                        ])
                        self.context = self.browser.new_context(accept_downloads=True,proxy=proxy_dict, **context_kwargs)

                        self.context.add_init_script(script=self._build_fingerprint_init_script())
                    page = self.context.new_page()
                    # page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"})
                    download = None

                    def on_download(d):
                        nonlocal download
                        download = d

                    if attachment_ext.lower() in ["jpg", "jpeg", "png", "gif", "webp"]:
                        response = page.goto(attachment_url,timeout=self.timeout * 1000)
                        page.wait_for_load_state("networkidle",timeout=self.timeout * 1000)  # 等待网络请求完成
                        if response:
                            if int(response.status) != 200:
                                if int(response.status) == 404:
                                    self.logger.error(
                                        f"【{self.task_id}】, Playwright链接失效,URL: {attachment_url}")
                                    download_status = "SUCCESS"
                                    break
                                raise ValueError("请求状态码不正确")
                        else:
                            raise ValueError("Playwright未获取到HTTP响应")
                        filename = self._generate_unique_filename(attachment_url, attachment_ext)
                        if not os.path.exists(os.path.join(self.attachment_temp_dir, self.config_data_name)):
                            os.mkdir(os.path.join(self.attachment_temp_dir, self.config_data_name))
                        local_path = os.path.join(os.path.join(self.attachment_temp_dir, self.config_data_name), filename)
                        with open(local_path, "wb") as f:
                            f.write(response.body())
                    elif attachment_ext.lower() in ["html"]:
                        response = page.goto(attachment_url, timeout=self.timeout * 1000)
                        page.wait_for_load_state("networkidle",timeout=self.timeout * 1000)  # 等待网络请求完成
                        # time.sleep(10)
                        if response:
                            if int(response.status) != 200:
                                if int(response.status) == 404:
                                    self.logger.error(
                                        f"【{self.task_id}】, Playwright链接失效,URL: {attachment_url}")
                                    download_status = "SUCCESS"
                                    break
                                raise ValueError("请求状态码不正确")
                        else:
                            raise ValueError("Playwright未获取到HTTP响应")
                        filename = self._generate_unique_filename(attachment_url, attachment_ext)
                        if not os.path.exists(os.path.join(self.attachment_temp_dir, self.config_data_name)):
                            os.mkdir(os.path.join(self.attachment_temp_dir, self.config_data_name))
                        local_path = os.path.join(os.path.join(self.attachment_temp_dir, self.config_data_name),
                                                  filename)
                        with open(local_path, "w",encoding='utf-8') as f:
                            f.write(page.content())
                    else:
                        page.on("download", on_download)
                        page.goto("about:blank", timeout=self.timeout * 1000)
                        response = None
                        with page.expect_response(lambda resp: attachment_url in resp.url) as resp_info:
                            # JS 创建 a 标签下载
                            page.evaluate("""(url) => {
                                                const a = document.createElement('a');
                                                a.href = url;
                                                a.download = '';
                                                document.body.appendChild(a);
                                                a.click();
                                                setTimeout(() => a.remove(), 100);
                                            }""", attachment_url)

                        response = resp_info.value

                        page.wait_for_event("download", timeout=self.timeout * 1000)
                        if  not download:
                            self.logger.error(f"附件【{attachment_name}】下载失败：{attachment_url}")
                            download_status = "FAILED"
                            continue

                        if not attachment_ext:
                            if response:
                                attachment_ext = self.get_file_type_by_headers(response.headers)
                            if not attachment_ext:
                                attachments_item = {
                                    "url": attachment_url,
                                    "file_name": attachment_name,
                                }
                                self.logger.info(
                                    f"【{self.task_id}】【detail】【{attachment_name}】 未提取到附件文件类型 URL: {attachment_url}")
                                download_status = "SUCCESS"
                                break

                        # 保存附件
                        filename = self._generate_unique_filename(attachment_url, attachment_ext)
                        if not os.path.exists(os.path.join(self.attachment_temp_dir, self.config_data_name)):
                            os.mkdir(os.path.join(self.attachment_temp_dir, self.config_data_name))
                        local_path = os.path.join(os.path.join(self.attachment_temp_dir, self.config_data_name),
                                                  filename)
                        download.save_as(local_path)
                    file_url = local_path
                    attachments_item = {
                        "file": file_url,
                        "url": attachment_url,
                        "file_name": attachment_name,
                    }
                    self.logger.info(
                        f"【{self.task_id}】【detail】【{attachment_name}】附件处理完成 | 本地路径: {local_path} | URL: {attachment_url}")
                    download_status = "SUCCESS"
                    break
                except PlaywrightTimeoutError:
                    self.logger.error(
                        f"【{self.task_id}】, Playwright下载超时（链接可能失效/文件过大）,URL: {attachment_url}")
                    download_status = "SUCCESS"
                    break
                except Exception as e:
                    self.logger.error(
                        f"【{self.task_id}】Playwright请求失败(重试 {retry_num + 1}/{self.retry_times}): {e}")
                    download_status = "FAILED"
                    time.sleep(2)
                    import traceback
                    traceback.print_exc()

                finally:
                    # 关闭 Playwright 浏览器上下文
                    if self.context:
                        self.context.close()
                        self.context = None
                    if self.browser:
                        self.browser.close()
                        self.browser = None
                    if self.playwright:
                        self.playwright.stop()
                        self.playwright = None
            else:
                raise ValueError(f"不支持的请求模式: {download_mode}")
        return download_status, attachments_item

    def get_file_type_by_headers(self, headers):
        """
        只通过响应头判断文件类型：pdf / doc / docx / png / jpg / gif 等
        """
        # 1. 获取 Content-Type
        content_type = headers.get("Content-Type", "").lower()

        # 2. 映射表（MIME类型 → 文件类型）
        mime_map = {
            "application/pdf": "pdf",
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/vnd.ms-excel": "xls",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "image/png": "png",
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/gif": "gif",
            "image/bmp": "bmp",
            "image/webp": "webp",
            "application/zip": "zip",
            "application/x-rar-compressed": "rar",
            "application/rar": "rar",
            "application/x-7z-compressed": "7z"
        }

        # 先从 Content-Type 判断
        for mime, t in mime_map.items():
            if mime in content_type:
                return t

        # 3. 兜底：从 Content-Disposition 里的 filename 判断
        disp = headers.get("Content-Disposition", "")
        pattern = r'filename="([^"]+)"'
        suffix_match = re.search(pattern, disp)
        if suffix_match:
            encoded_str = suffix_match.group(1)
            # 解析 =?UTF-8?B?xxx?= 格式
            if encoded_str.startswith("=?UTF-8?B?") and encoded_str.endswith("?="):
                b64_data = encoded_str.replace("=?UTF-8?B?", "").replace("?=", "")
                try:
                    # base64解码
                    file_name = base64.b64decode(b64_data).decode("utf-8")
                    disp = file_name
                except Exception as e:
                    self.logger.error(f"【{self.task_id}】响应头提取文件类型解码失败：{str(e)}")
        if ".pdf" in disp:
            return "pdf"
        elif ".doc" in disp:
            return "doc"
        elif ".docx" in disp:
            return "docx"
        elif ".xls" in disp:
            return "xls"
        elif ".xlsx" in disp:
            return "xlsx"
        elif ".png" in disp:
            return "png"
        elif ".jpg" in disp or ".jpeg" in disp:
            return "jpg"
        elif ".gif" in disp:
            return "gif"
        elif ".zip" in disp:
            return "zip"
        elif ".rar" in disp:
            return "rar"
        elif ".txt" in disp:
            return "txt"

        return ""


    @staticmethod
    def is_file_size_over(target_size: str, max_size: str) -> bool:
        """
        判断文件大小是否超过指定最大大小
        :param target_size: 文件大小字符串，如 "1024KB", "5Mb", "200000"
        :param max_size: 最大允许大小，如 "2MB", "1GB"
        :return: 超过返回 True，否则返回 False
        """
        # 单位换算基准：全部转为字节 B
        unit_map = {
            'B': 1,
            'K': 1024,
            'M': 1024 ** 2,
            'G': 1024 ** 3,
            'T': 1024 ** 4
        }

        def convert_to_bytes(size_str: str) -> int:
            """内部工具函数：把带单位的大小转为字节数"""
            if not size_str:
                return 0

            # 统一转大写，去掉空格，兼容 Kb / KB / kb 等写法
            s = size_str.strip().upper()

            # 提取数字和单位
            num_str = ''
            unit = 'B'  # 默认单位字节

            for c in s:
                if c.isdigit() or c == '.':
                    num_str += c
                else:
                    # 遇到非数字，取第一个字母作为单位
                    if c in unit_map:
                        unit = c
                    break

            try:
                num = float(num_str)
            except:
                raise ValueError(f"无法解析大小：{size_str}")

            return int(num * unit_map[unit])

        # 转换为字节后比较
        target_bytes = convert_to_bytes(target_size)
        max_bytes = convert_to_bytes(max_size)

        return target_bytes > max_bytes


    def _run_detail_request(self, entrance_url: str, config: Dict[str, Any], task_params: Dict[str, Any]) -> Any:
        """执行详情接口请求"""
        field_result_dict = {}
        spider_status = "FAILED"
        crawler_result = None
        attachments_list = []
        if not entrance_url:
            self.logger.error(f"【{self.task_id}】缺少详情接口URL")
            return spider_status, None
        self.logger.info(f"【{self.task_id}】开始执行Detail任务 | 入口URL: {entrance_url}")
        detail_config = config.get("detail",{})
        base_url, payload = self.parse_entrance_url_payload(entrance_url,detail_config.get('method','GET'))
        attachment_config = detail_config.get("attachment", {})
        is_download_attach = attachment_config.get("enable", False)
        # 1. 请求并保存结果
        is_detail_start = False
        if not detail_config.get("captcha", {}).get('startcheck', ''):
            is_detail_start = True
        elif detail_config.get("captcha", {}).get('startcheck', '') in entrance_url:
            is_detail_start = True
        if is_detail_start and detail_config.get("captcha", {}) and detail_config.get("captcha", {}).get("enable", True):
            session = requests.Session()
            ctx = {"list_url": entrance_url}
            spider_status, trace_url, content, attachment_field_results_list = self.captcha_validate(
                detail_config.get("captcha", {}), ctx=ctx, session=session)
            if session:
                session.close()
            if spider_status =='OUTlIMIT':
                spider_status = 'SUCCESS'
        else:
            spider_status, trace_url, content,attachment_field_results_list = self._request(detail_config, base_url, payload)
        if spider_status == "FAILED" or not content:
            self.logger.error(f"【{self.task_id}】【detail】请求入口页失败")
            spider_status = "FAILED"
            return spider_status, None
        if spider_status == "NOT_FIND":
            return spider_status, crawler_result
        if f"{base_url} is a file requests" in content:
            attachment_url = base_url
            attachment_name = base_url.split('/')[-1]
            if not attachment_url or not attachment_name:
                self.logger.error(f"【{self.task_id}】【detail】附件字段提取不一致")
                spider_status = "FAILED"
                return spider_status, None
            attachment_ext = self._extract_ext(attachment_name)
            if not attachment_ext:
                attachment_ext = self._extract_ext(attachment_url)
            download_status, download_item = self._download_attachment_file(attachment_name, attachment_url,
                                                                                attachment_ext,
                                                                                request_config=attachment_config)
            if download_status == "FAILED":
                spider_status = "FAILED"
                return spider_status, crawler_result
            if download_item:
                attachments_list.append(download_item)
            spider_status = "SUCCESS"
            self.logger.info(f"【{self.task_id}】完成执行Detail任务 | 入口URL: {entrance_url}")
            crawler_result = {
                "source_site": config.get("source_site", ""),
                "industry": config.get("industry", "13"),
                "notice_type": config.get("notice_type", "1062"),
                "source_name": config.get("name", ""),
                "data": {"trace": trace_url,
                        "crawl_time": datetime.now().strftime("%Y%m%d"),
                        "detail_url": entrance_url,
                        "publish_time": task_params.get("begin_date", ""),
                        "content": "<body></body>",
                        "title": base_url,
                },
                "files": attachments_list
            }
            extra_info = json.loads(task_params.get('extra_info', '{}')) if isinstance(
                task_params.get('extra_info'), str) else task_params.get('extra_info', {})
            for key, value in extra_info.items():
                if key not in crawler_result['data']:
                    crawler_result['data'][key] = value
            return spider_status, crawler_result

        # 2. 动态提取字段
        fields_config = detail_config.get("fields", {})
        decrypt_config = detail_config.get("decrypt", [])
        for decrypt_dict in decrypt_config:
            content = self.common_decrypt(content, decrypt_dict)
        encrypt_config = detail_config.get("encrypt", [])
        for encrypt_dict in encrypt_config:
            content = self.common_encrypt(content, encrypt_dict)
        extract_status, field_results = self._extract_fields(content, fields_config, base_url=base_url)
        if extract_status == "FAILED" or field_results is None:
            self.logger.error(f"【{self.task_id}】【detail】字段提取失败")
            spider_status = "FAILED"
            return spider_status, {"data": {"trace": trace_url}}
        if extract_status == "NO_RESULT" or not field_results:
            self.logger.info(f"【{self.task_id}】【detail】字段提取为空")
            spider_status = "FAILED"
            return spider_status, {"data": {"trace": trace_url}}
        field_result_dict.update(field_results[0])
        extra_info = json.loads(task_params.get('extra_info', '{}')) if isinstance(task_params.get('extra_info'),
                                                                                   str) else task_params.get(
            'extra_info', {})
        for key, value in extra_info.items():
            if key not in field_result_dict:
                field_result_dict[key] = value
        field_result_dict.update({"trace": trace_url,
                                  "crawl_time": datetime.now().strftime("%Y%m%d"),
                                  "detail_url": entrance_url,
                            })
        # 3. 下载附件
        attachment_fields_config = attachment_config.get("fields", {})
        if is_download_attach:
            if "attach" in attachment_config:
                get_attach_config=attachment_config.get("attach",{})
                get_extract_status, get_field_results = self._extract_fields(content,
                                                                             get_attach_config.get("fields", {}),
                                                                             base_url=base_url)
                if get_extract_status == "FAILED" or not get_field_results:
                    self.logger.error(f"【{self.task_id}】【detail】附件请求字段提取失败")
                    # spider_status = "FAILED"
                    # if 'data' not in crawler_result:
                    #     crawler_result['data'] = {}
                    # crawler_result['data'].update({"trace": trace_url})
                    # return spider_status, crawler_result
                else:
                    get_attach_base_url, get_attach_payload = self.parse_entrance_url_payload(
                        self.render(get_attach_config.get('url', ''), get_field_results[0]),
                        get_attach_config.get('method', 'GET'))
                    self.logger.info(f"【{self.task_id}】【detail】附件单独请求URL:{get_attach_base_url}")
                    is_start = False
                    if not get_attach_config.get("captcha", {}).get('startcheck', ''):
                        is_start = True
                    elif get_attach_config.get("captcha", {}).get('startcheck', '') in get_attach_base_url or get_attach_config.get("captcha", {}).get('startcheck', '') in content:
                        is_start = True
                    if is_start and get_attach_config.get("captcha", {}) and get_attach_config.get("captcha", {}).get(
                            "enable",
                            True):
                        session = requests.Session()
                        ctx = {"list_url": get_attach_base_url}
                        spider_status, get_attach_trace_url, temp_content, _attachment_list_field_results = self.captcha_validate(get_attach_config.get("captcha", {}), ctx=ctx, session=session)
                        if session:
                            session.close()

                        if spider_status == 'FAILED':
                            self.logger.error(f"【{self.task_id}】【detail】附件单独请求验证码失败")
                            return spider_status, {"data": {"trace": trace_url}}
                        else:
                            content=temp_content
                            base_url = get_attach_base_url
                    else:
                        spider_status, get_attach_trace_url, temp_content, _attachment_list_field_results = self._request(
                            get_attach_config, get_attach_base_url, get_attach_payload,is_save=get_attach_config.get("issave",True))
                        if spider_status == "FAILED" or not content:
                            self.logger.error(f"【{self.task_id}】【detail】附件单独请求失败")
                        else:
                            content=temp_content
                            base_url = get_attach_base_url
            if "iframe" in attachment_config:
                iframe_extract_status,iframe_field_results = self._extract_fields(content,
                                                                                      {'iframe':attachment_config.get('iframe',{})},base_url=base_url)
                if iframe_extract_status == "FAILED" or not iframe_field_results:
                    self.logger.error(f"【{self.task_id}】【detail】附件iframe字段提取失败")
                    spider_status = "FAILED"
                    return spider_status, {"data": {"trace": trace_url}}
                for iframe_field_result in iframe_field_results:
                    spider_status, iframe_trace_url, content, attach_info_list = self._request(attachment_fields_config, iframe_field_result.get('iframe'),is_save=False)
                    if spider_status == "FAILED" or not content:
                        self.logger.error(f"【{self.task_id}】【detail】附件iframe请求失败")
                        spider_status = "FAILED"
                        return spider_status, {"data": {"trace": trace_url}}
                    attachment_extract_status, attachment_field_results = self._extract_fields(content,
                                                                                               attachment_fields_config,
                                                                                               base_url=self.parse_entrance_url_payload(iframe_field_result.get('iframe'))[0])
                    if "request" in fields_config.get('content',{}):
                        content_attachment_extract_status, content_attachment_field_results = self._extract_fields(field_result_dict.get("content",""),
                                                                                                   attachment_fields_config,
                                                                                                   base_url=base_url)
                        if content_attachment_field_results:
                            attachment_field_results.extend(content_attachment_field_results)
                    if attachment_extract_status == "FAILED" or attachment_field_results is None:
                        self.logger.error(f"【{self.task_id}】【detail】附件字段提取失败")
                        spider_status = "FAILED"
                        return spider_status, None
                    if attachment_extract_status == "NO_RESULT" or not attachment_field_results:
                        self.logger.info(f"【{self.task_id}】【detail】附件字段提取为空")
                        spider_status = "NO_RESULT"
                    for attachment_field_item in attachment_field_results:
                        attachment_url = attachment_field_item.get("url")
                        attachment_name = attachment_field_item.get("name")
                        attachment_size = attachment_field_item.get("size")
                        if not attachment_url or not attachment_name:
                            self.logger.error(f"【{self.task_id}】【detail】附件字段提取不一致")
                            spider_status = "FAILED"
                            return spider_status, None
                        if attachment_url.strip().startswith('mailto') or attachment_url.strip().startswith('file:'):
                            self.logger.info(f"【{self.task_id}】【detail】附件URL存在链接连接或者本地链接：{attachment_url}")
                            continue
                        if attachment_size and self.is_file_size_over(attachment_size,str(self.max_attachment_size)):
                            self.logger.error(
                                f"【{self.task_id}】【detail】附件文件[{attachment_name}]大小已经超过指定阈值")
                            attachments_list.append({'url': attachment_url, 'file_name': attachment_name})
                            continue
                        attachment_ext = self._extract_ext(attachment_name)
                        if not attachment_ext:
                            attachment_ext = self._extract_ext(attachment_url)
                            if not attachment_ext and attachment_fields_config.get('name',{}).get('ishtml',False):
                                attachment_ext = "html"
                        if attachment_url:
                            download_status, download_item = self._download_attachment_file(attachment_name,
                                                                                            attachment_url,
                                                                                            attachment_ext,request_config=attachment_config)
                            if download_status == "FAILED":
                                spider_status = "FAILED"
                                return spider_status, crawler_result
                            if download_item:
                                attachments_list.append(download_item)
            else:
                attachment_extract_status, attachment_field_results = self._extract_fields(content,
                                                                                           attachment_fields_config,base_url=base_url)
                if "request" in fields_config.get('content', {}):
                    content_attachment_extract_status, content_attachment_field_results = self._extract_fields(
                        field_result_dict.get("content", ""),
                        attachment_fields_config,
                        base_url=base_url)
                    if content_attachment_field_results:
                        attachment_field_results.extend(content_attachment_field_results)
                if attachment_extract_status == "FAILED" or attachment_field_results is None:
                    self.logger.error(f"【{self.task_id}】【detail】附件字段提取失败")
                    spider_status = "FAILED"
                    return spider_status, None
                if attachment_extract_status == "NO_RESULT" or not attachment_field_results:
                    if attachment_field_results_list:
                        self.logger.info(f"【{self.task_id}】【detail】附件采用点击型文件")
                        attachment_field_results = attachment_field_results_list
                    else:
                        self.logger.info(f"【{self.task_id}】【detail】附件字段提取为空")
                        spider_status = "NO_RESULT"
                for attachment_field_item in attachment_field_results:
                    attachment_url = attachment_field_item.get("url").replace('\\',"/")
                    attachment_name = attachment_field_item.get("name")
                    attachment_size = attachment_field_item.get("size")
                    if not attachment_url or not attachment_name:
                        self.logger.error(f"【{self.task_id}】【detail】附件字段提取不一致")
                        spider_status = "FAILED"
                        return spider_status, None
                    if attachment_url.strip().startswith('mailto') or attachment_url.strip().startswith('file:'):
                        self.logger.info(f"【{self.task_id}】【detail】附件URL存在链接连接或者本地链接：{attachment_url}")
                        continue

                    if attachment_size and self.is_file_size_over(attachment_size, str(self.max_attachment_size)):
                        self.logger.error(
                            f"【{self.task_id}】【detail】附件文件[{attachment_name}]大小已经超过指定阈值")
                        attachments_list.append({'url': attachment_url, 'file_name': attachment_name})
                        continue
                    attachment_ext = self._extract_ext(attachment_name)
                    if not attachment_ext:
                        attachment_ext = self._extract_ext(attachment_url)
                        if not attachment_ext and attachment_fields_config.get('name', {}).get('ishtml', False):
                            attachment_ext = "html"
                    if attachment_url:
                        download_item = {}
                        is_start=False
                        if not attachment_config.get("captcha", {}).get('startcheck',''):
                            is_start = True
                        elif attachment_config.get("captcha", {}).get('startcheck','') in attachment_url or attachment_config.get("captcha", {}).get('startcheck', '') in content:
                            is_start=True
                        if is_start and attachment_config.get("captcha", {}) and attachment_config.get("captcha", {}).get("enable",
                                                                                                             True):
                            session = requests.Session()
                            ctx = {"list_url": attachment_url}
                            download_status, download_trace_url, download_content, download_list = self.captcha_validate(
                                attachment_config.get("captcha", {}), ctx=ctx, session=session)
                            if session:
                                session.close()

                            if download_status == 'FAILED':
                                self.logger.error(
                                    f"【{self.task_id}】【detail】附件文件【{attachment_name}】下载失败：{attachment_url}")
                                download_item = {
                                    "url": attachment_url,
                                    "file_name": attachment_name,
                                }
                            if  download_status =='OUTlIMIT':
                                self.logger.error(
                                    f"【{self.task_id}】【detail】附件文件【{attachment_name}】文件超限：{attachment_url}")
                                download_item = {
                                    "url": attachment_url,
                                    "file_name": attachment_name,
                                }
                            elif download_status == 'SUCCESS':
                                if not attachment_ext and download_list:
                                    attachment_ext=download_list[0].get("attach_ext","")
                                if not attachment_ext:
                                    self.logger.error(
                                        f"【{self.task_id}】【detail】【{attachment_name}】附件文件类型提取为空")
                                    attachments_list.append({'url': attachment_url, 'file_name': attachment_name})
                                    continue
                                # 保存附件
                                filename = self._generate_unique_filename(attachment_url, attachment_ext)
                                if not os.path.exists(os.path.join(self.attachment_temp_dir, self.config_data_name)):
                                    os.mkdir(os.path.join(self.attachment_temp_dir, self.config_data_name))
                                local_path = os.path.join(os.path.join(self.attachment_temp_dir, self.config_data_name),
                                                          filename)
                                with open(local_path, "wb") as f:
                                    f.write(download_content)
                                file_url = local_path
                                download_item = {
                                    "file": file_url,
                                    "url": attachment_url,
                                    "file_name": attachment_name,
                                }
                                self.logger.info(
                                    f"【{self.task_id}】【detail】【{attachment_name}】附件处理完成 | 本地路径: {local_path} | URL: {attachment_url}")
                        else:
                            download_status,download_item=self._download_attachment_file(attachment_name,attachment_url,attachment_ext,request_config=attachment_config)
                        if download_status == "FAILED":
                            spider_status = "FAILED"
                            return spider_status, crawler_result
                        if download_item:
                            attachments_list.append(download_item)
        spider_status = "SUCCESS"
        self.logger.info(f"【{self.task_id}】完成执行Detail任务 | 入口URL: {entrance_url}")
        crawler_result = {
            "data": field_result_dict,
            "files": attachments_list,
            "source_site": config.get("source_site", ""),
            "industry": config.get("industry", "13"),
            "notice_type": config.get("notice_type", "1062"),
            "source_name": config.get("name", ""),
        }
        return spider_status, crawler_result

