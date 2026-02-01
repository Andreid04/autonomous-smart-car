const activeKeys = new Set();
const pressedDisplay = document.getElementById("pressed");
const speedDisplay = document.getElementById("speed");

function sendCommand(cmd) {
  fetch("/control", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cmd })
  })
    .then(r => r.json())
    .then(data => {
      if (data.speed !== undefined) {
        speedDisplay.textContent = "Speed: " + data.speed + "%";
      }
    })
    .catch(console.error);
}

function updatePressedDisplay() {
  pressedDisplay.textContent =
    "Pressed: " + Array.from(activeKeys).join(" ").toUpperCase();
}

document.addEventListener("keydown", (e) => {
  const key = e.key.toLowerCase();
  if (!["w", "a", "s", "d", "z", "c"].includes(key)) return;

  // If movement key
  if (["w", "a", "s", "d"].includes(key) && !activeKeys.has(key)) {
    activeKeys.add(key);
    sendCommand(key);
    updatePressedDisplay();
  }

  // Speed up/down
  if (key === "z") {
    sendCommand("inc_speed");
  }
  if (key === "c") {
    sendCommand("dec_speed");
  }
});

document.addEventListener("keyup", (e) => {
  const key = e.key.toLowerCase();

  if (["w", "a", "s", "d"].includes(key)) {
    activeKeys.delete(key);
    updatePressedDisplay();

    // If no keys are pressed → stop
    if (activeKeys.size === 0) {
      sendCommand("stop");
      return;
    }

    // Continue moving based on remaining keys
    const last = Array.from(activeKeys).pop();
    sendCommand(last);
  }
});

function startAudio() {
    const audio = document.getElementById('car-audio');
    const btn = document.querySelector('button[onclick="startAudio()"]');

    // 1. Immediately disable button to prevent double-clicks
    btn.disabled = true;
    btn.innerText = "⌛ Connecting...";
    btn.style.opacity = "0.6";

    // Use a hardcoded path since url_for doesn't work in .js files
    const audioUrl = "/audio?t=" + new Date().getTime();
    
    console.log("Attempting to connect to: " + audioUrl);
    audio.src = audioUrl;

    audio.play().then(() => {
        console.log("Playback started successfully");
        btn.innerText = "🔊 Audio Live";
        btn.style.background = "#6c757d";

        // 2. Buffer-skip logic: Keep audio as live as possible
        setInterval(() => {
            if (audio.buffered.length > 0) {
                const end = audio.buffered.end(0);
                const diff = end - audio.currentTime;
                // If we are more than 2 seconds behind the stream, jump to the end
                if (diff > 1.0) {
                    audio.currentTime = end - 0.1;
                }
            }
        }, 1000);

    }).catch(err => {
        console.error("Playback failed:", err);
        // If it fails here, it's usually a network/stream error, not a click error
    });
}


