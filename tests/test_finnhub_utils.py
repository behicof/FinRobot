import json
import types
import sys
import pathlib
import importlib.util

# Provide a minimal pandas stub to satisfy module imports
sys.modules.setdefault("pandas", types.SimpleNamespace(DataFrame=dict))

root = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(root))

# Pre-create parent packages to avoid importing heavy dependencies
if "finrobot" not in sys.modules:
    finrobot_pkg = types.ModuleType("finrobot")
    finrobot_pkg.__path__ = [str(root / "finrobot")]
    sys.modules["finrobot"] = finrobot_pkg
if "finrobot.data_source" not in sys.modules:
    ds_pkg = types.ModuleType("finrobot.data_source")
    ds_pkg.__path__ = [str(root / "finrobot" / "data_source")]
    sys.modules["finrobot.data_source"] = ds_pkg

module_path = root / "finrobot/data_source/finnhub_utils.py"
spec = importlib.util.spec_from_file_location("finrobot.data_source.finnhub_utils", module_path)
f_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f_utils)
FinnHubUtils = f_utils.FinnHubUtils


class DummyClient:
    def company_basic_financials(self, symbol, all_arg):
        return {
            "metric": {"alpha": 1, "beta": 2},
            "series": {
                "quarterly": {
                    "alpha": [{"v": 1}],
                    "beta": [{"v": 2}],
                }
            },
        }


def test_get_basic_financials_filters_columns(monkeypatch):
    monkeypatch.setenv("FINNHUB_API_KEY", "test")
    monkeypatch.setattr(f_utils.finnhub, "Client", lambda api_key: DummyClient())
    result = FinnHubUtils.get_basic_financials("DUM", selected_columns=["beta"])
    parsed = json.loads(result)
    assert parsed == {"beta": 2}
