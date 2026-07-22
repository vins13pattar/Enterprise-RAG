const http = require('http');

const pages = [
  ['Chat', 'Streaming grounded answers with citations and retrieval diagnostics.'],
  ['Documents', 'Upload files, add URLs, inspect chunks, retry, delete, and re-index.'],
  ['Knowledge Bases', 'Configure workspaces, embeddings, chunking, retrieval, and instructions.'],
  ['Evaluation', 'Run RAG quality tests and compare strategies.'],
  ['Human Review', 'Approve, edit, or reject low-confidence answers.'],
  ['Observability', 'Metrics for latency, tokens, costs, errors, cache, and quality.'],
  ['Administration', 'Manage users, roles, audit logs, provider status, and health.'],
];

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Enterprise Knowledge Assistant</title>
  <style>
    body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #0f172a; }
    main { padding: 32px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
    section { background: white; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04); }
    h1 { margin-bottom: 8px; }
    h2 { margin-top: 0; font-size: 18px; }
    p { color: #475569; }
  </style>
</head>
<body>
  <main>
    <h1>Enterprise Knowledge Assistant</h1>
    <p>Modular RAG platform with ingestion, retrieval, generation, review, evaluation, and observability.</p>
    <div class="grid">
      ${pages.map(([title, description]) => `<section><h2>${title}</h2><p>${description}</p></section>`).join('')}
    </div>
  </main>
</body>
</html>`;

const port = Number(process.env.PORT || 3000);
http.createServer((_request, response) => {
  response.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  response.end(html);
}).listen(port, '0.0.0.0', () => {
  console.log(`Enterprise RAG web shell listening on ${port}`);
});
