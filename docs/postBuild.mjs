import path from 'path';
import fs from 'fs-extra';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// move dist to server assets
const dist = path.resolve(__dirname, '.vitepress', 'dist');
const assets = path.resolve(__dirname, '..', 'lires_server', 'assets');
const dest = path.resolve(assets, 'docs');

// check if path is correct
if (!fs.existsSync(assets) || !fs.existsSync(dist)) {
    console.error(`dist dir ${dist} or assets dir ${assets} does not exist`);
    process.exit(1);
}

// if dest does exist, remove it
if (fs.existsSync(dest)) {
    console.info(`Removing ${dest}`);
    fs.removeSync(dest);
    fs.mkdirSync(dest);
}

// copy dist to lires_server/assets/docs
fs.copy(dist, dest).then(() => {
    console.info(`Copied dist to ${dest}`);
}).catch(err => console.error(err));
