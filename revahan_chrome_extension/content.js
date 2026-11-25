(function() {
  const LOCAL_URL = "https://revahan.onrender.com";
  const CLOUD_URL = "https://revahan.onrender.com";

  // Check if current search query contains "revahan"
  const urlParams = new URLSearchParams(window.location.search);
  const query = (urlParams.get("q") || "").toLowerCase();
  
  if (!query.includes("revahan") && !document.title.toLowerCase().includes("revahan")) {
    return;
  }

  console.log("[ReVahan Extension] Detected ReVahan search query:", query);

  function injectBanner() {
    if (document.getElementById("revahan-quick-card")) return;

    // Find insertion target on Google or Bing
    let target = document.querySelector("#rso") || 
                 document.querySelector("#center_col") || 
                 document.querySelector("#search") ||
                 document.querySelector("#b_results") || 
                 document.querySelector("main") ||
                 document.body;

    if (!target) return;

    const card = document.createElement("div");
    card.id = "revahan-quick-card";
    card.style.cssText = `
      margin: 16px 0 24px 0;
      padding: 20px 24px;
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      border: 2px solid #00f2fe;
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0, 242, 254, 0.25), 0 0 1px 1px rgba(255,255,255,0.1);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #ffffff;
      position: relative;
      z-index: 99999;
      animation: revahanFadeIn 0.4s ease-out;
    `;

    card.innerHTML = `
      <style>
        @keyframes revahanFadeIn {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .revahan-btn-primary {
          background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
          color: #0f172a !important;
          font-weight: 700;
          font-size: 14px;
          padding: 10px 22px;
          border-radius: 9999px;
          text-decoration: none !important;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          box-shadow: 0 4px 14px rgba(0, 242, 254, 0.4);
          transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .revahan-btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(0, 242, 254, 0.6);
          color: #000000 !important;
        }
        .revahan-btn-secondary {
          background: rgba(255, 255, 255, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: #e2e8f0 !important;
          font-weight: 600;
          font-size: 13px;
          padding: 9px 18px;
          border-radius: 9999px;
          text-decoration: none !important;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          transition: background 0.15s ease;
        }
        .revahan-btn-secondary:hover {
          background: rgba(255, 255, 255, 0.16);
          color: #ffffff !important;
        }
        .revahan-badge {
          background: rgba(0, 242, 254, 0.15);
          color: #38bdf8;
          font-size: 12px;
          padding: 4px 10px;
          border-radius: 6px;
          border: 1px solid rgba(56, 189, 248, 0.3);
          font-weight: 500;
        }
      </style>
      <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
        <div style="display: flex; align-items: center; gap: 16px;">
          <div style="width: 52px; height: 52px; border-radius: 12px; background: #0284c7; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.5);">
            🚗
          </div>
          <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
              <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">ReVahan AI System</h2>
              <span style="background: #10b981; color: #ffffff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 12px; text-transform: uppercase;">● Running Live</span>
            </div>
            <p style="margin: 0; font-size: 13px; color: #94a3b8; max-width: 580px;">
              India's premier AI Used Vehicle Price Predictor with 70+ top brands, 400+ models, and all 36 States/UTs.
            </p>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
          <a href="${LOCAL_URL}" target="_blank" class="revahan-btn-primary">
            <span>🚀 Open App (127.0.0.1:5000)</span>
          </a>
          <a href="${CLOUD_URL}" target="_blank" class="revahan-btn-secondary">
            <span>🌐 Live Cloud Link</span>
          </a>
        </div>
      </div>

      <div style="margin-top: 14px; pt: 12px; border-top: 1px solid rgba(255, 255, 255, 0.1); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding-top: 12px;">
        <span style="font-size: 12px; color: #64748b; font-weight: 600;">Quick Access:</span>
        <a href="${LOCAL_URL}#cars" target="_blank" class="revahan-badge">🚘 Cars (32 Brands)</a>
        <a href="${LOCAL_URL}#bikes" target="_blank" class="revahan-badge">🏍️ Bikes (20 Brands)</a>
        <a href="${LOCAL_URL}#lorries" target="_blank" class="revahan-badge">🚛 Commercial Lorries (10 Brands)</a>
        <a href="${LOCAL_URL}#autos" target="_blank" class="revahan-badge">🛺 Auto Rickshaws (8 Brands)</a>
        <a href="${LOCAL_URL}" target="_blank" class="revahan-badge">🎙️ Voice Assistant</a>
      </div>
    `;

    // Prepend to target container
    target.insertBefore(card, target.firstChild);
    console.log("[ReVahan Extension] Successfully injected ReVahan card into search page!");
  }

  // Attempt inject immediately and also on DOM updates
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectBanner);
  } else {
    injectBanner();
  }
  setTimeout(injectBanner, 600);
  setTimeout(injectBanner, 1500);
})();
