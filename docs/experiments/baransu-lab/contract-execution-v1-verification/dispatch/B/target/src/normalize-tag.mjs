export function normalizeTag(input) {
  const tag = input.trim();
  if (tag === "") {
    throw new Error("EMPTY_TAG");
  }

  return tag.replace(/[A-Z]/g, (letter) =>
    String.fromCharCode(letter.charCodeAt(0) + 32),
  );
}
