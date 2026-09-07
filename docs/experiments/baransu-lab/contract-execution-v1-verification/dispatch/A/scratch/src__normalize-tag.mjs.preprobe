export function normalizeTag(input) {
  const trimmed = input.trim();
  if (trimmed === "") {
    throw new Error("EMPTY_TAG");
  }
  return trimmed.replace(/[A-Z]/g, (character) => character.toLowerCase());
}
