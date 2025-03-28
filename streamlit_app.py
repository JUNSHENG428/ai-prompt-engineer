import streamlit as st
import json
import os
import time
import random
import base64
from prompt_engineer import PromptEngineer

# 导入API密钥管理模块
try:
    from api_secrets import get_api_key, get_api_config, save_api_key
    SECRETS_MODULE_AVAILABLE = True
except ImportError:
    SECRETS_MODULE_AVAILABLE = False
    print("警告: 未找到API密钥管理模块 (api_secrets.py)，将使用基本方法获取API密钥")

# 设置页面配置
st.set_page_config(
    page_title="AI提示工程师",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/auto-prompting_engineer',
        'Report a bug': 'https://github.com/yourusername/auto-prompting_engineer/issues',
        'About': "# AI提示工程师\n这是一个自动提示词工程工具，可以根据您的需求生成优化的提示词。"
    }
)

# 定义主题颜色
THEMES = {
    "light": {
        "primary": "#1E88E5",
        "secondary": "#26A69A",
        "background": "#FFFFFF",
        "text": "#212121",
        "accent": "#FF5722",
        "output_bg": "#F5F7F9",
        "output_border": "#E0E0E0"
    },
    "dark": {
        "primary": "#90CAF9",
        "secondary": "#80CBC4",
        "background": "#121212",
        "text": "#EEEEEE",
        "accent": "#FFAB91",
        "output_bg": "#1E1E1E",
        "output_border": "#333333"
    },
    "blue": {
        "primary": "#2196F3",
        "secondary": "#03A9F4",
        "background": "#E3F2FD",
        "text": "#0D47A1",
        "accent": "#FFC107",
        "output_bg": "#BBDEFB",
        "output_border": "#90CAF9"
    },
    "green": {
        "primary": "#4CAF50",
        "secondary": "#8BC34A",
        "background": "#E8F5E9",
        "text": "#1B5E20",
        "accent": "#FF9800",
        "output_bg": "#C8E6C9",
        "output_border": "#A5D6A7"
    }
}

# 初始化会话状态
if 'history' not in st.session_state:
    st.session_state.history = []
if 'theme' not in st.session_state:
    st.session_state.theme = "light"
if 'show_tips' not in st.session_state:
    st.session_state.show_tips = True
if 'prompt_count' not in st.session_state:
    st.session_state.prompt_count = 0
if 'last_save_time' not in st.session_state:
    st.session_state.last_save_time = None

# 获取当前主题
current_theme = THEMES[st.session_state.theme]

# 自定义页面样式
def get_css():
    return f"""
    <style>
        /* 全局样式 */
        .main .block-container {{
            padding-top: 1rem;
            max-width: 1200px;
        }}
        
        /* 标题和文本样式 */
        h1, h2, h3 {{
            color: {current_theme["primary"]};
            font-weight: 600;
        }}
        
        .stTextArea textarea {{
            font-size: 1rem;
            border-radius: 0.5rem;
            border-color: {current_theme["output_border"]};
        }}
        
        /* 输出区域样式 */
        .output-area {{
            background-color: {current_theme["output_bg"]};
            border-radius: 0.5rem;
            padding: 1.2rem;
            border: 1px solid {current_theme["output_border"]};
            margin-bottom: 1rem;
            overflow-x: auto;
        }}
        
        /* 历史记录项目样式 */
        .history-item {{
            padding: 0.8rem;
            border-radius: 0.5rem;
            margin-bottom: 0.8rem;
            border-left: 4px solid {current_theme["primary"]};
            background-color: {current_theme["output_bg"]};
        }}
        
        /* 按钮样式 */
        .custom-button {{
            border-radius: 0.4rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}
        
        .custom-button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        }}
        
        /* 提示卡片样式 */
        .tip-card {{
            background-color: {current_theme["output_bg"]};
            border-left: 4px solid {current_theme["secondary"]};
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        /* 标签页样式 */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {current_theme["output_bg"]};
            border-radius: 4px 4px 0px 0px;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }}
        
        /* 侧边栏样式 */
        .sidebar .sidebar-content {{
            padding: 1rem;
        }}
        
        /* 动画效果 */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .stButton button {{
            width: 100%;
        }}
        
        .fadeIn {{
            animation: fadeIn 0.5s ease-in-out;
        }}
        
        /* 分隔线样式 */
        hr {{
            margin: 1.5rem 0 !important;
            border-color: {current_theme["output_border"]} !important;
        }}
        
        /* 徽章样式 */
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.5rem;
            background-color: {current_theme["primary"]};
            color: white;
            border-radius: 1rem;
            font-size: 0.8rem;
            margin-right: 0.5rem;
        }}
    </style>
    """

st.markdown(get_css(), unsafe_allow_html=True)

# 辅助函数
def load_config():
    """从config.json加载配置"""
    # 如果API密钥管理模块可用，优先使用
    if SECRETS_MODULE_AVAILABLE:
        config = get_api_config()
        if config.get("api_key"):
            st.sidebar.success("✅ 已加载API配置", icon="✅")
        return config
    
    # 否则，使用原始方法加载配置
    config = {
        "api_key": "",
        "api_provider": "deepseek",
        "model": "deepseek-chat",
        "default_format": "standard",
        "language": "zh"
    }
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
            st.sidebar.success("配置已从config.json加载", icon="✅")
        except Exception as e:
            st.sidebar.error(f"加载配置失败: {e}", icon="❌")
    return config

def save_config(config):
    """保存配置到config.json"""
    try:
        # 如果API密钥管理模块可用，使用更安全的方法保存API密钥
        if SECRETS_MODULE_AVAILABLE and config.get("api_key"):
            # 先保存API密钥
            save_api_key(
                config["api_key"], 
                provider=config["api_provider"], 
                method="config"
            )
            
            # 移除API密钥后保存其他配置
            config_without_key = config.copy()
            config_without_key.pop("api_key", None)  # 安全地移除API密钥
            
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config_without_key, f, indent=2, ensure_ascii=False)
        else:
            # 否则使用原始方法
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        st.session_state.last_save_time = time.time()
        st.sidebar.success("配置已保存", icon="✅")
    except Exception as e:
        st.sidebar.error(f"保存配置失败: {e}", icon="❌")

def load_examples(examples_file=None):
    """加载示例数据"""
    default_examples = [
        {"input": "写一首关于自然的诗", "output": "树木轻轻摇曳..."},
        {"input": "解释量子物理", "output": "量子物理是研究..."}
    ]
    
    if not examples_file:
        if os.path.exists("examples.json"):
            examples_file = "examples.json"
    
    if examples_file and os.path.exists(examples_file):
        try:
            with open(examples_file, "r", encoding="utf-8") as f:
                examples = json.load(f)
            return examples
        except Exception as e:
            st.sidebar.error(f"加载示例失败: {e}", icon="❌")
    
    return default_examples

def get_random_tip():
    """获取随机提示技巧"""
    tips = [
        "🌟 **专家讨论**格式适合探讨有争议性的话题，能呈现多种观点。",
        "💡 使用具体的、清晰的需求描述可以获得更精准的提示词。",
        "📚 自定义示例可以大幅提高生成结果的质量和相关性。",
        "🔄 尝试不同的格式可以带来意想不到的灵感。",
        "⚡ Deepseek的模型在技术内容上表现出色，而OpenAI在创意内容上较强。",
        "📋 保存您的配置可以在下次使用时快速恢复设置。",
        "🔍 详细明确的需求描述有助于生成更加精确的提示词。"
    ]
    return random.choice(tips)

def add_to_history(requirement, prompt, format_name, model_name):
    """添加生成记录到历史"""
    history_item = {
        "timestamp": time.time(),
        "requirement": requirement,
        "prompt": prompt,
        "format": format_name,
        "model": model_name
    }
    st.session_state.history.insert(0, history_item)
    st.session_state.prompt_count += 1
    # 限制历史记录最多保存20条
    if len(st.session_state.history) > 20:
        st.session_state.history = st.session_state.history[:20]

def get_format_badge(format_name):
    """获取格式对应的徽章HTML"""
    colors = {
        "standard": "#2196F3",
        "expert-panel": "#4CAF50",
        "examples": "#FF9800"
    }
    labels = {
        "standard": "标准",
        "expert-panel": "专家讨论",
        "examples": "带示例"
    }
    return f'<span style="background-color:{colors[format_name]};color:white;padding:2px 8px;border-radius:10px;font-size:0.8em;">{labels[format_name]}</span>'

def format_timestamp(timestamp):
    """格式化时间戳为可读格式"""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# 页面构建开始
# 加载配置
config = load_config()

# 侧边栏
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🧠 AI提示工程师</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>让AI为您生成完美提示词</p>", unsafe_allow_html=True)
    
    # 主题选择
    st.subheader("🎨 界面主题")
    theme_cols = st.columns(4)
    if theme_cols[0].button("标准", key="theme_light", use_container_width=True):
        st.session_state.theme = "light"
        st.rerun()
    if theme_cols[1].button("暗黑", key="theme_dark", use_container_width=True):
        st.session_state.theme = "dark"
        st.rerun()
    if theme_cols[2].button("蓝色", key="theme_blue", use_container_width=True):
        st.session_state.theme = "blue"
        st.rerun()
    if theme_cols[3].button("绿色", key="theme_green", use_container_width=True):
        st.session_state.theme = "green"
        st.rerun()
    
    # API设置区域
    st.subheader("⚙️ API设置")
    
    # 如果API密钥管理模块可用，显示当前状态
    if SECRETS_MODULE_AVAILABLE:
        current_key = get_api_key(config["api_provider"])
        if current_key:
            st.success(f"✅ 已加载 {config['api_provider']} API密钥")
            # 显示部分遮蔽的API密钥作为安全措施
            masked_key = current_key[:4] + "..." + current_key[-4:] if len(current_key) > 8 else "***"
            st.info(f"当前密钥: {masked_key}")
    
    api_key = st.text_input("API密钥", value=config["api_key"], type="password", key="api_key")
    api_provider = st.selectbox("API提供商", ["deepseek", "openai"], index=0 if config["api_provider"] == "deepseek" else 1)
    
    # 根据API提供商显示相应的模型选择
    models = {
        "deepseek": ["deepseek-chat", "deepseek-coder"],
        "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    }
    model = st.selectbox("模型", models[api_provider])
    
    # 语言选择
    language = st.selectbox(
        "界面语言", 
        ["中文", "English"], 
        index=0 if config.get("language", "zh") == "zh" else 1
    )
    
    # 高级设置
    with st.expander("高级设置"):
        temperature = st.slider("温度 (创造性)", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        max_tokens = st.slider("最大生成长度", min_value=100, max_value=2000, value=1000, step=100)
    
    # 保存设置按钮
    if st.button("💾 保存设置", use_container_width=True):
        new_config = {
            "api_key": api_key,
            "api_provider": api_provider,
            "model": model,
            "default_format": config["default_format"],
            "language": "zh" if language == "中文" else "en",
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        save_config(new_config)
        config = new_config
    
    # 统计信息
    st.markdown("---")
    st.markdown(f"📊 已生成提示数: **{st.session_state.prompt_count}**")
    if st.session_state.last_save_time:
        st.markdown(f"⏱️ 上次保存: {format_timestamp(st.session_state.last_save_time)}")
    
    # 提示小贴士开关
    show_tips = st.toggle("显示提示技巧", value=st.session_state.show_tips)
    if show_tips != st.session_state.show_tips:
        st.session_state.show_tips = show_tips
        st.rerun()

# 主页面标题
st.markdown("<h1 style='text-align: center;'>🧠 AI提示工程师</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;font-size: 1.2em;'>智能提示词生成和优化工具</p>", unsafe_allow_html=True)

# 显示技巧提示
if st.session_state.show_tips:
    with st.container():
        st.markdown(f"""
        <div class='tip-card fadeIn'>
            <strong>💡 提示技巧:</strong> {get_random_tip()}
        </div>
        """, unsafe_allow_html=True)

# 主要内容区域
tabs = st.tabs(["✨ 生成提示", "📋 历史记录", "ℹ️ 使用帮助"])

# 生成提示标签页
with tabs[0]:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 需求输入")
        
        # 用户需求输入
        requirement = st.text_area("输入您的需求", height=150, 
                                    placeholder="例如：'设计一个健康饮食指南'或'如何高效管理团队'",
                                    help="详细描述您需要生成什么类型的内容，越具体越好")
        
        # 提示格式选择
        st.subheader("提示格式")
        format_options = {
            "standard": "标准 - 简洁明了的指导",
            "expert-panel": "专家讨论 - 多角度深入分析",
            "examples": "带示例 - 通过示例学习模式"
        }
        prompt_format = st.radio(
            "选择格式", 
            options=list(format_options.keys()), 
            format_func=lambda x: format_options[x],
            horizontal=True,
            help="不同格式适合不同类型的内容生成需求"
        )
        
        # 如果选择了示例格式，显示示例文件上传
        examples = None
        if prompt_format == "examples":
            st.subheader("示例设置")
            example_file = st.file_uploader("上传示例文件(JSON格式)", type=["json"])
            if example_file:
                try:
                    examples = json.loads(example_file.getvalue().decode())
                    st.success(f"已加载{len(examples)}个示例")
                except Exception as e:
                    st.error(f"解析示例文件失败: {e}")
                    examples = load_examples()
            else:
                examples = load_examples()
                examples_df = st.dataframe(
                    [{"输入": ex["input"], "输出": ex["output"]} for ex in examples],
                    use_container_width=True,
                    height=150
                )
                st.info("使用默认示例。您可以上传自定义JSON文件。")
        
        # 定制选项
        with st.expander("更多选项", expanded=False):
            tone_options = ["专业", "友好", "幽默", "简洁", "详细"]
            tone = st.select_slider("语气风格", options=tone_options, value="专业")
            
            audience_options = ["通用", "初学者", "专业人士", "管理层", "学生"]
            audience = st.select_slider("目标受众", options=audience_options, value="通用")
        
        # 生成按钮
        generate_col1, generate_col2 = st.columns([3, 1])
        generate_button = generate_col1.button(
            "🚀 生成提示", 
            type="primary", 
            use_container_width=True,
            help="点击生成基于您需求的提示词"
        )
        reset_button = generate_col2.button(
            "🔄 重置", 
            use_container_width=True,
            help="清除所有输入"
        )
        
        if reset_button:
            st.rerun()
    
    # 结果显示区域
    with col2:
        st.header("✨ 生成结果")
        
        if generate_button:
            if not requirement:
                st.error("请输入需求")
            elif not api_key:
                st.error("请在侧边栏设置API密钥")
            else:
                try:
                    with st.spinner("正在生成提示..."):
                        # 增加功能参数
                        extra_params = {}
                        if tone != "专业":
                            extra_params["tone"] = tone
                        if audience != "通用":
                            extra_params["audience"] = audience
                        
                        # 初始化提示工程师
                        prompt_engineer = PromptEngineer(
                            api_key=api_key,
                            model_name=model,
                            api_provider=api_provider
                        )
                        
                        # 根据选择的格式生成提示
                        if prompt_format == "standard":
                            prompt = prompt_engineer.generate_formatted_prompt(
                                requirement, 
                                temperature=temperature, 
                                max_tokens=max_tokens
                            )
                        elif prompt_format == "expert-panel":
                            prompt = prompt_engineer.generate_expert_panel_prompt(requirement)
                        elif prompt_format == "examples":
                            prompt = prompt_engineer.generate_prompt_with_examples(requirement, examples)
                        
                        # 添加到历史记录
                        add_to_history(requirement, prompt, prompt_format, model)
                        
                        # 显示生成的提示
                        st.markdown('<div class="output-area fadeIn">', unsafe_allow_html=True)
                        st.markdown(prompt)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # 保存提示到文件
                        col_download1, col_download2 = st.columns(2)
                        with col_download1:
                            st.download_button(
                                label="📄 下载提示为TXT",
                                data=prompt,
                                file_name=f"prompt_{int(time.time())}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        with col_download2:
                            if st.button("📋 复制到剪贴板", use_container_width=True):
                                st.markdown(f"""
                                <script>
                                    navigator.clipboard.writeText(`{prompt.replace('`', '\\`')}`);
                                    alert('已复制到剪贴板!');
                                </script>
                                """, unsafe_allow_html=True)
                                st.success("已复制到剪贴板!")
                
                except Exception as e:
                    st.error(f"生成提示时出错: {e}")
        else:
            # 当没有生成内容时显示的占位内容
            st.markdown("""
            <div style="text-align:center;padding:50px 0;color:#888;">
                <span style="font-size:3em;">✨</span>
                <p>您生成的提示将显示在这里</p>
                <p style="font-size:0.9em;">点击"生成提示"按钮开始</p>
            </div>
            """, unsafe_allow_html=True)

# 历史记录标签页
with tabs[1]:
    st.header("📋 您的生成历史")
    
    if not st.session_state.history:
        st.info("还没有生成历史记录。生成一些提示后，它们将显示在这里。")
    else:
        # 历史记录筛选
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            format_filter = st.multiselect(
                "按格式筛选", 
                options=["standard", "expert-panel", "examples"],
                format_func=lambda x: {"standard": "标准", "expert-panel": "专家讨论", "examples": "带示例"}[x]
            )
        with filter_col2:
            model_filter = st.multiselect(
                "按模型筛选", 
                options=list(set(item["model"] for item in st.session_state.history))
            )
        with filter_col3:
            sort_by = st.selectbox(
                "排序方式",
                options=["最新优先", "最旧优先"]
            )
        
        # 应用筛选和排序
        filtered_history = st.session_state.history.copy()
        if format_filter:
            filtered_history = [item for item in filtered_history if item["format"] in format_filter]
        if model_filter:
            filtered_history = [item for item in filtered_history if item["model"] in model_filter]
        
        if sort_by == "最旧优先":
            filtered_history.reverse()
            
        # 清空历史按钮
        if st.button("🗑️ 清空历史", use_container_width=True):
            st.session_state.history = []
            st.session_state.prompt_count = 0
            st.rerun()
            
        # 显示历史记录
        for i, history_item in enumerate(filtered_history):
            with st.expander(f"{history_item['requirement'][:50]}... ({format_timestamp(history_item['timestamp'])})"):
                st.markdown(f"""
                <p>
                    {get_format_badge(history_item['format'])}
                    <span style="margin-left:10px;font-size:0.9em;color:#666;">模型: {history_item['model']}</span>
                </p>
                <p><strong>需求:</strong> {history_item['requirement']}</p>
                <div class="output-area">
                    {history_item['prompt']}
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(4)
                if cols[0].button("复制提示", key=f"copy_{i}", use_container_width=True):
                    st.write(f"""
                    <script>
                        navigator.clipboard.writeText(`{history_item['prompt'].replace('`', '\\`')}`);
                        alert('已复制到剪贴板!');
                    </script>
                    """, unsafe_allow_html=True)
                    st.success("已复制到剪贴板!")
                
                if cols[1].button("下载", key=f"download_{i}", use_container_width=True):
                    filename = f"prompt_{int(history_item['timestamp'])}.txt"
                    b64 = base64.b64encode(history_item['prompt'].encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">下载文件</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
                if cols[2].button("重新使用", key=f"reuse_{i}", use_container_width=True):
                    # 设置表单值并切换到生成选项卡
                    st.session_state.reuse_requirement = history_item['requirement']
                    st.session_state.reuse_format = history_item['format']
                    st.rerun()
                
                if cols[3].button("删除", key=f"delete_{i}", use_container_width=True):
                    st.session_state.history.remove(history_item)
                    st.rerun()

# 使用帮助标签页
with tabs[2]:
    st.header("ℹ️ 使用指南")
    
    st.subheader("🔍 什么是AI提示工程师?")
    st.markdown("""
    AI提示工程师是一个智能工具，帮助您创建结构化、高效的提示词，以便从AI模型中获得最佳结果。无论您是需要创建内容、解决问题还是生成创意，良好的提示词都是成功的关键。
    """)
    
    st.subheader("🚀 如何使用")
    st.markdown("""
    1. **输入需求** - 在左侧输入框中详细描述您的需求
    2. **选择格式** - 根据您的需求选择合适的提示格式:
       - **标准格式**: 简洁明了的指导，适合大多数场景
       - **专家讨论**: 模拟专家小组讨论，提供多角度分析，适合复杂话题
       - **带示例**: 包含示例的提示，帮助AI理解特定模式
    3. **配置API** - 在侧边栏中设置您的API密钥和模型
    4. **生成提示** - 点击"生成提示"按钮
    5. **使用结果** - 复制或下载生成的提示词，用于您的AI交互
    """)
    
    with st.expander("✨ 提示格式详解"):
        st.markdown("""
        ### 标准格式
        适合大多数使用场景，生成简洁明了的指导。这种格式通常包含:
        - 明确的任务描述
        - 输出格式要求
        - 风格和语气指导
        
        ### 专家讨论格式
        模拟多位专家从不同角度分析问题，适合:
        - 复杂或有争议的话题
        - 需要多角度思考的问题
        - 深度探讨某个领域
        
        ### 带示例格式
        提供具体示例帮助AI理解模式，特别适合:
        - 特定格式的内容生成
        - 希望保持一致风格的创作
        - 教学或解释复杂概念
        """)
    
    with st.expander("💡 提示技巧"):
        st.markdown("""
        1. **具体明确** - 越具体的需求描述会产生越精确的提示词
        2. **指定角色** - 考虑在需求中指定专业角色(如"作为一名营销专家")
        3. **说明受众** - 明确指出目标受众有助于调整内容的复杂度
        4. **使用示例** - 自定义示例能显著提高结果质量
        5. **迭代改进** - 如果第一次结果不理想，调整需求后重试
        """)
    
    with st.expander("🔧 故障排除"):
        st.markdown("""
        **问题**: API调用失败
        **解决方案**: 检查API密钥是否正确，以及是否有足够的配额
        
        **问题**: 生成的提示不符合预期
        **解决方案**: 尝试更详细地描述您的需求，或尝试不同的提示格式
        
        **问题**: 响应时间过长
        **解决方案**: 大型模型(如GPT-4)在复杂请求时可能较慢，尝试使用更小的模型
        """)

# 页脚
st.markdown("---")
footer_cols = st.columns([3, 1])
with footer_cols[0]:
    st.markdown("<p style='color:#888;'>© 2023 AI提示工程师 | 由自动提示词工程助力</p>", unsafe_allow_html=True)
with footer_cols[1]:
    st.markdown("<p style='text-align:right;color:#888;'>版本 2.0</p>", unsafe_allow_html=True) 