/**
 * The museum's fonts (SIL Open Font License, bundled in web/public/fonts), loaded once for the boards, the neon sign
 * and the photo labels: a clear book serif for everything meant to be read, an elegant display serif for titles, a
 * calligraphy for the grand titles and a handwriting for the neon.
 */
export const TEXT = "Keepsakes Text";                    // Lora 500, 600 and 500 italic: easy to read, even small
export const SERIF = "Keepsakes Serif";                  // Cormorant Garamond
export const CALLIGRAPHY = "Keepsakes Calligraphy";      // Great Vibes
export const HAND = "Keepsakes Hand";                    // Dancing Script

let loading: Promise<void> | null = null;

export function loadFonts(url = "/fonts"): Promise<void> {
  return (loading ??= (async () => {
    const face = (family: string, file: string, weight = 400, style = "normal") =>
      `@font-face { font-family: "${family}"; font-weight: ${weight}; font-style: ${style}; src: url("${url}/${file}.woff2") format("woff2"); }`;
    const style = document.createElement("style");
    style.textContent = [
      face(TEXT, "lora-latin-500-normal", 500), face(TEXT, "lora-latin-600-normal", 600), face(TEXT, "lora-latin-500-italic", 500, "italic"),
      face(SERIF, "cormorant-garamond-latin-600-normal", 600), face(CALLIGRAPHY, "great-vibes-latin-400-normal"),
      face(HAND, "dancing-script-latin-500-normal", 500),
    ].join("\n");
    document.head.appendChild(style);
    const found = await Promise.all([
      `500 40px "${TEXT}"`, `600 40px "${TEXT}"`, `italic 500 40px "${TEXT}"`, `600 40px "${SERIF}"`, `40px "${CALLIGRAPHY}"`, `500 40px "${HAND}"`,
    ].map((font) => document.fonts.load(font)));
    if (found.some((faces) => !faces.length)) console.warn(`fonts: not all fonts found in ${url}, using the browser's own`);
  })());
}
