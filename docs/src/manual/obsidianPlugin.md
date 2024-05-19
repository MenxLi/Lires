
# Obsidian 插件
<!-- Reference Lires entries from the [Obsidian](https://obsidian.md/). -->
从 [Obsidian](https://obsidian.md/) 引用 Lires 条目。

## 安装
目前本插件尚未发布到 Obsidian 社区插件库，需要[从源码构建插件](../deployment/obsidianPlugin.md)
或从关于页面下载已构建的插件。

随后手动安装插件：
将插件文件夹拷贝到 Obsidian 插件文件夹中（`<vault>/.obsidian/plugins/`），
重启 Obsidian，并在设置中[启用插件](#启用插件)。

::: details 详细步骤
1. 下载并解压得到`lires-obsidian-plugin`文件夹
2. 将`lires-obsidian-plugin`文件夹拷贝到`<vault>/.obsidian/plugins/`文件夹中，其中`<vault>`是你的 Obsidian 笔记本文件夹（如`/Users/username/Documents/Obsidian/MyVault/.obsidian/plugins/`）。如在`.obsidian`中没有`plugins`文件夹，可以手动创建。
3. 重启 Obsidian
:::

<!-- ## Enable the plugin
Following [the guide](https://docs.obsidian.md/Plugins/Getting+started/Build+a+plugin#Step+3+Enable+the+plugin), do:

1. Open Obsidian
2. Go to `Settings` -> `Community plugins`
3. Select `Turn on community plugins` if you haven't already
4. Enable the `Lires` plugin -->

## 启用插件
参考[官方指南](https://docs.obsidian.md/Plugins/Getting+started/Build+a+plugin#Step+3+Enable+the+plugin)，进行如下操作：

1. 打开 Obsidian
2. 点击 `设置` -> `社区插件`
3. 如果尚未启用社区插件，选择 `启用社区插件`
4. 启用 `Lires` 插件


## 设置Lires账户信息
打开 Obsidian，点击设置 -> 社区插件 -> Lires -> 设置，输入你的 Lires 账户信息，重启 Obsidian。

## 使用
Lires 插件使用代码块形式引用Lires条目，
目前支持两种引用方式：

1. `lires-cite`：使用短名称引用条目  
2. `lires-ref`：生成引用条目的简介信息

![obsidian-plugin-gif](https://pic4.zhimg.com/v2-1963de23d479e77d4b904bd7d36b7f5f_b.webp)