# 界面元素

本页面介绍软件的用户界面元素，供读者参考，以便于阅读后续使用说明。

目前本软件主要实现了以下界面：
- 登录页面
- 主页面
- 阅读器
- 推送页面
- 关于页面

可通过点击导航栏中的链接，或界面中的相应按钮，进入相应页面。  
以下是各个页面的界面元素介绍。

## 工具栏
工具栏是所有页面中的通用元素， 在工具栏左侧包含设置和返回/退出登陆按钮， 右侧是页面导航。
例如，下图是主界面中的工具栏：

<img class='lires-manual-screenshot' 
    style='width: 100%'
    src='https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/pic/lires-toolbar-dark-v1.7.3.png' 
    alt='lires-toolbar'>

## 数据卡片
数据卡片（Data Card）是Lires的数据条目展示形式，是主页中的数据内容，也是其他页面中的可编辑数据展示形式。 以下为一张数据卡片：
<img class='lires-manual-screenshot' 
    style='width: 100%'
    src='https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/pic/lires-datacard-dark-v1.3.0.png' 
    alt='lires-datacard'>

数据卡片包含了文献标题和作者的基本信息以及操作按钮：
- 阅读器（Reader）：点击`Reader`按钮，可以打开该阅读器对文献信息阅读，同时记录笔记。
- 链接（Link）：点击`Link`按钮，可以在新窗口打开文献链接，当文献没有URL字段时不显示。
- 概览（Summary）：点击`Summary`按钮，可以显示文献的详细信息，尝试使用AI进行总结。
- 引用（Cite）：点击`Cite`按钮，可以显示数种引用格式，点击即可复制。
- 操作（Actions）：点击`Actions`按钮，可以展开操作菜单，包含了编辑条目信息、添加和删除文档、 以及删除条目等操作。

通过点击`Actions`和`Abstract`按钮，可将数据卡片完全展开如下：
<img class='lires-manual-screenshot' 
    style='width: 100%'
    src='https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/pic/lires-datacardExpand-dark-v1.3.0.png' 
    alt='lires-datacardExpand'>

摘要（Abstract）处用于填入文献的摘要信息，点击摘要正文部分即可进行编辑，当编辑完成后自动保存。

概览（Summary）界面中展示了包括全部作者、期刊、数据大小等详细信息，尝试使用AI进行自动总结， 并基于语义搜索展示文献库中所有最相关文献。下图是概览界面的展示：
<img class='lires-manual-screenshot' 
    style='width: 100%'
    src='https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/pic/lires-datacardSummary-dark-v1.3.0.png' 
    alt='lires-datacardSummary'>


若文献库中有同名作者，会在作者名后面标注数字，点击数字即可展开作者的其他条目数据卡片。

---
::: info
待完善
:::