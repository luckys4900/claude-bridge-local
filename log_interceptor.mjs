const origFetch = global.fetch;
global.fetch = async (input, init = {}) => {
  const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
  if (url.includes("anthropic.com")) {
    process.stderr.write("[FETCH] " + url + "\n");
  }
  try {
    return await origFetch(input, init);
  } catch(e) {
    process.stderr.write("[FETCH_ERR] " + url + " => " + e.message + "\n");
    throw e;
  }
};
