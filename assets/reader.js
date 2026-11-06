// Load unchanged figures from the original DOCX ZIP, avoiding duplicate assets.
// Only stored/deflated entries in this repository's bounded Word files are used.
(async () => {
  const images = [...document.querySelectorAll('img[data-docx-part]')];
  if (!images.length) return;
  try {
    const response = await fetch(document.body.dataset.document);
    if (!response.ok) throw new Error('Word download unavailable');
    const buffer = await response.arrayBuffer();
    if (buffer.byteLength > 10 * 1024 * 1024) throw new Error('Document exceeds reader limit');
    const bytes = new Uint8Array(buffer), view = new DataView(buffer);
    let end = bytes.length - 22;
    while (end >= Math.max(0, bytes.length - 65557) && view.getUint32(end, true) !== 0x06054b50) end--;
    if (end < 0) throw new Error('Missing ZIP directory');
    const count = view.getUint16(end + 10, true);
    let offset = view.getUint32(end + 16, true);
    const entries = new Map();
    for (let i = 0; i < count; i++) {
      if (view.getUint32(offset, true) !== 0x02014b50) throw new Error('Invalid ZIP directory');
      const nameLength = view.getUint16(offset + 28, true);
      const extra = view.getUint16(offset + 30, true), comment = view.getUint16(offset + 32, true);
      const name = new TextDecoder().decode(bytes.slice(offset + 46, offset + 46 + nameLength));
      entries.set(name, {method:view.getUint16(offset + 10,true), compressed:view.getUint32(offset + 20,true), size:view.getUint32(offset + 24,true), local:view.getUint32(offset + 42,true)});
      offset += 46 + nameLength + extra + comment;
    }
    for (const image of images) {
      const entry = entries.get(image.dataset.docxPart);
      if (!entry || entry.size > 5 * 1024 * 1024) throw new Error('Missing or oversized figure');
      const start = entry.local + 30 + view.getUint16(entry.local + 26,true) + view.getUint16(entry.local + 28,true);
      const compressed = bytes.slice(start,start + entry.compressed);
      let blob = new Blob([compressed],{type:image.dataset.mime});
      if (entry.method === 8) blob = await new Response(blob.stream().pipeThrough(new DecompressionStream('deflate-raw'))).blob();
      else if (entry.method !== 0) throw new Error('Unsupported compression');
      if (blob.size !== entry.size) throw new Error('Figure size mismatch');
      image.src = URL.createObjectURL(new Blob([blob],{type:image.dataset.mime}));
    }
  } catch (error) {
    document.getElementById('figure-status').textContent = 'Figures could not load in this browser. Download the original Word document to view them.';
  }
})();
