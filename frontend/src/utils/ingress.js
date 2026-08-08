// Home Assistant ingress serves the app under /api/hassio_ingress/<token>/ and
// strips that prefix before the request reaches the server, so only the browser
// needs to know about it. Resolving against the document base covers both the
// desktop build (served from /) and the add-on.
const documentBase = () => globalThis.document?.baseURI
  || globalThis.location?.href
  || 'http://localhost/';

export const resolveUrl = (input) => (
  typeof input === 'string' && input.startsWith('/') && !input.startsWith('//')
    ? new URL(input.slice(1), documentBase()).href
    : input
);
