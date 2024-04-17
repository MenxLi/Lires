import fs from 'fs-extra';
import path from 'path';

if (fs.existsSync('./dist-api')){
  const assetDir = '../lires_server/assets';
  const apiDestDir = path.resolve(assetDir, 'js-api');

  if (!fs.existsSync(assetDir)){
    console.error(`dist dir ${assetDir} does not exist`);
    process.exit(1);
  }
  if (fs.existsSync(apiDestDir)){
    fs.removeSync(apiDestDir);
  }
  fs.copy('./dist-api', apiDestDir)
    .then(() => console.log('API copied successfully!'))
    .catch(err => console.error(err));
}