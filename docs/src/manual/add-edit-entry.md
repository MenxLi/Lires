
# 添加与编辑条目
将一条新条目添加到文献库中，或编辑已有条目的信息。

## 条目编辑窗口

通过点击主页右上角工具栏中的`添加条目 (New)`按钮，或点击扩展数据卡中的`Edit`按钮， 可以进入条目编辑页面。条目编辑页面中可编辑包括文献信息、标签和URL在内的条目信息。

下方展示了条目编辑界面，在界面左侧可以输入文献信息（目前支持bibtex、endnote和nbib格式）和URL，右侧可以添加标签。

在新建条目时会出现`Select document`按钮，可以通过点击该按钮或者拖拽上传文件， 文件将作为条目的附件，省去后续添加文档。

<img class='lires-manual-screenshot' 
    style='width: 20rem;'
    src='https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/pic/lires-newEntry-v1.4.3.png' 
    alt='lires-newEntry'>

::: tip
当数据卡片展开，并且鼠标悬停在数据卡片上时，可以使用空格键进入编辑界面
:::

## 文献信息录入
当上述窗口打开时，除了手动粘贴录入文献信息，还可使用如下方式：

1. 向信息输入框（或主页）内拖入文本文档（如bibtex文件），此时将会将文本文档内容读取并输入文献信息栏。
2. 当有文献索引号（如ArXiv ID、DOI）时，可以点击Bibtex标签旁的`from-source`按钮，此时将弹出如下界面，可使尝试使用文献索引号从网络获取文献信息。
3. 当需要完全手动输入时，可以点击Bibtex标签旁的`template`，此时可以选择插入bibtex模版，以辅助录入

## 标签录入
通过右侧的标签栏即可选择现有标签或添加新标签。
标签栏选择框内显示标签为文献库中所有标签的集合，通过点击即可选择现有标签。
标签支持多级嵌套，当需要添加新的多级标签时，需要使用->符号将层级标签相连，如下图所示：

<img class='lires-manual-screenshot' 
    style='width: 15rem;'
    src='https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/pic/lires-addTag-v1.3.0.png' 
    alt='lires-addTag'>

## URL录入
通过在URL栏内输入即可添加URL。