import marimo

__generated_with = "0.13.4"
app = marimo.App(
    width="medium",
    layout_file="layouts/Niemack_CAS598_Final.grid.json",
)


@app.cell
def _():
    import marimo as mo
    import random
    import pandas as pd
    from statistics import median
    import matplotlib.pyplot as plt
    import altair as alt
    from itertools import groupby
    import math
    import copy
    return alt, copy, groupby, math, median, mo, pd, random


@app.cell
def _(mo):
    mo.hstack([mo.md("""# Comparison of compensation strategies for employee retention""")])
    return


@app.cell
def _(alt, copy, groupby, math, median, mo, pd, random):
    def calculate_cost(grouped):
        if type(grouped[0][0]) == list:
            return sum([x[0] for xs in grouped for x in xs])
        else:
            return sum([x for xs in grouped for x in xs])


    def find_increase_linear(xs, rate, years, competitor_band):
        new = []
        for i, x in enumerate(xs):
            for band in reversed(competitor_band):
                if band <= x:
                    target = band
                    for i in range(1, years + 1):
                        target = target * (1 + rate)

                    linear_increase = (target - x) / years

                    new.append([x, linear_increase, target])
                    break
        return new


    def increase_linear(grouped):
        for i, x in enumerate(grouped):
            for j, v in enumerate(x):
                if v[1] > 0:
                    grouped[i][j][0] = v[0] + v[1]
                else:
                    grouped[i][j][0] = v[0]

        return grouped


    def attrition_linear(grouped, year, years, band, comp_rate, comp_crossover):
        rate = 0.5 / years

        top = max(band)
        for y in range(0, year):
            top = top * (1 + rate)

        band.append(top)

        for i, group in enumerate(grouped):
            if len(group) > 1:
                starting_length = len(group)
                amount = math.ceil(len(group) * rate)
                random.shuffle(group)
                attritioned = group[amount:]

                for p in reversed(band):
                    if p <= median([x[0] for x in attritioned]):
                        new_target = p

                        for k in range(1, comp_crossover + 1):
                            new_target = new_target * (1 + comp_rate)

                        linear_increase = (new_target - p) / comp_crossover

                        while len(attritioned) < starting_length:
                            attritioned.append(
                                [
                                    p,
                                    linear_increase
                                    if year < years
                                    else linear_increase * 0.1,
                                    new_target,
                                ]
                            )
                        break

                grouped[i] = attritioned

        return grouped, band


    def increase_percentage(grouped, rate):
        for i, x in enumerate(grouped):
            for j, value in enumerate(x):
                grouped[i][j] = value * (1 + rate)

        return grouped


    def attrition(grouped, year, years, band, rate):
        rate = 0.5 / years

        top = max(band)
        for y in range(0, year):
            top = top * (1 + rate)

        band.append(top)

        for i, group in enumerate(grouped):
            if len(group) > 1:
                starting_length = len(group)
                amount = math.ceil(len(group) * rate)
                random.shuffle(group)
                attritioned = group[amount:]
                for p in reversed(band):
                    if p <= median(attritioned):
                        while len(attritioned) < starting_length:
                            attritioned.append(p)
                        break
                grouped[i] = attritioned

        return grouped, band


    def percentage(xs, pay_band, rate, turnover, steps):
        print("starting median: ", median(xs))
        per = []
        grouped = sorted([list(j) for i, j in groupby(xs)])
        band = copy.deepcopy(pay_band)

        medians = []

        for year in range(1, steps):
            per.append(calculate_cost(grouped))
            grouped = increase_percentage(grouped, rate)
            grouped, band = attrition(grouped, year, turnover, band, rate)
            medians.append(median([x for xs in grouped for x in xs]))

        print("final median: ", median([x for xs in grouped for x in xs]))
        print("lowest paid: ", min(grouped[0]))
        print("highest paid: ", max(grouped[-1]))
        print(len(grouped))
        total = sum(per)
        print("total cost: ", total)

        data = pd.DataFrame({"year": range(1, steps), "cost": per})
        chart = (
            alt.Chart(data, title="Annual Payroll Cost")
            .mark_line(color="blue")
            .encode(
                x="year",
                y="cost",
            )
        )

        percent_chart = mo.ui.altair_chart(chart)

        data = pd.DataFrame({"year": range(1, steps), "pay": medians})
        chart = (
            alt.Chart(data, title="Annual Median Pay")
            .mark_line(color="cyan")
            .encode(
                x="year",
                y="pay",
            )
        )

        percent_median_chart = mo.ui.altair_chart(chart)

        return total, per, percent_chart, percent_median_chart, medians


    def linear(xs, comp_band, comp_rate, comp_crossover, turnover, steps):
        print("starting median: ", median(xs))
        linear_xs = find_increase_linear(xs, comp_rate, comp_crossover, comp_band)
        linear = []
        grouped = sorted([list(j) for i, j in groupby(linear_xs)])
        band = copy.deepcopy(xs)

        medians = []

        for year in range(0, steps):
            linear.append(calculate_cost(grouped))
            grouped = increase_linear(grouped)
            grouped, band = attrition_linear(
                grouped, year, turnover, band, comp_rate, comp_crossover
            )
            interem = []
            for group in grouped:
                for unit in group:
                    interem.append(unit[0])

            medians.append(median(interem))

        final = []
        for group in grouped:
            for unit in group:
                final.append(unit[0])

        print("final median: ", median(final))
        print("lowest paid: ", min(grouped[0]))
        print("highest paid: ", max(grouped[-1]))
        print(len(grouped))
        linear_total = sum(linear)
        print("total cost: ", linear_total)
        print(len(linear))

        data = pd.DataFrame({"year": range(0, steps), "cost": linear})
        chart = (
            alt.Chart(data, title="Annual Payroll Cost")
            .mark_line(color="orange")
            .encode(
                x="year",
                y="cost",
            )
        )

        linear_chart = mo.ui.altair_chart(chart)

        data = pd.DataFrame({"year": range(0, steps), "pay": medians})
        chart = (
            alt.Chart(data, title="Annual Median Pay")
            .mark_line(color="red")
            .encode(
                x="year",
                y="pay",
            )
        )

        linear_median_chart = mo.ui.altair_chart(chart)

        return linear_total, linear, linear_chart, linear_median_chart, medians
    return linear, percentage


@app.cell
def _(mo):
    simulation_years = mo.ui.number(
        start=1, stop=1000, step=1, value=50, label="number of years to simulate"
    )

    empolyees = mo.ui.number(
        start=1, stop=1000, step=1, value=500, label="number of employees per firm"
    )
    mo.hstack([simulation_years, empolyees])
    return empolyees, simulation_years


@app.cell
def _(empolyees, random):

    bands = [
        [25000, 31000, 37000],
        [30000, 36000, 42000],
        [35000, 41000, 47000],
        [39151, 46002, 52854],
        [43066, 50602, 58139],
        [47373, 55663, 63953],
        [52110, 61229, 70349],
        [52110, 68577, 80006],
        [64005, 76806, 89607],
        [71686, 86023, 100360],
        [80288, 96346, 112404],
        [89923, 107908, 125892],
        [101301, 124094, 146887],
        [129441, 155329, 181217],
        [144973, 173968, 202963],
        [172900, 211803, 250705],
        [195534, 239530, 283525],
        [220368, 275460, 330552],
    ]

    weights = [5, 7, 7, 3, 3, 2, 2, 1, 1, 1, 1, 1, 1, .5, .5, .1, .1, .1]

    low = [i[0] for i in bands]
    mid = [i[1] for i in bands]
    high = [i[2] for i in bands]

    using_low = sorted(random.choices(low, weights=weights, k=empolyees.value))
    using_mid = sorted(random.choices(mid, weights=weights, k=empolyees.value))
    using_high = sorted(random.choices(high, weights=weights, k=empolyees.value))
    return high, low, mid, using_high, using_low, using_mid


@app.cell
def _(mo, using_high, using_low, using_mid):
    competitor1_payband_dropdown = mo.ui.dropdown(
        options={"high": using_high, "medium": using_mid, "low": using_low},
        value="medium",
        label="choose payband",
    )

    competitor1_rate_of_increase = mo.ui.number(
        start=0, stop=100, step=1, value=4, label="average annual percent increase"
    )

    competitor1_expected_turnover = mo.ui.number(
        start=0,
        stop=50,
        step=1,
        value=4,
        label="number of years until 50% of staff has turned over",
    )

    competitor2_payband_dropdown = mo.ui.dropdown(
        options={"high": using_high, "medium": using_mid, "low": using_low},
        value="high",
        label="choose payband",
    )

    competitor2_expected_turnover = mo.ui.number(
        start=0,
        stop=50,
        step=1,
        value=4,
        label="number of years until 50% of staff has turned over",
    )

    mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("## Firm 1:"),
                    competitor1_payband_dropdown,
                    competitor1_rate_of_increase,
                    competitor1_expected_turnover,
                ]
            ),
            mo.vstack(
                [
                    mo.md("## Firm 2:"),
                    competitor2_payband_dropdown,
                    competitor2_expected_turnover,
                ]
            ),
        ]
    )
    return (
        competitor1_expected_turnover,
        competitor1_payband_dropdown,
        competitor1_rate_of_increase,
        competitor2_expected_turnover,
        competitor2_payband_dropdown,
    )


@app.cell
def _():
    return


@app.cell
def _(
    alt,
    competitor1_expected_turnover,
    competitor1_payband_dropdown,
    competitor1_rate_of_increase,
    competitor2_expected_turnover,
    competitor2_payband_dropdown,
    high,
    linear,
    low,
    mid,
    mo,
    pd,
    percentage,
    simulation_years,
):
    if competitor1_payband_dropdown.value == "high":
        comp_payband = high
    elif competitor1_payband_dropdown.value == "medium":
        comp_payband = mid
    else:
        comp_payband = low

    percentage_total, percent, percent_chart, percent_median_chart, percent_medians = percentage(
        competitor1_payband_dropdown.value,
        comp_payband,
        competitor1_rate_of_increase.value / 100,
        competitor1_expected_turnover.value,
        simulation_years.value,
    )

    linear_total, l, linear_chart, linear_median_chart, linear_medians = linear(
        competitor2_payband_dropdown.value,
        comp_payband,
        competitor1_rate_of_increase.value / 100,
        competitor1_expected_turnover.value,
        competitor2_expected_turnover.value,
        simulation_years.value,
    )

    data = pd.DataFrame(
        {
            "year": range(1, simulation_years.value),
            "firm 1": percent,
            "firm 2": l[1:],
        }
    )
    chart = (
        alt.Chart(
            data.reset_index().melt(
                id_vars="year", var_name="firms", value_name="cost"
            ), title="Compare Annual Cost"
        )
        .mark_line()
        .encode(x="year", y="cost", color="firms")
    )

    both_chart = mo.ui.altair_chart(chart)

    data = pd.DataFrame(
        {
            "year": range(1, simulation_years.value),
            "firm 1": percent_medians,
            "firm 2": linear_medians[1:],
        }
    )
    chart = (
        alt.Chart(
            data.reset_index().melt(
                id_vars="year", var_name="firms", value_name="pay"
            ), title="Compare Median Pay"
        )
        .mark_line()
        .encode(x="year", y="pay", color="firms")
    )

    both_medians_chart = mo.ui.altair_chart(chart)

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack([percent_chart, percent_median_chart]),
                    mo.vstack([linear_chart, linear_median_chart]),
                ]
            ),
            both_chart,
            both_medians_chart
        ]
    )
    return


if __name__ == "__main__":
    app.run()
