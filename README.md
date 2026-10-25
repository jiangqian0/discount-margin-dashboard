# Jiacheng Xu – Discount & Margin Dashboard

**Live app:** [ADD YOUR STREAMLIT URL]  
**Files:** `app.py` (the dashboard), `eda.ipynb` (exploratory analysis), `order_data.csv` (data), `pyproject.toml` / `requirements.txt` (dependencies)

---

## Step 1 – Dataset and decision-maker

**Dataset.** `order_data.csv`: 5,000 retail orders from January 2016 to December 2020 (0.5 MB, so no sampling was needed). One row is one order line, with the order date, market (APAC, EMEA, LATAM, US), product category and sub-category, customer segment, ship mode, order priority, sales, quantity, discount, profit and shipping cost. There are no missing values and no duplicate rows.

**Source.** [ADD THE KAGGLE DATASET LINK]. The columns follow the well-known *Global Superstore* retail dataset. The EDA suggests this file is **simulated** rather than real company data: orders are split almost exactly evenly across years and markets, discount and shipping cost are uniformly distributed, and every market (including APAC and EMEA) has the same four US-style regions. I treat it as a realistic stand-in for a retailer's order history and say so on the dashboard.

**Decision-maker.** The **Regional Sales Operations Manager**, who sets the discount cap for each market before the weekly promotion cycle.

## Step 2 – Why a dashboard

1. **Who and how often.** The Regional Sales Operations Manager, every Monday morning, before the week's promotions are approved.
2. **Decision it supports.** *If the manager sees a market's profit margin fall below the 16% target, or the share of its sales sold at discounts over 40% creep up, they will tighten that market's discount cap in the next promotion cycle.*
3. **What happens today without it.** The manager asks an analyst for a spreadsheet of last week's orders, pivots it by market, and works out margins by hand. That takes an hour or more each week, and a slipping market is often noticed only at the month-end finance review, after three or four more weeks of over-discounted orders.
4. **Why a dashboard, not a report or an alert.** The same person asks the same three questions every week (Is margin on target? Are we discounting too deeply? In which market?) and needs to compare markets and periods quickly before acting. A weekly email cannot be filtered to one market, and an alert alone would not show *why* margin moved. The one condition that cannot wait a week is handled as an alert (Step 4).

## Step 3 – What the dashboard shows, and why

The EDA is in `eda.ipynb`. Its key findings:

- Overall profit margin is **16.2%**, and it is almost identical in every market, category, segment, ship mode and order priority (all between 16.1% and 16.4%).
- The one clear relationship is with **discount depth**: margin falls from **17.0%** on orders discounted 0–10% to **15.3%** on orders discounted more than 40%.
- Monthly margin moves between **15.0% and 17.2%** with no trend.
- Sales are right-skewed: the median order is about \$543, but 73 orders exceed \$3,000.

**Headline numbers (top of the page).** These answer "is anything wrong right now?" for the selected market and period:

| Metric | Why it is there |
|---|---|
| **Profit margin**, with the gap to the 16% target | The number the decision is based on |
| **Sales**, vs. the same period last year | Shows whether a margin change comes with a volume change; deeper discounts should at least buy more sales |
| **Share of sales at discounts over 40%**, vs. last year | The lever the manager controls; red when it rises |

**Supporting charts (middle).**

1. *Monthly profit margin vs. the 16% target* – shows whether a low margin is a one-month dip or a run of months below target. The y-axis has a few points of headroom so that small monthly wiggles are not exaggerated.
2. *Profit margin by discount depth* – explains **why** margin moved: bars below the target line are coloured differently, so the manager can see at which discount level orders stop paying for themselves.

**Filters.** Only two: **market** (each decision is made per market) and **period** (defaults to the last 12 full months, the window the manager reviews).

**Bottom.** A collapsed table of margin by market and category, for the occasional follow-up question. It is collapsed so it does not compete with the headline numbers.

**Two things I chose not to show.**

1. **Margin by category, sub-category, segment, ship mode or order priority.** They looked worth checking, but every one of them sits at about 16%. Twelve sub-category bars of nearly equal height would take up space and change no decision.
2. **A combined sales-and-profit chart with two y-axes.** It is a common dashboard chart, but two scales on one chart make it easy to read a crossing of the lines as meaningful. Margin already combines sales and profit in one number on one scale.

I also dropped **region**, **shipping cost** and **quantity**: shipping cost is not under this manager's control, quantity adds nothing beyond sales, and region is explained below.

**What could mislead the viewer, and how the dashboard handles it.**

- **Region has no clear meaning.** Every market, including APAC and EMEA, has "Central", "East", "South" and "West" regions in almost equal numbers. Since I could not tell what the field means, it is left out rather than shown and misread.
- **Margin of a group is total profit ÷ total sales,** not the average of order margins, so large orders weigh more. A caption under the charts says this.
- **Small monthly movements.** Monthly margin stays within about two points of the target, so a one-month change can look dramatic on a zoomed chart. The chart shows the target line and extra headroom, and the caption says to compare with the target rather than with the previous month.
- **The data may be simulated, and it stops in December 2020.** The data line at the bottom of the page states the period and that the source is still to be confirmed.

**Page order.** Headline numbers → the two "why" charts → the detail table → the data and refresh line. Most readers never scroll, so the three numbers that decide whether action is needed come first.

## Step 4 – Refresh frequency

1. **Data refresh: nightly.** Orders and discounts would be loaded from the order system once a night. Margin only moves meaningfully over weeks, and discount caps are set once a week, so hourly or real-time data would add cost without changing any decision.
2. **Review: weekly, every Monday,** before the week's promotions are approved. Refresh and review are not the same: the data is fresh every morning, but the decision is made once a week.
3. **What to track and what triggers action.** Track each market's **trailing four-week profit margin**. If it falls **below 15%** (one point under target), that is an **alert** to the manager on the same day, not something to wait for until Monday, because every extra week at that level means more orders sold below target.
4. **Cost of stale data.** One day out of date costs almost nothing, since the decision is weekly. One week out of date means a whole promotion cycle is set on old numbers: a market that has started over-discounting keeps doing so for another week, In this data the company sells about \$14,000 a week across all markets, so each point of margin lost is about \$140 of profit a week; the loss is small in one week but repeats every week the problem goes unseen, often until the month-end review.

On the dashboard, the bottom line reads: *Data: Jan 2016 – Dec 2020, 5,000 orders, static CSV snapshot. Production refresh: nightly from the order system; reviewed every Monday before the weekly promotion cycle.*

---

### Run locally

```bash
uv sync
uv run streamlit run app.py
```
