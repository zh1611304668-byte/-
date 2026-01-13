"""
纪念钞预约系统 - 独立自动填写程序
连接到你已经打开的浏览器，直接操作当前页面
不会重新加载页面，速度极快
"""

import json
import time
import asyncio
from playwright.async_api import async_playwright

class BrowserConnector:
    """连接到已打开的浏览器并自动填写"""
    
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.browser = None
        self.page = None
        
    async def connect_to_browser(self, cdp_url="http://localhost:9222"):
        """连接到已经打开的浏览器"""
        print(f"🔗 正在连接到浏览器: {cdp_url}")
        
        playwright = await async_playwright().start()
        try:
            # 连接到已运行的浏览器
            self.browser = await playwright.chromium.connect_over_cdp(cdp_url)
            
            # 获取所有打开的页面
            contexts = self.browser.contexts
            if not contexts:
                print("❌ 没有找到打开的页面")
                return False
                
            # 获取当前活动页面
            pages = contexts[0].pages
            if not pages:
                print("❌ 没有找到活动标签页")
                return False
                
            self.page = pages[-1]  # 使用最后一个标签页
            print(f"✅ 已连接到页面: {self.page.url}")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print("\n💡 请确保:")
            print("   1. 浏览器已经打开")
            print("   2. 浏览器以调试模式启动 (运行 start_browser.bat)")
            return False
    
    async def fill_form_ultra_fast(self):
        """超高速填写表单"""
        if not self.page:
            print("❌ 未连接到页面")
            return
            
        start_time = time.time()
        print("\n⚡ 开始超高速填写...")
        
        user_info = self.config['user_info']
        
        try:
            # 并发填写所有文本字段
            await asyncio.gather(
                # 姓名
                self.smart_fill(
                    ['input[name*="name" i]', 'input[placeholder*="姓名" i]'],
                    user_info['name']
                ),
                
                # 证件号码
                self.smart_fill(
                    ['input[name*="id" i]', 'input[placeholder*="证件" i]', 'input[placeholder*="身份证" i]'],
                    user_info['id_number']
                ),
                
                # 手机号
                self.smart_fill(
                    ['input[name*="phone" i]', 'input[name*="mobile" i]', 'input[placeholder*="手机" i]'],
                    user_info['phone']
                ),
                
                # 数量
                self.smart_fill(
                    ['input[type="number"]', 'input[name*="quantity" i]', 'input[placeholder*="数量" i]'],
                    str(self.config['quantity'])
                ),
                
                return_exceptions=True
            )
            
            # 选择证件类型
            try:
                await self.page.select_option('select', user_info['id_type'])
                print(f"  ✅ 证件类型: {user_info['id_type']}")
            except:
                pass
            
            # 选择兑换网点
            location = self.config['exchange_location']
            try:
                # 点击下拉框
                await self.page.click('select', timeout=1000)
                # 选择包含关键词的选项
                await self.page.select_option('select', label=location['name'])
                print(f"  ✅ 兑换网点: {location['name']}")
            except Exception as e:
                print(f"  ⚠️ 网点选择失败: {e}")
            
            elapsed = time.time() - start_time
            print(f"\n✅ 填写完成! 耗时: {elapsed:.3f} 秒")
            print("💡 请检查验证码并手动输入，然后点击提交\n")
            
        except Exception as e:
            print(f"\n❌ 填写失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def smart_fill(self, selectors, value):
        """智能填写 - 尝试多个选择器"""
        for selector in selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    await element.fill(value)
                    field_name = selector.split('[')[1].split('*=')[1].strip('"')
                    print(f"  ✅ {field_name}: {value}")
                    return True
            except:
                continue
        return False
    
    async def show_all_inputs(self):
        """显示页面所有输入框（调试用）"""
        print("\n=== 页面所有表单元素 ===")
        inputs = await self.page.query_selector_all('input, select, textarea')
        for i, inp in enumerate(inputs):
            name = await inp.get_attribute('name') or ''
            placeholder = await inp.get_attribute('placeholder') or ''
            input_type = await inp.get_attribute('type') or ''
            print(f"[{i}] name={name}, placeholder={placeholder}, type={input_type}")
    
    async def run(self):
        """主运行函数"""
        print("""
╔════════════════════════════════════════╗
║   纪念钞预约 - 独立自动填写程序        ║
║   连接模式：不重新加载页面             ║
╚════════════════════════════════════════╝
        """)
        
        print(f"📋 用户: {self.config['user_info']['name']}")
        print(f"📞 手机: {self.config['user_info']['phone']}")
        print(f"🏦 网点: {self.config['exchange_location']['name']}\n")
        
        # 连接到浏览器
        success = await self.connect_to_browser()
        if not success:
            return
        
        # 执行填写
        await self.fill_form_ultra_fast()
        
        # 保持连接
        print("⏸️  程序保持运行，按 Ctrl+C 退出\n")
        try:
            await asyncio.sleep(300)  # 等待5分钟
        except KeyboardInterrupt:
            print("\n👋 程序已停止")

def main():
    try:
        connector = BrowserConnector()
        asyncio.run(connector.run())
    except KeyboardInterrupt:
        print("\n\n👋 程序已手动停止")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()
