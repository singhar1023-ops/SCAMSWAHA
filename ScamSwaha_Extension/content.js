console.log("ScamSwaha Extension Active on WhatsApp Web! 🔥");

// Yahan apna Render wala Link daalna hai deploy hone ke baad
// For example: "https://scamswaha-ai.onrender.com/api/scan"
// Abhi ke liye localhost rakha hai testing ke liye
const SERVER_URL = "https://scamswaha.onrender.com/api/scan";

const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                let msgElements = node.querySelectorAll('.selectable-text span');
                if (msgElements.length === 0 && node.classList && node.classList.contains('selectable-text')) {
                    msgElements = [node];
                }
                
                msgElements.forEach(el => {
                    let text = el.innerText.trim();
                    if(text.length > 10 && !el.hasAttribute('data-scanned')) {
                        el.setAttribute('data-scanned', 'true');
                        checkScam(text, el);
                    }
                });
            }
        });
    });
});

setTimeout(() => {
    observer.observe(document.body, { childList: true, subtree: true });
}, 5000);

async function checkScam(text, element) {
    try {
        let response = await fetch(SERVER_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });
        let data = await response.json();
        
        if (data.score > 35) {
            let alertTag = document.createElement("span");
            let severity = data.score > 75 ? "CRITICAL" : "WARNING";
            let color = data.score > 75 ? "#FF1744" : "#FFD600";
            
            alertTag.innerHTML = ` 🚨 [SCAMSWAHA: ${data.score}% RISK - ${severity}]`;
            alertTag.style.color = color;
            alertTag.style.fontWeight = "bold";
            alertTag.style.backgroundColor = "rgba(0,0,0,0.85)";
            alertTag.style.padding = "2px 6px";
            alertTag.style.borderRadius = "5px";
            alertTag.style.marginLeft = "5px";
            alertTag.style.fontSize = "12px";
            alertTag.style.border = `1px solid ${color}`;
            alertTag.style.boxShadow = `0 0 5px ${color}`;
            
            element.appendChild(alertTag);
        }
    } catch (e) {
        console.log("ScamSwaha API is not running.", e);
    }
}
