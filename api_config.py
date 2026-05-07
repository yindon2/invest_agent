"""
企鹅奇才 · API 配置管理器
========================
管理用户的 API keys（Tushare, OpenAI 等），安全存储到 config.json。
"""
import os, json, shutil, urllib.request, urllib.error
from pathlib import Path

CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / 'config.json'
CONFIG_DEFAULT = CONFIG_DIR / 'config.default.json'

class ApiConfig:
    def __init__(self):
        self._data = self._load()

    def _load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        if CONFIG_DEFAULT.exists():
            shutil.copy(str(CONFIG_DEFAULT), str(CONFIG_FILE))

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get_all(self):
        return self._data.get('apis', {})

    def get(self, name, key='token'):
        apis = self._data.get('apis', {})
        api = apis.get(name, {})
        return api.get(key, '')

    def set(self, name, token, enabled=True):
        if 'apis' not in self._data:
            self._data['apis'] = {}
        if name in self._data['apis']:
            self._data['apis'][name]['token'] = token
            self._data['apis'][name]['enabled'] = enabled
        else:
            self._data['apis'][name] = {
                'name': name,
                'token': token,
                'enabled': enabled,
                'description': ''
            }
        self._save()

    def delete(self, name):
        self._data.get('apis', {}).pop(name, None)
        self._save()

    def status(self):
        """返回所有 API 的配置状态（隐藏完整 token，只显示前4位）"""
        apis = self._data.get('apis', {})
        result = {}
        for name, info in apis.items():
            token = info.get('token', '')
            masked = token[:4] + '*' * (len(token) - 4) if token and len(token) > 4 else ('' if not token else '****')
            result[name] = {
                'name': info.get('name', name),
                'configured': bool(token),
                'enabled': info.get('enabled', False),
                'masked': masked,
                'description': info.get('description', '')
            }
        return result

    def test_tushare(self):
        """测试 Tushare token 是否有效"""
        token = self.get('tushare', 'token')
        if not token:
            return {'ok': False, 'msg': '未配置 Tushare Token'}
        try:
            import tushare as ts
            ts.set_token(token)
            pro = ts.pro_api()
            df = pro.stock_basic(exchange='', list_status='L', fields='ts_code')
            count = len(df) if df is not None else 0
            if count > 0:
                return {'ok': True, 'msg': f'验证成功，可获取 {count} 只股票数据'}
            return {'ok': False, 'msg': 'Token 无效或未授权'}
        except ImportError:
            return {'ok': False, 'msg': '未安装 tushare 库 (pip install tushare)'}
        except Exception as e:
            return {'ok': False, 'msg': f'验证失败: {str(e)}'}

    def test_openai(self):
        """测试 OpenAI/Claude API key 是否有效"""
        key = self.get('openai', 'key')
        if not key:
            return {'ok': False, 'msg': '未配置 API Key'}
        if key.startswith('sk-') and len(key) > 20:
            return {'ok': True, 'msg': 'Key 格式正确（仅验证格式，未发起实际请求）'}
        return {'ok': False, 'msg': 'Key 格式不正确（应以 sk- 开头）'}

    def test_deepseek(self):
        """测试 DeepSeek API key 是否有效"""
        key = self.get('deepseek', 'key')
        if not key:
            return {'ok': False, 'msg': '未配置 DeepSeek API Key'}
        try:
            import urllib.request
            import json
            req = urllib.request.Request(
                'https://api.deepseek.com/v1/models',
                headers={'Authorization': f'Bearer {key}'},
                method='GET'
            )
            resp = urllib.request.urlopen(req, timeout=10)
            if resp.status == 200:
                return {'ok': True, 'msg': 'DeepSeek API 连接成功，Key 有效'}
            return {'ok': False, 'msg': f'API 返回异常: HTTP {resp.status}'}
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return {'ok': False, 'msg': 'Key 无效（HTTP 401 未授权）'}
            return {'ok': False, 'msg': f'API 测试失败: HTTP {e.code}'}
        except urllib.error.URLError as e:
            return {'ok': False, 'msg': f'无法连接 DeepSeek API: {e.reason}'}
        except ImportError:
            return {'ok': False, 'msg': 'urllib 不可用'}
        except Exception as e:
            return {'ok': False, 'msg': f'测试失败: {str(e)}'}


api_config = ApiConfig()
