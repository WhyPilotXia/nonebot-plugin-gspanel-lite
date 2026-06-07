# nonebot-plugin-gspanel-lite

轻量级原神 UID 信息查询插件，通过 Enka 展示公开角色信息。

## 安装

使用 NB-CLI 安装：

```bash
nb plugin install nonebot-plugin-gspanel-lite
```

也可以使用 pip 安装：

```bash
pip install nonebot-plugin-gspanel-lite
```

## 使用

发送命令：

```text
/uid 218847690
```

插件会优先渲染 Enka 页面截图，渲染失败时回退到文本解析结果。

## 配置

无需配置。

## 效果图

<img width="569" height="675" alt="image" src="https://github.com/user-attachments/assets/f63a6907-dd3c-43e7-bb27-eea529be18bf" />

<img width="1280" height="1600" alt="f2057300831fee73b3fcbea30dd3ff04_720" src="https://github.com/user-attachments/assets/113ff4a3-9bfd-4f29-9f8a-b23e2c8cd2ce" />

## 文本回退示例

```text
nickname lingu李玥
level 57
signature 刚入坑求大佬带带
worldLevel 8
nameCardId 210192
finishAchievementNum 648
towerFloorIndex 8
towerLevelIndex 3
avatarInfoList_count 12
avatar_1 avatarId=10000073 equipList_count=6
avatar_2 avatarId=10000098 equipList_count=6
avatar_3 avatarId=10000052 equipList_count=6
```
