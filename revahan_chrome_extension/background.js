const LOCAL_URL = "http://127.0.0.1:5000";
const CLOUD_URL = "https://lee-duncan-similarly-halifax.trycloudflare.com";

// Set default omnibox suggestion
chrome.omnibox.setDefaultSuggestion({
  description: "🚗 Launch <match>ReVahan</match> - Used Vehicle Price Prediction System (<url>127.0.0.1:5000</url>)"
});

// Omnibox suggestions when user types after 'revahan '
chrome.omnibox.onInputChanged.addListener((text, suggest) => {
  const suggestions = [
    { content: LOCAL_URL, description: "🚀 Open <match>ReVahan</match> Local Web App (<url>127.0.0.1:5000</url>)" },
    { content: CLOUD_URL, description: "🌐 Open <match>ReVahan</match> Live Public Link (Cloudflare)" },
    { content: LOCAL_URL + "#predict", description: "🚘 Value a <match>Car, Bike, Lorry or Auto</match>" },
    { content: LOCAL_URL + "#assistant", description: "🎙️ Talk to <match>ReVahan AI Voice Assistant</match>" }
  ];
  suggest(suggestions);
});

// Omnibox enter
chrome.omnibox.onInputEntered.addListener((text, disposition) => {
  let targetUrl = LOCAL_URL;
  if (text.startsWith("http://") || text.startsWith("https://")) {
    targetUrl = text;
  } else if (text.trim().toLowerCase() === "cloud" || text.trim().toLowerCase() === "online") {
    targetUrl = CLOUD_URL;
  } else if (text.trim()) {
    targetUrl = LOCAL_URL + "?search=" + encodeURIComponent(text);
  }

  if (disposition === "currentTab") {
    chrome.tabs.update({ url: targetUrl });
  } else {
    chrome.tabs.create({ url: targetUrl });
  }
});
