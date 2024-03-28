import fs from 'fs-extra';

fs.copy('../docs/src/.vitepress/dist', './dist/documentation')
  .then(() => console.log('Documents copied successfully!'))
  .catch(err => console.error(err));
