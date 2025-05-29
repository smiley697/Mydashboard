# NOTE: This script requires running in an environment where Streamlit is installed.
# To install dependencies, run: pip install streamlit pandas seaborn matplotlib

try:
    import streamlit as st
    import seaborn as sns
    import pandas as pd
    import matplotlib.pyplot as plt
    import io
    import traceback
except ModuleNotFoundError as e:
    raise ImportError("Required module not found. Make sure you have installed 'streamlit', 'pandas', 'seaborn', and 'matplotlib'.") from e

st.set_page_config(page_title="Customer Data Plot Dashboard", layout="wide")
st.title("📊 Customer Data Visualization Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# Plot style selection
plot_styles = plt.style.available
selected_style = st.selectbox("Choose a Matplotlib style", plot_styles)
plt.style.use(selected_style)

# Initialize session state for plots if not already set
if "plots" not in st.session_state:
    st.session_state["plots"] = {}

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("Preview of Dataset")
        st.dataframe(df.head())

        st.subheader("Choose Plot Type")
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

        if not numeric_columns:
            st.warning("No numeric columns found in the uploaded dataset.")
        else:
            plot_type = st.selectbox("Plot Type", ["Histogram", "Boxplot", "Scatterplot", "Correlation Heatmap"])

            plot_name = ""
            fig, ax = plt.subplots()

            if plot_type == "Histogram":
                col = st.selectbox("Select column for histogram", numeric_columns)
                sns.histplot(data=df, x=col, kde=True, ax=ax)
                plot_name = f"histogram_{col}"

            elif plot_type == "Boxplot":
                col = st.selectbox("Select column for boxplot", numeric_columns)
                sns.boxplot(data=df, y=col, ax=ax)
                plot_name = f"boxplot_{col}"

            elif plot_type == "Scatterplot":
                x_col = st.selectbox("X-axis", numeric_columns, key="x")
                y_col = st.selectbox("Y-axis", numeric_columns, key="y")
                sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
                plot_name = f"scatterplot_{x_col}_vs_{y_col}"

            elif plot_type == "Correlation Heatmap":
                corr = df[numeric_columns].corr()
                sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
                plot_name = "correlation_heatmap"

            st.pyplot(fig)

            # Save the figure in memory
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            st.session_state["plots"][plot_name] = buf

            st.success(f"Plot '{plot_name}' generated and saved.")

    except Exception as e:
        st.error(f"⚠️ An error occurred while processing the file: {e}")
        st.code(traceback.format_exc())

if st.session_state["plots"]:
    st.subheader("Download Generated Plots")
    plot_to_download = st.selectbox("Select a plot to download", list(st.session_state["plots"].keys()))
    buf = st.session_state["plots"][plot_to_download]
    st.download_button(
        label="Download Plot as PNG",
        data=buf.getvalue(),
        file_name=f"{plot_to_download}.png",
        mime="image/png"
    )
