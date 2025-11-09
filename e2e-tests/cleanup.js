/**
 * Cleanup Script for E2E Tests
 * Removes all test files and generated reports
 */

const fs = require('fs');
const path = require('path');

console.log('🧹 Cleaning up E2E test files...\n');

// Directories to clean
const dirsToClean = [
  'reports',
  'test-results',
  'playwright-report'
];

// Remove directories
dirsToClean.forEach(dir => {
  const dirPath = path.join(__dirname, dir);
  if (fs.existsSync(dirPath)) {
    fs.rmSync(dirPath, { recursive: true, force: true });
    console.log(`✓ Removed ${dir}/`);
  }
});

console.log('\n✨ Cleanup complete!');
console.log('\n💡 To delete the entire e2e-tests directory, run:');
console.log('   rm -r e2e-tests  (Linux/Mac)');
console.log('   rmdir /s /q e2e-tests  (Windows CMD)');
console.log('   Remove-Item -Recurse -Force e2e-tests  (PowerShell)');
