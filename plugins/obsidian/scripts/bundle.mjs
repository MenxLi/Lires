import fs from 'fs-extra';
import path from 'path';
import {fileURLToPath} from 'url';

const neededFiles = [
    'styles.css',
    'manifest.json',
    'versions.json',
];

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcRoot = path.resolve(__dirname, '..');
const distDir = path.resolve(srcRoot, 'dist');
const projectRoot = path.resolve(srcRoot, '../..');
const serverAssetDir = path.resolve(projectRoot, 'lires_server/assets');
const assetDestDir = path.resolve(serverAssetDir, 'obsidian-plugin');

neededFiles.forEach(file => {
    fs.copy(`./${file}`, `${distDir}/${file}`)
        .catch(err => console.error(err));
})
console.info('Copied needed files to dist dir');

// check if path is correct
if (!fs.existsSync(serverAssetDir)) {
    console.error(`dist dir ${distDir} does not exist`);
    process.exit(1);
}
// if assetDestDir does exist, remove it
if (fs.existsSync(assetDestDir)) {
    console.info(`Removing ${assetDestDir}`);
    fs.removeSync(assetDestDir);
    fs.mkdirSync(assetDestDir);
}

// copy dist to lires_server/assets/obsidian-plugin,
// ignore the 'data.json' file
fs.copy(distDir, assetDestDir, {
    filter: (src, dest) => {
        return !src.endsWith('data.json');
    }
}).then(() => {
    console.info(`Copied dist to ${assetDestDir}`);
}).catch(err => console.error(err));
