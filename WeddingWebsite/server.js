/*
 * Fallback local server for the Wedding Website (Node.js).
 * Usage:  node server.js [port]
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, 'www.dreamsinvite.com');
const PORT = parseInt(process.argv[2] || '8000', 10);
const START = '/dev-weds-ananya098f.html?test=';

const CLEAN_URLS = {
  '/': 'dev-weds-ananya098f.html',
  '/dev-weds-ananya': 'dev-weds-ananya.html',
  '/ethan-weds-lily': 'ethan-weds-lily.html',
  '/templates': 'templates7f3d.html',
  '/services': 'services.html',
  '/contact': 'contact.html',
  '/privacy': 'privacy.html',
  '/refund': 'refund.html',
};
const TYPES = {
  '.html':'text/html; charset=utf-8', '.js':'application/javascript; charset=utf-8',
  '.css':'text/css; charset=utf-8', '.json':'application/json', '.png':'image/png',
  '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.gif':'image/gif', '.svg':'image/svg+xml',
  '.ico':'image/x-icon', '.webmanifest':'application/manifest+json', '.mp4':'video/mp4',
  '.mp3':'audio/mpeg', '.woff2':'font/woff2', '.txt':'text/plain', '.xml':'application/xml',
  '.rsc':'text/x-component; charset=utf-8',
};

function resolveFile(urlPath) {
  const [rawPath, rawQuery = ''] = urlPath.split('?');
  let p = decodeURIComponent(rawPath);
  if (CLEAN_URLS[p]) p = '/' + CLEAN_URLS[p];
  else if (!path.extname(p)) {
    const slug = p.replace(/^\/+|\/+$/g, '');
    const rsc = slug + '.rsc';
    const candidate = slug + '.html';
    if (rawQuery.includes('_rsc') && fs.existsSync(path.join(ROOT, rsc))) p = '/' + rsc;
    else if (fs.existsSync(path.join(ROOT, candidate))) p = '/' + candidate;
  }
  const file = path.join(ROOT, p);
  return file === ROOT || file.startsWith(ROOT + path.sep) ? file : null;
}

http.createServer((req, res) => {
  const file = resolveFile(req.url);
  if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    return res.end('404 Not Found');
  }
  const stat = fs.statSync(file);
  const type = TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream';
  const headers = {
    'Content-Type': type,
    'Accept-Ranges': 'bytes',
    'Cache-Control': 'no-cache',
  };
  const range = req.headers.range;
  if (range) {
    const m = /bytes=(\d*)-(\d*)/.exec(range);
    if (m) {
      let start = m[1] ? parseInt(m[1], 10) : Math.max(0, stat.size - parseInt(m[2], 10));
      let end = m[2] && m[1] ? parseInt(m[2], 10) : stat.size - 1;
      end = Math.min(end, stat.size - 1);
      if (start > end || start >= stat.size) {
        res.writeHead(416, { 'Content-Range': `bytes */${stat.size}` });
        return res.end();
      }
      res.writeHead(206, { ...headers, 'Content-Range': `bytes ${start}-${end}/${stat.size}`, 'Content-Length': end - start + 1 });
      return fs.createReadStream(file, { start, end }).pipe(res);
    }
  }
  res.writeHead(200, { ...headers, 'Content-Length': stat.size });
  fs.createReadStream(file).pipe(res);
}).listen(PORT, '127.0.0.1', () => {
  console.log('Wedding Website is ready!');
  console.log(`Open: http://localhost:${PORT}${START}`);
  console.log('Press Ctrl+C to stop.');
});
