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
在收到指令后，会立即贴一个表情表示开始处理：


<img width="580" height="300" alt="QQ_1780846050134" src="https://github.com/user-attachments/assets/707ea968-d01f-4591-93a0-e60dc0dbfae5" />


等待约20s返回图片结果：

<img width="579" height="645" alt="QQ_1780846060866" src="https://github.com/user-attachments/assets/89a7255b-9237-48c9-a648-4f3fc8f2977b" />


<img width="495" height="499" alt="QQ_1780846079498" src="https://github.com/user-attachments/assets/72e298da-1928-468d-9e82-e0c76018ac08" />

图片示例：


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
