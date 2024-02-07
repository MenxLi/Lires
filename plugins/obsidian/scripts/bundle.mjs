import fs from 'fs-extra';

const neededFiles = [
    'styles.css',
    'manifest.json',
    'versions.json',
];

neededFiles.forEach(file => {
    fs.copy(`./${file}`, `./dist/${file}`)
        // .then(() => console.log(`${file} copied successfully!`))
        .catch(err => console.error(err));
})