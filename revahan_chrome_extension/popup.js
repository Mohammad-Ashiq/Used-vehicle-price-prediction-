const LOCAL_URL = "https://revahan.onrender.com";
const CLOUD_URL = "https://revahan.onrender.com";

document.getElementById("openLocalBtn").addEventListener("click", () => {
  chrome.tabs.create({ url: LOCAL_URL });
});

document.getElementById("openCloudBtn").addEventListener("click", () => {
  chrome.tabs.create({ url: CLOUD_URL });
});
