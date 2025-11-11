import streamlit as st
import pandas as pd
import plotly.express as px

# --- 檔案設定 ---
# 設定您的 Excel 檔案名稱
FILE_NAME = 'Finance_Record.xlsx'
# 修正：設定您的工作表名稱為「工作表1」
SHEET_NAME = '工作表1' 

# 設定 Streamlit 頁面配置
st.set_page_config(layout="wide", page_title="Personal Asset Tracker")

# --- 數據載入與處理函式 ---
def load_data():
    """載入並處理 Excel 數據"""
    try:
        # 讀取 Excel 檔案
        # openpyxl 是讀取 .xlsx 格式檔案的引擎
        df = pd.read_excel(FILE_NAME, sheet_name=SHEET_NAME, engine='openpyxl')
        
        # 確保日期欄位是日期格式
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 移除所有日期為空值的列，只保留有效數據
        df = df.dropna(subset=['日期']).reset_index(drop=True)
        
        # 將日期設定為索引
        df = df.set_index('日期')
        
        return df
    except FileNotFoundError:
        st.error(f"錯誤：找不到檔案 {FILE_NAME}。請確保檔案已存在且檔名正確。")
        return pd.DataFrame()
    except ValueError as e:
        st.error(f"錯誤：請檢查 Excel 工作表名稱是否為 '{SHEET_NAME}'，或數據格式是否有誤。詳細錯誤: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"讀取檔案時發生其他錯誤: {e}")
        return pd.DataFrame()

# --- 儀表板主要內容 ---
df = load_data()

# 檢查 DataFrame 是否有足夠數據來繪圖 (至少需要兩行)
if not df.empty and len(df) > 1:
    st.title("💰 Personal Asset Tracker (個人資產追蹤)")
    st.markdown("---")

    # 1. 總資產趨勢圖 (曲線圖)
    st.header("📈 總資產累積變化")
    
    fig_total = px.line(
        df,
        y='總資產 (元)',
        title='總資產 (台股+美股) 歷史曲線',
        labels={'總資產 (元)': '資產金額 (元)'}
    )
    fig_total.update_layout(hovermode="x unified") # 統一顯示滑鼠懸停資訊
    st.plotly_chart(fig_total, use_container_width=True)


    # 2. 每日變化量比較圖 (柱狀圖)
    st.header("📉 兩項資產每日盈虧貢獻")
    
    # 選擇需要的欄位繪圖
    df_changes = df[['資產一 每日變化 (元)', '資產二 每日變化 (元)']]
    
    fig_changes = px.bar(
        df_changes,
        title='資產一 vs. 資產二 每日變化量比較',
        labels={'value': '變化金額 (元)', 'variable': '資產類別'},
        barmode='group', # 並排顯示
        color_discrete_map={ # 讓顏色更具識別性
            '資產一 每日變化 (元)': '#1f77b4',
            '資產二 每日變化 (元)': '#ff7f0e'
        }
    )
    st.plotly_chart(fig_changes, use_container_width=True)

    st.markdown("---")
    
    # 3. 關鍵數據總覽 (Metric Cards)
    st.header("📝 數據總覽與摘要")
    
    # 計算總結數據
    start_asset = df['總資產 (元)'].iloc[0]
    latest_asset = df['總資產 (元)'].iloc[-1]
    total_gain = latest_asset - start_asset
    
    # 顯示摘要卡片
    col1, col2, col3 = st.columns(3)
    
    col1.metric("📊 最新總資產", f"NT$ {latest_asset:,.0f}")
    col2.metric(
        "🚀 總累積盈虧", 
        f"NT$ {total_gain:,.0f}", 
        f"{total_gain/start_asset:.2%}" # 顯示百分比變化
    )
    col3.metric("📅 記錄天數", f"{len(df)} 天")
    
    # 4. 原始數據表格 (可選)
    if st.checkbox('顯示詳細數據表格'):
        # 格式化數字以增強可讀性
        st.dataframe(df.style.format("{:,.0f}")) 

else:
    # 數據不足或檔案無法載入時的提示
    st.warning("⚠️ 數據不足或檔案載入失敗！")
    st.info(f"請檢查：\n1. Excel 檔案 '{FILE_NAME}' 是否已關閉並位於程式碼同一目錄。\n2. Excel 工作表名稱是否為 '{SHEET_NAME}'。\n3. Excel 中是否已填寫**至少兩行**有效的日期與資產數據。")

# 確保 Streamlit 能夠運行 Plotly
st.markdown("<style>.stAlert{white-space: pre-wrap;}</style>", unsafe_allow_html=True)
