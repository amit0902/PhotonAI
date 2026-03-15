def calculate_system_size(monthly_units, pr=0.75):
    daily_kwh = monthly_units / 30
    required_kw = daily_kwh / (4.5 * pr)
    return daily_kwh, round(required_kw, 2)


def series_parallel(required_kw, module_watt=540, series=3):
    total_modules = int((required_kw * 1000) / module_watt)
    parallel = max(1, total_modules // series)

    return {
        "modules": total_modules,
        "series": series,
        "parallel": parallel
    }
