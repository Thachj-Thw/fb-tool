from . import *
import json


def get_groups(*args: Account, save_as: str = None) -> list[dict]:
    data = []
    for account in args:
        groups = account.list_groups()
        data.append({"account": account.name, "uid": account.uid, "groups": groups})
    if save_as:
        with open(save_as, mode="w", encoding="utf-8") as file:
            json.dump(obj=data, fp=file, ensure_ascii=False, indent=4)
    return data
