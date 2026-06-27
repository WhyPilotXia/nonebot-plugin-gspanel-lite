import json
import re
from json import JSONDecodeError
from typing import Any, Optional

import aiohttp
from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import get_new_page


__plugin_meta__ = PluginMetadata(
    name="GSPanel Lite",
    description="通过 Enka 查询原神、崩铁、绝区零、终末地 UID 公开展示信息",
    usage=(
        "发送 /uid <UID> 查询原神公开角色展示信息\n"
        "发送 /uid <原神/崩铁/绝区零/终末地> <UID> 查询指定游戏公开展示信息\n"
        "也可以使用 /uid <gs/hsr/zzz/ef> <UID>"
    ),
    type="application",
    homepage="https://github.com/WhyPilotXia/nonebot-plugin-gspanel-lite",
    supported_adapters={"~onebot.v11"},
)


DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=20)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
}
GAME_URL_PATHS = {
    "gs": "u",
    "hsr": "hsr",
    "zzz": "zzz",
    "ef": "ef",
}
GAME_NAMES = {
    "gs": "原神",
    "hsr": "崩铁",
    "zzz": "绝区零",
    "ef": "终末地",
}
GAME_ALIASES = {
    "gs": "gs",
    "原神": "gs",
    "genshin": "gs",
    "genshinimpact": "gs",
    "hsr": "hsr",
    "崩铁": "hsr",
    "星铁": "hsr",
    "崩坏星穹铁道": "hsr",
    "starrail": "hsr",
    "zzz": "zzz",
    "绝区零": "zzz",
    "zenless": "zzz",
    "zenlesszonezero": "zzz",
    "ef": "ef",
    "终末地": "ef",
    "endfield": "ef",
}


class EnkaQueryError(Exception):
    pass


def parse_uid_query(query: str) -> tuple[str, str]:
    text = query.strip()
    if not text:
        raise EnkaQueryError("UID 不能为空。")

    parts = text.split(maxsplit=1)
    if len(parts) == 1:
        if parts[0].lower() in GAME_ALIASES:
            raise EnkaQueryError("UID 不能为空。")
        return "gs", parts[0]

    game = GAME_ALIASES.get(parts[0].lower())
    if not game:
        supported = "原神/崩铁/绝区零/终末地 或 gs/hsr/zzz/ef"
        raise EnkaQueryError(f"不支持的游戏：{parts[0]}，请使用 {supported}。")

    uid = parts[1].strip()
    if not uid:
        raise EnkaQueryError("UID 不能为空。")

    return game, uid


def build_enka_url(game: str, uid: str) -> str:
    path = GAME_URL_PATHS[game]
    return f"https://enka.network/{path}/{uid}/"


async def fetch_text(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, headers=HEADERS) as response:
        text = await response.text(encoding="utf-8", errors="replace")
        if response.status >= 400:
            body = text[:300].replace("\n", " ")
            raise EnkaQueryError(f"请求失败 HTTP {response.status}: {body}")
        return text


def extract_const_data_value(html: str) -> str:
    match = re.search(r"const\s+data\s*=", html)
    if not match:
        raise EnkaQueryError("HTML 中没有找到 const data。")

    start = html.find("[", match.end())
    if start == -1:
        raise EnkaQueryError("const data 后没有找到数组开头。")

    depth = 0
    quote: Optional[str] = None
    escaped = False

    for index in range(start, len(html)):
        char = html[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue

        if char in ("'", '"', "`"):
            quote = char
        elif char in "[{(":
            depth += 1
        elif char in "]})":
            depth -= 1
            if depth == 0:
                return html[start:index + 1]

    raise EnkaQueryError("const data 数组没有正常闭合。")


def js_object_literal_to_json(js_text: str) -> str:
    text = js_text
    text = re.sub(r"\bvoid\s+0\b", "null", text)
    text = re.sub(r"\bundefined\b", "null", text)
    text = re.sub(r":\s*(\.\d+)", r": 0\1", text)
    text = re.sub(
        r"(?P<prefix>[{,\s])(?P<key>[A-Za-z_$][\w$]*)\s*:",
        r'\g<prefix>"\g<key>":',
        text,
    )
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text


def find_profile_data(value: Any) -> Optional[dict[str, Any]]:
    if isinstance(value, dict):
        data = value.get("data")
        if isinstance(data, dict) and isinstance(data.get("playerInfo"), dict):
            return data

        for child in value.values():
            result = find_profile_data(child)
            if result:
                return result

    elif isinstance(value, list):
        for child in value:
            result = find_profile_data(child)
            if result:
                return result

    return None


def find_player_info(value: Any) -> Optional[dict[str, Any]]:
    profile_data = find_profile_data(value)
    if profile_data:
        return profile_data.get("playerInfo")
    return None


def parse_profile_data_from_html(html: str) -> dict[str, Any]:
    const_data = extract_const_data_value(html)
    json_text = js_object_literal_to_json(const_data)

    try:
        data = json.loads(json_text)
    except JSONDecodeError as exc:
        preview = json_text[max(0, exc.pos - 120):exc.pos + 180].replace("\n", " ")
        raise EnkaQueryError(
            f"HTML 中 const data 解析失败: {exc}; 附近内容: {preview}"
        ) from exc

    profile_data = find_profile_data(data)
    if not profile_data:
        raise EnkaQueryError("const data 中没有找到 playerInfo/avatarInfoList。")

    return profile_data


def format_value(value: Any, limit: int = 80) -> str:
    text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def format_profile_summary(profile_data: dict[str, Any]) -> str:
    player_info = profile_data.get("playerInfo", {})
    avatar_list = profile_data.get("avatarInfoList", [])

    lines = []

    for key, value in player_info.items():
        lines.append(f"{key} {format_value(value)}")

    if isinstance(avatar_list, list):
        lines.append(f"avatarInfoList_count {len(avatar_list)}")

        for index, avatar in enumerate(avatar_list[:3], start=1):
            avatar_id = avatar.get("avatarId") if isinstance(avatar, dict) else None
            equip_count = len(avatar.get("equipList", [])) if isinstance(avatar, dict) else 0
            lines.append(
                f"avatar_{index} avatarId={avatar_id} equipList_count={equip_count}"
            )

    return "\n".join(lines) if lines else "没有可展示的数据。"


async def get_profile_data(uid: str, game: str = "gs") -> dict[str, Any]:
    uid = uid.strip()
    if not uid:
        raise EnkaQueryError("UID 不能为空。")

    async with aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT) as session:
        html = await fetch_text(session, build_enka_url(game, uid))
        return parse_profile_data_from_html(html)


async def get_player_info(uid: str, game: str = "gs") -> dict[str, Any]:
    profile_data = await get_profile_data(uid, game)
    player_info = profile_data.get("playerInfo")

    if not isinstance(player_info, dict):
        raise EnkaQueryError("没有找到 playerInfo。")

    return player_info


async def getuid(uid: str, game: str = "gs") -> str:
    try:
        profile_data = await get_profile_data(uid, game)
    except EnkaQueryError as exc:
        return str(exc)

    return format_profile_summary(profile_data)


async def render_enka_page(uid: str, game: str = "gs") -> bytes:
    uid = uid.strip()
    if not uid:
        raise EnkaQueryError("UID 不能为空。")

    async with get_new_page(
        viewport={"width": 1700, "height": 1200},
        device_scale_factor=1,
    ) as page:
        try:
            await page.goto(
                build_enka_url(game, uid),
                wait_until="load",
                timeout=15000,
            )
        except Exception as e:
            logger.warning(
                f"{e} {GAME_NAMES[game]} UID {uid} 页面加载超时，尝试强行截图..."
            )

        await page.wait_for_timeout(4000)

        return await page.screenshot(full_page=True, type="png")


uid_matcher = on_command("uid")


@uid_matcher.handle()
async def _handle(matcher: Matcher, uid_arg: Message = CommandArg()):
    if uid_arg.extract_plain_text():
        matcher.set_arg("uid", uid_arg)


@uid_matcher.got("uid", prompt="你想查询哪个 UID？")
async def _(bot: Bot, event: GroupMessageEvent, uid_query: str = ArgPlainText("uid")):
    try:
        game, uid = parse_uid_query(uid_query)
    except EnkaQueryError as exc:
        await uid_matcher.send(str(exc))
        return

    try:
        await bot.call_api(
            "set_msg_emoji_like",
            group_id=event.group_id,
            message_id=event.message_id,
            emoji_id="318",
            set=True,
        )
    except Exception as e:
        logger.warning(e)

    try:
        image = await render_enka_page(uid, game)
        await uid_matcher.send(MessageSegment.image(image))
        return
    except Exception as e:
        logger.opt(exception=e).warning("Enka 页面渲染失败，回退到文本解析")

    info = await getuid(uid=uid, game=game)
    await uid_matcher.send(info)
