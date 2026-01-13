"""
纪念钞预约系统 - 图形界面版本
简洁美观的GUI，支持多身份信息配置，一键配置和执行
"""

import json
import asyncio
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread
from playwright.async_api import async_playwright

class UserInfoEditorDialog(tk.Toplevel):
    """身份信息编辑对话框"""
    def __init__(self, parent, initial_data=None):
        super().__init__(parent)
        self.title("编辑身份信息")
        self.geometry("400x350")
        self.resizable(False, False)
        self.parent = parent
        self.result = None
        
        # 模态设置
        self.transient(parent)
        self.grab_set()
        
        # 居中显示
        self.center_window()
        
        # 创建表单
        self.create_widgets(initial_data)
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
    def create_widgets(self, data):
        data = data or {}
        padding = {'padx': 20, 'pady': 10}
        
        # 姓名
        tk.Label(self, text="姓名:").pack(anchor=tk.W, **padding)
        self.name_var = tk.StringVar(value=data.get('name', ''))
        tk.Entry(self, textvariable=self.name_var, width=30).pack(padx=20)
        
        # 证件类型
        tk.Label(self, text="证件类型:").pack(anchor=tk.W, **padding)
        self.id_type_var = tk.StringVar(value=data.get('id_type', '身份证'))
        types = ["身份证", "护照", "港澳通行证", "台胞证"]
        ttk.Combobox(self, textvariable=self.id_type_var, values=types, state="readonly", width=28).pack(padx=20)
        
        # 证件号码
        tk.Label(self, text="证件号码:").pack(anchor=tk.W, **padding)
        self.id_num_var = tk.StringVar(value=data.get('id_number', ''))
        tk.Entry(self, textvariable=self.id_num_var, width=30).pack(padx=20)
        
        # 手机号码
        tk.Label(self, text="手机号码:").pack(anchor=tk.W, **padding)
        self.phone_var = tk.StringVar(value=data.get('phone', ''))
        tk.Entry(self, textvariable=self.phone_var, width=30).pack(padx=20)
        
        # 按钮
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20, fill=tk.X)
        
        tk.Button(btn_frame, text="取消", command=self.destroy, width=10).pack(side=tk.RIGHT, padx=20)
        tk.Button(btn_frame, text="确定", command=self.on_ok, width=10, bg="#0078d4", fg="white").pack(side=tk.RIGHT)
        
    def on_ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "姓名不能为空", parent=self)
            return
            
        self.result = {
            "name": name,
            "id_type": self.id_type_var.get(),
            "id_number": self.id_num_var.get().strip(),
            "phone": self.phone_var.get().strip()
        }
        self.destroy()

class LocationEditorDialog(tk.Toplevel):
    """网点信息编辑对话框"""
    def __init__(self, parent, bank_type, initial_data=None):
        super().__init__(parent)
        self.title(f"编辑网点信息 - {bank_type}")
        self.geometry("450x400")
        self.resizable(False, False)
        self.parent = parent
        self.bank_type = bank_type
        self.result = None
        
        self.transient(parent)
        self.grab_set()
        self.center_window()
        
        self.create_widgets(initial_data)
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
    def create_widgets(self, data):
        data = data or {}
        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.entries = {}
        
        if self.bank_type == "农业银行":
            # 级联路经编辑
            labels = ["省分行", "市分行", "支行", "营业室"]
            path = data.get('cascade_path', [])
            # 补齐或截断
            current_values = path + [''] * (4 - len(path))
            
            tk.Label(main_frame, text="请按顺序填写网点层级：", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
            
            for i, label in enumerate(labels):
                row = tk.Frame(main_frame)
                row.pack(fill=tk.X, pady=5)
                tk.Label(row, text=f"{label}:", width=10, anchor=tk.W).pack(side=tk.LEFT)
                entry = tk.Entry(row)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entry.insert(0, current_values[i])
                self.entries[f"level_{i}"] = entry
                
        else: # 工商银行
            # 独立字段编辑
            fields = [
                ("province", "省份"),
                ("city", "城市"),
                ("district", "区县"),
                ("outlet", "网点")
            ]
            icbc_data = data.get('icbc_location', {})
            
            tk.Label(main_frame, text="请填写网点详细信息：", font=("微软雅黑", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
            
            for key, label in fields:
                row = tk.Frame(main_frame)
                row.pack(fill=tk.X, pady=5)
                tk.Label(row, text=f"{label}:", width=10, anchor=tk.W).pack(side=tk.LEFT)
                entry = tk.Entry(row)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entry.insert(0, icbc_data.get(key, ''))
                self.entries[key] = entry
                
        # 按钮区域
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20, fill=tk.X)
        
        tk.Button(btn_frame, text="取消", command=self.destroy, width=10).pack(side=tk.RIGHT, padx=20)
        tk.Button(btn_frame, text="确定", command=self.on_ok, width=10, bg="#0078d4", fg="white").pack(side=tk.RIGHT)
        
    def on_ok(self):
        if self.bank_type == "农业银行":
            path = []
            for i in range(4):
                val = self.entries[f"level_{i}"].get().strip()
                if val:
                    path.append(val)
            
            if not path:
                messagebox.showwarning("提示", "至少填写一级网点信息", parent=self)
                return
                
            self.result = {
                "cascade_path": path,
                "name": path[-1] if path else "未命名网点"
            }
        else:
            icbc_data = {}
            for key in ["province", "city", "district", "outlet"]:
                icbc_data[key] = self.entries[key].get().strip()
            
            # 简单验证
            if not icbc_data["outlet"]:
                messagebox.showwarning("提示", "网点名称不能为空", parent=self)
                return
                
            self.result = {
                "icbc_location": icbc_data,
                "name": icbc_data["outlet"]
            }
        self.destroy()

class AutoFillerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("也许纪念钞预约 - 超高速自动填写")
        self.window.geometry("600x800")
        self.window.resizable(False, False)
        
        # 设置主题色
        self.bg_color = "#f0f0f0"
        self.accent_color = "#0078d4"
        self.window.configure(bg=self.bg_color)
        
        # 状态变量
        self.is_running = False
        # 多窗口管理 - 使用字典存储每个用户的浏览器实例
        self.browser_instances = {}  # {user_index: browser}
        self.page_instances = {}     # {user_index: page}
        self.window_status = {}      # {user_index: 'disconnected'|'connected'|'filling'|'done'}
        
        # 数据变量
        self.config = {}
        self.user_infos = [] # 存储身份信息列表
        self.current_location = {} # 存储当前网点信息
        
        # 事件循环管理
        self.loop = None
        self.loop_thread = None
        
        self.create_widgets()
        self.load_config()
        
        # 启动后台事件循环
        self._start_event_loop()
        
    def create_widgets(self):
        """创建界面组件"""
        
        # 1. 标题
        title_frame = tk.Frame(self.window, bg="#0078d4", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎯 也许纪念钞预约 - 超高速自动填写",
            font=("微软雅黑", 16, "bold"),
            bg="#0078d4",
            fg="white"
        )
        title_label.pack(pady=15)
        
        # 主容器
        main_frame = tk.Frame(self.window, bg=self.bg_color, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 2. 银行配置区域
        bank_frame = tk.LabelFrame(main_frame, text="🏦 银行选择", font=("微软雅黑", 10, "bold"), bg=self.bg_color, fg="#333", padx=10, pady=10)
        bank_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.bank_var = tk.StringVar(value="农业银行")
        self.bank_combo = ttk.Combobox(
            bank_frame,
            textvariable=self.bank_var,
            font=("微软雅黑", 10),
            state="readonly",
            values=["农业银行", "工商银行"],
            width=25
        )
        self.bank_combo.pack(anchor=tk.W)
        self.bank_combo.bind("<<ComboboxSelected>>", self.on_bank_changed)
        
        # 3. 身份信息管理区域
        user_frame = tk.LabelFrame(main_frame, text="👥 身份信息配置 (支持多选)", font=("微软雅黑", 10, "bold"), bg=self.bg_color, fg="#333", padx=10, pady=10)
        user_frame.pack(fill=tk.X, pady=5)
        
        # 列表和按钮的容器
        list_container = tk.Frame(user_frame, bg=self.bg_color)
        list_container.pack(fill=tk.X)
        
        # 使用Treeview替代Listbox以支持多列显示
        columns = ('name', 'status')
        self.user_tree = ttk.Treeview(
            list_container,
            columns=columns,
            show='headings',
            height=4,
            selectmode=tk.BROWSE
        )
        self.user_tree.heading('name', text='用户信息')
        self.user_tree.heading('status', text='状态')
        self.user_tree.column('name', width=350)
        self.user_tree.column('status', width=100)
        
        list_scroll = tk.Scrollbar(list_container, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=list_scroll.set)
        
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # 右侧按钮
        btn_box = tk.Frame(user_frame, bg=self.bg_color, pady=5)
        btn_box.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_box, text="+ 添加", command=self.add_user, width=8, bg="#4CAF50", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_box, text="✎ 编辑", command=self.edit_user, width=8, bg="#2196F3", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_box, text="× 删除", command=self.delete_user, width=8, bg="#F44336", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        # 多窗口操作按钮
        tk.Button(btn_box, text="🔗 连接选中", command=self.connect_selected, width=10, bg="#FF9800", fg="white", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_box, text="⚡ 填写选中", command=self.fill_selected, width=10, bg="#9C27B0", fg="white", relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)

        # 4. 网点配置区域
        location_frame = tk.LabelFrame(main_frame, text="📍 兑换网点配置", font=("微软雅黑", 10, "bold"), bg=self.bg_color, fg="#333", padx=10, pady=10)
        location_frame.pack(fill=tk.X, pady=5)
        
        loc_inner = tk.Frame(location_frame, bg=self.bg_color)
        loc_inner.pack(fill=tk.X)
        
        self.location_display = tk.Label(
            loc_inner, 
            text="暂无网点信息", 
            font=("微软雅黑", 9), 
            bg="#eef", 
            fg="#333",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=5,
            pady=5
        )
        self.location_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(loc_inner, text="编辑网点", command=self.edit_location, bg="#FF9800", fg="white", relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        
        # 5. 数量配置
        qty_frame = tk.Frame(main_frame, bg=self.bg_color)
        qty_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(qty_frame, text="预约数量:", font=("微软雅黑", 10, "bold"), bg=self.bg_color).pack(side=tk.LEFT)
        self.qty_entry = tk.Entry(qty_frame, width=10, font=("微软雅黑", 10))
        self.qty_entry.pack(side=tk.LEFT, padx=10)
        self.qty_entry.insert(0, "20")
        
        # 6. 主要操作按钮
        action_frame = tk.Frame(main_frame, bg=self.bg_color)
        action_frame.pack(fill=tk.X, pady=10)
        
        # 保存配置
        tk.Button(action_frame, text="💾 保存配置", command=self.save_config, bg="#4CAF50", fg="white", font=("微软雅黑", 9, "bold"), relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        # 批量操作按钮
        tk.Button(action_frame, text="🔗 全部连接", command=self.connect_all, bg="#FF9800", fg="white", font=("微软雅黑", 9, "bold"), relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="❌ 全部断开", command=self.disconnect_all, bg="#F44336", fg="white", font=("微软雅黑", 9, "bold"), relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="⚡ 全部填写", command=self.fill_all, bg="#0078d4", fg="white", font=("微软雅黑", 10, "bold"), relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        # 7. 日志区域
        log_label = tk.Label(main_frame, text="📝 运行日志", font=("微软雅黑", 10, "bold"), bg=self.bg_color, fg="#333")
        log_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, font=("Consolas", 9), bg="#1e1e1e", fg="#00ff00", height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        """输出日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.window.update()
    
    # --- 身份信息管理 ---
    def refresh_user_list(self):
        """刷新用户列表显示"""
        # 清空现有项
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # 添加所有用户
        for idx, user in enumerate(self.user_infos):
            status = self.window_status.get(idx, '⚪ 未连接')
            name_display = f"👤 {user.get('name', '未命名')} - {user.get('id_number', '')}"
            self.user_tree.insert('', tk.END, iid=str(idx), values=(name_display, status))
            
    def on_user_select(self, event):
        """用户选择事件"""
        selection = self.user_tree.selection()
        if selection:
            # selection是字符串列表，每个元素是iid
            pass  # 可以在这里添加选中后的操作
            
    def add_user(self):
        """添加新用户"""
        dialog = UserInfoEditorDialog(self.window)
        self.window.wait_window(dialog)
        if dialog.result:
            idx = len(self.user_infos)
            self.user_infos.append(dialog.result)
            self.window_status[idx] = '⚪ 未连接'
            self.refresh_user_list()
            # 选中新增的
            self.user_tree.selection_set(str(idx))
            self.user_tree.see(str(idx))
            
    def edit_user(self):
        """编辑用户信息"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要编辑的身份信息")
            return
        
        index = int(selection[0])
        user = self.user_infos[index]
        dialog = UserInfoEditorDialog(self.window, user)
        self.window.wait_window(dialog)
        if dialog.result:
            self.user_infos[index] = dialog.result
            self.refresh_user_list()
            self.user_tree.selection_set(str(index))
            
    def delete_user(self):
        """删除用户"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的身份信息")
            return
            
        if messagebox.askyesno("确认", "确定要删除这条身份信息吗？"):
            index = int(selection[0])
            # 如果该用户有连接的浏览器，先断开
            if index in self.browser_instances:
                Thread(target=lambda: self._disconnect_single_browser(index), daemon=True).start()
            
            del self.user_infos[index]
            if index in self.window_status:
                del self.window_status[index]
            
            # 重新索引所有数据
            self._reindex_after_delete(index)
            self.refresh_user_list()

    # --- 网点管理 ---
    def update_location_display(self):
        bank = self.bank_var.get()
        if bank == "农业银行":
            path = self.current_location.get("cascade_path", [])
            text = " → ".join(path) if path else "未配置网点"
        else:
            icbc = self.current_location.get("icbc_location", {})
            parts = [icbc.get(k, '') for k in ['province', 'city', 'district', 'outlet']]
            parts = [p for p in parts if p]
            text = " - ".join(parts) if parts else "未配置网点"
        self.location_display.config(text=text)

    def edit_location(self):
        bank = self.bank_var.get()
        dialog = LocationEditorDialog(self.window, bank, self.current_location)
        self.window.wait_window(dialog)
        if dialog.result:
            # 更新网点信息
            self.current_location.update(dialog.result)
            self.update_location_display()
            
    def on_bank_changed(self, event):
        self.update_location_display()
        
    # --- 配置加载与保存 ---
    def load_config(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            # 加载基础设置
            self.bank_var.set(self.config.get("bank", "农业银行"))
            self.qty_entry.delete(0, tk.END)
            self.qty_entry.insert(0, str(self.config.get("quantity", 20)))
            
            # 加载身份列表
            # 兼容旧版本：如果是旧格式（字典），转为列表
            user_info = self.config.get("user_info")
            user_infos = self.config.get("user_infos")
            
            if user_infos and isinstance(user_infos, list):
                self.user_infos = user_infos
            elif user_info and isinstance(user_info, dict):
                self.user_infos = [user_info]
            else:
                self.user_infos = [] # 默认空
            
            # 初始化状态
            for idx in range(len(self.user_infos)):
                self.window_status[idx] = '⚪ 未连接'
                
            self.refresh_user_list()
            
            # 恢复之前的选择
            sel_idx = self.config.get("selected_user_index", 0)
            if 0 <= sel_idx < len(self.user_infos):
                self.user_tree.selection_set(str(sel_idx))
                self.user_tree.see(str(sel_idx))
            
            # 加载网点信息
            self.current_location = self.config.get("exchange_location", {})
            self.update_location_display()
            
            self.log("✅ 配置已加载")
        except Exception as e:
            self.log(f"⚠️ 加载配置失败: {e}")
            self.user_infos = []
            
    def save_config(self):
        config = {
            "bank": self.bank_var.get(),
            "bank_configs": self.config.get("bank_configs", {}), # 保留原有
            "user_infos": self.user_infos,
            "selected_user_index": int(self.user_tree.selection()[0]) if self.user_tree.selection() else 0,
            "exchange_location": self.current_location,
            "quantity": int(self.qty_entry.get()),
            "target_url": self.config.get("target_url", "http://纪念钞.vip:8888/new-abchina"),
            "settings": self.config.get("settings", {
                "auto_submit": False,
                "use_ocr": True,
                "timeout": 5000
            })
        }
        
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.log("✅ 配置已保存")
            messagebox.showinfo("成功", "配置已保存！")
        except Exception as e:
            self.log(f"❌ 保存失败: {e}")
            messagebox.showerror("错误", f"保存失败: {e}")

    # --- 异步事件循环管理 ---
    def _start_event_loop(self):
        """启动后台异步事件循环"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        self.loop_thread = Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
        import time
        time.sleep(0.1)
        
    def _run_async(self, coro):
        """在后台事件循环中运行异步协程"""
        if self.loop is None:
            raise RuntimeError("事件循环未启动")
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    # --- 多窗口浏览器控制 ---
    def _reindex_after_delete(self, deleted_index):
        """删除用户后重新索引所有数据"""
        # 重建字典，索引减1
        new_browsers = {}
        new_pages = {}
        new_status = {}
        
        for idx in sorted(self.browser_instances.keys()):
            if idx > deleted_index:
                new_browsers[idx - 1] = self.browser_instances[idx]
                new_pages[idx - 1] = self.page_instances[idx]
                new_status[idx - 1] = self.window_status[idx]
            elif idx < deleted_index:
                new_browsers[idx] = self.browser_instances[idx]
                new_pages[idx] = self.page_instances[idx]
                new_status[idx] = self.window_status[idx]
        
        self.browser_instances = new_browsers
        self.page_instances = new_pages
        self.window_status = new_status
    
    def update_user_status(self, user_index, status):
        """更新用户状态显示"""
        self.window_status[user_index] = status
        # 更新树视图中的状态列
        if str(user_index) in self.user_tree.get_children():
            current_values = self.user_tree.item(str(user_index), 'values')
            if current_values:
                self.user_tree.item(str(user_index), values=(current_values[0], status))
    
    def connect_selected(self):
        """连接选中的用户窗口"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要连接的用户")
            return
        
        user_index = int(selection[0])
        self.log(f"🔗 正在为用户 [{self.user_infos[user_index]['name']}] 连接浏览器...")
        Thread(target=lambda: self._connect_single_browser(user_index), daemon=True).start()
    
    def fill_selected(self):
        """填写选中的用户窗口"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要填写的用户")
            return
        
        user_index = int(selection[0])
        
        if user_index not in self.page_instances:
            messagebox.showwarning("提示", "该用户尚未连接浏览器，请先连接")
            return
        
        user_data = self.user_infos[user_index]
        self.log(f"⚡ 开始为用户 [{user_data['name']}] 自动填写...")
        Thread(target=lambda: self._fill_single_user(user_index, user_data), daemon=True).start()
    
    def connect_all(self):
        """连接所有用户的浏览器窗口"""
        if not self.user_infos:
            messagebox.showwarning("提示", "没有配置的用户信息")
            return
        
        self.log("🔗 开始批量连接所有用户...")
        for idx in range(len(self.user_infos)):
            if idx not in self.browser_instances:
                Thread(target=lambda i=idx: self._connect_single_browser(i), daemon=True).start()
                import time
                time.sleep(0.5)  # 错开启动时间
    
    def disconnect_all(self):
        """断开所有浏览器连接"""
        if not self.browser_instances:
            self.log("⚠️ 没有活动的浏览器连接")
            return
        
        self.log("🔌 正在断开所有连接...")
        indices = list(self.browser_instances.keys())
        for idx in indices:
            Thread(target=lambda i=idx: self._disconnect_single_browser(i), daemon=True).start()
    
    def fill_all(self):
        """为所有已连接的用户执行自动填写"""
        if not self.page_instances:
            messagebox.showwarning("提示", "没有已连接的浏览器窗口")
            return
        
        self.log("⚡ 开始批量填写所有窗口...")
        for idx, page in self.page_instances.items():
            user_data = self.user_infos[idx]
            Thread(target=lambda i=idx, u=user_data: self._fill_single_user(i, u), daemon=True).start()
    
    def _connect_single_browser(self, user_index):
        """连接单个用户的浏览器"""
        try:
            user_name = self.user_infos[user_index]['name']
            self.window.after(0, lambda: self.update_user_status(user_index, '🔗 连接中...'))
            
            # 计算端口号: 基础9222 + user_index
            port = 9222 + user_index
            
            async def connect():
                playwright = await async_playwright().start()
                browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
                contexts = browser.contexts
                if contexts and contexts[0].pages:
                    page = contexts[0].pages[-1]
                    return browser, page
                else:
                    await browser.close()
                    return None, None
            
            browser, page = self._run_async(connect())
            
            if browser and page:
                self.browser_instances[user_index] = browser
                self.page_instances[user_index] = page
                self.log(f"✅ 用户 [{user_name}] 已连接 (端口:{port}, URL:{page.url})")
                self.window.after(0, lambda: self.update_user_status(user_index, '✅ 已连接'))
            else:
                self.log(f"❌ 用户 [{user_name}] 连接失败: 未找到页面 (端口:{port})")
                self.window.after(0, lambda: self.update_user_status(user_index, '❌ 连接失败'))
                
        except Exception as e:
            user_name = self.user_infos[user_index]['name']
            self.log(f"❌ 用户 [{user_name}] 连接失败: {e}")
            self.window.after(0, lambda: self.update_user_status(user_index, '❌ 连接失败'))
    
    def _disconnect_single_browser(self, user_index):
        """断开单个用户的浏览器"""
        try:
            if user_index in self.browser_instances:
                user_name = self.user_infos[user_index]['name']
                self._run_async(self.browser_instances[user_index].close())
                del self.browser_instances[user_index]
                del self.page_instances[user_index]
                self.log(f"✅ 用户 [{user_name}] 已断开连接")
                self.window.after(0, lambda: self.update_user_status(user_index, '⚪ 未连接'))
        except Exception as e:
            self.log(f"❌ 断开失败: {e}")

    def _perform_fill_for_page(self, page, user_data, user_name):
        """为指定页面执行自动填写"""
        import time
        current_bank = self.bank_var.get()
        bank_config = self.config.get("bank_configs", {}).get(current_bank, {})
        field_indices = bank_config.get("field_indices", {})
        use_cascader = bank_config.get("use_cascader", True)
        
        # 1. 填写基础信息
        self.log(f"[{user_name}] 📝 填写基础信息...")
        
        js_code_fill = f'''() => {{
            let filled = {{'name': false, 'id': false, 'phone': false, 'qty': false}};
            let logs = [];
            const inputs = document.querySelectorAll('input.el-input__inner[type="text"]');
            
            function fillByIndex(index, value, fieldName) {{
                if (inputs[index]) {{
                    const input = inputs[index];
                    input.focus();
                    input.value = value;
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                    if (input.value === value) {{
                        logs.push(`✅ ${{fieldName}}: OK`);
                        return true;
                    }}
                }}
                logs.push(`⚠️ ${{fieldName}}: 失败`);
                return false;
            }}
            
            filled.name = fillByIndex({field_indices.get('name', 0)}, '{user_data.get('name')}', '姓名');
            filled.id = fillByIndex({field_indices.get('id_number', 1)}, '{user_data.get('id_number')}', '证件号');
            filled.phone = fillByIndex({field_indices.get('phone', 2)}, '{user_data.get('phone')}', '手机');
            filled.qty = fillByIndex({field_indices.get('quantity', 7)}, '{self.qty_entry.get()}', '数量');
            
            return {{ filled, logs }};
        }}'''
        
        result_fill = self._run_async(page.evaluate(js_code_fill))
        for log in result_fill['logs']:
            self.log(f"[{user_name}]   {log}")
            
        time.sleep(0.5)
        
        # 2. 选择网点
        self.log(f"[{user_name}] 📍 选择网点...")
        
        if use_cascader:
            # 农业银行：级联选择
            cascade_path = self.current_location.get("cascade_path", [])
            if cascade_path:
                for level, target_text in enumerate(cascade_path):
                    self.log(f"[{user_name}]    [{level+1}/4] 正在选择: {target_text}")
                    
                    async def _select_level(level_idx, text):
                        input_idx = 6 + level_idx
                        box = await page.evaluate(f'''() => {{
                            const inputs = document.querySelectorAll('input.el-input__inner[type="text"]');
                            const target = inputs[{input_idx}];
                            if(!target) return null;
                            target.scrollIntoView({{block: 'center'}});
                            const rect = target.getBoundingClientRect();
                            return {{x: rect.x + rect.width/2, y: rect.y + rect.height/2}};
                        }}''')
                        
                        if not box:
                            return {"success": False, "msg": f"未找到第{level_idx+1}级输入框"}
                        
                        await page.mouse.click(box['x'], box['y'])
                        await asyncio.sleep(0.3)
                        
                        result = await page.evaluate(f'''async () => {{
                            const targetText = "{text}";
                            await new Promise(r => setTimeout(r, 300));
                            
                            const selectors = ['li', '[role="menuitem"]', '.el-cascader-node'];
                            let found = false;
                            
                            for(let sel of selectors) {{
                                const options = document.querySelectorAll(sel);
                                for(let opt of options) {{
                                    if(opt.textContent.trim() === targetText && opt.offsetWidth > 0) {{
                                        opt.click();
                                        found = true;
                                        break;
                                    }}
                                }}
                                if(found) break;
                            }}
                            
                            if(!found) return {{success: false, msg: '未找到选项'}};
                            return {{success: true}};
                        }}''')
                        
                        return result
                    
                    result = self._run_async(_select_level(level, target_text))
                    
                    if result.get("success"):
                        self.log(f"[{user_name}]       ✅ 已选择: {target_text}")
                        time.sleep(0.3)
                    else:
                        self.log(f"[{user_name}]       ❌ 失败: {result.get('msg', '未知错误')}")
                        break
        else:
            # 工商银行：独立下拉框
            self._perform_icbc_location_selection(page, self.current_location.get("icbc_location", {}), field_indices, user_name)
    
    def _perform_icbc_location_selection(self, page, loc_data, indices, user_name):
        """执行工商银行多下拉选择"""
        targets = [
            (indices.get('province', 3), loc_data.get('province'), '省份'),
            (indices.get('city', 4), loc_data.get('city'), '城市'),
            (indices.get('district', 5), loc_data.get('district'), '区县'),
            (indices.get('outlet', 6), loc_data.get('outlet'), '网点')
        ]
        
        js_code = f'''async () => {{
            const logs = [];
            const targets = {json.dumps(targets)};
            
            try {{
                const inputs = document.querySelectorAll('input.el-input__inner[type="text"]');
                
                for (let [idx, val, name] of targets) {{
                    if (!val) continue;
                    
                    const input = inputs[idx];
                    if (!input) {{
                        logs.push(`❌ 未找到输入框: ${{name}}`);
                        continue;
                    }}
                    
                    input.click();
                    logs.push(`🔽 打开 ${{name}}`);
                    await new Promise(r => setTimeout(r, 500));
                    
                    const options = document.querySelectorAll('.el-select-dropdown__item');
                    let found = false;
                    for (let opt of options) {{
                        if (opt.textContent.trim() === val && opt.style.display !== 'none') {{
                            opt.click();
                            logs.push(`   ✅ 选择: ${{val}}`);
                            found = true;
                            break;
                        }}
                    }}
                    
                    if (!found) logs.push(`   ⚠️ 未找到选项: ${{val}}`);
                    await new Promise(r => setTimeout(r, 500));
                }}
                return {{ success: true, logs: logs }};
            }} catch (e) {{
                return {{ success: false, logs: [e.message] }};
            }}
        }}'''
        
        result = self._run_async(page.evaluate(js_code))
        for log in result['logs']:
            self.log(f"[{user_name}] {log}")
        
    def _perform_icbc_location_selection_old(self, loc_data, indices):
        """执行工商银行多下拉选择（旧版本，保留用于兼容）"""
        # 注意：这个函数现在已被_perform_icbc_location_selection(page, loc_data, indices, user_name)替代
        pass

    def show_debug_info(self):
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要使用的身份信息")
            return
        
        user_data = self.user_infos[selection[0]]
        self.log(f"\n⚡ 开始自动填写 (用户: {user_data.get('name')})...")
        self.fill_btn.config(state=tk.DISABLED)
        
        Thread(target=self._integrated_fill_thread, args=(user_data,), daemon=True).start()
        
    def _integrated_fill_thread(self, user_data):
        try:
            bank_config = self.config.get("bank_configs", {}).get(current_bank, {})
            field_indices = bank_config.get("field_indices", {})
            use_cascader = bank_config.get("use_cascader", True)
            
            # 1. 填写基础信息
            self.log("📝 步骤1: 填写基础信息...")
            
            js_code_fill = f'''() => {{
                let filled = {{'name': false, 'id': false, 'phone': false, 'qty': false}};
                let logs = [];
                const inputs = document.querySelectorAll('input.el-input__inner[type="text"]');
                
                function fillByIndex(index, value, fieldName) {{
                    if (inputs[index]) {{
                        const input = inputs[index];
                        input.focus();
                        input.value = value;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                        if (input.value === value) {{
                            logs.push(`✅ ${{fieldName}}: OK`);
                            return true;
                        }}
                    }}
                    logs.push(`⚠️ ${{fieldName}}: 失败`);
                    return false;
                }}
                
                filled.name = fillByIndex({field_indices.get('name', 0)}, '{user_data.get('name')}', '姓名');
                filled.id = fillByIndex({field_indices.get('id_number', 1)}, '{user_data.get('id_number')}', '证件号');
                filled.phone = fillByIndex({field_indices.get('phone', 2)}, '{user_data.get('phone')}', '手机');
                filled.qty = fillByIndex({field_indices.get('quantity', 7)}, '{self.qty_entry.get()}', '数量');
                
                return {{ filled, logs }};
            }}'''
            
            result_fill = self._run_async(self.page.evaluate(js_code_fill))
            for log in result_fill['logs']:
                self.log(f"  {log}")
                
            time.sleep(0.5)
            
            # 2. 选择网点
            self.log(f"📍 步骤2: 选择网点 ({current_bank})...")
            
            if use_cascader:
                # 农业银行：4个独立输入框，每个对应一级
                self.log("   开始逐级选择网点...")
                cascade_path = self.current_location.get("cascade_path", [])
                
                if not cascade_path:
                    self.log("❌ 未配置级联路径")
                else:
                    for level, target_text in enumerate(cascade_path):
                        self.log(f"   [{level+1}/4] 正在选择: {target_text}")
                        
                        async def _select_level(level_idx, text):
                            # 点击对应级别的输入框
                            input_idx = 6 + level_idx
                            box = await self.page.evaluate(f'''() => {{
                                const inputs = document.querySelectorAll('input.el-input__inner[type="text"]');
                                const target = inputs[{input_idx}];
                                if(!target) return null;
                                target.scrollIntoView({{block: 'center'}});
                                const rect = target.getBoundingClientRect();
                                return {{x: rect.x + rect.width/2, y: rect.y + rect.height/2}};
                            }}''')
                            
                            if not box:
                                return {{"success": False, "msg": f"未找到第{level_idx+1}级输入框"}}
                            
                            # 物理点击
                            await self.page.mouse.click(box['x'], box['y'])
                            await asyncio.sleep(0.3)  # 等待面板打开
                            
                            # 在面板中查找并点击选项
                            result = await self.page.evaluate(f'''async () => {{
                                const targetText = "{text}";
                                const logs = [];
                                
                                // 等待面板出现
                                let panelFound = false;
                                for(let i=0; i<20; i++) {{
                                    const panels = document.querySelectorAll('[class*="dropdown"], [class*="cascader"]');
                                    for(let p of panels) {{
                                        const rect = p.getBoundingClientRect();
                                        if(rect.width > 0 && rect.height > 0) {{
                                            panelFound = true;
                                            break;
                                        }}
                                    }}
                                    if(panelFound) break;
                                    await new Promise(r => setTimeout(r, 50));
                                }}
                                
                                if(!panelFound) return {{success: false, msg: '面板未打开'}};
                                
                                await new Promise(r => setTimeout(r, 300));
                                
                                // 查找选项
                                const selectors = ['li', '[role="menuitem"]', '.el-cascader-node'];
                                let found = false;
                                
                                for(let sel of selectors) {{
                                    const options = document.querySelectorAll(sel);
                                    for(let opt of options) {{
                                        if(opt.textContent.includes(targetText) && opt.offsetWidth > 0) {{
                                            opt.click();
                                            found = true;
                                            break;
                                        }}
                                    }}
                                    if(found) break;
                                }}
                                
                                if(!found) return {{success: false, msg: '未找到选项'}};
                                return {{success: true}};
                            }}''')
                            
                            return result
                        
                        result = self._run_async(_select_level(level, target_text))
                        
                        if result.get("success"):
                            self.log(f"      ✅ 已选择: {target_text}")
                            # 等待一下让面板关闭
                            import time
                            time.sleep(0.3)
                        else:
                            self.log(f"      ❌ 失败: {result.get('msg', '未知错误')}")
                            break
            else:
                self._perform_icbc_location_selection(self.current_location.get("icbc_location", {}), field_indices)
                
            self.log("\n✅ 自动操作完成！")
            
        except Exception as e:
            self.log(f"❌ 自动失败: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.window.after(0, lambda: self.fill_btn.config(state=tk.NORMAL))

    def _perform_cascader_selection(self, cascade_path):
        """执行级联选择 (仅包含查找逻辑，点击已在外部执行)"""
        # ... 原有的 JS 查找逻辑，去掉前面的点击部分 ...
        
        js_code = f'''async () => {{
            const logs = [];
            const cascadePath = {json.dumps(cascade_path)};
            
            try {{
                // 检查面板是否打开 - 使用更宽松的检测
                let panelFound = false;
                let panelInfo = '';
                
                for(let i=0; i<30; i++) {{ 
                    // 尝试多种选择器
                    const selectors = [
                        '.el-cascader-panel',
                        '.el-cascader__dropdown', 
                        '.el-cascader-menus',
                        '.el-popper[role="tooltip"]',
                        '[class*="cascader"]',
                        '[class*="dropdown"]'
                    ];
                    
                    for(let selector of selectors) {{
                        const panels = document.querySelectorAll(selector);
                        for(let p of panels) {{
                            // 更宽松的判断：只要元素有宽高就算
                            const rect = p.getBoundingClientRect();
                            if(rect.width > 0 && rect.height > 0) {{
                                panelFound = true;
                                panelInfo = `发现面板: ${{selector}}, 尺寸: ${{rect.width}}x${{rect.height}}`;
                                break;
                            }}
                        }}
                        if(panelFound) break;
                    }}
                    if(panelFound) break;
                    await new Promise(r => setTimeout(r, 100));
                }}
                
                if(!panelFound) {{
                     logs.push('❌ 物理点击后仍未检测到弹出层');
                     // 调试信息：列出页面上所有可能是弹出层的元素
                     const allEls = document.querySelectorAll('[class*="cascad"], [class*="dropdown"], [class*="popper"]');
                     const info = Array.from(allEls).slice(0, 5).map(el => {{
                         const rect = el.getBoundingClientRect();
                         return `${{el.className}}: ${{rect.width}}x${{rect.height}}`;
                     }});
                     logs.push(`🔍 页面上的相关元素: ${{info.join(', ')}}`);
                     return {{ success: false, logs: logs }};
                }}
                
                logs.push(`✅ ${{panelInfo}}`);
                
                logs.push('✅ 面板已检测到，开始选择');
                
                // --- 查找选项逻辑 (同前) ---
                const optionSelectors = [
                    '.el-cascader-node', 
                    'li[role="menuitem"]',
                    '.el-scrollbar__view li',
                    'li'
                ];
                
                for (let level = 0; level < cascadePath.length; level++) {{
                    const targetText = cascadePath[level];
                    logs.push(`   正在查找: ${{targetText}}`);
                    
                    // 如果不是第一级，点击前一级后需要等待新的列出现
                    if(level > 0) {{
                        // 记录当前有多少个菜单列
                        const beforeCount = document.querySelectorAll('.el-cascader-menu, .el-cascader-panel__wrap, [class*="cascader-menu"]').length;
                        // 等待新列出现（最多等3秒）
                        let newPanelAppeared = false;
                        for(let wait=0; wait<30; wait++) {{
                            await new Promise(r => setTimeout(r, 100));
                            const afterCount = document.querySelectorAll('.el-cascader-menu, .el-cascader-panel__wrap, [class*="cascader-menu"]').length;
                            if(afterCount > beforeCount) {{
                                newPanelAppeared = true;
                                logs.push(`   ↪ 第${{level+1}}级面板已加载`);
                                break;
                            }}
                        }}
                        if(!newPanelAppeared) {{
                            // 即使没检测到新面板，也给500ms缓冲时间
                            await new Promise(r => setTimeout(r, 500));
                        }}
                    }} else {{
                        // 第一级直接等待800ms
                        await new Promise(r => setTimeout(r, 800));
                    }} 
                    
                    let found = false;
                    let matchedEl = null;
                    
                    // 标准查找
                    for (let sel of optionSelectors) {{
                        const options = document.querySelectorAll(sel);
                        for (let opt of options) {{
                            if (opt.textContent.includes(targetText) && opt.offsetWidth > 0) {{
                                matchedEl = opt;
                                break;
                            }}
                        }}
                        if (matchedEl) break;
                    }}
                    
                    // 兜底查找
                    if (!matchedEl) {{
                         const walkers = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                         let node;
                         while(node = walkers.nextNode()) {{
                             if(node.textContent.includes(targetText)) {{
                                 const p = node.parentElement;
                                 if(p && p.offsetWidth > 0 && p.tagName !== 'SCRIPT' && p.tagName !== 'STYLE') {{
                                     matchedEl = p;
                                     const li = p.closest('li');
                                     if(li) matchedEl = li;
                                     break;
                                 }}
                             }}
                         }}
                    }}
                    
                    if (matchedEl) {{
                        matchedEl.scrollIntoView({{block: "nearest"}});
                        matchedEl.click();
                        found = true;
                        logs.push(`   ✅ 点击: ${{matchedEl.textContent.trim()}}`);
                    }} else {{
                        logs.push(`   ❌ 没找到: ${{targetText}}`);
                        return {{ success: false, logs: logs }};
                    }}
                }}
                return {{ success: true, logs: logs }};
            }} catch (e) {{
                return {{ success: false, logs: [`❌ JS错误: ${{e.message}}`] }};
            }}
        }}'''
        
        result = self._run_async(self.page.evaluate(js_code))
        for log in result['logs']:
            self.log(log)

    def _perform_icbc_location_selection(self, loc_data, indices):
        """执行工商银行多下拉选择"""
        if not loc_data:
            self.log("❌ 未配置网点信息")
            return
            
        targets = [
            (indices.get('province', 3), loc_data.get('province'), '省份'),
            (indices.get('city', 4), loc_data.get('city'), '城市'),
            (indices.get('district', 5), loc_data.get('district'), '区县'),
            (indices.get('outlet', 6), loc_data.get('outlet'), '网点')
        ]
        
        js_code = f'''async () => {{
            const logs = [];
            const targets = {json.dumps(targets)};
            
            try {{
                const inputs = document.querySelectorAll('input.el-input__inner[type="text"]');
                
                for (let [idx, val, name] of targets) {{
                    if (!val) continue;
                    
                    const input = inputs[idx];
                    if (!input) {{
                        logs.push(`❌ 未找到输入框: ${{name}}`);
                        continue;
                    }}
                    
                    input.click();
                    logs.push(`🔽 打开 ${{name}}`);
                    await new Promise(r => setTimeout(r, 500));
                    
                    const options = document.querySelectorAll('.el-select-dropdown__item');
                    let found = false;
                    for (let opt of options) {{
                        if (opt.textContent.trim() === val && opt.style.display !== 'none') {{
                            opt.click();
                            logs.push(`   ✅ 选择: ${{val}}`);
                            found = true;
                            break;
                        }}
                    }}
                    
                    if (!found) logs.push(`   ⚠️ 未找到选项: ${{val}}`);
                    await new Promise(r => setTimeout(r, 500));
                }}
                return {{ success: true, logs: logs }};
            }} catch (e) {{
                return {{ success: false, logs: [e.message] }};
            }}
        }}'''
        
        result = self._run_async(self.page.evaluate(js_code))
        for log in result['logs']:
            self.log(log)

    def show_debug_info(self):
        self.log("🔍 正在获取页面元素...")
        self.debug_btn.config(state=tk.DISABLED)
        
        def _debug_thread():
            try:
                async def debug():
                    inputs = await self.page.evaluate('''() => {
                        return Array.from(document.querySelectorAll('input.el-input__inner')).map((el, i) => 
                            `[${i}] ${el.placeholder || '无占位符'} (Val: ${el.value})`
                        )
                    }''')
                    return inputs
                    
                result = self._run_async(debug())
                for info in result:
                    self.log(info)
            except Exception as e:
                self.log(f"调试出错: {e}")
            finally:
                self.window.after(0, lambda: self.debug_btn.config(state=tk.NORMAL))
                
        Thread(target=_debug_thread, daemon=True).start()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = AutoFillerGUI()
    app.run()
