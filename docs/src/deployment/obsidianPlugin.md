
# Obsidian Plugin
Build the [Obsidian](https://obsidian.md/) plugin.

## Installation
Build the plugin with:
```bash
make obsidian-build
```

Then, copy everything under the `plugins/obsidian/dist` directory 
to your Obsidian plugins directory, 
i.e.
```sh
mkdir -p <YOUR_VAULT>/.obsidian/plugins/lires
cp plugins/obsidian/dist/* <YOUR_VAULT>/.obsidian/plugins/lires/
```

## Enable the plugin
Following [the guide](https://docs.obsidian.md/Plugins/Getting+started/Build+a+plugin#Step+3+Enable+the+plugin), do:

1. Open Obsidian
2. Go to `Settings` -> `Community plugins`
3. Select `Turn on community plugins` if you haven't already
4. Enable the `Lires` plugin

## Usage
Please refer to the [user manual](../manual/obsidianPlugin.md) for the usage of the plugin.
