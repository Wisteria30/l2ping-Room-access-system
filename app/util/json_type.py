# mypyでなにがJSONとして適切か定まっていない（なんか未だ議論中っぽい？）
# ひとまずなんでも許可するってしないと通らない．．．
# https://github.com/python/typing/issues/182
import typing as t

# JSON = t.Union[str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
JSON = t.Dict[str, t.Any]
