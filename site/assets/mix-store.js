/* One local project. Audio and a settings recovery copy commit atomically in IndexedDB. */
(function () {
  const KEY = 'sb-mix-project-v1';
  let dbPromise;
  function db() {
    if (!dbPromise) dbPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open('sb-mix-v1', 1);
      request.onupgradeneeded = () => {
        request.result.createObjectStore('project');
        request.result.createObjectStore('clips');
      };
      request.onsuccess = () => {
        request.result.onversionchange = () => { request.result.close(); dbPromise = null; };
        resolve(request.result);
      };
      request.onerror = () => { dbPromise = null; reject(request.error); };
      request.onblocked = () => { dbPromise = null; reject(new Error('Close other Stickbeats tabs and retry.')); };
    });
    return dbPromise;
  }
  async function load() {
    const database = await db();
    return new Promise((resolve, reject) => {
      const tx = database.transaction(['project', 'clips'], 'readonly');
      const p = tx.objectStore('project').get('current');
      const keys = tx.objectStore('clips').getAllKeys();
      const values = tx.objectStore('clips').getAll();
      tx.oncomplete = () => {
        let settings = p.result;
        if (!settings) { try { settings = JSON.parse(localStorage.getItem(KEY)); } catch (_) {} }
        resolve({ settings, clips: new Map(keys.result.map((k, i) => [k, values.result[i]])) });
      };
      tx.onabort = () => reject(tx.error || new Error('Could not read the local project.'));
    });
  }
  async function save(settings, clips) {
    const database = await db();
    await new Promise((resolve, reject) => {
      const tx = database.transaction(['project', 'clips'], 'readwrite');
      tx.objectStore('project').put(settings, 'current');
      const store = tx.objectStore('clips');
      store.clear();
      for (const [file, clip] of clips) store.put(clip, file);
      tx.oncomplete = resolve;
      tx.onabort = () => reject(tx.error || new Error('Could not save the local project.'));
    });
    // IndexedDB is the recovery source if localStorage is unavailable or a page closes mid-write.
    try { localStorage.setItem(KEY, JSON.stringify(settings)); } catch (_) {}
  }
  window.MixStore = { load, save };
})();
