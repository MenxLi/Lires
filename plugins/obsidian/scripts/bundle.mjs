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
const assetDestDir = path.resolve(projectRoot, 'lires_server/assets/obsidian-plugin');

neededFiles.forEach(file => {
    fs.copy(`./${file}`, `${distDir}/${file}`)
        .catch(err => console.error(err));
})
console.info('Copied needed files to dist dir');

// make another copy to asset dir
neededFiles.forEach(file => {
    fs.copy(`./${file}`, `${assetDestDir}/${file}`)
        .catch(err => console.error(err));
})
console.info('Copied needed files to asset dir');