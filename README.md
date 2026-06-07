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

<img width="1700" height="1274" alt="4e8f43db5be95a710fc32cef31c45d6f" src="https://github.com/user-attachments/assets/7e2e7fc1-2d56-422d-990f-b16c7da4af09" />


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
