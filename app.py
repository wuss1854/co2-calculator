import streamlit as st
import CoolProp.CoolProp as CP
import pandas as pd

# 设置页面配置 (标题、图标、布局)
st.set_page_config(page_title="CO2 物性计算器", page_icon="🧪", layout="centered")

# --- 标题与介绍 ---
st.title("🧪 CO2 物性查询工具")
st.markdown("基于 **CoolProp** 核心库 | 支持移动端访问")

# --- 输入区域 (使用表单，避免输入过程中频繁刷新) ---
with st.form("input_form"):
    st.subheader("1. 工况输入")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temp_val = st.number_input("温度数值", value=25.0, step=1.0)
        temp_unit = st.selectbox("温度单位", ["°C", "K", "°F"])
    
    with col2:
        pres_val = st.number_input("压力数值", value=7.38, step=0.1)
        pres_unit = st.selectbox("压力单位", ["MPa", "bar", "Pa", "atm", "psi"])

    # 提交按钮
    submitted = st.form_submit_button("🚀 开始计算")

# --- 计算逻辑 ---
if submitted:
    # 1. 单位转换到 SI (K, Pa)
    try:
        # 温度转换
        if temp_unit == "°C": T_si = temp_val + 273.15
        elif temp_unit == "K": T_si = temp_val
        elif temp_unit == "°F": T_si = (temp_val - 32) * 5/9 + 273.15
        
        # 压力转换
        if pres_unit == "MPa": P_si = pres_val * 1e6
        elif pres_unit == "bar": P_si = pres_val * 1e5
        elif pres_unit == "Pa": P_si = pres_val
        elif pres_unit == "atm": P_si = pres_val * 101325
        elif pres_unit == "psi": P_si = pres_val * 6894.76

        # 2. CoolProp 计算
        fluid = "CO2"
        
        # 获取物性
        rho = CP.PropsSI('D', 'P', P_si, 'T', T_si, fluid)      # 密度 kg/m3
        visc = CP.PropsSI('V', 'P', P_si, 'T', T_si, fluid)     # 粘度 Pa·s
        cp = CP.PropsSI('C', 'P', P_si, 'T', T_si, fluid)       # 比热 J/kg/K
        cond = CP.PropsSI('L', 'P', P_si, 'T', T_si, fluid)     # 导热 W/m/K
        h = CP.PropsSI('H', 'P', P_si, 'T', T_si, fluid) / 1000 # 焓 kJ/kg
        phase = CP.PhaseSI('P', P_si, 'T', T_si, fluid)         # 相态

        # 3. 结果展示
        st.subheader("2. 计算结果")
        
        # 状态提示
        st.info(f"当前流体状态: **{phase}**")

        # 使用 Metrics 显示核心数据
        m1, m2 = st.columns(2)
        m1.metric("密度 (Density)", f"{rho:.2f} kg/m³")
        m2.metric("动力粘度 (Viscosity)", f"{visc:.6f} Pa·s")
        
        m3, m4 = st.columns(2)
        m3.metric("定压比热容 (Cp)", f"{cp:.2f} J/(kg·K)")
        m4.metric("导热系数 (Conductivity)", f"{cond:.4f} W/(m·K)")

        m5, m6 = st.columns(2)
        m5.metric("比焓 (Enthalpy)", f"{h:.2f} kJ/kg")
        m6.empty() # 占位

        # 生成可供复制的表格数据
        st.caption("详细数据表 (可复制):")
        data = {
            "物性参数": ["密度", "动力粘度", "定压比热容", "导热系数", "比焓"],
            "数值": [rho, visc, cp, cond, h],
            "单位": ["kg/m³", "Pa·s", "J/(kg·K)", "W/(m·K)", "kJ/kg"]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ 计算出错: {e}")
        st.warning("请检查输入的温度和压力是否在 CO2 的物理定义范围内。")

else:
    st.info("👆 请输入参数并点击“开始计算”")
