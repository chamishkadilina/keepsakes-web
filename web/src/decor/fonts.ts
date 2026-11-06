/**
 * The museum's three fonts (SIL Open Font License, bundled in web/public/fonts), loaded once for the love letter, the
 * quote board, the neon sign and the photo labels: a handwriting, a calligraphy and an elegant serif.
 */
export const HAND = "Keepsakes Hand";                    // Dancing Script
export const CALLIGRAPHY = "Keepsakes Calligraphy";      // Great Vibes
export const SERIF = "Keepsakes Serif";                  // Cormorant Garamond

let loading: Promise<void> | null = null;

export function loadFonts(url = "/fonts"): Promise<void> {
  return (loading ??= (async () => {
    const style = document.createElement("style");
    style.textContent = `@font-face { font-family: "${HAND}"; font-weight: 500; src: url("${url}/dancing-script-latin-500-normal.woff2") format("woff2"); }
      @font-face { font-family: "${CALLIGRAPHY}"; src: url("${url}/great-vibes-latin-400-normal.woff2") format("woff2"); }
      @font-face { font-family: "${SERIF}"; font-weight: 600; src: url("${url}/cormorant-garamond-latin-600-normal.woff2") format("woff2"); }`;
    document.head.appendChild(style);
    const found = await Promise.all([
      document.fonts.load(`500 40px "${HAND}"`), document.fonts.load(`40px "${CALLIGRAPHY}"`), document.fonts.load(`600 40px "${SERIF}"`),
    ]);
    if (found.some((faces) => !faces.length)) console.warn(`fonts: not all fonts found in ${url}, using the browser's own`);
  })());
}
