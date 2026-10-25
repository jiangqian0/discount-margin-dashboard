"""
Jiacheng Xu - Discount & Margin Dashboard (BANA409 Assignment 4, Part 1)

For: the Regional Sales Operations Manager, who sets each market's discount
caps before the weekly promotion cycle.
Decision: if a market's profit margin falls below the 16% target, or too much
of its sales come from deep discounts (over 40%), the manager tightens the
discount cap for that market in the next promotion cycle.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

TEAM_NAME = "Jiacheng Xu"
DATA_PATH = "order_data.csv"
MARGIN_TARGET = 16.0      # % - company margin target
DEEP_DISCOUNT = 0.40      # discounts above this count as "deep"

st.set_page_config(page_title=f"{TEAM_NAME} - Discount & Margin", layout="wide")

# Column names used by the Kaggle "Global Superstore" file, mapped to ours,
# so the same app works if the CSV is swapped for that dataset.
RENAME = {"Order Date": "order_date", "Market": "market", "Category": "category",
          "Sub-Category": "sub_category", "Segment": "segment", "Sales": "sales",
          "Quantity": "quantity", "Discount": "discount", "Profit": "profit"}


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path).rename(columns=RENAME)
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", dayfirst=True)
    df["discount_band"] = pd.cut(
        df["discount"], bins=[-0.001, 0.10, 0.20, 0.30, 0.40, 1.0],
        labels=["0-10%", "10-20%", "20-30%", "30-40%", "Over 40%"])
    return df


def margin(frame: pd.DataFrame) -> float:
    """Profit margin of a group = total profit / total sales (not an average of order margins)."""
    s = frame["sales"].sum()
    return frame["profit"].sum() / s * 100 if s else float("nan")


def deep_share(frame: pd.DataFrame) -> float:
    s = frame["sales"].sum()
    return frame.loc[frame["discount"] > DEEP_DISCOUNT, "sales"].sum() / s * 100 if s else float("nan")


df = load_data()
first_day, last_day = df["order_date"].min().date(), df["order_date"].max().date()

# ---------------------------------------------------------------------------
# Filters: only the two the manager uses - which market, which period
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")
market = st.sidebar.selectbox("Market", ["All markets"] + sorted(df["market"].unique()))
default_start = (pd.Timestamp(last_day).to_period("M").start_time - pd.DateOffset(months=11)).date()  # last 12 full months
period = st.sidebar.date_input("Period", value=(default_start, last_day),
                               min_value=first_day, max_value=last_day)
if not (isinstance(period, tuple) and len(period) == 2):
    st.info("Pick an end date to complete the period.")
    st.stop()
start, end = pd.Timestamp(period[0]), pd.Timestamp(period[1])

scope = df if market == "All markets" else df[df["market"] == market]
view = scope[scope["order_date"].between(start, end)]
# Same period one year earlier, for the deltas
prior = scope[scope["order_date"].between(start - pd.DateOffset(years=1),
                                          end - pd.DateOffset(years=1))]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title(f"{TEAM_NAME} - Discount & Margin Dashboard")
st.caption("For the Regional Sales Operations Manager: if a market's profit margin falls below "
           f"the {MARGIN_TARGET:.0f}% target or deep discounts (over {DEEP_DISCOUNT:.0%}) take too "
           "much of its sales, tighten that market's discount cap in the next weekly promotion cycle.")

if view.empty:
    st.warning("No orders in this market and period.")
    st.stop()

# ---------------------------------------------------------------------------
# Top: three headline numbers - is anything wrong right now?
# ---------------------------------------------------------------------------
m_now, s_now, d_now = margin(view), view["sales"].sum(), deep_share(view)
has_prior = not prior.empty
k1, k2, k3 = st.columns(3)
k1.metric("Profit margin", f"{m_now:.1f}%",
          delta=f"{m_now - MARGIN_TARGET:+.1f} pts vs {MARGIN_TARGET:.0f}% target")
k2.metric("Sales", f"${s_now:,.0f}",
          delta=f"{(s_now / prior['sales'].sum() - 1) * 100:+.1f}% vs same period last year" if has_prior else None)
k3.metric(f"Sales at discounts over {DEEP_DISCOUNT:.0%}", f"{d_now:.1f}%",
          delta=f"{d_now - deep_share(prior):+.1f} pts vs last year" if has_prior else None,
          delta_color="inverse")

# ---------------------------------------------------------------------------
# Middle: why did the margin move?
# ---------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    monthly = (view.set_index("order_date").resample("MS")[["sales", "profit"]].sum()
               .assign(margin=lambda d: d["profit"] / d["sales"] * 100).reset_index())
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=monthly["order_date"], y=monthly["margin"], mode="lines+markers",
                              name="Monthly margin", line=dict(color="#2a78d6", width=3)))
    fig1.add_hline(y=MARGIN_TARGET, line_dash="dash", line_color="#c4502a",
                   annotation_text=f"Target {MARGIN_TARGET:.0f}%", annotation_position="top left")
    lo = min(monthly["margin"].min(), MARGIN_TARGET) - 4
    hi = max(monthly["margin"].max(), MARGIN_TARGET) + 4
    fig1.update_layout(title="Monthly profit margin vs. target", yaxis_title="Profit margin (%)",
                       yaxis_range=[lo, hi],  # a few points of headroom so small wiggles are not exaggerated
                       xaxis_title=None, height=380, margin=dict(l=10, r=10, t=50, b=10),
                       showlegend=False)
    st.plotly_chart(fig1, width="stretch")

with right:
    bands = (view.groupby("discount_band", observed=False)
             .agg(sales=("sales", "sum"), profit=("profit", "sum")).reset_index())
    bands["margin"] = bands["profit"] / bands["sales"] * 100
    bands["color"] = ["Below target" if m < MARGIN_TARGET else "At or above target"
                      for m in bands["margin"]]
    fig2 = px.bar(bands, x="discount_band", y="margin", color="color",
                  color_discrete_map={"Below target": "#c4502a", "At or above target": "#2a78d6"},
                  text=bands["margin"].round(1),
                  labels={"discount_band": "Discount given", "margin": "Profit margin (%)",
                          "color": ""},
                  title="Profit margin by discount depth")
    fig2.add_hline(y=MARGIN_TARGET, line_dash="dash", line_color="#c4502a")
    fig2.update_traces(textposition="outside")
    fig2.update_layout(height=380, margin=dict(l=10, r=10, t=50, b=10),
                       yaxis_range=[0, max(bands["margin"].max(), MARGIN_TARGET) * 1.2],
                       legend=dict(orientation="h", y=1.02, x=1, xanchor="right"))
    st.plotly_chart(fig2, width="stretch")

st.caption("Margins are total profit / total sales for the group, so large orders weigh more than "
           "small ones. The monthly line moves within a narrow range; compare it with the target, "
           "not with the month before.")

# ---------------------------------------------------------------------------
# Bottom: detail for digging in
# ---------------------------------------------------------------------------
with st.expander("Detail: margin by market and category"):
    detail = (scope[scope["order_date"].between(start, end)]
              .groupby(["market", "category"])
              .agg(orders=("sales", "size"), sales=("sales", "sum"), profit=("profit", "sum"))
              .reset_index())
    detail["margin_%"] = (detail["profit"] / detail["sales"] * 100).round(1)
    detail["sales"] = detail["sales"].round(0)
    detail["profit"] = detail["profit"].round(0)
    st.dataframe(detail.sort_values("margin_%"), hide_index=True, width="stretch")

st.caption(f"**Data:** {first_day:%b %Y} - {last_day:%b %Y}, {len(df):,} orders, static CSV snapshot "
           "(source to be confirmed; see README). **Production refresh:** nightly from the order "
           "system; reviewed every Monday before the weekly promotion cycle.")
