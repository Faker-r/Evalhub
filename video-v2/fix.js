const fs = require('fs');
const path = require('path');

const scenesDir = path.join(__dirname, 'src', 'scenes');
const audioFile = path.join(__dirname, 'src', 'Audio.tsx');

const filesToFixed = [
  ...fs.readdirSync(scenesDir).filter(f => f.endsWith('.tsx')).map(f => path.join(scenesDir, f)),
  audioFile
];

let filesChanged = 0;

for (const file of filesToFixed) {
  const originalContent = fs.readFileSync(file, 'utf8');
  let content = originalContent;
  
  // Replace \` with `
  content = content.replace(/\\`/g, '`');
  
  // Replace \${ with ${
  content = content.replace(/\\\$\{/g, '${');

  if (content !== originalContent) {
    fs.writeFileSync(file, content, 'utf8');
    filesChanged++;
    console.log(`Fixed ${path.basename(file)}`);
  }
}

console.log(`Finished fixing ${filesChanged} files.`);
