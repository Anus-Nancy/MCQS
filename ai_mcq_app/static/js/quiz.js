const form = document.getElementById("quiz-form");

if (form) {
  const stored = JSON.parse(localStorage.getItem("mcq-answers") || "{}");
  Object.entries(stored).forEach(([name, value]) => {
    const input = document.querySelector(`input[name="${name}"][value="${value}"]`);
    if (input) {
      input.checked = true;
    }
  });

  form.addEventListener("change", (event) => {
    if (event.target.matches("input[type='radio']")) {
      stored[event.target.name] = event.target.value;
      localStorage.setItem("mcq-answers", JSON.stringify(stored));
    }
  });

  form.addEventListener("submit", () => {
    localStorage.removeItem("mcq-answers");
  });
}
