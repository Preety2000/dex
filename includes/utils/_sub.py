from includes.core.cache import AppCache
from includes.core.config import main_database
from includes.core.metadata import MetaData
from includes.db.models.owner import Subject
from includes.metrics import MetricsManager
from includes.schemas.trending import ArticleTrendingService


def configure_page(
    template: str | None = None, title: str | None = None, suffix: bool | str = False
) -> None:
    """Sets page template and updates metadata title with optional suffix."""
    if template:
        MetaData.template = template

    if title:
        suffix_text = MetaData.site_name if suffix is True else suffix
        MetaData.title = f"{title} • {suffix_text}" if suffix_text else title


def get_nested_value(data, key):

    if isinstance(data, dict) and key in data:
        return data[key]

    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, dict):
                result = get_nested_value(value, key)
                if result is not None:
                    return result

    return None


def distribute_amount(data, total, as_dict=True):
    total = int(total)
    n = len(data)

    if total < n * 5:
        raise ValueError("Minimum 5 per item required")

    vals = [5] * n
    rem = total - n * 5

    for i in range(rem // 5):
        vals[i % n] += 5

    return dict(zip(data, vals)) if as_dict else vals


async def get_code_to_subject():
    record = AppCache.get("get_code_to_subject", None)
    if record:
        return record

    with main_database() as dbm:
        query = dbm.query(Subject.id, Subject.name).order_by(Subject.name).all()

        record = {f"pe{id_}": name for id_, name in query}
        AppCache.add("get_code_to_subject", record)

    return record


async def apply_session_updates(data):
    update_key = "update_session_returns"

    if not isinstance(data, dict):
        return data

    if update_key in data:
        update_request = data.get(update_key) or {}

        item_id = update_request.get("id")
        update_method = update_request.get("update_type")
        update_option = update_request.get("update_option")

        if item_id and update_method and update_option:
            metric_method = getattr(
                MetricsManager,
                update_method,
                None,
            )

            if callable(metric_method):
                updated_data = await metric_method(
                    item_id,
                    update_option,
                    servic= ArticleTrendingService
                )

                if isinstance(updated_data, dict):
                    data.update(updated_data)

        data.pop(update_key, None)
        return data

    for key, value in data.items():
        if isinstance(value, (dict, list)):
            if get_nested_value(value, update_key):
                data[key] = await apply_session_updates(value)

    return data
