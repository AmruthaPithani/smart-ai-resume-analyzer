let lastData = null;

document.getElementById("file").onchange = function () {
  document.getElementById("preview").src =
    URL.createObjectURL(this.files[0]);
};

async function analyzeResume() {
  let file = document.getElementById("file").files[0];
  let role = document.getElementById("role").value;

  let fd = new FormData();
  fd.append("file", file);
  fd.append("role", role);

  let res = await fetch("/analyze", { method: "POST", body: fd });
  let data = await res.json();

  if (!res.ok) return alert(data.error);

  lastData = data;

  document.getElementById("output").innerHTML = `
    <h2>Score: ${data.score}%</h2>
    <h3>ATS: ${data.ats}%</h3>
    <h3>Grade: ${data.grade}</h3>
    <p>Found: ${data.found.join(", ")}</p>
    <p>Missing: ${data.missing.join(", ")}</p>
    <p><b>AI Suggestions:</b> ${data.suggestion}</p>
  `;
}

async function downloadReport() {
  if (!lastData) return alert("Analyze first");

  let res = await fetch("/download", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(lastData)
  });

  let blob = await res.blob();
  let a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "report.pdf";
  a.click();
}