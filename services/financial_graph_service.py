import matplotlib.pyplot as plt
from io import BytesIO


def generate_breakeven_chart_image(system_cost, annual_bill):

    years = list(range(0, 26))

    without_solar = []
    with_solar = []

    electricity_inflation = 0.04
    maintenance_rate = 0.01

    cumulative_without = 0
    cumulative_with = system_cost

    for year in years:

        if year == 0:
            without_solar.append(0)
            with_solar.append(system_cost)
            continue

        cumulative_without += annual_bill * ((1 + electricity_inflation) ** year)
        cumulative_with += system_cost * maintenance_rate

        without_solar.append(cumulative_without)
        with_solar.append(cumulative_with)

    fig, ax = plt.subplots()

    ax.plot(years, without_solar, label="Without Solar")
    ax.plot(years, with_solar, label="With Solar")

    ax.set_xlabel("Years")
    ax.set_ylabel("Cumulative Cost (₹)")
    ax.set_title("Solar Break-even Analysis")

    ax.legend()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png", bbox_inches="tight")
    plt.close()

    img_buffer.seek(0)

    return img_buffer

# import plotly.graph_objects as go


# def generate_breakeven_chart(system_cost, annual_bill):

#     years = list(range(0, 26))

#     without_solar = []
#     with_solar = []

#     electricity_inflation = 0.04
#     maintenance_rate = 0.01

#     cumulative_without = 0
#     cumulative_with = system_cost

#     break_even_year = None

#     for year in years:

#         if year > 0:

#             adjusted_bill = annual_bill * (1 + electricity_inflation) ** (year - 1)
#             cumulative_without += adjusted_bill

#             maintenance_cost = system_cost * maintenance_rate
#             cumulative_with += maintenance_cost

#         without_solar.append(cumulative_without)
#         with_solar.append(cumulative_with)

#         if break_even_year is None and cumulative_without >= cumulative_with:
#             break_even_year = year

#     fig = go.Figure()

#     fig.add_trace(
#         go.Scatter(
#             x=years,
#             y=without_solar,
#             name="Cost without Solar",
#             mode="lines+markers"
#         )
#     )

#     fig.add_trace(
#         go.Scatter(
#             x=years,
#             y=with_solar,
#             name="Cost with Solar",
#             mode="lines+markers"
#         )
#     )

#     if break_even_year:
#         fig.add_vline(
#             x=break_even_year,
#             line_dash="dash",
#             annotation_text=f"Break-even ~ Year {break_even_year}",
#             annotation_position="top"
#         )

#     fig.update_layout(
#         title="Solar Investment Break-even Analysis",
#         xaxis_title="Years",
#         yaxis_title="Total Cost (₹)",
#         template="plotly_dark"
#     )

#     return fig