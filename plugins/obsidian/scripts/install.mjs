import fs from 'fs-extra';

const distDir = new URL('../dist', import.meta.url).pathname; // Path: plugins/obsidian/dist/
console.log(`distDir: ${distDir}`);

// get the first argument passed to the script
const vault = process.argv[2];
if (vault === undefined) {
    console.log('Usage: node install.mjs <path_to_obsidian_vault>');
    process.exit(1);
}

/* @param {fs.PathLike} vault */
function checkPath(vault) {
    // make sure the vault exists
    if (!fs.existsSync(vault) || !fs.lstatSync(vault).isDirectory()) {
        console.log(`Vault does not exist: ${vault}`);
        return false;
    }
    // make sure the .obsidian directory exists
    const obsidianDir = `${vault}/.obsidian`;
    if (!fs.existsSync(obsidianDir)) {
        console.log(`.obsidian directory does not exist: ${obsidianDir}`);
        return false;
    }
    return obsidianDir;
}

// copy the dist directory to the vault's .obsidian/plugins directory
if (checkPath(vault)){
    const pluginsDir = `${vault}/.obsidian/plugins/lires`;
    if (fs.existsSync(pluginsDir)) {
        console.log(`Removing existing plugin directory: ${pluginsDir}`);
        fs.removeSync(pluginsDir);
    }
    fs.ensureDirSync(pluginsDir);
    fs.copy(distDir, pluginsDir)
        .then(() => console.log('Success! Plugin installed to: ' + pluginsDir))
        .catch(err => console.error(err));
}
else{
    process.exit(1);
}
