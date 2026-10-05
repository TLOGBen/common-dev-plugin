// The terminal's own color, for a cell that sets none.
export const DEFAULT = 0x01000000

// Little-endian u32 triplets [codePoint, fg, bg], base64 — the Raster's cells.
export function cells(grid: [number, number, number][]) {
  const bytes = new Uint8Array(grid.length * 12)
  const view = new DataView(bytes.buffer)
  grid.forEach(([cp, fg, bg], i) => {
    view.setUint32(i * 12, cp, true)
    view.setUint32(i * 12 + 4, fg, true)
    view.setUint32(i * 12 + 8, bg, true)
  })
  const abc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
  let out = ''
  for (let i = 0; i < bytes.length; i += 3) {
    const n = ((bytes[i] ?? 0) << 16) | ((bytes[i + 1] ?? 0) << 8) | (bytes[i + 2] ?? 0)
    out += abc.charAt((n >> 18) & 63) + abc.charAt((n >> 12) & 63)
    out += i + 1 < bytes.length ? abc.charAt((n >> 6) & 63) : '='
    out += i + 2 < bytes.length ? abc.charAt(n & 63) : '='
  }
  return out
}
