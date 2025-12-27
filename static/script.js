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
