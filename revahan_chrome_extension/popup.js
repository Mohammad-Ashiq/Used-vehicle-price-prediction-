const LOCAL_URL = "http://127.0.0.1:5000";
const CLOUD_URL = "https://lee-duncan-similarly-halifax.trycloudflare.com";

document.getElementById("openLocalBtn").addEventListener("click", () => {
  chrome.tabs.create({ url: LOCAL_URL });
});

document.getElementById("openCloudBtn").addEventListener("click", () => {
  chrome.tabs.create({ url: CLOUD_URL });
});
