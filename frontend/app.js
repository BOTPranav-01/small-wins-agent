const API_BASE_URL = ""; // Set this to the deployed API URL to use Amazon Bedrock.
const DEMO_PLAN = {
  headline: "Let's make this feel less heavy.",
  next_step: "Open the thing you are avoiding and write down the three words it must contain.",
  minutes: 7,
  why_it_matters: "A tiny outline replaces the blank page with somewhere to begin.",
  permission_slip: "You do not need to finish everything today. Starting counts.",
  when_done: "Take a sip of water and decide whether to stop or do one more tiny step."
};

const $ = (id) => document.getElementById(id);
const button = $("plan-button");

function showPlan(plan) {
  $("headline").textContent = plan.headline;
  $("minutes").textContent = `${plan.minutes} min`;
  $("next-step").textContent = plan.next_step;
  $("why").textContent = plan.why_it_matters;
  $("permission").textContent = `“${plan.permission_slip}”`;
  $("when-done").textContent = plan.when_done;
  $("result").hidden = false;
  $("result").scrollIntoView({ behavior: "smooth", block: "start" });
}

button.addEventListener("click", async () => {
  const thoughts = $("thoughts").value.trim();
  if (!thoughts) {
    $("status").textContent = "Give me the messy version first — it does not need to be polished.";
    $("thoughts").focus();
    return;
  }
  button.disabled = true;
  $("status").textContent = "Finding the kindest place to begin…";
  try {
    if (!API_BASE_URL) {
      await new Promise((resolve) => setTimeout(resolve, 650));
      showPlan(DEMO_PLAN);
      $("status").textContent = "Demo mode — connect the API for a live Bedrock response.";
    } else {
      const result = await fetch(API_BASE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thoughts, energy: $("energy").value, tone: $("tone").value })
      });
      const data = await result.json();
      if (!result.ok) throw new Error(data.error || "The agent could not respond.");
      showPlan(data.plan);
      $("status").textContent = "";
    }
  } catch (error) {
    $("status").textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

$("copy-button").addEventListener("click", async () => {
  await navigator.clipboard.writeText($("next-step").textContent);
  $("copy-button").textContent = "Copied — go make it tiny";
  setTimeout(() => { $("copy-button").textContent = "Copy my next step"; }, 2200);
});
