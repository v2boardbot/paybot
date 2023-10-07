import requests
import urllib3
from lxml import etree
from typing import Union
import re
from utils import read_config


class Pay:
    def __init__(self, api, pid, key):
        self._api = api
        self._pid = pid
        self._key = key
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }
        self.session = requests.Session()
        self.login()

    def _request(self, method, url, **kwargs):
        urllib3.disable_warnings()
        res = self.session.request(method, url, verify=False, headers=self.headers, **kwargs)
        return res

    def query_info(self) -> Union[dict, str]:
        """
        查询账户余额，查询成功返回float，否则返回错误文本
        :return: float | str
        """
        # url = f'{self._api}/api.php?act=query&pid={self._pid}&key={self._key}'
        url = f'{self._api}/user/ajax2.php?act=getcount'
        res = self._request('get', url)
        obj = res.json()
        if obj['code'] == 0:
            # return f'查询结果:{obj["money"]} 元'
            data = {
                "今日收入": obj['order_today']['all'],
                "已结算余额": obj['settle_money'],
                "昨日收入": obj['order_lastday']['all'],
                "订单总数": obj['orders'],
                "今日订单": obj['orders_today']
            }
            return data
        elif obj['code'] == -3:
            result = self.login()
            if result is True:
                return self.query_info()
            else:
                return result
        else:
            return res.text

    def query_money(self) -> Union[dict, str]:
        url = f'{self._api}/user/apply.php'
        res = self._request('get', url)
        if res.text.find('./login.php') != -1:
            result = self.login()
            if result is True:
                return self.query_money()
            else:
                return result
        tree = etree.HTML(res.text)
        data = {
            '当前余额': ''.join(tree.xpath('//*[@id="content"]/div/div[2]/div/div[2]/form/div[4]/div/input/@value')),
            '可提现余额': ''.join(tree.xpath('//input[@name="tmoney"]/@value')),
        }
        return data

    def login(self):
        self.session = requests.Session()
        self._request('get', self._api)
        self.headers['referer'] = f'{self._api}/user/login.php'
        params = (
            ('m', 'key'),
        )
        # 获取csrf_token
        response = self._request('get', url=f'{self._api}/user/login.php', params=params)
        tree = etree.HTML(response.text)
        csrf_token = ''.join(tree.xpath('//input[@name="csrf_token"]/@value'))
        params = (
            ('act', 'login'),
        )
        data = {
            'type': '0',
            'user': self._pid,
            'pass': self._key,
            'csrf_token': csrf_token
        }
        url = f'{self._api}/user/ajax.php'
        response = self._request('post', url, data=data, params=params)
        try:
            if response.json()['code'] == 0: return True
            return response.json()
        except Exception as e:
            return f'error: {e}, response: {response.text}'

    def cash_out(self):
        params = (
            ('act', 'do'),
        )
        data = self.query_money()
        if isinstance(data, dict):
            money = data.get('可提现余额')
            try:
                money = int(float(money))
            except:
                return f'余额取整数失败，{money}'
        else:
            return f'获取余额错误，{data}'
        data = {
            'money': str(money),
            'submit': '\u7533\u8BF7\u63D0\u73B0'
        }
        self.headers['referer'] = f'{self._api}/user/apply.php'
        url = f'{self._api}/user/apply.php'
        response = self._request('post', url, params=params, data=data)
        result = re.findall("alert\('(.*?)'\)", response.text)
        if result:
            return ''.join(result) + f'\n提现金额:{money}'
        else:
            return response.text


pay_config = read_config().get('pay')
pay = Pay(pay_config.get('url'), pay_config.get('pid'), pay_config.get('key'))
