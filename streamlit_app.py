import streamlit as st
import json
import os
import time
import random
import base64
from prompt_engineer import PromptEngineer

# 导入新的评估模块
try:
    from prompt_quality_evaluator import PromptQualityEvaluator
    EVALUATOR_AVAILABLE = True
except ImportError:
    EVALUATOR_AVAILABLE = False
    print("警告: 未找到提示质量评估模块，相关功能将不可用")

# 导入编程模板和智能建议器
try:
    from programming_prompt_templates import get_programming_templates, list_task_types, list_ai_tools
    from prompt_advisor import PromptAdvisor
    PROGRAMMING_TEMPLATES_AVAILABLE = True
except ImportError:
    PROGRAMMING_TEMPLATES_AVAILABLE = False
    print("警告: 未找到编程模板模块，相关功能将不可用")

# 导入API密钥管理模块
try:
    from api_secrets import get_api_key, get_api_config, save_api_key
    SECRETS_MODULE_AVAILABLE = True
except ImportError:
    SECRETS_MODULE_AVAILABLE = False
    print("警告: 未找到API密钥管理模块 (api_secrets.py)，将使用基本方法获取API密钥")

# 检查Streamlit secrets
def check_streamlit_secrets():
    """检查Streamlit secrets配置"""
    try:
        # 尝试访问secrets
        if hasattr(st, 'secrets') and st.secrets:
            return True
    except Exception:
        pass
    return False

STREAMLIT_SECRETS_AVAILABLE = check_streamlit_secrets()

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
    """从多个来源加载配置"""
    config = {
        "api_key": "",
        "api_provider": "deepseek",
        "model": "deepseek-chat",
        "default_format": "standard",
        "language": "zh"
    }
    
    # 首先尝试从config.json加载基本配置
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception as e:
            st.sidebar.warning(f"加载config.json失败: {e}", icon="⚠️")
    
    # 然后尝试从不同来源加载API密钥
    api_key_loaded = False
    
    # 1. 尝试从API密钥管理模块加载
    if SECRETS_MODULE_AVAILABLE:
        try:
            api_config = get_api_config()
            if api_config.get("api_key"):
                config.update(api_config)
                st.sidebar.success("✅ 已从安全存储加载API配置", icon="🔐")
                api_key_loaded = True
        except Exception as e:
            st.sidebar.warning(f"从安全存储加载失败: {e}", icon="⚠️")
    
    # 2. 尝试从Streamlit secrets加载
    if not api_key_loaded and STREAMLIT_SECRETS_AVAILABLE:
        try:
            provider = config.get("api_provider", "deepseek")
            key_name = f"{provider.upper()}_API_KEY"
            if key_name in st.secrets:
                config["api_key"] = st.secrets[key_name]
                st.sidebar.success("✅ 已从Streamlit secrets加载API密钥", icon="🔑")
                api_key_loaded = True
        except Exception as e:
            st.sidebar.warning(f"从Streamlit secrets加载失败: {e}", icon="⚠️")
    
    # 3. 尝试从环境变量加载
    if not api_key_loaded:
        provider = config.get("api_provider", "deepseek")
        env_key = f"{provider.upper()}_API_KEY"
        env_value = os.getenv(env_key)
        if env_value:
            config["api_key"] = env_value
            st.sidebar.success(f"✅ 已从环境变量加载{provider}密钥", icon="🌍")
            api_key_loaded = True
    
    # 如果没有找到API密钥，显示提示
    if not api_key_loaded and not config.get("api_key"):
        st.sidebar.info("💡 请在侧边栏设置API密钥或使用安全存储", icon="💡")
    
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
        "examples": "#FF9800",
        "coding": "#9C27B0",
        "cursor": "#00BCD4",
        "architecture": "#795548",
        "programming_template": "#E91E63"
    }
    labels = {
        "standard": "标准",
        "expert-panel": "专家讨论",
        "examples": "带示例",
        "coding": "编程任务",
        "cursor": "Cursor优化",
        "architecture": "系统架构",
        "programming_template": "编程模板"
    }
    return f'<span style="background-color:{colors.get(format_name, "#666")};color:white;padding:2px 8px;border-radius:10px;font-size:0.8em;">{labels.get(format_name, format_name)}</span>'

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
if EVALUATOR_AVAILABLE and PROGRAMMING_TEMPLATES_AVAILABLE:
    tabs = st.tabs(["✨ 生成提示", "🧑‍💻 编程模板", "🤖 智能建议", "📊 质量评估", "📋 历史记录", "ℹ️ 使用帮助"])
elif EVALUATOR_AVAILABLE:
    tabs = st.tabs(["✨ 生成提示", "📊 质量评估", "📋 历史记录", "ℹ️ 使用帮助"])
elif PROGRAMMING_TEMPLATES_AVAILABLE:
    tabs = st.tabs(["✨ 生成提示", "🧑‍💻 编程模板", "🤖 智能建议", "📋 历史记录", "ℹ️ 使用帮助"])
else:
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
            "examples": "带示例 - 通过示例学习模式",
            "coding": "编程任务 - 代码生成优化提示",
            "cursor": "Cursor优化 - 专为Cursor AI编辑器设计",
            "architecture": "系统架构 - 软件架构设计提示"
        }
        prompt_format = st.radio(
            "选择格式", 
            options=list(format_options.keys()), 
            format_func=lambda x: format_options[x],
            horizontal=False,
            help="不同格式适合不同类型的内容生成需求"
        )
        
        # 根据选择的格式显示相应的配置选项
        if prompt_format == "coding":
            st.subheader("编程设置")
            programming_language = st.selectbox(
                "编程语言", 
                ["Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby"],
                index=0,
                help="选择要生成代码的编程语言"
            )
            coding_task_type = st.selectbox(
                "任务类型",
                ["general", "debug", "refactor", "review", "test", "optimize", "document"],
                format_func=lambda x: {
                    "general": "通用开发",
                    "debug": "调试代码", 
                    "refactor": "代码重构",
                    "review": "代码审查",
                    "test": "编写测试",
                    "optimize": "性能优化",
                    "document": "添加文档"
                }[x],
                help="选择具体的编程任务类型"
            )
        
        elif prompt_format == "cursor":
            st.subheader("Cursor AI 设置")
            project_context = st.text_area(
                "项目上下文",
                placeholder="描述项目的背景、技术栈、文件结构等...",
                height=100,
                help="提供项目的详细上下文，帮助Cursor更好地理解需求"
            )
            file_types = st.multiselect(
                "相关文件类型",
                ["Python", "JavaScript", "TypeScript", "React", "Vue", "HTML", "CSS", "JSON", "Markdown"],
                default=["Python", "JavaScript", "TypeScript"],
                help="选择将要处理的文件类型"
            )
            
        elif prompt_format == "architecture":
            st.subheader("架构设计设置")
            system_type = st.selectbox(
                "系统类型",
                ["web_application", "microservice", "mobile_app", "desktop_app", "api_service", "data_pipeline"],
                format_func=lambda x: {
                    "web_application": "Web应用",
                    "microservice": "微服务",
                    "mobile_app": "移动应用",
                    "desktop_app": "桌面应用",
                    "api_service": "API服务",
                    "data_pipeline": "数据管道"
                }[x],
                help="选择要设计的系统类型"
            )
            technologies = st.multiselect(
                "技术栈",
                ["React", "Vue", "Angular", "Node.js", "Django", "FastAPI", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS", "Azure"],
                default=["React", "Node.js", "PostgreSQL", "Docker"],
                help="选择项目使用的技术栈"
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
                        elif prompt_format == "coding":
                            prompt = prompt_engineer.generate_coding_prompt(
                                requirement, 
                                programming_language=programming_language, 
                                coding_task_type=coding_task_type,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                        elif prompt_format == "cursor":
                            prompt = prompt_engineer.generate_cursor_optimized_prompt(
                                requirement, 
                                context=project_context, 
                                file_types=file_types,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                        elif prompt_format == "architecture":
                            prompt = prompt_engineer.generate_architecture_prompt(
                                requirement, 
                                system_type=system_type, 
                                technologies=technologies,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                        
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

# 编程模板标签页
if PROGRAMMING_TEMPLATES_AVAILABLE:
    with tabs[1]:
        st.header("🧑‍💻 编程Prompt模板")
        
        st.markdown("""
        <div class='tip-card'>
            <strong>💡 编程模板功能</strong><br>
            提供专门针对编程任务的Prompt模板，包括代码生成、调试、重构、测试等常见场景。
        </div>
        """, unsafe_allow_html=True)
        
        template_col1, template_col2 = st.columns([1, 1])
        
        with template_col1:
            st.subheader("📋 选择模板")
            
            # 初始化模板管理器
            templates_manager = get_programming_templates()
            
            # 任务类型筛选
            task_types = list_task_types()
            task_type_labels = {
                "code_generation": "代码生成",
                "code_review": "代码审查", 
                "bug_fixing": "Bug修复",
                "refactoring": "代码重构",
                "code_explanation": "代码解释",
                "api_design": "API设计",
                "database_design": "数据库设计",
                "testing": "测试编写",
                "documentation": "文档编写",
                "optimization": "性能优化",
                "architecture_design": "架构设计",
                "deployment": "部署配置"
            }
            
            selected_task_type = st.selectbox(
                "任务类型",
                options=task_types,
                format_func=lambda x: task_type_labels.get(x, x),
                help="选择您要执行的编程任务类型"
            )
            
            # AI工具筛选
            ai_tools = list_ai_tools()
            ai_tool_labels = {
                "cursor": "Cursor",
                "github_copilot": "GitHub Copilot",
                "codewhisperer": "CodeWhisperer",
                "tabnine": "TabNine",
                "chatgpt": "ChatGPT",
                "claude": "Claude",
                "general": "通用"
            }
            
            selected_ai_tool = st.selectbox(
                "AI工具",
                options=ai_tools,
                format_func=lambda x: ai_tool_labels.get(x, x),
                help="选择您使用的AI编程工具"
            )
            
            # 获取匹配的模板
            from programming_prompt_templates import ProgrammingTaskType, AITool
            task_type_enum = ProgrammingTaskType(selected_task_type)
            ai_tool_enum = AITool(selected_ai_tool)
            
            matching_templates = []
            for template in templates_manager.list_all_templates():
                if (template.task_type == task_type_enum or 
                    template.ai_tool == ai_tool_enum or 
                    template.ai_tool == AITool.GENERAL):
                    matching_templates.append(template)
            
            if matching_templates:
                template_names = [t.name for t in matching_templates]
                selected_template_name = st.selectbox(
                    "选择模板",
                    options=template_names,
                    help="选择最适合您需求的模板"
                )
                
                # 获取选中的模板
                selected_template = next(t for t in matching_templates if t.name == selected_template_name)
                
                # 显示模板信息
                st.subheader("📄 模板信息")
                st.write(f"**描述**: {selected_template.description}")
                st.write(f"**任务类型**: {task_type_labels.get(selected_template.task_type.value, selected_template.task_type.value)}")
                st.write(f"**AI工具**: {ai_tool_labels.get(selected_template.ai_tool.value, selected_template.ai_tool.value)}")
                
                # 显示需要的变量
                if selected_template.variables:
                    st.subheader("📝 需要填写的变量")
                    template_vars = {}
                    for var in selected_template.variables:
                        template_vars[var] = st.text_input(
                            f"{var}",
                            placeholder=f"请输入{var}...",
                            help=f"模板中的{var}变量"
                        )
                
                # 显示使用技巧
                if selected_template.tips:
                    with st.expander("💡 使用技巧", expanded=False):
                        for tip in selected_template.tips:
                            st.info(tip)
                
                # 显示示例
                if selected_template.examples:
                    with st.expander("📚 使用示例", expanded=False):
                        for example in selected_template.examples:
                            st.code(example)
            else:
                st.warning("没有找到匹配的模板")
        
        with template_col2:
            st.subheader("✨ 生成的Prompt")
            
            if 'selected_template' in locals() and selected_template:
                generate_template_button = st.button(
                    "🚀 生成Prompt",
                    type="primary",
                    use_container_width=True,
                    help="基于模板和您的输入生成Prompt"
                )
                
                if generate_template_button:
                    try:
                        # 检查是否所有必需变量都已填写
                        missing_vars = [var for var in selected_template.variables if not template_vars.get(var)]
                        if missing_vars:
                            st.error(f"请填写以下必需变量: {', '.join(missing_vars)}")
                        else:
                            # 生成模板ID
                            template_id = list(templates_manager.templates.keys())[
                                list(templates_manager.templates.values()).index(selected_template)
                            ]
                            
                            # 生成Prompt
                            generated_prompt = templates_manager.generate_prompt(template_id, **template_vars)
                            
                            # 显示生成的Prompt
                            st.markdown(f"""
                            <div class='output-area'>
                                <h4>生成的Prompt:</h4>
                                <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace;">{generated_prompt}</pre>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 复制按钮
                            st.code(generated_prompt, language="text")
                            
                            # 添加到历史记录
                            requirement_summary = f"使用模板: {selected_template.name}"
                            add_to_history(requirement_summary, generated_prompt, "programming_template", "Template")
                            
                            st.success("✅ Prompt已生成并添加到历史记录")
                    
                    except Exception as e:
                        st.error(f"生成Prompt时出错: {e}")
            else:
                st.markdown("""
                <div style="text-align:center;padding:50px 0;color:#888;">
                    <span style="font-size:3em;">🧑‍💻</span>
                    <p>生成的Prompt将显示在这里</p>
                    <p style="font-size:0.9em;">选择模板并填写变量后点击生成</p>
                </div>
                """, unsafe_allow_html=True)

# 智能建议标签页
if PROGRAMMING_TEMPLATES_AVAILABLE:
    with tabs[2]:
        st.header("🤖 智能Prompt建议")
        
        st.markdown("""
        <div class='tip-card'>
            <strong>💡 智能建议功能</strong><br>
            分析您的编程需求，自动推荐最适合的模板和改进建议，让您的Prompt更加精准有效。
        </div>
        """, unsafe_allow_html=True)
        
        advisor_col1, advisor_col2 = st.columns([1, 1])
        
        with advisor_col1:
            st.subheader("📝 描述您的需求")
            
            user_requirement = st.text_area(
                "详细描述您的编程需求",
                height=200,
                placeholder="例如：我想用Python创建一个函数来处理CSV文件数据，需要读取、清洗和分析数据...",
                help="越详细的描述能获得越准确的建议"
            )
            
            analyze_button = st.button(
                "🔍 分析需求",
                type="primary",
                use_container_width=True,
                help="分析您的需求并提供智能建议"
            )
        
        with advisor_col2:
            st.subheader("🎯 智能分析结果")
            
            if analyze_button and user_requirement:
                try:
                    with st.spinner("正在分析您的需求..."):
                        advisor = PromptAdvisor()
                        result = advisor.analyze_and_recommend(user_requirement)
                        
                        # 显示分析结果
                        analysis = result["analysis"]
                        
                        st.markdown(f"""
                        <div style="background-color:{current_theme["output_bg"]};padding:15px;border-radius:8px;margin-bottom:15px;">
                            <h4>🔍 需求分析</h4>
                            <p><strong>任务类型:</strong> {task_type_labels.get(analysis['task_type'], analysis['task_type'])} 
                               <span style="color:{current_theme['accent']};font-size:0.9em;">(置信度: {analysis['confidence']:.1%})</span></p>
                            <p><strong>编程语言:</strong> {analysis['language']}</p>
                            <p><strong>AI工具:</strong> {ai_tool_labels.get(analysis['ai_tool'], analysis['ai_tool'])}</p>
                            <p><strong>复杂度:</strong> {analysis['complexity']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 显示关键词
                        if analysis["keywords"]:
                            st.markdown("**🏷️ 识别的关键词:**")
                            keywords_html = " ".join([f"<span style='background-color:{current_theme['primary']};color:white;padding:2px 8px;border-radius:12px;font-size:0.8em;margin:2px;'>{kw}</span>" for kw in analysis["keywords"]])
                            st.markdown(keywords_html, unsafe_allow_html=True)
                        
                        # 显示缺失信息
                        if analysis["missing_info"]:
                            st.markdown("**⚠️ 建议补充的信息:**")
                            for info in analysis["missing_info"]:
                                st.warning(f"• {info}", icon="💡")
                        
                        # 显示推荐模板
                        st.subheader("📋 推荐模板")
                        recommendations = result["recommendations"]
                        
                        if recommendations:
                            for i, rec in enumerate(recommendations, 1):
                                with st.expander(f"推荐 {i}: {rec['template_name']} (相关性: {rec['relevance_score']:.1%})", expanded=i==1):
                                    # 推荐理由
                                    if rec["reasons"]:
                                        st.markdown("**推荐理由:**")
                                        for reason in rec["reasons"]:
                                            st.success(f"• {reason}", icon="✅")
                                    
                                    # 改进建议
                                    if rec["improvements"]:
                                        st.markdown("**改进建议:**")
                                        for improvement in rec["improvements"]:
                                            st.info(f"• {improvement}", icon="💡")
                                    
                                    # 示例Prompt预览
                                    st.markdown("**Prompt预览:**")
                                    st.code(rec["example_prompt"], language="text")
                                    
                                    # 使用此模板按钮
                                    if st.button(f"使用模板: {rec['template_name']}", key=f"use_template_{i}"):
                                        st.session_state.selected_template_id = rec['template_id']
                                        st.success(f"已选择模板: {rec['template_name']}")
                                        st.info("请切换到'编程模板'标签页继续配置")
                        else:
                            st.warning("未找到匹配的模板推荐")
                        
                        # 显示通用建议
                        if result["tips"]:
                            st.subheader("💡 使用建议")
                            for tip in result["tips"]:
                                st.info(tip)
                
                except Exception as e:
                    st.error(f"分析过程中出错: {e}")
            
            elif analyze_button and not user_requirement:
                st.error("请输入您的编程需求")
            
            else:
                st.markdown("""
                <div style="text-align:center;padding:50px 0;color:#888;">
                    <span style="font-size:3em;">🤖</span>
                    <p>智能分析结果将显示在这里</p>
                    <p style="font-size:0.9em;">描述您的需求并点击"分析需求"</p>
                </div>
                """, unsafe_allow_html=True)

# 质量评估标签页
tab_index = 3 if PROGRAMMING_TEMPLATES_AVAILABLE else 1
if EVALUATOR_AVAILABLE:
    with tabs[tab_index]:
        st.header("📊 提示质量评估")
        
        st.markdown("""
        <div class='tip-card'>
            <strong>💡 质量评估功能</strong><br>
            评估您生成的提示词质量，从清晰度、具体性、完整性、结构性和可操作性五个维度进行分析，并提供改进建议。
        </div>
        """, unsafe_allow_html=True)
        
        # 评估输入
        eval_col1, eval_col2 = st.columns([1, 1])
        
        with eval_col1:
            st.subheader("📝 输入评估内容")
            
            # 选择评估来源
            eval_source = st.radio(
                "选择评估来源",
                ["手动输入", "从历史记录选择"],
                horizontal=True
            )
            
            if eval_source == "手动输入":
                prompt_to_evaluate = st.text_area(
                    "要评估的提示词",
                    height=200,
                    placeholder="在此输入您想要评估的提示词...",
                    help="输入完整的提示词内容"
                )
                original_requirement = st.text_input(
                    "原始需求（可选）",
                    placeholder="输入生成此提示词的原始需求...",
                    help="提供原始需求有助于更准确的评估"
                )
            else:
                if st.session_state.history:
                    selected_history = st.selectbox(
                        "选择历史记录",
                        options=range(len(st.session_state.history)),
                        format_func=lambda x: f"{st.session_state.history[x]['requirement'][:50]}... ({format_timestamp(st.session_state.history[x]['timestamp'])})"
                    )
                    prompt_to_evaluate = st.session_state.history[selected_history]['prompt']
                    original_requirement = st.session_state.history[selected_history]['requirement']
                    
                    st.text_area(
                        "提示词预览",
                        value=prompt_to_evaluate,
                        height=150,
                        disabled=True
                    )
                else:
                    st.info("暂无历史记录可供选择")
                    prompt_to_evaluate = ""
                    original_requirement = ""
            
            # 评估按钮
            evaluate_button = st.button(
                "🔍 开始评估",
                type="primary",
                use_container_width=True,
                help="对提示词进行质量评估"
            )
        
        with eval_col2:
            st.subheader("📋 评估结果")
            
            if evaluate_button and prompt_to_evaluate:
                try:
                    with st.spinner("正在评估提示质量..."):
                        evaluator = PromptQualityEvaluator()
                        report = evaluator.evaluate_prompt(prompt_to_evaluate, original_requirement)
                        
                        # 显示总体评分
                        st.markdown(f"""
                        <div style="text-align:center;padding:20px;background-color:{current_theme["output_bg"]};border-radius:10px;margin-bottom:20px;">
                            <h2 style="color:{current_theme["primary"]};margin:0;">总体评分</h2>
                            <h1 style="font-size:3em;margin:10px 0;color:{current_theme["accent"]};">{report.overall_score}/10</h1>
                            <h3 style="margin:0;color:{current_theme["text"]};">等级: {report.grade}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 详细评分
                        st.subheader("📊 详细评分")
                        metric_names = {
                            "clarity": "清晰度",
                            "specificity": "具体性", 
                            "completeness": "完整性",
                            "structure": "结构性",
                            "actionability": "可操作性"
                        }
                        
                        for score in report.scores:
                            metric_name = metric_names.get(score.metric.value, score.metric.value)
                            
                            # 创建进度条颜色
                            if score.score >= 8:
                                bar_color = "#4CAF50"  # 绿色
                            elif score.score >= 6:
                                bar_color = "#FF9800"  # 橙色
                            else:
                                bar_color = "#F44336"  # 红色
                            
                            st.markdown(f"""
                            <div style="margin-bottom:15px;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <strong>{metric_name}</strong>
                                    <span style="font-weight:bold;color:{bar_color};">{score.score}/10</span>
                                </div>
                                <div style="background-color:#E0E0E0;border-radius:10px;height:8px;margin:5px 0;">
                                    <div style="background-color:{bar_color};height:100%;border-radius:10px;width:{score.score*10}%;"></div>
                                </div>
                                <small style="color:#666;">{score.explanation}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 优势和改进建议
                        col_strengths, col_improvements = st.columns(2)
                        
                        with col_strengths:
                            if report.strengths:
                                st.subheader("✅ 优势")
                                for strength in report.strengths:
                                    st.success(strength, icon="✅")
                        
                        with col_improvements:
                            if report.improvements:
                                st.subheader("🔧 改进建议")
                                for i, improvement in enumerate(report.improvements, 1):
                                    st.warning(f"{i}. {improvement}", icon="💡")
                        
                        # 详细报告下载
                        detailed_report = evaluator.generate_detailed_report(report)
                        st.download_button(
                            label="📄 下载详细评估报告",
                            data=detailed_report,
                            file_name=f"prompt_evaluation_{int(time.time())}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"评估过程中出错: {e}")
            
            elif evaluate_button and not prompt_to_evaluate:
                st.error("请输入要评估的提示词")
            
            else:
                st.markdown("""
                <div style="text-align:center;padding:50px 0;color:#888;">
                    <span style="font-size:3em;">📊</span>
                    <p>评估结果将显示在这里</p>
                    <p style="font-size:0.9em;">输入提示词并点击"开始评估"</p>
                </div>
                """, unsafe_allow_html=True)

# 历史记录标签页
if PROGRAMMING_TEMPLATES_AVAILABLE and EVALUATOR_AVAILABLE:
    history_tab_index = 4
elif PROGRAMMING_TEMPLATES_AVAILABLE:
    history_tab_index = 3
elif EVALUATOR_AVAILABLE:
    history_tab_index = 2
else:
    history_tab_index = 1

with tabs[history_tab_index]:
    st.header("📋 您的生成历史")
    
    if not st.session_state.history:
        st.info("还没有生成历史记录。生成一些提示后，它们将显示在这里。")
    else:
        # 历史记录筛选
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            all_formats = list(set(item["format"] for item in st.session_state.history))
            format_labels = {
                "standard": "标准", 
                "expert-panel": "专家讨论", 
                "examples": "带示例",
                "coding": "编程任务",
                "cursor": "Cursor优化", 
                "architecture": "系统架构"
            }
            format_filter = st.multiselect(
                "按格式筛选", 
                options=all_formats,
                format_func=lambda x: format_labels.get(x, x)
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
if PROGRAMMING_TEMPLATES_AVAILABLE and EVALUATOR_AVAILABLE:
    help_tab_index = 5
elif PROGRAMMING_TEMPLATES_AVAILABLE:
    help_tab_index = 4
elif EVALUATOR_AVAILABLE:
    help_tab_index = 3
else:
    help_tab_index = 2

with tabs[help_tab_index]:
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
       - **编程任务**: 专为代码生成、调试、重构等编程任务优化
       - **Cursor优化**: 专门为Cursor AI编辑器设计的提示格式
       - **系统架构**: 用于软件系统架构设计和技术规划
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
        
        ### 编程任务格式
        专为软件开发优化，支持多种编程场景:
        - 代码生成和实现
        - 代码调试和修复
        - 代码重构和优化
        - 代码审查和测试
        - 技术文档编写
        
        ### Cursor优化格式
        专门为Cursor AI编辑器设计，包含:
        - 项目上下文理解
        - 文件结构集成
        - 代码风格保持
        - 逐步实现指导
        
        ### 系统架构格式
        用于软件系统设计，涵盖:
        - 高层架构设计
        - 技术栈选择
        - 数据库设计
        - 安全性考虑
        - 部署和扩展策略
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