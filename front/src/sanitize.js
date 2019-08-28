import sanitizeHtml from "sanitize-html"

const allowedTags = [
  "h3",
  "h4",
  "h5",
  "h6",
  "blockquote",
  "p",
  "a",
  "ul",
  "ol",
  "nl",
  "li",
  "b",
  "i",
  "strong",
  "em",
  "strike",
  "code",
  "hr",
  "br",
  "div",
  "table",
  "thead",
  "caption",
  "tbody",
  "tr",
  "th",
  "td",
  "pre",
  "iframe"
]
const allowedAttributes = {
  a: ["href", "name", "target"],
  // We don't currently allow img itself by default, but this
  // would make sense if we did. You could add srcset here,
  // and if you do the URL is checked for safety
  img: ["src"]
}

export default function sanitize(input) {
  return sanitizeHtml(input, {allowedAttributes, allowedAttributes})
}
