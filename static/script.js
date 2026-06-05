let lastData = null;
let skillChart = null;

// ---------------- PREVIEW PDF ----------------

document.getElementById("file").onchange = function () {

    const file = this.files[0];

    if(file){

        document
        .getElementById("preview")
        .src = URL.createObjectURL(file);

    }

};

// ---------------- ANALYZE ----------------

async function analyzeResume(){

    const file =
    document.getElementById("file").files[0];

    const role =
    document.getElementById("role").value;

    if(!file){

        alert("Please upload a resume.");

        return;
    }

    const btn =
    document.querySelector(".sidebar button");

    btn.disabled = true;

    btn.innerText = "Analyzing...";

    document.getElementById("output").innerHTML = `
    
    <div class="result-card">
    
    <h3>🤖 AI Analysis In Progress</h3>
    
    <p>
    Extracting resume data...
    Matching skills...
    Calculating ATS score...
    Generating recommendations...
    </p>
    
    </div>
    
    `;

    try{

        let fd = new FormData();

        fd.append("file", file);

        fd.append("role", role);

        fd.append("job_description",document.getElementById("jobDescription").value);

        let res = await fetch("/analyze", {

            method:"POST",

            body:fd

        });

        let data = await res.json();

        if(!res.ok){

            alert(data.error);

            return;
        }

        lastData = data;

        // ---------------- KPI CARDS ----------------

        document
        .getElementById("scoreCard")
        .innerText =
        data.score + "%";

        document
        .getElementById("atsCard")
        .innerText =
        data.ats + "%";

        document
        .getElementById("gradeCard")
        .innerText =
        data.grade;

        document
        .getElementById("skillCount")
        .innerText =
        data.found.length+"%";

        // ---------------- SKILLS ----------------

        const foundSkills =
        data.found
        .map(skill =>
        `<span class="skill found">${skill}</span>`)
        .join("");

        const missingSkills =
        data.missing
        .map(skill =>
        `<span class="skill missing">${skill}</span>`)
        .join("");

        // ---------------- QUESTIONS ----------------

        const questionsHtml =
        (data.questions || [])
        .map(q =>
        `<li>${q}</li>`)
        .join("");

        // ---------------- ALERTS ----------------

        const alertsHtml =
        (data.alerts || [])
        .map(a =>
        `<li>${a}</li>`)
        .join("");
        // ---------------- RESUME SECTION ANALYSIS ----------------
        const sectionsHtml =
            Object.entries(
                data.sections || {}
            )
            .map(
                ([name,status]) =>
                    `<li>${status ? "✅" : "❌"}${name}</li>`
            )
            .join("");


        // ---------------- OUTPUT ----------------

        document.getElementById("output").innerHTML = `
        <div class="result-card">

    <h3>📊 Resume Analysis Summary</h3>

    <p>
        Resume Score:
        <strong>${data.score}%</strong>
    </p>

    <p>
        ATS Score:
        <strong>${data.ats}%</strong>
    </p>

    <p>
        Grade:
        <strong>${data.grade}</strong>
    </p>

</div>

<div class="result-card">

    <h3>🤖 AI Role Prediction</h3>

    <p>

        Predicted Role:

        <strong>

        ${data.predicted_role || "Not Available"}

        </strong>

    </p>

    <p>

        Confidence:

        ${data.prediction_confidence || 0}%

    </p>

</div>

<div class="result-card">

    <h3>🎯 Job Description Match</h3>

    <p>

        Match Score:

        <strong>

        ${data.jd_score || 0}%

        </strong>

    </p>

    <p>

        Matched Keywords:

        ${(data.jd_matched || []).join(", ") || "None"}

    </p>

    <p>

        Missing Keywords:

        ${(data.jd_missing || []).join(", ") || "None"}

    </p>

</div>

<div class="result-card">

    <h3>✅ Matched Skills</h3>

    <div>

        ${foundSkills}

    </div>

</div>

<div class="result-card">

    <h3>❌ Missing Skills</h3>

    <div>

        ${missingSkills}

    </div>

</div>

<div class="result-card">

    <h3>🧠 AI Recommendations</h3>

    <p>

        ${data.suggestion
        .replace(/\n/g,"<br>")}

    </p>

</div>

<div class="result-card">

    <h3>🎤 Interview Questions</h3>

    <ul>

        ${questionsHtml}

    </ul>

</div>

<div class="result-card">

    <h3>🚨 Resume Anomaly Detection</h3>

    <ul>

        ${
            alertsHtml ||
            "<li>No major issues detected.</li>"
        }

    </ul>

</div>

<div class="result-card">

    <h3>📋 Resume Section Analysis</h3>

    <ul>

        ${sectionsHtml || "<li>No section data available</li>"}

    </ul>

</div>
        
        // ---------------- CHART ----------------

        createSkillChart(
            data.found.length,
            data.missing.length
        );

    }

    catch(err){

        console.log(err);

        alert("Something went wrong.");

    }

    finally{

        btn.disabled = false;

        btn.innerText =
        "🚀 Analyze Resume";
    }

}

// ---------------- SKILL CHART ----------------

function createSkillChart(found, missing){

    const ctx =
    document
    .getElementById("skillChart");

    if(skillChart){

        skillChart.destroy();

    }

    skillChart = new Chart(ctx,{

        type:"doughnut",

        data:{

            labels:[
                "Matched Skills",
                "Missing Skills"
            ],

            datasets:[{

                data:[
                    found,
                    missing
                ],

                backgroundColor:[
                    "#22c55e",
                    "#ef4444"
                ]

            }]

        },

        options:{

            responsive:true,

            plugins:{

                legend:{
                    position:"bottom"
                }

            }

        }

    });

}

// ---------------- DOWNLOAD REPORT ----------------

async function downloadReport(){

    if(!lastData){

        alert(
            "Analyze a resume first."
        );

        return;
    }

    let res =
    await fetch("/download",{

        method:"POST",

        headers:{

            "Content-Type":
            "application/json"

        },

        body:
        JSON.stringify(lastData)

    });

    let blob =
    await res.blob();

    let a =
    document.createElement("a");

    a.href =
    URL.createObjectURL(blob);

    a.download =
    "resume_report.pdf";

    a.click();
}
