from typing import Callable

from tools.register import (
    get_capacity_curve,
    get_history_features,
    get_reservoir_characteristics,
    get_realtime_water_condition,
    tools
)

from tools.tools_template import (
    # generate_capacity_curve,
    # generate_history_features,
    # generate_reservoir_characteristics,
    # generate_realtime_water_condition,
    GENERATR_TEMPLATE,
)

def test_template(func: Callable, **kwargs):
    data = func(**kwargs)
    func_name = func.__name__

    template_func = GENERATR_TEMPLATE[func_name]
    result = template_func(data=data)
    print(result)

if __name__ == "__main__":
    # test_template(get_capacity_curve, ennm="小浪底")
    # test_template(get_history_features, ennm="小浪底")
    # test_template(get_reservoir_characteristics, ennm="小浪底")
    # test_template(get_realtime_water_condition, ennm="小浪底")
    import json

    print(json.dumps(tools, indent=4, ensure_ascii=False))