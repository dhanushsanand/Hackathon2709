declare module 'marked' {
  export function parse(md: string): string;
  export const marked: { parse: (md: string) => string };
  export default marked;
}
