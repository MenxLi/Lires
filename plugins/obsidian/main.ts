import { App, MarkdownView, Modal, Plugin, PluginSettingTab, Setting } from 'obsidian';
import { DataInfoT } from '../../lires_web/src/api/protocalT';
import LiresAPI from './liresapi';

interface PluginSettings {
	endpoint: string;
	credential: string;
}

const DEFAULT_SETTINGS: PluginSettings = {
	endpoint: '',
	credential: ''
}

const summaryStore = new Map<string, DataInfoT>();

export default class LiresPlugin extends Plugin {
	settings: PluginSettings;
	api: LiresAPI;
	view: MarkdownView;

	async onload() {
		await this.loadSettings();
		// This adds a settings tab so the user can configure various aspects of the plugin
		this.addSettingTab(new LiresSettingTab(this.app, this));
		this.api = new LiresAPI().init(() => this.settings.endpoint, () => this.settings.credential);
		console.log('loading Lires plugin');
		this.registerMarkdownPostProcessor((el, ctx) => {
			function replaceCiteBlock(settings: PluginSettings, citeBlock: HTMLElement, summary: DataInfoT) {
				const summaryEl = document.createElement('a');
				summaryEl.href = `${settings.endpoint}/doc/${summary.uuid}`;
				summaryEl.innerText = `${summary.author} (${summary.year})`;
				summaryEl.title = summary.title;
				citeBlock.replaceWith(summaryEl);
			}
			const citeBlocks = Array.from(el.querySelectorAll('span.lires-cite')) as HTMLElement[];
			console.log('found', citeBlocks.length, 'cite blocks');
			for (const citeBlock of citeBlocks) {
				const inner = citeBlock.innerHTML.trim()
				// inner must start with 'lirs:'
				const uid = inner.slice(6);
				if (uid) {
					const summary = summaryStore.get(uid);
					if (summary) {
						console.log('using cached summary for', uid);
						replaceCiteBlock(this.settings, citeBlock, summary);
					}
					else{
						console.log('requesting summary for', uid);
						this.api.reqDatapointSummary(uid).then((summary) => {
							if (summary) {
								summaryStore.set(uid, summary);
								replaceCiteBlock(this.settings, citeBlock, summary);
							}
						});
					}
				}
			}
		});

	}
	onunload() { }
	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}
	async saveSettings() {
		await this.saveData(this.settings);
	}
}


class DatacardModal extends Modal {
	constructor(app: App) {
		super(app);
	}

	onOpen() {
		const {contentEl} = this;
		contentEl.setText('Woah!');
	}

	onClose() {
		const {contentEl} = this;
		contentEl.empty();
	}
}

class LiresSettingTab extends PluginSettingTab {
	plugin: LiresPlugin;

	constructor(app: App, plugin: LiresPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const {containerEl} = this;

		containerEl.empty();

		new Setting(containerEl)
			.setName('Endpoint')
			.setDesc('The url of the Lires endpoint.')
			.addText(text => text
				.setPlaceholder('https://example.com:8080')
				.setValue(this.plugin.settings.endpoint)
				.onChange(async (value) => {
					this.plugin.settings.endpoint = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Credential')
			.setDesc('It\'s a secret')
			.addText(text => text
				.setPlaceholder('Enter your secret')
				.setValue(this.plugin.settings.credential)
				.onChange(async (value) => {
					this.plugin.settings.credential = value;
					await this.plugin.saveSettings();
				}));
	}
}
