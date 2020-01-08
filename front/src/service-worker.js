// This is the code piece that GenerateSW mode can't provide for us.
// This code listens for the user's confirmation to update the app.
self.addEventListener('message', (e) => {
  if (!e.data) {
    return;
  }

  switch (e.data) {
    case 'skipWaiting':
      self.skipWaiting();
      break;
    default:
      // NOOP
      break;
  }
});
workbox.core.clientsClaim();

// The precaching code provided by Workbox.
self.__precacheManifest = [].concat(self.__precacheManifest || []);
console.log('Files to be cached by service worker [before filtering]', self.__precacheManifest.length);
var excludedUrlsPrefix = [
  '/js/locale-',
  '/js/moment-locale-',
  '/js/admin',
  '/css/admin',
];
self.__precacheManifest = self.__precacheManifest.filter((e) => {
  return !excludedUrlsPrefix.some(prefix => e.url.startsWith(prefix))
});
console.log('Files to be cached by service worker [after filtering]', self.__precacheManifest.length);
// workbox.precaching.suppressWarnings(); // Only used with Vue CLI 3 and Workbox v3.
workbox.precaching.precacheAndRoute(self.__precacheManifest, {});
