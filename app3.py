import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

st.set_page_config(page_title="Lab 3", layout="wide")
st.title("Лабораторна №3 — Streamlit-додаток")

time_series = ["VCI", "TCI", "VHI"]

area_names = {
    "Вінницька": "Вінницька",
    "Волинська": "Волинська",
    "Дніпропетровська": "Дніпропетровська",
    "Донецька": "Донецька",
    "Житомирська": "Житомирська",
    "Закарпатська": "Закарпатська",
    "Запорізька": "Запорізька",
    "Івано-Франківська": "Івано-Франківська",
    "Київська": "Київська",
    "Кіровоградська": "Кіровоградська",
    "Луганська": "Луганська",
    "Львівська": "Львівська",
    "Миколаївська": "Миколаївська",
    "Одеська": "Одеська",
    "Полтавська": "Полтавська",
    "Рівненська": "Рівненська",
    "Сумська": "Сумська",
    "Тернопільська": "Тернопільська",
    "Харківська": "Харківська",
    "Херсонська": "Херсонська",
    "Хмельницька": "Хмельницька",
    "Черкаська": "Черкаська",
    "Чернівецька": "Чернівецька",
    "Чернігівська": "Чернігівська",
    "Республіка Крим": "Республіка Крим"
}

defaults = {
    "selected_series": "VCI",
    "selected_area": list(area_names.keys())[0],
    "week_range": (1, 52),
    "year_range": (2000, 2025)
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("скинути фільтри"):
        for key, value in defaults.items():
            st.session_state[key] = value

    selected_series = st.selectbox("обрати часовий ряд:", options=time_series, index=time_series.index(st.session_state.selected_series), key="selected_series")
    selected_area = st.selectbox("обрати область:", options=list(area_names.keys()), index=list(area_names.keys()).index(st.session_state.selected_area), key="selected_area")
    selected_area_code = area_names[selected_area]

    week_range = st.slider("обрати інтервал тижнів:", 1, 52, key="week_range")
    year_range = st.slider("обрати інтервал років:", 2000, 2025, key="year_range")

    sort_ascending = st.checkbox("сортувати за зростанням")
    sort_descending = st.checkbox("сортувати за спаданням")

    if sort_ascending and sort_descending:
        st.warning("неможливо одночасно сортувати і за зростанням, і за спаданням, оберіть лише один варіант")
        sort_ascending = False
        sort_descending = False

@st.cache_data
def load_data():
    all_files = glob.glob("*.csv")
    dfs = []

    for file in all_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                parsed_rows = []
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 5:
                        try:
                            year = int(parts[0])
                            week = int(parts[1])
                            vci = float(parts[2])
                            tci = float(parts[3])
                            vhi = float(parts[4])
                            parsed_rows.append([year, week, vci, tci, vhi])
                        except ValueError:
                            continue

            if parsed_rows:
                region_name = os.path.basename(file).split("_")[1].replace(".csv", "")
                df = pd.DataFrame(parsed_rows, columns=["year", "week", "VCI", "TCI", "VHI"])
                df["region"] = region_name
                dfs.append(df)

        except Exception as e:
            st.warning(f"пропущено {file}: {e}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()

df = load_data()

if not df.empty and "region" in df.columns:
    filtered_df = df[
        (df["region"] == selected_area_code) &
        (df["week"].between(week_range[0], week_range[1])) &
        (df["year"].between(year_range[0], year_range[1]))
    ]
else:
    st.error("не вдалося завантажити дані")
    st.stop()

if sort_ascending:
    filtered_df = filtered_df.sort_values(by=selected_series, ascending=True)
    st.info(f"дані відсортовано за зростанням ({selected_series})")
elif sort_descending:
    filtered_df = filtered_df.sort_values(by=selected_series, ascending=False)
    st.info(f"дані відсортовано за спаданням ({selected_series})")

with col2:
    tab1, tab2, tab3 = st.tabs(["таблиця", "графік", "порівняння по областях"])

    with tab1:
        st.subheader("таблиця з відфільтрованими даними")
        st.dataframe(filtered_df)

    with tab2:
        st.subheader(f"{selected_series} для {selected_area}")
        if not filtered_df.empty:
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.lineplot(data=filtered_df, x="week", y=selected_series, marker="o", ax=ax)
            ax.set_title(f"{selected_series} по тижнях у {selected_area}")
            ax.set_xlabel("тиждень")
            ax.set_ylabel(selected_series)
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.warning("немає даних для відображення")

    with tab3:
        st.subheader(f"порівняння {selected_series} для {selected_area} з іншими регіонами")
        fig, ax = plt.subplots(figsize=(8, 4))
        subset = df[(df["year"].between(year_range[0], year_range[1])) & (df["week"].between(week_range[0], week_range[1]))]
        subset_area = subset[subset["region"] == selected_area_code]
        subset_others = subset[subset["region"] != selected_area_code]

        sns.scatterplot(data=subset_others, x="year", y=selected_series, color="lightgray", label="інші області", alpha=0.4, ax=ax)
        sns.scatterplot(data=subset_area, x="year", y=selected_series, color="red", label=selected_area, ax=ax)

        ax.set_xlabel("рік")
        ax.set_ylabel(selected_series)
        ax.set_title(f"{selected_series} для {selected_area} у порівнянні з іншими")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
