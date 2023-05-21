const manifest = self.__WB_MANIFEST;
if (manifest) {
  // do nothing
}

self.addEventListener('install', function(event) {
  console.log('service worker install');
});

self.addEventListener('activate', function(event) {
  console.log('service worker activate');
});

self.addEventListener('fetch', event => {
  console.log(`fetch ${event.request.url}`);
});
