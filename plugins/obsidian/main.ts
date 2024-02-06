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


		this.registerMarkdownCodeBlockProcessor('lires-cite', (source, el, ctx) => {
			// source is the content of the code block
			// each line is a uuid of the data
			const uids = source.split('\n').filter(uid => uid.length > 0);
			const promises = uids.map(async uid => {
				if (!summaryStore.has(uid)){
					const data = await this.api.reqDatapointSummary(uid);
					if (data){ summaryStore.set(uid, data); }
				}
				const data = summaryStore.get(uid);
				if (data){
					el.appendChild(getCitationLineElem(this, data));
				}
			})
			Promise.all(promises).then(() => {
				const linkDiv = document.createElement('div');
				linkDiv.style.width = '100%';
				linkDiv.style.display = 'flex';
				linkDiv.style.paddingRight = '1em';
				linkDiv.style.justifyContent = 'flex-end';
				linkDiv.appendChild(getLinkSpan({
					text: "details",
					clickHandler: (evt) => {
						new DetailModal(this, uids).open();
					}
				}))
				el.appendChild(linkDiv);
			})

		})
	}
	onunload() { }
	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}
	async saveSettings() {
		await this.saveData(this.settings);
	}
}


class BibtexModal extends Modal {
	data: DataInfoT;
	constructor(app: App, data: DataInfoT) {
		super(app);
		this.data = data;
	}

	onOpen() {
		const {contentEl} = this;
		const elem = document.createElement('textarea');
		elem.value = this.data.bibtex;
		elem.style.width = '100%';
		elem.style.height = '100%';
		elem.style.minHeight = '300px';
		elem.style.resize = 'none';
		elem.readOnly = true;
		contentEl.appendChild(elem);
	}

	onClose() {
		const {contentEl} = this;
		contentEl.empty();
	}
}

class DetailModal extends Modal {
	plugin: LiresPlugin;
	uids: string[];
	constructor(plugin: LiresPlugin, uids: string[]) {
		super(plugin.app);
		this.uids = uids;
		this.plugin = plugin;
	}

	onOpen() {
		const {contentEl} = this;
		this.uids.forEach(async uid => {
			const data = await this.plugin.api.reqDatapointSummary(uid);
			if (data){ contentEl.appendChild(getReferenceLineElem(this.plugin, data)); }
		});
	}

	onClose(): void {
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

function getLinkSpan({
	url = '' , text = '', clickHandler = null, startBracket = '[', endBracket = '] '
}: {
	url?: string,
	text?: string,
	clickHandler?: null | ((event: MouseEvent)=>void)
	startBracket?: string,
	endBracket?: string
} = {}){
	const span = document.createElement('span');
	span.classList.add('lires-cite-link');
	const link = document.createElement('a');
	link.classList.add('lires-cite-link');
	link.innerText = text;
	if (url){
		link.href = url;
	}
	if (clickHandler){
		link.onclick = clickHandler;
	}
	span.appendChild(document.createTextNode(startBracket));
	span.appendChild(link);
	span.appendChild(document.createTextNode(endBracket));
	return span;
}

function getCitationLineElem(plugin: LiresPlugin, data: DataInfoT){
	// a short string to be used in the citation in the form of APA
	const elem = document.createElement('div');
	elem.style.display = 'flex';
	const dotElem = document.createElement('span');
	dotElem.innerText = '•';
	dotElem.style.marginRight = '0.5em';
	elem.appendChild(dotElem);

	const citeElem = document.createElement('span');
	citeElem.classList.add('lires-cite');
	citeElem.innerText = data.author + ` (${data.year})` + ` ${data.title}`;
	elem.appendChild(citeElem);
	return elem;
}

function getReferenceLineElem(plugin: LiresPlugin, data: DataInfoT){
	const elem = document.createElement('div');
	elem.classList.add('lires-cite');
	const title = document.createElement('h3');
	title.classList.add('lires-cite-title');
	title.innerText = data.title+` (${data.year})`;
	elem.appendChild(title);

	const infoElem = document.createElement('div');
	infoElem.style.marginLeft = '1em';

	const uuid = document.createElement('span');
	uuid.classList.add('lires-cite-uuid');
	uuid.innerText = 'UID: ' + data.uuid;
	infoElem.appendChild(uuid);
	infoElem.appendChild(document.createElement('br'));

	if (data.publication){
		const publication = document.createElement('b');
		publication.classList.add('lires-cite-publication');
		publication.innerText = 'Publication: ' + data.publication;
		infoElem.appendChild(publication);
		infoElem.appendChild(document.createElement('br'));
	}

	const authors = document.createElement('span');
	authors.classList.add('lires-cite-authors');
	for (const author of data.authors){
		const authorElem = document.createElement('span');
		authorElem.classList.add('lires-cite-author');
		authorElem.innerText = 'Authors: ' + author;
		authors.appendChild(authorElem);
	}
	infoElem.appendChild(authors);
	infoElem.appendChild(document.createElement('br'));


	if (data.has_file){
		infoElem.appendChild(getLinkSpan({
			url: plugin.settings.endpoint+'/doc/'+data.uuid,
			text: 'doc'
		}));
	}
	
	if (data.url){
		infoElem.appendChild(getLinkSpan({
			url: data.url,
			text: 'url'
		}));
	}

	infoElem.appendChild(getLinkSpan({
		text: 'bibtex',
		clickHandler: (evt) => {
			new BibtexModal(plugin.app, data).open()
		}
	}));

	elem.appendChild(infoElem);
	return elem;
}