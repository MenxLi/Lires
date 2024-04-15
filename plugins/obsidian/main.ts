import { App, MarkdownView, Modal, Plugin, PluginSettingTab, Setting, MarkdownRenderer } from 'obsidian';
import { DataInfoT } from '../../lires_web/src/api/protocol';
import type { UserInfo } from '../../lires_web/src/api/protocol';
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

async function getDataInfo(uids: string[], api: LiresAPI): Promise<(DataInfoT | undefined)[]>{
	const promises = uids.map(async uid => {
		if (!summaryStore.has(uid)){
			const data = await api.reqDatapointSummary(uid);
			if (data){ summaryStore.set(uid, data); }
		}
		return summaryStore.get(uid);
	})
	return await Promise.all(promises);
}

export default class LiresPlugin extends Plugin {
	settings: PluginSettings;
	api: LiresAPI;
	userInfo: UserInfo;
	view: MarkdownView;

	async onload() {
		await this.loadSettings();
		// This adds a settings tab so the user can configure various aspects of the plugin
		this.addSettingTab(new LiresSettingTab(this.app, this));
		this.api = new LiresAPI().init(() => this.settings.endpoint, () => this.settings.credential);
		console.log('loading Lires plugin, time: ', Date.now());

		this.api.reqUserInfo().then((userInfo) => {
			this.userInfo = userInfo;
		});

		this.registerMarkdownCodeBlockProcessor('lires-cite', (source, el, ctx) => {
			// source is the content of the code block
			// each line is a uuid of the data
			const uids = source.split('\n').filter(uid => uid.length > 0);
			getDataInfo(uids, this.api).then((dInfos) => {
				for (const dInfo of dInfos){
					if (dInfo){
						el.appendChild(getCitationLineElem(this, dInfo));
					}
				}
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
		this.registerMarkdownCodeBlockProcessor('lires-ref', (source, el, ctx) => {
			// source is the content of the code block
			// each line is a uuid of the data
			const uids = source.split('\n').filter(uid => uid.length > 0);
			getDataInfo(uids, this.api).then((dInfos) => {
				for (const dInfo of dInfos){
					if (dInfo){
						el.appendChild(getReferenceLineElem(this, dInfo));
					}
				}
			})
		})

	}
	onunload() {}
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
		getDataInfo(this.uids, this.plugin.api).then(
			(dInfos) => {
				for (const dInfo of dInfos){
					if (dInfo){ contentEl.appendChild(getReferenceLineElem(this.plugin, dInfo)); }
				}
			}
		);
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
	elem.classList.add('lires-cite-line');

	const citeUID = document.createElement('span');
	citeUID.classList.add('lires-cite-uuid');
	citeUID.innerText = data.uuid;

	const dotElem = document.createElement('span');
	dotElem.innerText = '•';
	dotElem.style.marginRight = '0.5em';
	elem.appendChild(dotElem);

	const citeSpan = document.createElement('span');
	citeSpan.classList.add('lires-cite');
	citeSpan.innerText = data.author + ` (${data.year})` + ` ${data.title}`;
	citeSpan.style.marginTop = '0em';

	const citeElem = document.createElement('div');
	citeElem.style.display = 'flex';
	citeElem.style.flexDirection = 'row';
	citeElem.appendChild(dotElem);
	citeElem.appendChild(citeSpan);

	elem.appendChild(citeUID);
	elem.appendChild(citeElem);
	return elem;
}

function getReferenceLineElem(plugin: LiresPlugin, data: DataInfoT){
	const elem = document.createElement('div');
	elem.classList.add('lires-ref');

	const uuid = document.createElement('span');
	uuid.classList.add('lires-ref-uuid');
	uuid.innerText = 'lires:'+ data.uuid;
	elem.appendChild(uuid);
	elem.appendChild(document.createElement('br'));

	const title = document.createElement('h3');
	title.classList.add('lires-ref-title');
	title.innerText = data.title;
	elem.appendChild(title);

	const infoElem = document.createElement('div');
	infoElem.classList.add('lires-ref-info');
	infoElem.style.marginLeft = '1em';
	infoElem.style.marginTop = '0.5em';

	if (data.publication){
		const publication = document.createElement('span');
		publication.classList.add('lires-ref-publication');
		publication.innerText = `(${data.year}) ` + data.publication;
		infoElem.appendChild(publication);
		infoElem.appendChild(document.createElement('br'));
	}

	const authors = document.createElement('span');
	authors.classList.add('lires-ref-authors');
	// authors.appendChild(document.createTextNode('Authors: '));
	for (const author of data.authors){
		const authorElem = document.createElement('span');
		authorElem.classList.add('lires-ref-author');
		authorElem.innerText = author;
		if (author !== data.authors[data.authors.length-1]){
			authorElem.innerText += '; ';
		}
		authors.appendChild(authorElem);
	}
	infoElem.appendChild(authors);
	infoElem.appendChild(document.createElement('br'));

	const abstractDetail = document.createElement('details');
	abstractDetail.classList.add('lires-ref-detail');
	const summaryAbstract = document.createElement('summary');
	summaryAbstract.innerText = 'Abstract';
	abstractDetail.appendChild(summaryAbstract);
	const abstract = document.createElement('p');
	abstract.classList.add('lires-ref-detail-p');
	function onUnfoldAbstract(evt: Event){
		// abstractDetail.removeEventListener('toggle', onUnfold);
		if (!evt.target || !(evt.target instanceof HTMLDetailsElement)) return;
		if (!evt.target.open){ return; }
		abstract.innerHTML = 'Loading...';
		plugin.api.reqDatapointAbstract(data.uuid).then((text) => {
			if (text !== ''){ abstract.innerText = text; }
			else { abstract.innerText = 'Not available'; }
		})
	}
	abstractDetail.addEventListener('toggle', onUnfoldAbstract);
	abstractDetail.appendChild(abstract);
	infoElem.appendChild(abstractDetail);

	const noteDetail = document.createElement('details');
	noteDetail.classList.add('lires-ref-detail');
	const summaryNote = document.createElement('summary');
	summaryNote.innerText = 'Note';
	noteDetail.appendChild(summaryNote);
	const note = document.createElement('div');
	note.classList.add('lires-ref-detail');
	function onUnfoldNote(evt: Event){
		if (!evt.target || !(evt.target instanceof HTMLDetailsElement)) return;
		if (!evt.target.open){ return; }
		note.innerHTML = 'Loading...';
		note.style.maxWidth = '100%';
		plugin.api.reqDatapointNote(data.uuid).then((text) => {
			if (text !== ''){
				note.innerHTML = '';
				text = plugin.api.parseMarkdown(
					plugin.settings.endpoint,
					text, data, plugin.userInfo
				);
				MarkdownRenderer.render(
					plugin.app, text, note, '__none_exist__', plugin
				);
			}
			else { note.innerText = 'Not available'; }
		})
	}
	noteDetail.addEventListener('toggle', onUnfoldNote);
	noteDetail.appendChild(note);

	infoElem.appendChild(getLinkSpan({
		url: plugin.settings.endpoint+'#reader/'+data.uuid,
		text: 'reader'
	}));
	
	if (data.has_file){
		infoElem.appendChild(getLinkSpan({
			url: plugin.settings.endpoint+'/doc/'+data.uuid + '?_u=' + plugin.userInfo.id,
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

	if (data.has_abstract){ infoElem.appendChild(abstractDetail); }
	if (data.note_linecount){ infoElem.appendChild(noteDetail); }

	elem.appendChild(infoElem);

	return elem;
}