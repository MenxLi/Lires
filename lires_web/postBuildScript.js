import fs from 'fs-extra';

fs.copy('../docs', './dist/docs')
  .then(() => console.log('Documents copied successfully!'))
  .catch(err => console.error(err));
