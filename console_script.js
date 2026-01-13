// ===================================================
// 纪念钞预约系统 - 超高速自动填写脚本 (控制台版本)
// 使用方法：
// 1. 打开预约网页
// 2. 按 F12 打开开发者工具
// 3. 切换到 Console (控制台) 标签
// 4. 复制整个脚本，粘贴到控制台并回车
// ===================================================

// 配置信息 - 请在这里修改你的个人信息
const CONFIG = {
    name: "张三",
    idType: "身份证",
    idNumber: "110101199001011234",
    phone: "13800138000",
    locationKeyword: "辽宁省",  // 兑换网点关键词
    quantity: 20,
    autoSubmit: false  // 是否自动提交（建议false，手动确认）
};

// ===================================================
// 核心代码 - 请勿修改
// ===================================================

class AutoFiller {
    constructor(config) {
        this.config = config;
        console.log('%c🚀 纪念钞预约自动填写脚本启动', 'color: #00ff00; font-size: 16px; font-weight: bold');
        console.log('%c配置信息:', 'color: #00aaff; font-weight: bold', config);
    }

    // 智能查找输入框
    findInput(keywords, type = 'input') {
        for (let keyword of keywords) {
            // 尝试多种选择器
            const selectors = [
                `${type}[name*="${keyword}" i]`,
                `${type}[placeholder*="${keyword}" i]`,
                `${type}[id*="${keyword}" i]`,
                `${type}[class*="${keyword}" i]`
            ];

            for (let selector of selectors) {
                const element = document.querySelector(selector);
                if (element) {
                    console.log(`✅ 找到字段 [${keyword}]:`, selector);
                    return element;
                }
            }
        }
        console.warn(`⚠️ 未找到字段:`, keywords);
        return null;
    }

    // 快速填写文本
    async fillText(element, value) {
        if (!element) return false;

        // 模拟真实输入
        element.focus();
        element.value = value;

        // 触发所有可能的事件
        ['input', 'change', 'blur'].forEach(eventType => {
            element.dispatchEvent(new Event(eventType, { bubbles: true }));
        });

        return true;
    }

    // 选择下拉框
    async selectOption(element, keyword) {
        if (!element) return false;

        // 查找包含关键词的选项
        const options = Array.from(element.options);
        const targetOption = options.find(opt =>
            opt.text.includes(keyword) || opt.value.includes(keyword)
        );

        if (targetOption) {
            element.value = targetOption.value;
            element.dispatchEvent(new Event('change', { bubbles: true }));
            console.log(`✅ 已选择: ${targetOption.text}`);
            return true;
        }

        console.warn(`⚠️ 未找到匹配选项: ${keyword}`);
        return false;
    }

    // 验证码识别 (简化版本 - 需要手动输入)
    async handleCaptcha() {
        const captchaInput = this.findInput(['captcha', '验证码', 'code', 'verify']);
        if (!captchaInput) return;

        console.log('%c⚠️ 请手动输入验证码', 'color: orange; font-size: 14px; font-weight: bold');
        // 这里可以集成OCR API，但为了速度，建议手动输入
    }

    // 超高速填写
    async fillForm() {
        const startTime = performance.now();
        console.log('%c⚡ 开始超高速填写...', 'color: yellow; font-size: 14px');

        try {
            // 并发填写所有字段
            await Promise.all([
                // 姓名
                this.fillText(
                    this.findInput(['name', '姓名', 'username']),
                    this.config.name
                ),

                // 证件号码
                this.fillText(
                    this.findInput(['id', 'idcard', '证件', '身份证', 'card']),
                    this.config.idNumber
                ),

                // 手机号
                this.fillText(
                    this.findInput(['phone', 'mobile', '手机', 'tel']),
                    this.config.phone
                ),

                // 数量
                this.fillText(
                    this.findInput(['quantity', 'amount', '数量', 'num']),
                    this.config.quantity.toString()
                )
            ]);

            // 证件类型下拉框
            const idTypeSelect = this.findInput(['idtype', '证件类型', 'cardtype'], 'select');
            if (idTypeSelect) {
                await this.selectOption(idTypeSelect, this.config.idType);
            }

            // 兑换网点
            const locationSelect = this.findInput(['location', 'bank', '网点', 'branch'], 'select');
            if (locationSelect) {
                await this.selectOption(locationSelect, this.config.locationKeyword);
            }

            // 验证码处理
            await this.handleCaptcha();

            const elapsed = performance.now() - startTime;
            console.log(`%c✅ 填写完成! 耗时: ${elapsed.toFixed(0)}ms`, 'color: #00ff00; font-size: 16px; font-weight: bold');

            // 自动提交
            if (this.config.autoSubmit) {
                this.submit();
            } else {
                console.log('%c💡 请检查信息后手动点击提交按钮', 'color: #00aaff; font-size: 14px');
            }

        } catch (error) {
            console.error('❌ 填写失败:', error);
        }
    }

    // 提交表单
    submit() {
        const submitBtn = document.querySelector('button[type="submit"], button:contains("提交"), button:contains("确认"), .submit-btn');
        if (submitBtn) {
            submitBtn.click();
            console.log('✅ 已自动提交');
        } else {
            console.warn('⚠️ 未找到提交按钮');
        }
    }

    // 显示所有表单元素（调试用）
    debugShowAllInputs() {
        console.log('%c=== 页面所有表单元素 ===', 'color: cyan; font-size: 14px; font-weight: bold');

        document.querySelectorAll('input, select, textarea').forEach((el, index) => {
            console.log(`[${index}]`, {
                type: el.tagName,
                name: el.name,
                id: el.id,
                placeholder: el.placeholder,
                class: el.className
            });
        });
    }
}

// ===================================================
// 自动执行
// ===================================================

console.log('%c═══════════════════════════════════════', 'color: #00aaff');
console.log('%c   纪念钞预约 - 超高速自动填写脚本   ', 'color: #00ff00; font-size: 16px; font-weight: bold');
console.log('%c═══════════════════════════════════════', 'color: #00aaff');
console.log('');

const filler = new AutoFiller(CONFIG);

// 立即执行填写
filler.fillForm();

// 导出到全局，方便手动调用
window.autoFiller = filler;

console.log('');
console.log('%c💡 常用命令:', 'color: cyan; font-weight: bold');
console.log('  autoFiller.fillForm()     - 重新填写');
console.log('  autoFiller.submit()       - 提交表单');
console.log('  autoFiller.debugShowAllInputs() - 显示所有表单元素');
console.log('');
