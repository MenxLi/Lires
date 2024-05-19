
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

## Usage
Please refer to the [user manual](../manual/obsidianPlugin.md) for the usage of the plugin.
