let quizQuestions=[], career="", seconds=600, timerId=null, studentProfile={}, requiredSkills=[], history=[], answers={};

function esc(t){return String(t ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));}
function getCareer(){return document.getElementById("customCareer").value.trim() || document.getElementById("career").value.trim();}

async function startAssessment(){
 career=getCareer();
 if(!career){alert("Please select or enter your target career.");return;}
 const currentSkills=document.getElementById("currentSkills").value.trim();
 studentProfile={
   name:document.getElementById("studentName").value.trim()||"Student",
   education:document.getElementById("education").value.trim()||"Engineering Student",
   current_skills:currentSkills||"Not specified",
   academic_score:Number(document.getElementById("academicScore").value)||0,
   resume_text:document.getElementById("resumeText").value||"",
   job_description:document.getElementById("jobDescription").value||""
 };
 const res=await fetch("/api/questions",{method:"POST",headers:{"Content-Type":"application/json"},
 body:JSON.stringify({career,current_skills:currentSkills,job_description:studentProfile.job_description})});
 const data=await res.json();
 if(data.error){alert(data.error);return;}
 requiredSkills=data.skills||[]; history=[]; answers={}; quizQuestions=[];
 document.getElementById("profile").classList.add("hidden");
 document.getElementById("quiz").classList.remove("hidden");
 document.getElementById("quizTitle").textContent=career+" — Adaptive Assessment";
 await showQuestion(data.question);
 startTimer(); window.scrollTo({top:0,behavior:"smooth"});
}

async function showQuestion(q){
 if(!q){submitAssessment();return;}
 quizQuestions.push(q);
 const box=document.getElementById("questions");
 box.innerHTML=`<div class="question"><div class="adaptive-badge">🧠 Adaptive Question ${quizQuestions.length}</div>
 <h3>Q${quizQuestions.length}. ${esc(q.question)}</h3>
 <small>Skill: ${esc(q.skill)} &nbsp;•&nbsp; Difficulty: ${esc(q.difficulty)}</small>
 ${q.options.map(o=>`<label class="option"><input type="radio" name="currentQ" value="${esc(o)}"> ${esc(o)}</label>`).join("")}</div>`;
 document.getElementById("progress").textContent=`Question ${quizQuestions.length} of 15 • Skills: ${requiredSkills.join(", ")}`;
 document.getElementById("nextBtn").classList.remove("hidden");
 document.getElementById("submitBtn").classList.toggle("hidden",quizQuestions.length<5);
}

async function nextQuestion(){
 const q=quizQuestions[quizQuestions.length-1];
 const selected=document.querySelector('input[name="currentQ"]:checked');
 if(!selected){alert("Please select an answer.");return;}
 const correct=selected.value===getCorrectAnswerForCurrent(q.id);
 answers[q.id]=selected.value;
 history.push({id:q.id,skill:q.skill,difficulty:q.difficulty.toLowerCase(),correct});
 if(history.length>=15){submitAssessment();return;}
 const res=await fetch("/api/next_question",{method:"POST",headers:{"Content-Type":"application/json"},
 body:JSON.stringify({career,skills:requiredSkills,history,current_skills:studentProfile.current_skills,job_description:studentProfile.job_description})});
 const data=await res.json();
 if(!data.question){submitAssessment();return;}
 await showQuestion(data.question);
}

function getCorrectAnswerForCurrent(id){
 // The correct answer is fetched securely only after the answer is submitted.
 // The browser gets it from a one-time local answer map populated by /api/answer-check.
 // Fallback is handled by checkAnswer().
 return window._correctAnswers?.[id] || "";
}

async function checkAnswer(q,selected){
 const res=await fetch("/api/check_answer",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:q.id,answer:selected})});
 const d=await res.json(); return !!d.correct;
}

// Override nextQuestion with server-side answer checking.
async function nextQuestionSecure(){
 const q=quizQuestions[quizQuestions.length-1];
 const selected=document.querySelector('input[name="currentQ"]:checked');
 if(!selected){alert("Please select an answer.");return;}
 const correct=await checkAnswer(q,selected.value);
 answers[q.id]=selected.value;
 history.push({id:q.id,skill:q.skill,difficulty:q.difficulty.toLowerCase(),correct});
 if(history.length>=15){submitAssessment();return;}
 const res=await fetch("/api/next_question",{method:"POST",headers:{"Content-Type":"application/json"},
 body:JSON.stringify({career,skills:requiredSkills,history,current_skills:studentProfile.current_skills,job_description:studentProfile.job_description})});
 const data=await res.json();
 if(!data.question){submitAssessment();return;}
 showQuestion(data.question);
}

function startTimer(){
 clearInterval(timerId); seconds=600; updateTimer();
 timerId=setInterval(()=>{seconds--;updateTimer();if(seconds<=0){clearInterval(timerId);submitAssessment();}},1000);
}
function updateTimer(){let m=String(Math.floor(seconds/60)).padStart(2,"0"),s=String(seconds%60).padStart(2,"0");document.getElementById("timer").textContent=`${m}:${s}`;}

async function submitAssessment(){
 clearInterval(timerId);
 if(quizQuestions.length){
   const selected=document.querySelector('input[name="currentQ"]:checked');
   if(selected && !answers[quizQuestions[quizQuestions.length-1].id]){
     const q=quizQuestions[quizQuestions.length-1];
     answers[q.id]=selected.value;
     const correct=await checkAnswer(q,selected.value);
     history.push({id:q.id,skill:q.skill,difficulty:q.difficulty.toLowerCase(),correct});
   }
 }
 const res=await fetch("/api/evaluate",{method:"POST",headers:{"Content-Type":"application/json"},
 body:JSON.stringify({career,skills:requiredSkills,answers,profile:studentProfile})});
 const data=await res.json(); showResult(data);
}

function showResult(data){
 document.getElementById("quiz").classList.add("hidden");document.getElementById("result").classList.remove("hidden");
 document.getElementById("profileSummary").innerHTML=`<strong>👋 ${esc(data.profile.name)}</strong><br>🎓 ${esc(data.profile.education)} &nbsp; • &nbsp; 🎯 ${esc(data.career)}<br>🧩 Current Skills: ${esc(data.profile.current_skills)} &nbsp; • &nbsp; 📚 Academic: ${data.profile.academic_score}%`;
 document.getElementById("overall").textContent=data.overall_score+"%";document.getElementById("assessment").textContent=data.assessment_score+"%";
 document.getElementById("skillCards").innerHTML=data.skills.map(s=>`<div class="skill"><div class="skill-row"><strong>${esc(s.skill)}</strong><span>${s.score}% — ${s.level}</span></div><div class="bar"><div class="fill" style="width:${s.score}%"></div></div><small>${s.correct}/${s.total} correct</small></div>`).join("");
 document.getElementById("recommendations").innerHTML=data.recommendations.map((r,i)=>`<div>✨ <strong>Recommendation ${i+1}</strong><br>${esc(r)}</div>`).join("");
 document.getElementById("roadmap").innerHTML=data.roadmap.map(r=>`<div class="roadmap-card"><h4>🚀 ${esc(r.skill)} <span class="priority">${esc(r.priority)} Priority</span></h4><ol>${r.steps.map(s=>`<li>${esc(s)}</li>`).join("")}</ol></div>`).join("");
 const r=data.resume||{};
 document.getElementById("resumeAnalysis").innerHTML=`<h3>📄 Resume Skill Extraction</h3>
 ${r.match===null ? "<p>No resume text provided.</p>" : `<p><b>Resume Skill Match:</b> ${r.match}%</p><p><b>Detected:</b> ${esc((r.detected_skills||[]).join(", ")||"None")}</p><p><b>Missing:</b> ${esc((r.missing_skills||[]).join(", ")||"None")}</p>`}`;
 const j=data.job_match||{};
 document.getElementById("jobAnalysis").innerHTML=`<h3>💼 Job Description Matcher</h3>
 ${j.match===null ? "<p>No job description provided.</p>" : `<p><b>Job Requirement Match:</b> ${j.match}%</p><p><b>Detected:</b> ${esc((j.detected_skills||[]).join(", ")||"None")}</p><p><b>Missing:</b> ${esc((j.missing_skills||[]).join(", ")||"None")}</p>`}`;
 window.scrollTo({top:0,behavior:"smooth"});
}

document.addEventListener("DOMContentLoaded",()=>{
 document.getElementById("nextBtn").onclick=nextQuestionSecure;
 document.getElementById("submitBtn").onclick=submitAssessment;
 document.getElementById("customCareer").addEventListener("input",e=>{if(e.target.value.trim())document.getElementById("career").value="";});
});
